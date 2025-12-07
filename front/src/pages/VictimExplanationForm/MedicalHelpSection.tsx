import React from 'react';
import { InputField } from '@/components/InputField/InputField';
import { CheckboxField } from '@/components/CheckboxField/CheckboxField';
import { Section } from '@/components/Section';
import { MedicalHelpDetails } from '@/types';

interface MedicalHelpSectionProps {
  data: boolean | MedicalHelpDetails;
  onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>, path: (string | number)[]) => void;
  onUpdate: (path: (string | number)[], value: any) => void;
}

export const MedicalHelpSection: React.FC<MedicalHelpSectionProps> = ({
  data,
  onChange,
  onUpdate,
}) => {
  const isDetails = typeof data === 'object' && data !== null;

  return (
    <Section title="8. Medical Help & Consequences">
      <CheckboxField
        id="receivedMedicalHelp"
        label="Did the injured person receive medical help?"
        checked={isDetails}
        onChange={checked => onUpdate(['medicalHelp'], checked ? { sickLeaveOnAccidentDay: false } : false)}
      />

      {isDetails && (
        <div className="mt-4 p-4 border border-gray-300 rounded-lg bg-gray-50 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <InputField
              label="Date of First Aid"
              id="firstAidDate"
              type="date"
              value={data.dateOfFirstAid}
              onChange={e => onChange(e, ['medicalHelp', 'dateOfFirstAid'])}
            />
            <InputField
              label="Healthcare Facility Name"
              id="facilityName"
              value={data.healthcareFacilityName}
              onChange={e => onChange(e, ['medicalHelp', 'healthcareFacilityName'])}
            />
            <InputField
              label="Diagnosed Injury"
              id="injury"
              value={data.diagnosedInjury}
              onChange={e => onChange(e, ['medicalHelp', 'diagnosedInjury'])}
              className="md:col-span-2"
            />

            <CheckboxField
              id="sickLeaveAccidentDay"
              label="Received sick leave on the day of the accident?"
              checked={data.sickLeaveOnAccidentDay}
              onChange={checked => onUpdate(['medicalHelp', 'sickLeaveOnAccidentDay'], checked)}
            />
          </div>

          <h5 className="text-md font-semibold mt-4 text-blue-700 border-b pb-1">
            Hospitalization Period (Optional)
          </h5>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <InputField
              label="From"
              id="hospFrom"
              type="date"
              value={data.hospitalizationPeriod?.from}
              onChange={e =>
                onUpdate(['medicalHelp', 'hospitalizationPeriod'], {
                  ...data.hospitalizationPeriod,
                  from: e.target.value,
                })
              }
            />
            <InputField
              label="To"
              id="hospTo"
              type="date"
              value={data.hospitalizationPeriod?.to}
              onChange={e =>
                onUpdate(['medicalHelp', 'hospitalizationPeriod'], {
                  ...data.hospitalizationPeriod,
                  to: e.target.value,
                })
              }
            />
            <InputField
              label="Hospital Address"
              id="hospAddress"
              value={data.hospitalizationPeriod?.address}
              onChange={e =>
                onUpdate(['medicalHelp', 'hospitalizationPeriod'], {
                  ...data.hospitalizationPeriod,
                  address: e.target.value,
                })
              }
            />
          </div>

          <h5 className="text-md font-semibold mt-4 text-blue-700 border-b pb-1">Incapacity Period (Optional)</h5>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <InputField
              label="Incapacity From"
              id="incapFrom"
              type="date"
              value={data.incapacityPeriod?.from}
              onChange={e =>
                onUpdate(['medicalHelp', 'incapacityPeriod'], {
                  ...data.incapacityPeriod,
                  from: e.target.value,
                })
              }
            />
            <InputField
              label="Incapacity To"
              id="incapTo"
              type="date"
              value={data.incapacityPeriod?.to}
              onChange={e =>
                onUpdate(['medicalHelp', 'incapacityPeriod'], {
                  ...data.incapacityPeriod,
                  to: e.target.value,
                })
              }
            />
          </div>
        </div>
      )}
    </Section>
  );
};