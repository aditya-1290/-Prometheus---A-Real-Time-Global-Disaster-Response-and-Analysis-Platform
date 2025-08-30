import { Metadata } from 'next';
import ResourceLocator from '@/components/ResourceLocator';

export const metadata: Metadata = {
  title: 'Emergency Resources - Public Portal',
  description: 'Find emergency resources and supplies in your area',
};

export default function ResourcesPage() {
  return (
    <main className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">
        Emergency Resources
      </h1>

      <div className="prose max-w-none mb-8">
        <p className="text-lg text-gray-700">
          Locate available emergency resources and supplies in your area. This map shows the
          current status and availability of various emergency resources.
        </p>
      </div>

      <ResourceLocator />
    </main>
  );
}
