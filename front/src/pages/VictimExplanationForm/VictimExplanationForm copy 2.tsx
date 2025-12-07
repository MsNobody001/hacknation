import React, { useState, useCallback } from 'react';
import { Save, Eraser } from 'lucide-react';
import { AccidentExplanationRecord, CausedByMachine } from '@/types';
import { PersonalDataSection } from './PersonalDataSection';
import { AccidentDetailsSection } from './AccidentDetailsSection';
import { MachineToolSection } from './MachineToolSection';
import { OtherMachinerySection } from './OtherMachinerySection';
import { SafetyComplianceSection } from './SafetyComplianceSection';
import { IntoxicationSection } from './IntoxicationSection';
import { StateAuthoritySection } from './StateAuthoritySection';
import { MedicalHelpSection } from './MedicalHelpSection';

// --- INITIAL STATE ---
const initialRecord: AccidentExplanationRecord = {
  personalData: {
    pesel: '',
    idType: 'ID Card',
    idNumber: '',
    birthDate: '',
    birthPlace: '',
    phoneNumber: '',
    address: '',
    email: '',
  },
  accidentDetails: {
    date: new Date().toISOString().split('T')[0],
    time: '08:00',
    location: '',
    plannedWorkStart: '07:00',
    plannedWorkEnd: '15:00',
  },
  workActivityBeforeAccident: '',
  accidentCircumstances: '',
  accidentCause: '',
  causedByMachineOrTool: false,
  machineryToolsInfo: {
    involved: false,
  },
  usedProtectiveEquipment: false,
  usedSafetySupport: false,
  bhpCompliance: true,
  hasProperPreparation: true,
  bhpTraining: {
    completedTraining: true,
    hasRiskAssessment: true,
    riskReductionMeasures: '',
  },
  intoxication: {
    intoxicated: false,
    testedBy: 'none',
  },
  stateAuthorityActions: false,
  medicalHelp: false,
};

const VictimExplanationForm: React.FC = () => {
  const [record, setRecord] = useState<AccidentExplanationRecord>(initialRecord);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const updateRecord = useCallback((path: (string | number)[], value: any) => {
    setRecord(prevRecord => {
      const newRecord = { ...prevRecord };
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      let current: any = newRecord;

      for (let i = 0; i < path.length - 1; i++) {
        const key = path[i];
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-member-access
        current[key] = Array.isArray(current[key]) ? [...current[key]] : { ...current[key] };
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-member-access
        current = current[key];
      }

      const lastKey = path[path.length - 1];
      // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-member-access
      current[lastKey] = value;

      return newRecord;
    });
  }, []);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>, path: (string | number)[]) => {
      const value = e.target.type === 'checkbox' ? (e.target as HTMLInputElement).checked : e.target.value;
      updateRecord(path, value);
    },
    [updateRecord]
  );

  const handleSave = () => {
    console.log('Saving record:', record);
    setStatusMessage('Record saved successfully! Check the console for the JSON structure.');
    setTimeout(() => setStatusMessage(null), 5000);
  };

  const handleReset = () => {
    setRecord(initialRecord);
    setStatusMessage('Form has been reset to initial state.');
    setTimeout(() => setStatusMessage(null), 5000);
  };

  return (
    <div className="min-h-screen flex justify-center">
      <div className="w-full max-w-5xl flex flex-col">
        <div>
          <h1 className="text-3xl font-extrabold mb-6 text-center border-b pb-3 flex-shrink-0 flex-grow-0">
            Accident Explanation Record
          </h1>
        </div>

        {statusMessage && (
          <div className="p-4 mb-4 text-sm text-green-700 bg-green-100 rounded-lg shadow-md" role="alert">
            {statusMessage}
          </div>
        )}

        <form
          className="pb-4"
          onSubmit={e => {
            e.preventDefault();
            handleSave();
          }}
        >
          <PersonalDataSection
            data={record.personalData}
            onChange={e =>
              setRecord({
                ...record,
                personalData: e,
              })
            }
            defaultOpen
          />

          <AccidentDetailsSection
            data={record.accidentDetails}
            workActivityBeforeAccident={record.workActivityBeforeAccident}
            accidentCircumstances={record.accidentCircumstances}
            accidentCause={record.accidentCause}
            onChange={handleChange}
          />

          <MachineToolSection
            causedByMachine={record.causedByMachineOrTool}
            onChange={handleChange}
            onUpdate={updateRecord}
            initialMachineData={initialRecord.causedByMachineOrTool as CausedByMachine}
          />

          <OtherMachinerySection data={record.machineryToolsInfo} onChange={handleChange} onUpdate={updateRecord} />

          <SafetyComplianceSection
            usedProtectiveEquipment={record.usedProtectiveEquipment}
            usedSafetySupport={record.usedSafetySupport}
            bhpCompliance={record.bhpCompliance}
            hasProperPreparation={record.hasProperPreparation}
            bhpTraining={record.bhpTraining}
            onChange={handleChange}
            onUpdate={updateRecord}
          />

          <IntoxicationSection data={record.intoxication} onChange={e => setRecord({ ...record, intoxication: e})}  />

          <StateAuthoritySection data={record.stateAuthorityActions} onChange={handleChange} onUpdate={updateRecord} />

          <MedicalHelpSection data={record.medicalHelp} onChange={handleChange} onUpdate={updateRecord} />

          <div className="mt-10 pt-6 border-t flex justify-end space-x-4 mr-3">
            <button
              type="button"
              onClick={handleReset}
              className="flex items-center px-6 py-3 text-sm font-semibold bg-gray-200 rounded-xl shadow-md hover:bg-gray-300 transition duration-150 ease-in-out"
            >
              <Eraser className="w-4 h-4 mr-2" onClick={handleReset} /> Reset Form
            </button>
            <button
              type="submit"
              className="flex items-center px-6 py-3 text-sm font-semibold text-white bg-primary rounded-xl shadow-lg hover:bg-green-700 transition duration-150 ease-in-out transform hover:scale-105"
            >
              <Save className="w-4 h-4 mr-2" /> Save Record
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export { VictimExplanationForm };
