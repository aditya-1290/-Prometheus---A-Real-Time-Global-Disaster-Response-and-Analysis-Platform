import { Metadata } from 'next';
import DisasterMap from '@/components/DisasterMap';
import ReportForm from '@/components/ReportForm';

export const metadata: Metadata = {
  title: 'Report Disaster - Public Portal',
  description: 'Report a disaster or emergency situation',
};

export default function ReportPage() {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Report a Disaster</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="order-2 md:order-1">
          <ReportForm />
        </div>
        <div className="order-1 md:order-2">
          <DisasterMap />
        </div>
      </div>
    </div>
  );
}
