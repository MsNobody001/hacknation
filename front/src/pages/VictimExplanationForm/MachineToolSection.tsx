import React from 'react';
import { InputField } from '@/components/InputField/InputField';
import { CheckboxField } from '@/components/CheckboxField/CheckboxField';
import { Section } from '@/components/Section';
import { CausedByMachine } from '@/types';

interface MachineToolSectionProps {
  causedByMachine: false | CausedByMachine;
  onChange: (value: false | CausedByMachine) => void;
  initialMachineData: CausedByMachine;
}

export const MachineToolSection: React.FC<MachineToolSectionProps> = ({
  causedByMachine,
  onChange,
  initialMachineData,
}) => {
  const handleCheckboxChange = (checked: boolean) => {
    onChange(checked ? initialMachineData : false);
  };

  const handleFieldChange = (field: keyof CausedByMachine, value: unknown) => {
    if (causedByMachine === false) return;

    onChange({
      ...causedByMachine,
      [field]: value,
    });
  };

  const handleMachineInfoChange = (field: keyof CausedByMachine['machineInfo'], value: string) => {
    if (causedByMachine === false) return;

    onChange({
      ...causedByMachine,
      machineInfo: {
        ...causedByMachine.machineInfo,
        [field]: value,
      },
    });
  };

  return (
    <Section title="3. Accident Caused by a Machine/Tool">
      <CheckboxField
        id="causedByMachine"
        label="Check if the accident was directly caused by a machine or tool."
        checked={causedByMachine !== false}
        onChange={handleCheckboxChange}
      />
      {causedByMachine !== false && (
        <div className="mt-4 p-4 border border-blue-300 rounded-lg bg-blue-50">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 border p-4 rounded-lg bg-blue-50/50">
            <InputField
              label="Machine Name"
              id="machName"
              value={causedByMachine.machineInfo.name}
              onChange={e => handleMachineInfoChange('name', e.target.value)}
              required
            />
            <InputField
              label="Machine Type"
              id="machType"
              value={causedByMachine.machineInfo.type}
              onChange={e => handleMachineInfoChange('type', e.target.value)}
              required
            />
            <InputField
              label="Production Date"
              id="prodDate"
              type="date"
              value={causedByMachine.machineInfo.productionDate}
              onChange={e => handleMachineInfoChange('productionDate', e.target.value)}
              required
            />
          </div>
          <div className="mt-4 border-t pt-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <CheckboxField
                id="causativeFunctional"
                label="Was the causative machine functional?"
                checked={causedByMachine.wasFunctional ?? false}
                onChange={checked => handleFieldChange('wasFunctional', checked)}
              />
              <CheckboxField
                id="causativeManual"
                label="Used according to manual?"
                checked={causedByMachine.usedAccordingToManual ?? false}
                onChange={checked => handleFieldChange('usedAccordingToManual', checked)}
              />
              <InputField
                label="Description of Use"
                id="causativeUseDesc"
                value={causedByMachine.descriptionOfUse}
                onChange={e => handleFieldChange('descriptionOfUse', e.target.value)}
                className="md:col-span-2"
              />
            </div>
          </div>
        </div>
      )}
    </Section>
  );
};