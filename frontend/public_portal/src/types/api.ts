export interface DisasterReport {
  latitude: number;
  longitude: number;
  type: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  affectedArea: {
    radius: number;
    unit: 'km' | 'mi';
  };
}

export interface EmergencyRequest {
  location: {
    latitude: number;
    longitude: number;
  };
  type: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  details: string;
  contactInfo: {
    name: string;
    phone?: string;
    email?: string;
  };
}

export interface ResourceRequest {
  resourceType: string;
  quantity: number;
  priority: 'low' | 'medium' | 'high' | 'critical';
  deliveryLocation: {
    latitude: number;
    longitude: number;
    address?: string;
  };
  requestedBy: {
    name: string;
    organization: string;
    contactInfo: {
      phone?: string;
      email?: string;
    };
  };
}

export interface Disaster {
  id: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'active' | 'contained' | 'resolved';
  location: {
    latitude: number;
    longitude: number;
  };
  affectedArea: {
    radius: number;
    unit: 'km' | 'mi';
  };
  description: string;
  createdAt: string;
  updatedAt: string;
}

export interface DisasterUpdate {
  id: string;
  disasterId: string;
  status: 'active' | 'contained' | 'resolved';
  description: string;
  createdAt: string;
}

export interface Resource {
  id: string;
  type: string;
  name: string;
  quantity: number;
  status: 'available' | 'allocated' | 'depleted';
  location: {
    latitude: number;
    longitude: number;
    address?: string;
  };
}
