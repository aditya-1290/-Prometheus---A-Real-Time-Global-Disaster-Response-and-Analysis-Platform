import { Metadata } from 'next';
import SafetyGuide from '@/components/SafetyGuide';

export const metadata: Metadata = {
  title: 'Safety Information - Public Portal',
  description: 'Comprehensive safety guidelines and emergency preparedness information',
};

export default function SafetyPage() {
  const safetyGuides = [
    {
      type: 'Natural Disasters',
      description: 'Guidelines for various natural disasters and emergency situations',
      beforeTips: [
        {
          title: 'Create an Emergency Kit',
          description: 'Include water, non-perishable food, flashlights, batteries, first aid supplies, and important documents',
          priority: 'high'
        },
        {
          title: 'Develop an Emergency Plan',
          description: 'Create and practice a family emergency plan, including evacuation routes and meeting points',
          priority: 'high'
        },
        {
          title: 'Stay Informed',
          description: 'Keep emergency contact numbers handy and know how to access emergency alerts',
          priority: 'medium'
        }
      ],
      duringTips: [
        {
          title: 'Follow Official Instructions',
          description: 'Listen to and follow instructions from emergency officials',
          priority: 'high'
        },
        {
          title: 'Stay or Go',
          description: 'Know when to evacuate and when to shelter in place',
          priority: 'high'
        },
        {
          title: 'Communication',
          description: 'Use text messages instead of calls to conserve battery and network capacity',
          priority: 'medium'
        }
      ],
      afterTips: [
        {
          title: 'Safety Check',
          description: 'Check for injuries and damage to your surroundings',
          priority: 'high'
        },
        {
          title: 'Document Everything',
          description: 'Take photos of damage for insurance purposes',
          priority: 'medium'
        },
        {
          title: 'Seek Assistance',
          description: 'Contact emergency services or relief organizations if needed',
          priority: 'medium'
        }
      ]
    },
    {
      type: 'Medical Emergencies',
      description: 'Guidelines for handling medical emergencies and first aid situations',
      beforeTips: [
        {
          title: 'First Aid Training',
          description: 'Get certified in basic first aid and CPR',
          priority: 'high'
        },
        {
          title: 'Medical Information',
          description: 'Keep a list of medications, allergies, and medical conditions readily available',
          priority: 'high'
        }
      ],
      duringTips: [
        {
          title: 'Call Emergency Services',
          description: 'Call emergency services immediately for serious medical situations',
          priority: 'high'
        },
        {
          title: 'Basic First Aid',
          description: 'Apply appropriate first aid while waiting for professional help',
          priority: 'high'
        }
      ],
      afterTips: [
        {
          title: 'Follow Up',
          description: 'Seek follow-up medical care as recommended',
          priority: 'medium'
        },
        {
          title: 'Update Records',
          description: 'Keep medical records updated with new information',
          priority: 'low'
        }
      ]
    },
    {
      type: 'Home Safety',
      description: 'Guidelines for maintaining a safe home environment',
      beforeTips: [
        {
          title: 'Regular Maintenance',
          description: 'Regularly check and maintain safety equipment like smoke detectors and fire extinguishers',
          priority: 'high'
        },
        {
          title: 'Emergency Exits',
          description: 'Plan and practice emergency escape routes from your home',
          priority: 'high'
        }
      ],
      duringTips: [
        {
          title: 'Fire Safety',
          description: 'In case of fire, get out and stay out',
          priority: 'high'
        },
        {
          title: 'Gas Leaks',
          description: 'If you smell gas, leave immediately and call emergency services',
          priority: 'high'
        }
      ],
      afterTips: [
        {
          title: 'Professional Inspection',
          description: 'Have damaged areas inspected by professionals before returning',
          priority: 'high'
        },
        {
          title: 'Review and Update',
          description: 'Update your safety plan based on experience',
          priority: 'medium'
        }
      ]
    }
  ];

  return (
    <main className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">
        Safety Information
      </h1>

      <div className="prose max-w-none mb-8">
        <p className="text-lg text-gray-700">
          This page provides comprehensive safety guidelines for various emergency situations.
          Please familiarize yourself with these guidelines and share them with your family and community.
        </p>
      </div>

      <div className="space-y-6">
        {safetyGuides.map((guide, index) => (
          <div key={index} className="bg-white rounded-lg shadow">
            <SafetyGuide guides={[guide]} />
          </div>
        ))}
      </div>
    </main>
  );
}
