import { Alert } from '../types/api';
import { api } from './api';

export const alertService = {
  getAllAlerts: () => api.get<Alert[]>('/alerts'),
  getAlertById: (id: string) => api.get<Alert>(`/alerts/${id}`),
  createAlert: (data: Omit<Alert, 'id' | 'createdAt'>) => api.post<Alert>('/alerts', data),
  updateAlert: (id: string, data: Partial<Alert>) => api.patch<Alert>(`/alerts/${id}`, data),
  deleteAlert: (id: string) => api.delete<{ success: boolean }>(`/alerts/${id}`),
  
  // Alert preferences
  getUserAlertPreferences: () => api.get<{ preferences: Record<string, boolean> }>('/alerts/preferences'),
  updateUserAlertPreferences: (preferences: Record<string, boolean>) =>
    api.put<{ success: boolean }>('/alerts/preferences', preferences),
};
