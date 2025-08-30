import React, { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Disaster } from '../types/api';

interface CrisisMapProps {
  disasters: Disaster[];
  onMarkerClick?: (disaster: Disaster) => void;
}

const CrisisMap: React.FC<CrisisMapProps> = ({ disasters, onMarkerClick }) => {
  const mapRef = useRef<L.Map>(null);

  useEffect(() => {
    if (mapRef.current && disasters.length > 0) {
      const bounds = L.latLngBounds(
        disasters.map(d => [d.location.latitude, d.location.longitude])
      );
      mapRef.current.fitBounds(bounds);
    }
  }, [disasters]);

  const getSeverityColor = (severity: string) => {
    const colors = {
      low: 'green',
      medium: 'yellow',
      high: 'orange',
      critical: 'red'
    };
    return colors[severity as keyof typeof colors] || 'gray';
  };

  return (
    <MapContainer
      ref={mapRef}
      center={[0, 0]}
      zoom={2}
      style={{ height: '600px', width: '100%' }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; OpenStreetMap contributors'
      />
      {disasters.map((disaster) => (
        <Marker
          key={disaster.id}
          position={[disaster.location.latitude, disaster.location.longitude]}
          icon={L.divIcon({
            className: 'custom-div-icon',
            html: `<div style="background-color: ${getSeverityColor(disaster.severity)}; width: 10px; height: 10px; border-radius: 50%;"></div>`,
            iconSize: [10, 10]
          })}
          eventHandlers={{
            click: () => onMarkerClick?.(disaster)
          }}
        >
          <Popup>
            <div>
              <h3>{disaster.type}</h3>
              <p>Severity: {disaster.severity}</p>
              <p>Status: {disaster.status}</p>
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
};

export default CrisisMap;
