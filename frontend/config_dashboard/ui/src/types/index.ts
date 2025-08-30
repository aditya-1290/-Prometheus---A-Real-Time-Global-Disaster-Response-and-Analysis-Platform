// Common types for the application

export interface Alert {
  id: string;
  severity: 'critical' | 'warning' | 'info';
  message: string;
  timestamp: Date;
  service?: string;
  resolved: boolean;
}

export interface Service {
  id: string;
  name: string;
  status: 'healthy' | 'degraded' | 'down';
  lastChecked: Date;
  responseTime?: number;
  uptime?: number;
}

export interface MLModel {
  id: string;
  name: string;
  version: string;
  status: 'training' | 'ready' | 'deployed' | 'error';
  accuracy?: number;
  lastTrained?: Date;
}

export interface APIMetric {
  endpoint: string;
  method: string;
  responseTime: number;
  statusCode: number;
  timestamp: Date;
  errorRate?: number;
}

export interface DashboardStats {
  totalAlerts: number;
  activeAlerts: number;
  services: Service[];
  uptime: number;
  responseTime: number;
}

// Redux state types
export interface AppState {
  alerts: Alert[];
  services: Service[];
  mlModels: MLModel[];
  apiMetrics: APIMetric[];
  isLoading: boolean;
  error: string | null;
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  message: string;
  success: boolean;
}

// Form types
export interface AlertFilter {
  severity?: Alert['severity'];
  service?: string;
  resolved?: boolean;
  startDate?: Date;
  endDate?: Date;
}

export interface ServiceFilter {
  status?: Service['status'];
  name?: string;
}
