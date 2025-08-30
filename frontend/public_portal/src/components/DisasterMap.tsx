import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

interface DisasterMapProps {
  onLocationSelect?: (lat: number, lng: number) => void;
  markers?: Array<{
    lat: number;
    lng: number;
    type: string;
    severity: string;
  }>;
}

const DisasterMap: React.FC<DisasterMapProps> = ({ onLocationSelect, markers = [] }) => {
  const mapRef = useRef<L.Map | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current && !mapRef.current) {
      mapRef.current = L.map(containerRef.current).setView([0, 0], 2);

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
  }, [onLocationSelect]);

  useEffect(() => {
    if (mapRef.current) {
      // Clear existing markers
      mapRef.current.eachLayer((layer) => {
        if (layer instanceof L.Marker) {
          layer.remove();
        }
      });

      // Add new markers
      markers.forEach((marker) => {
        const severityColor = {
          low: 'green',
          medium: 'yellow',
          high: 'orange',
          critical: 'red'
        }[marker.severity] || 'gray';

        L.marker([marker.lat, marker.lng], {
          icon: L.divIcon({
            className: 'custom-div-icon',
            html: `<div style="background-color: ${severityColor}; width: 10px; height: 10px; border-radius: 50%;"></div>`,
            iconSize: [10, 10]
          })
        })
          .addTo(mapRef.current!)
          .bindPopup(`Type: ${marker.type}<br>Severity: ${marker.severity}`);
      });
    }
  }, [markers]);

  return <div ref={containerRef} style={{ height: '400px', width: '100%' }} />;
};

export default DisasterMap;
