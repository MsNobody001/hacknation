import React from 'react';
import { InputField } from '@/components/InputField/InputField';
import { CheckboxField } from '@/components/CheckboxField/CheckboxField';
import { SelectField } from '@/components/SelectField';
import { Section } from '@/components/Section';
import { BHPCompliance } from '@/types';

interface SafetyComplianceSectionProps {
  usedProtectiveEquipment: boolean | string[];
  usedSafetySupport: boolean | { requiredMoreThanOnePerson: boolean };
  bhpCompliance: boolean;
  hasProperPreparation: boolean;
  bhpTraining: BHPCompliance;
  onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>, path: (string | number)[]) => void;
  onUpdate: (path: (string | number)[], value: any) => void;
}

export const SafetyComplianceSection: React.FC<SafetyComplianceSectionProps> = ({
  usedProtectiveEquipment,
  usedSafetySupport,
  bhpCompliance,
  hasProperPreparation,
  bhpTraining,
  onChange,
  onUpdate,
}) => {
  return (
    <Section title="5. Safety Measures and Compliance">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Protective Equipment */}
        <div>
          <h3 className="font-semibold mb-2">Protective Equipment</h3>
          <SelectField
            label="Used Protective Equipment?"
            id="protectiveEquipment"
            value={
              typeof usedProtectiveEquipment === 'boolean'
                ? usedProtectiveEquipment
                  ? 'Yes'
                  : 'No'
                : 'List Provided'
            }
            onChange={e => {
              const val = e.target.value;
              if (val === 'Yes') onUpdate(['usedProtectiveEquipment'], ['']);
              if (val === 'No') onUpdate(['usedProtectiveEquipment'], false);
            }}
            options={['No', 'Yes']}
          />

          {Array.isArray(usedProtectiveEquipment) && (
            <div className="mt-3 space-y-2">
              <InputField
                label="List Protective Equipment (comma separated)"
                id="ppeList"
                value={usedProtectiveEquipment.join(', ')}
                onChange={e =>
                  onUpdate(
                    ['usedProtectiveEquipment'],
                    e.target.value.split(',').map(s => s.trim())
                  )
                }
                rows={2}
              />
            </div>
          )}
        </div>

        {/* Safety Support */}
        <div>
          <h3 className="font-semibold mb-2">Safety Support</h3>
          <SelectField
            label="Was Safety Support Used?"
            id="safetySupport"
            value={
              typeof usedSafetySupport === 'boolean'
                ? usedSafetySupport
                  ? 'Yes'
                  : 'No'
                : 'Details Provided'
            }
            onChange={e => {
              const val = e.target.value;
              if (val === 'Yes') onUpdate(['usedSafetySupport'], { requiredMoreThanOnePerson: false });
              if (val === 'No') onUpdate(['usedSafetySupport'], false);
            }}
            options={['No', 'Yes']}
          />

          {typeof usedSafetySupport === 'object' && usedSafetySupport !== null && (
            <div className="mt-3 p-3 bg-gray-50 rounded-lg">
              <CheckboxField
                id="multiPerson"
                label="Activity required more than one person?"
                checked={usedSafetySupport.requiredMoreThanOnePerson}
                onChange={checked => onUpdate(['usedSafetySupport', 'requiredMoreThanOnePerson'], checked)}
              />
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6 border-t pt-6">
        <CheckboxField
          id="bhpCompliance"
          label="BHP Compliance Met?"
          checked={bhpCompliance}
          onChange={checked => onUpdate(['bhpCompliance'], checked)}
        />
        <CheckboxField
          id="properPreparation"
          label="Proper Preparation Completed?"
          checked={hasProperPreparation}
          onChange={checked => onUpdate(['hasProperPreparation'], checked)}
        />
      </div>

      <div className="mt-6 border-t pt-6 bg-yellow-50/50 p-4 rounded-lg">
        <h3 className="font-semibold mb-3">BHP Training & Risk Assessment</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <CheckboxField
            id="completedTraining"
            label="Completed BHP Training?"
            checked={bhpTraining.completedTraining}
            onChange={checked => onUpdate(['bhpTraining', 'completedTraining'], checked)}
          />
          <CheckboxField
            id="hasRiskAssessment"
            label="Has Risk Assessment Document?"
            checked={bhpTraining.hasRiskAssessment}
            onChange={checked => onUpdate(['bhpTraining', 'hasRiskAssessment'], checked)}
          />
          <InputField
            label="Risk Reduction Measures (Optional)"
            id="riskMeasures"
            value={bhpTraining.riskReductionMeasures}
            onChange={e => onChange(e, ['bhpTraining', 'riskReductionMeasures'])}
            className="md:col-span-2"
            rows={2}
          />
        </div>
      </div>
    </Section>
  );
};