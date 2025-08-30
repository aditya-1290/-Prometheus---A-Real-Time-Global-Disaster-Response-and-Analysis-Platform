export const API_CONFIG = {
  baseUrl: (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api') as string,
  websocketUrl: (process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws') as string,
  
  // API endpoints
  endpoints: {
    disasters: {
      list: '/disasters',
      details: (id: string) => `/disasters/${id}`,
      create: '/disasters',
      update: (id: string) => `/disasters/${id}`,
      statistics: '/analytics/disasters'
    },
    
    emergency: {
      request: '/emergency/request',
      status: (id: string) => `/emergency/status/${id}`,
      list: '/emergency/requests',
      update: (id: string) => `/emergency/${id}`
    },
    
    resources: {
      available: '/resources/available',
      allocate: '/resources/allocate',
      list: '/resources',
      create: '/resources',
      update: (id: string) => `/resources/${id}`,
      statistics: '/analytics/resources'
    },
    
    alerts: {
      create: '/alerts',
      list: '/alerts',
      update: (id: string) => `/alerts/${id}`,
      delete: (id: string) => `/alerts/${id}`
    }
  },
  
  // Request configuration
  requestConfig: {
    headers: {
      'Content-Type': 'application/json'
    },
    timeout: 10000 // 10 seconds
  },

  // WebSocket event types
  wsEvents: {
    disaster: {
      update: 'disaster:update',
      new: 'disaster:new',
      statusChange: 'disaster:status'
    },
    emergency: {
      new: 'emergency:new',
      statusUpdate: 'emergency:status'
    },
    resource: {
      update: 'resource:update',
      allocation: 'resource:allocate'
    },
    alert: {
      new: 'alert:new',
      update: 'alert:update'
    }
  }
};
