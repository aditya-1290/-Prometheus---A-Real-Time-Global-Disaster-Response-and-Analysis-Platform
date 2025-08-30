import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { disasterService } from '@/services/api';
import PublicMap from '@/components/PublicMap';

interface DisasterDetailPageProps {
  params: {
    id: string;
  };
}

export async function generateMetadata(
  { params }: DisasterDetailPageProps
): Promise<Metadata> {
  try {
    const { data: disaster } = await disasterService.getDisasterById(params.id);
    return {
      title: `${disaster.type} - Disaster Details`,
      description: disaster.description,
    };
  } catch (error) {
    return {
      title: 'Disaster Not Found',
      description: 'The requested disaster information could not be found.',
    };
  }
}

export default async function DisasterDetailPage({ params }: DisasterDetailPageProps) {
  try {
    const [disasterRes, updatesRes] = await Promise.all([
      disasterService.getDisasterById(params.id),
      disasterService.getDisasterUpdates(params.id),
    ]);

    const disaster = disasterRes.data;
    const updates = updatesRes.data;

    return (
      <main className="container mx-auto p-4">
        <h1 className="text-3xl font-bold mb-6">
          {disaster.type}
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2">
            <div className="bg-white rounded-lg shadow mb-6">
              <PublicMap
                disasters={[disaster]}
                center={[disaster.location.latitude, disaster.location.longitude]}
                zoom={12}
              />
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-2xl font-semibold mb-4">Updates</h2>
              <div className="space-y-4">
                {updates.map((update) => (
                  <div
                    key={update.id}
                    className="border-l-4 border-blue-500 pl-4 py-2"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <span className={`px-2 py-1 rounded text-sm ${
                        update.status === 'active' ? 'bg-red-100 text-red-800' :
                        update.status === 'contained' ? 'bg-blue-100 text-blue-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {update.status}
                      </span>
                      <time className="text-sm text-gray-500">
                        {new Date(update.createdAt).toLocaleString()}
                      </time>
                    </div>
                    <p className="text-gray-700">{update.description}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-semibold mb-4">Details</h2>
            <dl className="space-y-4">
              <div>
                <dt className="text-sm font-medium text-gray-500">Status</dt>
                <dd className="mt-1">
                  <span className={`px-2 py-1 rounded text-sm ${
                    disaster.status === 'active' ? 'bg-red-100 text-red-800' :
                    disaster.status === 'contained' ? 'bg-blue-100 text-blue-800' :
                    'bg-green-100 text-green-800'
                  }`}>
                    {disaster.status}
                  </span>
                </dd>
              </div>

              <div>
                <dt className="text-sm font-medium text-gray-500">Severity</dt>
                <dd className="mt-1">
                  <span className={`px-2 py-1 rounded text-sm ${
                    disaster.severity === 'critical' ? 'bg-red-100 text-red-800' :
                    disaster.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                    disaster.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-green-100 text-green-800'
                  }`}>
                    {disaster.severity}
                  </span>
                </dd>
              </div>

              <div>
                <dt className="text-sm font-medium text-gray-500">Description</dt>
                <dd className="mt-1 text-gray-700">{disaster.description}</dd>
              </div>

              <div>
                <dt className="text-sm font-medium text-gray-500">Affected Area</dt>
                <dd className="mt-1 text-gray-700">
                  {disaster.affectedArea.radius} {disaster.affectedArea.unit}
                </dd>
              </div>

              <div>
                <dt className="text-sm font-medium text-gray-500">First Reported</dt>
                <dd className="mt-1 text-gray-700">
                  {new Date(disaster.createdAt).toLocaleString()}
                </dd>
              </div>

              <div>
                <dt className="text-sm font-medium text-gray-500">Last Updated</dt>
                <dd className="mt-1 text-gray-700">
                  {new Date(disaster.updatedAt).toLocaleString()}
                </dd>
              </div>
            </dl>
          </div>
        </div>
      </main>
    );
  } catch (error) {
    notFound();
  }
}
