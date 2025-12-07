import React from 'react';
import { Plus, X } from 'lucide-react';
import { InputField } from '@/components/InputField/InputField';
import { CheckboxField } from '@/components/CheckboxField/CheckboxField';
import { SelectField } from '@/components/SelectField';
import { Section } from '@/components/Section';
import { StateAuthorityAction } from '@/types';

interface StateAuthoritySectionProps {
  data: boolean | StateAuthorityAction[];
  onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>, path: (string | number)[]) => void;
  onUpdate: (path: (string | number)[], value: any) => void;
}

export const StateAuthoritySection: React.FC<StateAuthoritySectionProps> = ({
  data,
  onChange,
  onUpdate,
}) => {
  const isArray = Array.isArray(data);

  const handleAddAction = () => {
    const newAction: StateAuthorityAction = {
      name: '',
      address: '',
      status: 'pending',
    };
    if (isArray) {
      onUpdate(['stateAuthorityActions'], [...data, newAction]);
    } else {
      onUpdate(['stateAuthorityActions'], [newAction]);
    }
  };

  const handleRemoveAction = (index: number) => {
    if (isArray) {
      const newActions = data.filter((_, i) => i !== index);
      onUpdate(['stateAuthorityActions'], newActions.length > 0 ? newActions : false);
    }
  };

  return (
    <Section title="7. State Authority Actions">
      <CheckboxField
        id="authoritiesInvolved"
        label="Were State Authorities Involved?"
        checked={isArray}
        onChange={checked => onUpdate(['stateAuthorityActions'], checked ? [] : false)}
      />

      {isArray &&
        data.map((action, index) => (
          <div key={index} className="mt-4 p-4 border border-gray-300 rounded-lg bg-gray-50 space-y-3">
            <div className="flex justify-between items-center">
              <h4 className="font-semibold">Authority Action #{index + 1}</h4>
              <button
                type="button"
                onClick={() => handleRemoveAction(index)}
                className="p-1 text-red-600 hover:text-red-800 transition duration-150 rounded-full bg-red-100 hover:bg-red-200"
                aria-label="Remove authority action"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InputField
                label="Authority Name"
                id={`authName-${index}`}
                value={action.name}
                onChange={e => onChange(e, ['stateAuthorityActions', index, 'name'])}
                required
              />
              <InputField
                label="Case Number"
                id={`caseNum-${index}`}
                value={action.caseNumber}
                onChange={e => onChange(e, ['stateAuthorityActions', index, 'caseNumber'])}
              />
              <SelectField
                label="Status"
                id={`status-${index}`}
                value={action.status ?? 'pending'}
                onChange={e => onChange(e, ['stateAuthorityActions', index, 'status'])}
                options={['pending', 'finished', 'rejected']}
              />
              <InputField
                label="Address (Optional)"
                id={`authAddress-${index}`}
                value={action.address}
                onChange={e => onChange(e, ['stateAuthorityActions', index, 'address'])}
                className="md:col-span-1"
              />
            </div>
          </div>
        ))}

      {isArray && (
        <button
          type="button"
          onClick={handleAddAction}
          className="mt-4 flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition duration-150 ease-in-out shadow-md"
        >
          <Plus className="w-4 h-4 mr-2" /> Add Authority Action
        </button>
      )}
    </Section>
  );
};