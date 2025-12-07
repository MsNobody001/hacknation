import React from 'react';
import { CheckboxField } from '@/components/CheckboxField/CheckboxField';
import { SelectField } from '@/components/SelectField';
import { Section } from '@/components/Section';
import { Intoxication } from '@/types';

interface IntoxicationSectionProps {
  data: Intoxication;
  onChange: (value: Intoxication) => void;
}

export const IntoxicationSection: React.FC<IntoxicationSectionProps> = ({
  data,
  onChange,
}) => {
  return (
    <Section title="6. Intoxication Status">
      <CheckboxField
        id="intoxicated"
        label="Was the injured person intoxicated (alcohol/other substances)?"
        checked={data.intoxicated}
        onChange={checked => onChange({
          ...data,
          intoxicated: checked,
        })}
      />
      {data.intoxicated && (
        <div className="mt-4">
          <SelectField
            label="Tested By"
            id="testedBy"
            value={data.testedBy ?? 'none'}
            onChange={e => onChange({
          ...data,
          testedBy: e.target.value as 'police' | 'medicalHelp' | 'notTested',
        })}
            options={['none', 'police', 'medicalHelp']}
          />
        </div>
      )}
    </Section>
  );
};