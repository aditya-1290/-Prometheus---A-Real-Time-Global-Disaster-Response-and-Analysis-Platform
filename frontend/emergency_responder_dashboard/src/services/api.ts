import axios from 'axios';
import { 
  Disaster,
  DisasterUpdate,
  Resource,
  EmergencyRequest
} from '../types/api';

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api') as string;

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds
});

// Add authentication interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const emergencyService = {
  getAllEmergencies: () => api.get<EmergencyRequest[]>('/emergencies'),
  getEmergencyById: (id: string) => api.get<EmergencyRequest>(`/emergencies/${id}`),
  updateEmergencyStatus: (id: string, status: string) => 
    api.patch<EmergencyRequest>(`/emergencies/${id}`, { status }),
  assignResponder: (emergencyId: string, responderId: string) =>
    api.post<{ success: boolean }>(`/emergencies/${emergencyId}/assign`, { responderId }),
};

export const disasterService = {
  getAllDisasters: () => api.get<Disaster[]>('/disasters'),
  getDisasterById: (id: string) => api.get<Disaster>(`/disasters/${id}`),
  updateDisaster: (id: string, data: Partial<Disaster>) => 
    api.patch<Disaster>(`/disasters/${id}`, data),
  addUpdate: (id: string, update: Omit<DisasterUpdate, 'id' | 'disasterId' | 'createdAt'>) =>
    api.post<DisasterUpdate>(`/disasters/${id}/updates`, update),
  getUpdates: (id: string) => api.get<DisasterUpdate[]>(`/disasters/${id}/updates`),
};

export const resourceService = {
  getAllResources: () => api.get<Resource[]>('/resources'),
  allocateResource: (resourceId: string, emergencyId: string, quantity: number) =>
    api.post<{ success: boolean }>('/resources/allocate', {
      resourceId,
      emergencyId,
      quantity,
    }),
  updateResourceStatus: (resourceId: string, status: Resource['status']) =>
    api.patch<Resource>(`/resources/${resourceId}`, { status }),
  createResource: (data: Omit<Resource, 'id'>) => api.post<Resource>('/resources', data),
};

export const analyticsService = {
  getDisasterStatistics: () => 
    api.get<{
      total: number;
      active: number;
      byType: Record<string, number>;
      bySeverity: Record<string, number>;
      trend: {
        date: string;
        count: number;
      }[];
    }>('/analytics/disasters'),
  
  getResourceUtilization: () =>
    api.get<{
      available: number;
      allocated: number;
      byType: Record<string, { available: number; allocated: number }>;
      utilizationHistory: {
        date: string;
        utilized: number;
        available: number;
      }[];
    }>('/analytics/resources'),
  
  getResponseMetrics: () =>
    api.get<{
      averageResponseTime: number;
      resolvedEmergencies: number;
      pendingEmergencies: number;
      responseTimeByPriority: Record<string, number>;
      resolutionRateByType: Record<string, number>;
    }>('/analytics/response'),

  getAreaImpactMetrics: () =>
    api.get<{
      totalAffectedArea: number;
      populationImpacted: number;
      criticalInfrastructure: {
        type: string;
        count: number;
        status: string;
      }[];
      evacuationZones: {
        id: string;
        area: number;
        population: number;
        status: string;
      }[];
    }>('/analytics/impact'),

  getAlertMetrics: () =>
    api.get<{
      total: number;
      active: number;
      byType: Record<string, number>;
      bySeverity: Record<string, number>;
      responseRate: number;
      deliveryStats: {
        delivered: number;
        failed: number;
        pending: number;
      };
    }>('/analytics/alerts'),

  getPerformanceMetrics: (timeframe: 'day' | 'week' | 'month' | 'year') =>
    api.get<{
      responseTime: {
        average: number;
        trend: { date: string; value: number }[];
      };
      resourceEfficiency: {
        usage: number;
        waste: number;
        optimization: number;
      };
      coordinationScore: number;
      staffingEfficiency: {
        utilization: number;
        coverage: number;
        gaps: { shift: string; count: number }[];
      };
    }>(`/analytics/performance?timeframe=${timeframe}`),
};
