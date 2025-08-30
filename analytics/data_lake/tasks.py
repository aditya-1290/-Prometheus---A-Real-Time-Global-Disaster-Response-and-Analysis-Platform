from celery import shared_task
import boto3
import pandas as pd
import json
from datetime import datetime
from django.conf import settings
from .models import Dataset, DatasetVersion, ProcessingJob

s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME
)

@shared_task
def ingest_data(source_id, data, format_type):
    """Ingest data into the data lake"""
    try:
        # Generate S3 path
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        s3_path = f'raw/{source_id}/{timestamp}.{format_type}'
        
        # Convert data to appropriate format
        if format_type == 'parquet':
            df = pd.DataFrame(data)
            data_bytes = df.to_parquet()
        elif format_type == 'json':
            data_bytes = json.dumps(data).encode()
        else:
            data_bytes = data
        
        # Upload to S3
        s3_client.put_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=s3_path,
            Body=data_bytes
        )
        
        # Create dataset record
        dataset = Dataset.objects.create(
            source_id=source_id,
            name=f'Data from source {source_id} at {timestamp}',
            description='Raw ingested data',
            format=format_type,
            s3_path=s3_path,
            size_bytes=len(data_bytes),
            row_count=len(data) if isinstance(data, list) else None
        )
        
        return dataset.id
    
    except Exception as e:
        print(f"Error ingesting data: {str(e)}")
        raise

@shared_task
def process_dataset(job_id):
    """Process a dataset based on job specifications"""
    try:
        job = ProcessingJob.objects.get(id=job_id)
        job.status = 'running'
        job.started_at = datetime.now()
        job.save()
        
        try:
            # Get source data
            source_path = job.source_dataset.s3_path
            response = s3_client.get_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=source_path
            )
            
            if job.source_dataset.format == 'parquet':
                df = pd.read_parquet(response['Body'])
            elif job.source_dataset.format == 'json':
                data = json.loads(response['Body'].read())
                df = pd.DataFrame(data)
            else:
                raise ValueError(f"Unsupported format: {job.source_dataset.format}")
            
            # Apply processing based on job type
            if job.job_type == 'aggregate':
                result = process_aggregation(df, job.parameters)
            elif job.job_type == 'transform':
                result = process_transformation(df, job.parameters)
            elif job.job_type == 'analyze':
                result = process_analysis(df, job.parameters)
            else:
                raise ValueError(f"Unknown job type: {job.job_type}")
            
            # Save results
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            result_path = f'processed/{job.job_type}/{timestamp}.parquet'
            
            s3_client.put_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=result_path,
                Body=result.to_parquet()
            )
            
            # Update job status
            job.status = 'completed'
            job.completed_at = datetime.now()
            job.result_location = result_path
            job.save()
            
        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
            job.save()
            raise
        
    except ProcessingJob.DoesNotExist:
        print(f"Job {job_id} not found")
    except Exception as e:
        print(f"Error processing dataset: {str(e)}")
        raise

def process_aggregation(df, parameters):
    """Perform aggregation operations"""
    group_by = parameters.get('group_by', [])
    agg_funcs = parameters.get('aggregations', {})
    return df.groupby(group_by).agg(agg_funcs).reset_index()

def process_transformation(df, parameters):
    """Apply transformations to the dataset"""
    operations = parameters.get('operations', [])
    
    for op in operations:
        if op['type'] == 'rename':
            df = df.rename(columns=op['mapping'])
        elif op['type'] == 'filter':
            df = df.query(op['condition'])
        elif op['type'] == 'select':
            df = df[op['columns']]
        # Add more transformation types as needed
    
    return df

def process_analysis(df, parameters):
    """Perform analysis on the dataset"""
    analysis_type = parameters.get('type')
    
    if analysis_type == 'summary_stats':
        return df.describe()
    elif analysis_type == 'correlation':
        return df.corr()
    elif analysis_type == 'time_series':
        return process_time_series(df, parameters)
    
    return df

def process_time_series(df, parameters):
    """Process time series data"""
    date_column = parameters.get('date_column')
    value_column = parameters.get('value_column')
    freq = parameters.get('frequency', 'D')
    
    df[date_column] = pd.to_datetime(df[date_column])
    return df.set_index(date_column)[value_column].resample(freq).agg(parameters.get('aggregation', 'mean'))
