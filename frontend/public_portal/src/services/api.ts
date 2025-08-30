import axios from 'axios';
import {
  Disaster,
  DisasterReport,
  DisasterUpdate,
  EmergencyRequest,
  Resource,
  ResourceRequest
} from '../types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const disasterService = {
  getAllDisasters: () => api.get<Disaster[]>('/disasters'),
  getDisasterById: (id: string) => api.get<Disaster>(`/disasters/${id}`),
  reportDisaster: (data: DisasterReport) => api.post<Disaster>('/disasters/report', data),
  getDisasterUpdates: (disasterId: string) => api.get<DisasterUpdate[]>(`/disasters/${disasterId}/updates`),
};

export const emergencyService = {
  requestHelp: (data: EmergencyRequest) => api.post<{ requestId: string }>('/emergency/help-request', data),
  getEmergencyStatus: (requestId: string) => api.get<{ status: string; details: string }>(`/emergency/status/${requestId}`),
};

export const resourceService = {
  getAvailableResources: () => api.get<Resource[]>('/resources/available'),
  requestResource: (data: ResourceRequest) => api.post<{ requestId: string }>('/resources/request', data),
};
