import React from 'react';
import { InputField } from '@/components/InputField/InputField';
import { Section } from '@/components/Section';

export interface Address {
  street: string;
  city: string;
  postalCode: string;
  country: string;
}

export interface AccidentDetails {
  date: string;
  time: string;
  location: Address;
  plannedWorkStart: string;
  plannedWorkEnd: string;
}

interface AccidentDetailsSectionProps {
  data: AccidentDetails;
  workActivityBeforeAccident: string;
  accidentCircumstances: string;
  accidentCause: string;
  onChange: (details: AccidentDetails) => void;
  onWorkActivityChange: (value: string) => void;
  onCircumstancesChange: (value: string) => void;
  onCauseChange: (value: string) => void;
}

export const AccidentDetailsSection: React.FC<AccidentDetailsSectionProps> = ({
  data,
  workActivityBeforeAccident,
  accidentCircumstances,
  accidentCause,
  onChange,
  onWorkActivityChange,
  onCircumstancesChange,
  onCauseChange,
}) => {
  const handleChange = (field: keyof AccidentDetails, value: string | Address) => {
    onChange({
      ...data,
      [field]: value,
    });
  };

  const handleLocationChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    handleChange('location', e.target.value as unknown as Address);
  };

  return (
    <Section title="2. Accident Details">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <InputField
          label="Date"
          id="accDate"
          type="date"
          value={data.date}
          onChange={e => handleChange('date', e.target.value)}
          required
        />
        <InputField
          label="Time"
          id="accTime"
          type="time"
          value={data.time}
          onChange={e => handleChange('time', e.target.value)}
          required
        />
        <InputField
          label="Planned Work Start"
          id="workStart"
          type="time"
          value={data.plannedWorkStart}
          onChange={e => handleChange('plannedWorkStart', e.target.value)}
        />
        <InputField
          label="Planned Work End"
          id="workEnd"
          type="time"
          value={data.plannedWorkEnd}
          onChange={e => handleChange('plannedWorkEnd', e.target.value)}
        />
        <InputField
          label="Location"
          id="accLocation"
          value={typeof data.location === 'string' ? data.location : JSON.stringify(data.location)}
          onChange={handleLocationChange}
          className="md:col-span-4"
          rows={2}
          required
        />
      </div>
      <div className="space-y-4 mt-6">
        <InputField
          label="Work Activity Before Accident"
          id="activityBefore"
          value={workActivityBeforeAccident}
          onChange={e => onWorkActivityChange(e.target.value)}
          rows={3}
        />
        <InputField
          label="Accident Circumstances"
          id="circumstances"
          value={accidentCircumstances}
          onChange={e => onCircumstancesChange(e.target.value)}
          rows={3}
        />
        <InputField
          label="Accident Cause"
          id="cause"
          value={accidentCause}
          onChange={e => onCauseChange(e.target.value)}
          rows={3}
        />
      </div>
    </Section>
  );
};