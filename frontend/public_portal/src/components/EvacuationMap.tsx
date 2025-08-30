import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Box, Typography, Paper, List, ListItem, ListItemText, ListItemIcon } from '@mui/material';
import DirectionsIcon from '@mui/icons-material/Directions';
import WarningIcon from '@mui/icons-material/Warning';

interface EvacuationRoute {
  id: string;
  name: string;
  description: string;
  path: [number, number][];
  type: 'primary' | 'secondary' | 'emergency';
  status: 'open' | 'closed' | 'limited';
}

interface EvacuationMapProps {
  routes: EvacuationRoute[];
  userLocation?: [number, number];
  shelterLocations: Array<{
    id: string;
    name: string;
    location: [number, number];
    capacity: number;
    currentOccupancy: number;
    status: 'open' | 'full' | 'closed';
  }>;
}

const EvacuationMap: React.FC<EvacuationMapProps> = ({
  routes,
  userLocation,
  shelterLocations
}) => {
  const mapRef = useRef<L.Map | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [selectedRoute, setSelectedRoute] = useState<EvacuationRoute | null>(null);

  useEffect(() => {
    if (containerRef.current && !mapRef.current) {
      mapRef.current = L.map(containerRef.current).setView(
        userLocation || [0, 0],
        userLocation ? 13 : 2
      );

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
      }).addTo(mapRef.current);

      // Add user location marker if available
      if (userLocation) {
        L.marker(userLocation, {
          icon: L.divIcon({
            className: 'custom-div-icon',
            html: '<div style="background-color: #2196f3; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white;"></div>',
            iconSize: [16, 16],
            iconAnchor: [8, 8]
          })
        })
          .addTo(mapRef.current)
          .bindPopup('Your Location');
      }
    }

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, [userLocation]);

  useEffect(() => {
    if (mapRef.current) {
      // Clear existing routes
      mapRef.current.eachLayer((layer) => {
        if (layer instanceof L.Polyline || (layer instanceof L.Marker && layer.getPopup()?.getContent()?.includes('Shelter'))) {
          layer.remove();
        }
      });

      // Draw routes
      routes.forEach(route => {
        const color = route.type === 'primary' ? '#4caf50' : route.type === 'secondary' ? '#ff9800' : '#f44336';
        const dashArray = route.status === 'limited' ? '5, 10' : route.status === 'closed' ? '10, 10' : null;

        L.polyline(route.path, {
          color,
          weight: 4,
          opacity: route.status === 'closed' ? 0.5 : 1,
          dashArray
        })
          .addTo(mapRef.current!)
          .bindPopup(`
            <div>
              <h3>${route.name}</h3>
              <p>${route.description}</p>
              <p><strong>Status:</strong> ${route.status}</p>
            </div>
          `)
          .on('click', () => setSelectedRoute(route));
      });

      // Add shelter markers
      shelterLocations.forEach(shelter => {
        const color = shelter.status === 'open' ? '#4caf50' : shelter.status === 'full' ? '#ff9800' : '#f44336';
        
        L.marker(shelter.location, {
          icon: L.divIcon({
            className: 'custom-div-icon',
            html: `
              <div style="
                background-color: ${color};
                width: 16px;
                height: 16px;
                border-radius: 4px;
                border: 2px solid white;
                box-shadow: 0 0 4px rgba(0,0,0,0.4);
              "></div>
            `,
            iconSize: [20, 20],
            iconAnchor: [10, 10]
          })
        })
          .addTo(mapRef.current!)
          .bindPopup(`
            <div>
              <h3>${shelter.name}</h3>
              <p><strong>Status:</strong> ${shelter.status}</p>
              <p><strong>Capacity:</strong> ${shelter.currentOccupancy}/${shelter.capacity}</p>
            </div>
          `);
      });
    }
  }, [routes, shelterLocations]);

  return (
    <Box>
      <Paper elevation={3} sx={{ p: 2, mb: 2 }}>
        <Typography variant="h6" gutterBottom>
          Evacuation Routes & Shelters
        </Typography>
        <div 
          ref={containerRef} 
          style={{ height: '500px', width: '100%', borderRadius: '4px' }}
          className="shadow-lg mb-4"
        />
        {selectedRoute && (
          <Box mt={2}>
            <Typography variant="subtitle1" gutterBottom>
              Selected Route Information
            </Typography>
            <List>
              <ListItem>
                <ListItemIcon>
                  <DirectionsIcon />
                </ListItemIcon>
                <ListItemText 
                  primary={selectedRoute.name}
                  secondary={selectedRoute.description}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <WarningIcon />
                </ListItemIcon>
                <ListItemText 
                  primary="Status"
                  secondary={selectedRoute.status}
                />
              </ListItem>
            </List>
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default EvacuationMap;
