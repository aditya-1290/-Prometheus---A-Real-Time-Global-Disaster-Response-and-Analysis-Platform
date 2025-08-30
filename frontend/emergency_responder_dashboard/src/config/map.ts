export const MAP_CONFIG = {
  // Mapbox configuration
  mapbox: {
    apiKey: process.env.REACT_APP_MAPBOX_API_KEY || 'your_mapbox_api_key_here',
    styleUrl: 'mapbox://styles/mapbox/streets-v11',
    defaultCenter: [0, 0],
    defaultZoom: 2
  },
  
  // Tile layer configuration (OpenStreetMap as fallback)
  tileLayer: {
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19
  },

  // Custom marker colors
  markerColors: {
    disaster: {
      critical: '#dc2626',
      high: '#ea580c',
      medium: '#d97706',
      low: '#65a30d'
    },
    resource: {
      available: '#16a34a',
      allocated: '#ca8a04',
      depleted: '#dc2626'
    },
    shelter: {
      open: '#16a34a',
      full: '#ca8a04',
      closed: '#dc2626'
    }
  },

  // Map control options
  controls: {
    zoomControl: true,
    attributionControl: true,
    scaleControl: true
  },

  // Clustering configuration
  clustering: {
    enabled: true,
    maxClusterRadius: 50,
    spiderfyOnMaxZoom: true
  }
};
