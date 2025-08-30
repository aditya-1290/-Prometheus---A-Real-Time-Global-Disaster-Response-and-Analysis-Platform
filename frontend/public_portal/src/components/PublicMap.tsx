import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Disaster } from '@/types/api';

interface PublicMapProps {
  disasters?: Disaster[];
  center?: [number, number];
  zoom?: number;
  onLocationSelect?: (lat: number, lng: number) => void;
}

const PublicMap: React.FC<PublicMapProps> = ({
  disasters = [],
  center = [0, 0],
  zoom = 2,
  onLocationSelect
}) => {
  const mapRef = useRef<L.Map | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current && !mapRef.current) {
      mapRef.current = L.map(containerRef.current).setView(center, zoom);

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
      }).addTo(mapRef.current);

      if (onLocationSelect) {
        mapRef.current.on('click', (e: L.LeafletMouseEvent) => {
          onLocationSelect(e.latlng.lat, e.latlng.lng);
        });
      }
    }

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, [center, zoom, onLocationSelect]);

  useEffect(() => {
    if (mapRef.current) {
      // Clear existing markers
      mapRef.current.eachLayer((layer) => {
        if (layer instanceof L.Marker) {
          layer.remove();
        }
      });

      // Add disaster markers
      disasters.forEach((disaster) => {
        const severityColor = {
          low: '#2196f3',
          medium: '#ff9800',
          high: '#f44336',
          critical: '#b71c1c'
        }[disaster.severity] || '#757575';

        const marker = L.marker(
          [disaster.location.latitude, disaster.location.longitude],
          {
            icon: L.divIcon({
              className: 'custom-div-icon',
              html: `
                <div style="
                  background-color: ${severityColor};
                  width: 12px;
                  height: 12px;
                  border-radius: 50%;
                  border: 2px solid white;
                  box-shadow: 0 0 4px rgba(0,0,0,0.4);
                "></div>
              `,
              iconSize: [16, 16],
              iconAnchor: [8, 8]
            })
          }
        );

        marker
          .addTo(mapRef.current!)
          .bindPopup(`
            <div>
              <h3>${disaster.type}</h3>
              <p><strong>Status:</strong> ${disaster.status}</p>
              <p><strong>Severity:</strong> ${disaster.severity}</p>
              <p>${disaster.description}</p>
            </div>
          `);
      });

      // If there are disasters, fit bounds
      if (disasters.length > 0) {
        const bounds = L.latLngBounds(
          disasters.map(d => [d.location.latitude, d.location.longitude])
        );
        mapRef.current.fitBounds(bounds, { padding: [50, 50] });
      }
    }
  }, [disasters]);

  return (
    <div 
      ref={containerRef} 
      style={{ height: '500px', width: '100%', borderRadius: '8px' }}
      className="shadow-lg"
    />
  );
};

export default PublicMap;
