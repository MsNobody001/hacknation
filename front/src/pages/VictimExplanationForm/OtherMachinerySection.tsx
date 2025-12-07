import React from 'react';
import { InputField } from '@/components/InputField/InputField';
import { CheckboxField } from '@/components/CheckboxField/CheckboxField';
import { Section } from '@/components/Section';
import { MachineryToolsInfo } from '@/types';

interface OtherMachinerySectionProps {
  data: MachineryToolsInfo;
  onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>, path: (string | number)[]) => void;
  onUpdate: (path: (string | number)[], value: any) => void;
}

export const OtherMachinerySection: React.FC<OtherMachinerySectionProps> = ({
  data,
  onChange,
  onUpdate,
}) => {
  return (
    <Section title="4. Other Machinery/Tools Information">
      <CheckboxField
        id="otherMachineryInvolved"
        label="Were other machines or tools involved in the activity (but not the direct cause)?"
        checked={data.involved}
        onChange={checked => onUpdate(['machineryToolsInfo', 'involved'], checked)}
      />
      {data.involved && (
        <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4 border p-4 rounded-lg bg-blue-50/50">
          <InputField
            label="Tool/Machine Name"
            id="toolName"
            value={data.machineOrToolName}
            onChange={e => onChange(e, ['machineryToolsInfo', 'machineOrToolName'])}
          />
          <InputField
            label="Tool/Machine Type"
            id="toolType"
            value={data.machineType}
            onChange={e => onChange(e, ['machineryToolsInfo', 'machineType'])}
          />
          <InputField
            label="Production Date"
            id="toolProdDate"
            type="date"
            value={data.productionDate}
            onChange={e => onChange(e, ['machineryToolsInfo', 'productionDate'])}
          />
          <CheckboxField
            id="functional"
            label="Was functional?"
            checked={!!data.wasFunctional}
            onChange={checked => onUpdate(['machineryToolsInfo', 'wasFunctional'], checked)}
          />
          <CheckboxField
            id="manual"
            label="Used according to manual?"
            checked={!!data.usedAccordingToManual}
            onChange={checked => onUpdate(['machineryToolsInfo', 'usedAccordingToManual'], checked)}
          />
          <InputField
            label="Description of Use (Optional)"
            id="useDesc"
            value={data.descriptionOfUse}
            onChange={e => onChange(e, ['machineryToolsInfo', 'descriptionOfUse'])}
            className="md:col-span-3"
          />
        </div>
      )}
    </Section>
  );
};