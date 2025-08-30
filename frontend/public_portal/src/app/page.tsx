import { Metadata } from 'next';
import { disasterService } from '@/services/api';
import PublicMap from '@/components/PublicMap';
import SafetyGuide from '@/components/SafetyGuide';

export const metadata: Metadata = {
  title: 'Public Information Portal - Active Disasters',
  description: 'Real-time information about active disasters and emergency situations',
};

export default async function Home() {
  const { data: disasters } = await disasterService.getAllDisasters();

  return (
    <main className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">
        Active Emergency Situations
      </h1>

      <div className="mb-8">
        <PublicMap disasters={disasters} />
      </div>

      <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h2 className="text-2xl font-semibold mb-4">Current Status</h2>
          <div className="bg-white rounded-lg shadow p-4">
            <ul className="space-y-4">
              {disasters.map((disaster) => (
                <li key={disaster.id} className="border-b pb-4 last:border-0">
                  <h3 className="text-lg font-medium">
                    {disaster.type}
                  </h3>
                  <p className="text-gray-600">
                    {disaster.description}
                  </p>
                  <div className="mt-2 flex gap-2">
                    <span className={`px-2 py-1 rounded text-sm ${
                      disaster.severity === 'critical' ? 'bg-red-100 text-red-800' :
                      disaster.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                      disaster.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {disaster.severity}
                    </span>
                    <span className={`px-2 py-1 rounded text-sm ${
                      disaster.status === 'active' ? 'bg-red-100 text-red-800' :
                      disaster.status === 'contained' ? 'bg-blue-100 text-blue-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {disaster.status}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div>
          <h2 className="text-2xl font-semibold mb-4">Safety Information</h2>
          <SafetyGuide 
            guides={[
              {
                type: 'General Emergency',
                description: 'Basic safety guidelines for all emergency situations',
                beforeTips: [
                  {
                    title: 'Create an Emergency Kit',
                    description: 'Include water, food, medications, and essential supplies',
                    priority: 'high'
                  },
                  {
                    title: 'Have a Communication Plan',
                    description: 'Establish how to contact family members during emergencies',
                    priority: 'high'
                  }
                ],
                duringTips: [
                  {
                    title: 'Stay Informed',
                    description: 'Monitor official channels for updates and instructions',
                    priority: 'high'
                  },
                  {
                    title: 'Follow Official Instructions',
                    description: 'Comply with evacuation orders and safety directives',
                    priority: 'high'
                  }
                ],
                afterTips: [
                  {
                    title: 'Check for Injuries',
                    description: 'Assess yourself and others for injuries',
                    priority: 'high'
                  },
                  {
                    title: 'Document Damage',
                    description: 'Take photos of any damage for insurance purposes',
                    priority: 'medium'
                  }
                ]
              }
            ]}
          />
        </div>
      </section>
    </main>
  );
}
