import React from 'react';
import { InputField } from '@/components/InputField/InputField';
import { SelectField } from '@/components/SelectField';
import { Section } from '@/components/Section';
import { Person } from '@/types';

interface PersonalDataSectionProps {
  data: Person;
  onChange: (updatedPerson: Person) => void;
  defaultOpen?: boolean;
}

export const PersonalDataSection: React.FC<PersonalDataSectionProps> = ({
  data,
  onChange,
  defaultOpen = true
}) => {
  const handleFieldChange = (
    field: keyof Person,
    value: string
  ) => {
    onChange({
      ...data,
      [field]: value
    });
  };

  const handleAddressChange = (value: string) => {

    onChange({
      ...data,
      address: value,
    });
  };

  return (
    <Section title="1. Dane osobowe poszkodowanego" defaultOpen={defaultOpen}>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <InputField
          label="PESEL"
          id="pesel"
          value={data.pesel}
          onChange={e => handleFieldChange('pesel', e.target.value)}
          required
        />
        <SelectField
          label="ID Type"
          id="idType"
          value={data.idType}
          onChange={e => handleFieldChange('idType', e.target.value)}
          options={['Dowod', 'Paszport', ]}
        />
        <InputField
          label="ID Number"
          id="idNumber"
          value={data.idNumber}
          onChange={e => handleFieldChange('idNumber', e.target.value)}
          required
        />
        <InputField
          label="Birth Date"
          id="birthDate"
          type="date"
          value={data.birthDate}
          onChange={e => handleFieldChange('birthDate', e.target.value)}
        />
        <InputField
          label="Birth Place"
          id="birthPlace"
          value={data.birthPlace}
          onChange={e => handleFieldChange('birthPlace', e.target.value)}
        />
        <InputField
          label="Phone Number"
          id="phoneNumber"
          type="tel"
          value={data.phoneNumber}
          onChange={e => handleFieldChange('phoneNumber', e.target.value)}
        />
        <InputField
          label="Email"
          id="email"
          type="email"
          value={data.email}
          onChange={e => handleFieldChange('email', e.target.value)}
          className="md:col-span-1"
        />
        <InputField
          label="Address"
          id="address"
          value={data.address}
          onChange={e => handleAddressChange(e.target.value)}
          className="md:col-span-2"
          rows={2}
        />
      </div>
    </Section>
  );
};