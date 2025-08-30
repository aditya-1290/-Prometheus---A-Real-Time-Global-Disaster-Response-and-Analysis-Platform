import { useState } from 'react';
import { DisasterReport } from '@/types/api';
import { disasterService } from '@/services/api';

const ReportForm: React.FC = () => {
  const [formData, setFormData] = useState<Partial<DisasterReport>>({
    type: '',
    description: '',
    severity: 'medium',
    latitude: 0,
    longitude: 0,
    affectedArea: {
      radius: 1,
      unit: 'km'
    }
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      await disasterService.reportDisaster(formData as DisasterReport);
      setSuccess(true);
      setFormData({
        type: '',
        description: '',
        severity: 'medium',
        latitude: 0,
        longitude: 0,
        affectedArea: {
          radius: 1,
          unit: 'km'
        }
      });
    } catch (err) {
      setError('Failed to submit report. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    if (name.includes('.')) {
      const [parent, child] = name.split('.');
      setFormData(prev => ({
        ...prev,
        [parent]: {
          ...prev[parent as keyof DisasterReport],
          [child]: value
        }
      }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="type" className="block text-sm font-medium">
          Disaster Type
        </label>
        <input
          type="text"
          id="type"
          name="type"
          value={formData.type}
          onChange={handleChange}
          required
          className="mt-1 block w-full rounded-md border border-gray-300 p-2"
        />
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium">
          Description
        </label>
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          required
          rows={4}
          className="mt-1 block w-full rounded-md border border-gray-300 p-2"
        />
      </div>

      <div>
        <label htmlFor="severity" className="block text-sm font-medium">
          Severity
        </label>
        <select
          id="severity"
          name="severity"
          value={formData.severity}
          onChange={handleChange}
          required
          className="mt-1 block w-full rounded-md border border-gray-300 p-2"
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="latitude" className="block text-sm font-medium">
            Latitude
          </label>
          <input
            type="number"
            id="latitude"
            name="latitude"
            value={formData.latitude}
            onChange={handleChange}
            required
            step="any"
            className="mt-1 block w-full rounded-md border border-gray-300 p-2"
          />
        </div>
        <div>
          <label htmlFor="longitude" className="block text-sm font-medium">
            Longitude
          </label>
          <input
            type="number"
            id="longitude"
            name="longitude"
            value={formData.longitude}
            onChange={handleChange}
            required
            step="any"
            className="mt-1 block w-full rounded-md border border-gray-300 p-2"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="affectedArea.radius" className="block text-sm font-medium">
            Affected Area Radius
          </label>
          <input
            type="number"
            id="affectedArea.radius"
            name="affectedArea.radius"
            value={formData.affectedArea?.radius}
            onChange={handleChange}
            required
            min="0"
            step="0.1"
            className="mt-1 block w-full rounded-md border border-gray-300 p-2"
          />
        </div>
        <div>
          <label htmlFor="affectedArea.unit" className="block text-sm font-medium">
            Unit
          </label>
          <select
            id="affectedArea.unit"
            name="affectedArea.unit"
            value={formData.affectedArea?.unit}
            onChange={handleChange}
            required
            className="mt-1 block w-full rounded-md border border-gray-300 p-2"
          >
            <option value="km">Kilometers</option>
            <option value="mi">Miles</option>
          </select>
        </div>
      </div>

      {error && (
        <div className="text-red-600 text-sm">{error}</div>
      )}

      {success && (
        <div className="text-green-600 text-sm">Report submitted successfully!</div>
      )}

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-blue-400"
      >
        {isSubmitting ? 'Submitting...' : 'Submit Report'}
      </button>
    </form>
  );
};

export default ReportForm;
