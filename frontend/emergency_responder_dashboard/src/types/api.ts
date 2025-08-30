export interface Disaster {
  id: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  location: {
    lat: number;
    lng: number;
    address?: string;
  };
  status: 'active' | 'contained' | 'resolved';
  description: string;
  affectedArea: number;
  population: number;
  createdAt: string;
  updatedAt: string;
}

export interface DisasterUpdate {
  id: string;
  disasterId: string;
  type: 'status' | 'severity' | 'area' | 'info';
  content: string;
  createdAt: string;
}

export interface Resource {
  id: string;
  type: string;
  name: string;
  quantity: number;
  status: 'available' | 'allocated' | 'maintenance' | 'depleted';
  location: {
    lat: number;
    lng: number;
    address?: string;
  };
  capabilities: string[];
  lastMaintenance?: string;
  nextMaintenance?: string;
}

export interface EmergencyRequest {
  id: string;
  type: string;
  status: 'pending' | 'assigned' | 'in_progress' | 'resolved' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'critical';
  location: {
    lat: number;
    lng: number;
    address?: string;
  };
  description: string;
  requesterId: string;
  assignedResponderId?: string;
  createdAt: string;
  updatedAt: string;
}

export interface Alert {
  id: string;
  type: 'warning' | 'danger' | 'info' | 'update';
  title: string;
  message: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  scope: 'public' | 'responders' | 'admin';
  location?: {
    lat: number;
    lng: number;
    radius: number;
  };
  createdAt: string;
  expiresAt?: string;
  isActive: boolean;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data: T;
  message?: string;
  error?: string;
}
