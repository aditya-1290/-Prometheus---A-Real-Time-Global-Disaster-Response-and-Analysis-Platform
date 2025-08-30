import { Metadata } from 'next';
import EvacuationMap from '@/components/EvacuationMap';

export const metadata: Metadata = {
  title: 'Evacuation Routes - Public Portal',
  description: 'Current evacuation routes and shelter locations',
};

// This would typically come from an API
const MOCK_ROUTES = [
  {
    id: '1',
    name: 'North Evacuation Route',
    description: 'Primary evacuation route heading north through major highways',
    path: [[37.7749, -122.4194], [37.8049, -122.4194]],
    type: 'primary',
    status: 'open'
  },
  {
    id: '2',
    name: 'East Evacuation Route',
    description: 'Secondary route through eastern residential areas',
    path: [[37.7749, -122.4194], [37.7749, -122.3894]],
    type: 'secondary',
    status: 'open'
  },
  {
    id: '3',
    name: 'South Emergency Route',
    description: 'Emergency route through southern industrial zone',
    path: [[37.7749, -122.4194], [37.7449, -122.4194]],
    type: 'emergency',
    status: 'limited'
  }
];

const MOCK_SHELTERS = [
  {
    id: '1',
    name: 'Central Community Center',
    location: [37.7749, -122.4194],
    capacity: 500,
    currentOccupancy: 250,
    status: 'open'
  },
  {
    id: '2',
    name: 'North High School',
    location: [37.8049, -122.4194],
    capacity: 300,
    currentOccupancy: 300,
    status: 'full'
  },
  {
    id: '3',
    name: 'East Elementary School',
    location: [37.7749, -122.3894],
    capacity: 200,
    currentOccupancy: 100,
    status: 'open'
  }
];

export default function EvacuationPage() {
  return (
    <main className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">
        Evacuation Routes & Shelters
      </h1>

      <div className="prose max-w-none mb-8">
        <p className="text-lg text-gray-700">
          View current evacuation routes and emergency shelter locations. Routes are
          color-coded by type and updated in real-time based on conditions.
        </p>
      </div>

      <div className="bg-white rounded-lg shadow mb-8">
        <EvacuationMap
          routes={MOCK_ROUTES}
          shelterLocations={MOCK_SHELTERS}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h2 className="text-2xl font-semibold mb-4">Route Information</h2>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="space-y-4">
              {MOCK_ROUTES.map((route) => (
                <div key={route.id} className="border-b pb-4 last:border-0">
                  <h3 className="text-lg font-medium">{route.name}</h3>
                  <p className="text-gray-600 mb-2">{route.description}</p>
                  <div className="flex gap-2">
                    <span className={`px-2 py-1 rounded text-sm ${
                      route.type === 'primary' ? 'bg-green-100 text-green-800' :
                      route.type === 'secondary' ? 'bg-blue-100 text-blue-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {route.type}
                    </span>
                    <span className={`px-2 py-1 rounded text-sm ${
                      route.status === 'open' ? 'bg-green-100 text-green-800' :
                      route.status === 'limited' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {route.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div>
          <h2 className="text-2xl font-semibold mb-4">Emergency Shelters</h2>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="space-y-4">
              {MOCK_SHELTERS.map((shelter) => (
                <div key={shelter.id} className="border-b pb-4 last:border-0">
                  <h3 className="text-lg font-medium">{shelter.name}</h3>
                  <div className="flex justify-between items-center mb-2">
                    <span className={`px-2 py-1 rounded text-sm ${
                      shelter.status === 'open' ? 'bg-green-100 text-green-800' :
                      shelter.status === 'full' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {shelter.status}
                    </span>
                    <span className="text-sm text-gray-500">
                      {shelter.currentOccupancy} / {shelter.capacity} capacity
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div
                      className={`h-2.5 rounded-full ${
                        (shelter.currentOccupancy / shelter.capacity) >= 0.9
                          ? 'bg-red-500'
                          : (shelter.currentOccupancy / shelter.capacity) >= 0.7
                          ? 'bg-yellow-500'
                          : 'bg-green-500'
                      }`}
                      style={{
                        width: `${(shelter.currentOccupancy / shelter.capacity) * 100}%`
                      }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
