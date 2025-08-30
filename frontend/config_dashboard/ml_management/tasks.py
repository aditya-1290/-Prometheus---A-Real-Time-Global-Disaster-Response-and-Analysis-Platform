from celery import shared_task
from django.utils import timezone
import torch
from .models import MLModel, ModelMetrics, TrainingJob

@shared_task
def train_model(job_id):
    """Execute model training job"""
    job = TrainingJob.objects.get(id=job_id)
    model = job.model
    
    try:
        # Load training data
        train_data = load_training_data(job.training_data_path)
        val_data = load_training_data(job.validation_data_path)
        
        # Initialize model
        model_instance = initialize_model(model.model_type, job.hyperparameters)
        
        # Training loop
        metrics = train(model_instance, train_data, val_data, job.hyperparameters)
        
        # Save model artifacts
        save_model(model_instance, model.artifacts_path)
        
        # Log metrics
        ModelMetrics.objects.create(
            model=model,
            accuracy=metrics['accuracy'],
            precision=metrics['precision'],
            recall=metrics['recall'],
            f1_score=metrics['f1_score'],
            latency=metrics['latency']
        )
        
        # Update job status
        job.status = 'completed'
        job.end_time = timezone.now()
        job.save()
        
    except Exception as e:
        job.status = 'failed'
        job.end_time = timezone.now()
        job.error_message = str(e)
        job.save()

@shared_task
def evaluate_models():
    """Periodically evaluate deployed models"""
    deployed_models = MLModel.objects.filter(status='deployed')
    
    for model in deployed_models:
        try:
            # Load test data
            test_data = load_test_data(model.model_type)
            
            # Load model
            model_instance = load_model(model.artifacts_path)
            
            # Evaluate
            metrics = evaluate(model_instance, test_data)
            
            # Log metrics
            ModelMetrics.objects.create(
                model=model,
                accuracy=metrics['accuracy'],
                precision=metrics['precision'],
                recall=metrics['recall'],
                f1_score=metrics['f1_score'],
                latency=metrics['latency']
            )
            
        except Exception as e:
            print(f"Error evaluating model {model.name}: {e}")

@shared_task
def cleanup_old_models():
    """Archive old model versions"""
    # Get all models with newer versions
    active_models = MLModel.objects.filter(status='deployed')
    for model in active_models:
        # Find older versions of this model
        older_versions = MLModel.objects.filter(
            name=model.name,
            status='deployed',
            version__lt=model.version
        )
        # Deprecate older versions
        for old_version in older_versions:
            old_version.status = 'deprecated'
            old_version.save()
