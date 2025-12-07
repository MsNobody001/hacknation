import React, { useState, useCallback, useMemo, useEffect } from 'react';
import { Plus, X, Save, Eraser } from 'lucide-react';
import { InputField } from '@/components/InputField/InputField';
import {
  AccidentExplanationRecord,
  CausedByMachine,
  MachineInfo,
  MachineryToolsInfo,
  StateAuthorityAction,
} from '@/types';
import { CheckboxField } from '../../components/CheckboxField/CheckboxField';
import { SelectField } from '@/components/SelectField';
import { Section } from '@/components/Section';
import { useCtx } from '@/context';

const initialRecord: AccidentExplanationRecord = {
  personalData: {
    pesel: '',
    idType: '',
    idNumber: '',
    birthDate: '',
    birthPlace: '',
    phoneNumber: '',
    address: '',
    email: '',
  },
  accidentDetails: {
    date: '',
    time: '',
    location: '',
    plannedWorkStart: '',
    plannedWorkEnd: '',
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
    testedBy: 'notTested',
  },
  stateAuthorityActions: false,
  medicalHelp: false,
};

const VictimExplanationForm: React.FC = () => {
  const ctx = useCtx();

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
        // Ensure we spread objects/arrays at each step to maintain immutability
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
    // Simulate an API save operation
    setStatusMessage('Record saved successfully! Check the console for the JSON structure.');
    setTimeout(() => setStatusMessage(null), 5000);
  };

  const handleReset = () => {
    setRecord(initialRecord);
    setStatusMessage('Form has been reset to initial state.');
    setTimeout(() => setStatusMessage(null), 5000);
  };

  useEffect(() => {
    if (!ctx.collectedData) return;

    if (ctx.collectedData.accident_date) updateRecord(['accidentDetails', 'date'], ctx.collectedData.accident_date);
    if (ctx.collectedData.accident_time) updateRecord(['accidentDetails', 'time'], ctx.collectedData.accident_time);
    if (ctx.collectedData.location) updateRecord(['accidentDetails', 'location'], ctx.collectedData.location);
    if (ctx.collectedData.work_start_time) updateRecord(['accidentDetails', 'plannedWorkStart'], ctx.collectedData.work_start_time);
    if (ctx.collectedData.work_end_time) updateRecord(['accidentDetails', 'plannedWorkEnd'], ctx.collectedData.work_end_time);
    if (ctx.collectedData.injury_type) updateRecord(['medicalHelp', 'diagnosedInjury'], ctx.collectedData.injury_type);
    if (ctx.collectedData.circumstances) updateRecord(['accidentCircumstances'], ctx.collectedData.circumstances);
    if (ctx.collectedData.cause) updateRecord(['accidentCause'], ctx.collectedData.cause);
  }, [ctx.collectedData, updateRecord]);

  const renderPersonSection = useMemo(
    () => (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <InputField
          label="PESEL"
          id="pesel"
          value={record.personalData.pesel}
          onChange={e => handleChange(e, ['personalData', 'pesel'])}
          required
        />
        <SelectField
          label="Document tożsamości"
          id="idType"
          value={record.personalData.idType}
          onChange={e => handleChange(e, ['personalData', 'idType'])}
          options={['Dowod', 'Paszport', ]}
        />
        <InputField
          label="Seria numer"
          id="idNumber"
          value={record.personalData.idNumber}
          onChange={e => handleChange(e, ['personalData', 'idNumber'])}
          required
        />
        <InputField
          label="Birth Date"
          id="birthDate"
          type="date"
          value={record.personalData.birthDate}
          onChange={e => handleChange(e, ['personalData', 'birthDate'])}
        />
        <InputField
          label="Birth Place"
          id="birthPlace"
          value={record.personalData.birthPlace}
          onChange={e => handleChange(e, ['personalData', 'birthPlace'])}
        />
        <InputField
          label="Phone Number"
          id="phoneNumber"
          type="tel"
          value={record.personalData.phoneNumber}
          onChange={e => handleChange(e, ['personalData', 'phoneNumber'])}
        />
        <InputField
          label="Email"
          id="email"
          type="email"
          value={record.personalData.email}
          onChange={e => handleChange(e, ['personalData', 'email'])}
          className="md:col-span-1"
        />
        <InputField
          label="Address"
          id="address"
          value={record.personalData.address}
          onChange={e => handleChange(e, ['personalData', 'address'])}
          className="md:col-span-2"
          rows={2}
        />
      </div>
    ),
    [record.personalData, handleChange]
  );

  const renderAccidentDetails = useMemo(
    () => (
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <InputField
          label="Data wypadku"
          id="accDate"
          type="date"
          value={record.accidentDetails.date}
          onChange={e => handleChange(e, ['accidentDetails', 'date'])}
          required
        />
        <InputField
          label="Godzina wypadku"
          id="accTime"
          type="time"
          value={record.accidentDetails.time}
          onChange={e => handleChange(e, ['accidentDetails', 'time'])}
          required
        />
        <InputField
          label="Planowana godzina rozpoczęcia pracy"
          id="workStart"
          type="time"
          value={record.accidentDetails.plannedWorkStart}
          onChange={e => handleChange(e, ['accidentDetails', 'plannedWorkStart'])}
        />
        <InputField
          label="Planowana godzina zakończenia pracy"
          id="workEnd"
          type="time"
          value={record.accidentDetails.plannedWorkEnd}
          onChange={e => handleChange(e, ['accidentDetails', 'plannedWorkEnd'])}
        />
        <InputField
          label="Miesjce wypadku"
          id="accLocation"
          value={record.accidentDetails.location}
          onChange={e => handleChange(e, ['accidentDetails', 'location'])}
          className="md:col-span-4"
          rows={2}
          required
        />
      </div>
    ),
    [record.accidentDetails, handleChange]
  );

  const renderMachineryInfo = (info: MachineInfo, basePath: (string | number)[]) => (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 border p-4 rounded-lg bg-blue-50/50">
      <InputField
        label="Machine Name"
        id="machName"
        value={info.name}
        onChange={e => handleChange(e, [...basePath, 'name'])}
        required
      />
      <InputField
        label="Machine Type"
        id="machType"
        value={info.type}
        onChange={e => handleChange(e, [...basePath, 'type'])}
        required
      />
      <InputField
        label="Production Date"
        id="prodDate"
        type="date"
        value={info.productionDate}
        onChange={e => handleChange(e, [...basePath, 'productionDate'])}
        required
      />
    </div>
  );

  const renderMachineryToolsInfo = (info: MachineryToolsInfo, basePath: (string | number)[]) => (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 border p-4 rounded-lg bg-blue-50/50">
      <InputField
        label="Tool/Machine Name"
        id="toolName"
        value={info.machineOrToolName}
        onChange={e => handleChange(e, [...basePath, 'machineOrToolName'])}
      />
      <InputField
        label="Tool/Machine Type"
        id="toolType"
        value={info.machineType}
        onChange={e => handleChange(e, [...basePath, 'machineType'])}
      />
      <InputField
        label="Production Date"
        id="toolProdDate"
        type="date"
        value={info.productionDate}
        onChange={e => handleChange(e, [...basePath, 'productionDate'])}
      />
      <CheckboxField
        id="functional"
        label="Was functional?"
        checked={!!info.wasFunctional}
        onChange={checked => updateRecord([...basePath, 'wasFunctional'], checked)}
      />
      <CheckboxField
        id="manual"
        label="Used according to manual?"
        checked={!!info.usedAccordingToManual}
        onChange={checked => updateRecord([...basePath, 'usedAccordingToManual'], checked)}
      />
      <InputField
        label="Description of Use (Optional)"
        id="useDesc"
        value={info.descriptionOfUse}
        onChange={e => handleChange(e, [...basePath, 'descriptionOfUse'])}
        className="md:col-span-3"
      />
    </div>
  );

  const renderStateAuthorityActions = useMemo(() => {
    const actions = record.stateAuthorityActions;
    const isArray = Array.isArray(actions);

    const handleAddAction = () => {
      const newAction: StateAuthorityAction = {
        name: '',
        address: '',
        status: 'pending',
      };
      if (isArray) {
        updateRecord(['stateAuthorityActions'], [...actions, newAction]);
      } else {
        updateRecord(['stateAuthorityActions'], [newAction]);
      }
    };

    const handleRemoveAction = (index: number) => {
      if (isArray) {
        const newActions = actions.filter((_, i) => i !== index);
        updateRecord(['stateAuthorityActions'], newActions.length > 0 ? newActions : false);
      }
    };

    return (
      <div>
        <CheckboxField
          id="authoritiesInvolved"
          label="Were State Authorities Involved?"
          checked={isArray}
          onChange={checked => updateRecord(['stateAuthorityActions'], checked ? [] : false)}
        />

        {isArray &&
          actions.map((action, index) => (
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
                  onChange={e => handleChange(e, ['stateAuthorityActions', index, 'name'])}
                  required
                />
                <InputField
                  label="Case Number"
                  id={`caseNum-${index}`}
                  value={action.caseNumber}
                  onChange={e => handleChange(e, ['stateAuthorityActions', index, 'caseNumber'])}
                />
                <SelectField
                  label="Status"
                  id={`status-${index}`}
                  value={action.status ?? 'pending'}
                  onChange={e => handleChange(e, ['stateAuthorityActions', index, 'status'])}
                  options={['pending', 'finished', 'rejected']}
                />
                <InputField
                  label="Address (Optional)"
                  id={`authAddress-${index}`}
                  value={action.address}
                  onChange={e => handleChange(e, ['stateAuthorityActions', index, 'address'])}
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
      </div>
    );
  }, [record.stateAuthorityActions, updateRecord, handleChange]);

  const renderMedicalHelp = useMemo(() => {
    const medicalHelp = record.medicalHelp;
    const isDetails = typeof medicalHelp === 'object' && medicalHelp !== null;

    return (
      <div>
        <CheckboxField
          id="receivedMedicalHelp"
          label="Did the injured person receive medical help?"
          checked={isDetails}
          onChange={checked => updateRecord(['medicalHelp'], checked ? { sickLeaveOnAccidentDay: false } : false)}
        />

        {isDetails && (
          <div className="mt-4 p-4 border border-gray-300 rounded-lg bg-gray-50 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InputField
                label="Date of First Aid"
                id="firstAidDate"
                type="date"
                value={medicalHelp.dateOfFirstAid}
                onChange={e => handleChange(e, ['medicalHelp', 'dateOfFirstAid'])}
              />
              <InputField
                label="Healthcare Facility Name"
                id="facilityName"
                value={medicalHelp.healthcareFacilityName}
                onChange={e => handleChange(e, ['medicalHelp', 'healthcareFacilityName'])}
              />
              <InputField
                label="Diagnosed Injury"
                id="injury"
                value={medicalHelp.diagnosedInjury}
                onChange={e => handleChange(e, ['medicalHelp', 'diagnosedInjury'])}
                className="md:col-span-2"
              />

              <CheckboxField
                id="sickLeaveAccidentDay"
                label="Received sick leave on the day of the accident?"
                checked={medicalHelp.sickLeaveOnAccidentDay}
                onChange={checked => updateRecord(['medicalHelp', 'sickLeaveOnAccidentDay'], checked)}
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
                value={medicalHelp.hospitalizationPeriod?.from}
                onChange={e =>
                  updateRecord(['medicalHelp', 'hospitalizationPeriod'], {
                    ...medicalHelp.hospitalizationPeriod,
                    from: e.target.value,
                  })
                }
              />
              <InputField
                label="To"
                id="hospTo"
                type="date"
                value={medicalHelp.hospitalizationPeriod?.to}
                onChange={e =>
                  updateRecord(['medicalHelp', 'hospitalizationPeriod'], {
                    ...medicalHelp.hospitalizationPeriod,
                    to: e.target.value,
                  })
                }
              />
              <InputField
                label="Hospital Address"
                id="hospAddress"
                value={medicalHelp.hospitalizationPeriod?.address}
                onChange={e =>
                  updateRecord(['medicalHelp', 'hospitalizationPeriod'], {
                    ...medicalHelp.hospitalizationPeriod,
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
                value={medicalHelp.incapacityPeriod?.from}
                onChange={e =>
                  updateRecord(['medicalHelp', 'incapacityPeriod'], {
                    ...medicalHelp.incapacityPeriod,
                    from: e.target.value,
                  })
                }
              />
              <InputField
                label="Incapacity To"
                id="incapTo"
                type="date"
                value={medicalHelp.incapacityPeriod?.to}
                onChange={e =>
                  updateRecord(['medicalHelp', 'incapacityPeriod'], {
                    ...medicalHelp.incapacityPeriod,
                    to: e.target.value,
                  })
                }
              />
            </div>
          </div>
        )}
      </div>
    );
  }, [record.medicalHelp, updateRecord, handleChange]);

  return (
    <div className="min-h-screen  flex justify-center">
      <div className="w-full max-w-5xl flex flex-col">
        <div>
          <h1 className="text-3xl font-extrabold mb-6 text-center border-b pb-3 flex-shrink-0 flex-grow-0">
            Zapis wyjaśnień poszkodowanego
          </h1>
        </div>

        {/* Status Message */}
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
          {/* Section 1: Personal Data */}
          <Section title="1. Dane osobowe" defaultOpen>
            {renderPersonSection}
          </Section>

          {/* Section 2: Accident Details */}
          <Section title="2. Accident Details">
            {renderAccidentDetails}
            <div className="space-y-4 mt-6">
              <InputField
                label="Work Activity Before Accident"
                id="activityBefore"
                value={record.workActivityBeforeAccident}
                onChange={e => handleChange(e, ['workActivityBeforeAccident'])}
                rows={3}
              />
              <InputField
                label="Accident Circumstances"
                id="circumstances"
                value={record.accidentCircumstances}
                onChange={e => handleChange(e, ['accidentCircumstances'])}
                rows={3}
              />
              <InputField
                label="Accident Cause"
                id="cause"
                value={record.accidentCause}
                onChange={e => handleChange(e, ['accidentCause'])}
                rows={3}
              />
            </div>
          </Section>

          {/* Section 3: Machine/Tool Related Accident */}
          <Section title="3. Accident Caused by a Machine/Tool">
            <CheckboxField
              id="causedByMachine"
              label="Check if the accident was directly caused by a machine or tool."
              checked={record.causedByMachineOrTool !== false}
              onChange={checked =>
                updateRecord(
                  ['causedByMachineOrTool'],
                  checked ? (initialRecord.causedByMachineOrTool as CausedByMachine) : false
                )
              }
            />
            {record.causedByMachineOrTool !== false && (
              <div className="mt-4 p-4 border border-blue-300 rounded-lg bg-blue-50">
                {renderMachineryInfo(record.causedByMachineOrTool.machineInfo, [
                  'causedByMachineOrTool',
                  'machineInfo',
                ])}
                <div className="mt-4 border-t pt-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <CheckboxField
                      id="causativeFunctional"
                      label="Was the causative machine functional?"
                      checked={record.causedByMachineOrTool.wasFunctional ?? false}
                      onChange={checked => updateRecord(['causedByMachineOrTool', 'wasFunctional'], checked)}
                    />
                    <CheckboxField
                      id="causativeManual"
                      label="Used according to manual?"
                      checked={record.causedByMachineOrTool.usedAccordingToManual ?? false}
                      onChange={checked => updateRecord(['causedByMachineOrTool', 'usedAccordingToManual'], checked)}
                    />
                    <InputField
                      label="Description of Use"
                      id="causativeUseDesc"
                      value={record.causedByMachineOrTool.descriptionOfUse}
                      onChange={e => handleChange(e, ['causedByMachineOrTool', 'descriptionOfUse'])}
                      className="md:col-span-2"
                    />
                  </div>
                </div>
              </div>
            )}
          </Section>

          {/* Section 4: Other Machinery & Tools Involved */}
          <Section title="4. Other Machinery/Tools Information">
            <CheckboxField
              id="otherMachineryInvolved"
              label="Were other machines or tools involved in the activity (but not the direct cause)?"
              checked={record.machineryToolsInfo.involved}
              onChange={checked => updateRecord(['machineryToolsInfo', 'involved'], checked)}
            />
            {record.machineryToolsInfo.involved && (
              <div className="mt-4">{renderMachineryToolsInfo(record.machineryToolsInfo, ['machineryToolsInfo'])}</div>
            )}
          </Section>

          {/* Section 5: Safety and Compliance */}
          <Section title="5. Safety Measures and Compliance">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Protective Equipment */}
              <div>
                <h3 className="font-semibold mb-2">Protective Equipment</h3>
                <SelectField
                  label="Used Protective Equipment?"
                  id="protectiveEquipment"
                  value={
                    typeof record.usedProtectiveEquipment === 'boolean'
                      ? record.usedProtectiveEquipment
                        ? 'Yes'
                        : 'No'
                      : 'List Provided'
                  }
                  onChange={e => {
                    const val = e.target.value;
                    if (val === 'Yes') updateRecord(['usedProtectiveEquipment'], ['']);
                    if (val === 'No') updateRecord(['usedProtectiveEquipment'], false);
                  }}
                  options={['No', 'Yes']} // Simplification: 'Yes' means provide list
                />

                {Array.isArray(record.usedProtectiveEquipment) && (
                  <div className="mt-3 space-y-2">
                    <InputField
                      label="List Protective Equipment (comma separated)"
                      id="ppeList"
                      value={record.usedProtectiveEquipment.join(', ')}
                      onChange={e =>
                        updateRecord(
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
                    typeof record.usedSafetySupport === 'boolean'
                      ? record.usedSafetySupport
                        ? 'Yes'
                        : 'No'
                      : 'Details Provided'
                  }
                  onChange={e => {
                    const val = e.target.value;
                    if (val === 'Yes') updateRecord(['usedSafetySupport'], { requiredMoreThanOnePerson: false });
                    if (val === 'No') updateRecord(['usedSafetySupport'], false);
                  }}
                  options={['No', 'Yes']}
                />

                {typeof record.usedSafetySupport === 'object' && record.usedSafetySupport !== null && (
                  <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                    <CheckboxField
                      id="multiPerson"
                      label="Activity required more than one person?"
                      checked={record.usedSafetySupport.requiredMoreThanOnePerson}
                      onChange={checked => updateRecord(['usedSafetySupport', 'requiredMoreThanOnePerson'], checked)}
                    />
                  </div>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6 border-t pt-6">
              <CheckboxField
                id="bhpCompliance"
                label="BHP Compliance Met?"
                checked={record.bhpCompliance}
                onChange={checked => updateRecord(['bhpCompliance'], checked)}
              />
              <CheckboxField
                id="properPreparation"
                label="Proper Preparation Completed?"
                checked={record.hasProperPreparation}
                onChange={checked => updateRecord(['hasProperPreparation'], checked)}
              />
            </div>

            <div className="mt-6 border-t pt-6 bg-yellow-50/50 p-4 rounded-lg">
              <h3 className="font-semibold mb-3">BHP Training & Risk Assessment</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <CheckboxField
                  id="completedTraining"
                  label="Completed BHP Training?"
                  checked={record.bhpTraining.completedTraining}
                  onChange={checked => updateRecord(['bhpTraining', 'completedTraining'], checked)}
                />
                <CheckboxField
                  id="hasRiskAssessment"
                  label="Has Risk Assessment Document?"
                  checked={record.bhpTraining.hasRiskAssessment}
                  onChange={checked => updateRecord(['bhpTraining', 'hasRiskAssessment'], checked)}
                />
                <InputField
                  label="Risk Reduction Measures (Optional)"
                  id="riskMeasures"
                  value={record.bhpTraining.riskReductionMeasures}
                  onChange={e => handleChange(e, ['bhpTraining', 'riskReductionMeasures'])}
                  className="md:col-span-2"
                  rows={2}
                />
              </div>
            </div>
          </Section>

          {/* Section 6: Intoxication */}
          <Section title="6. Intoxication Status">
            <CheckboxField
              id="intoxicated"
              label="Was the injured person intoxicated (alcohol/other substances)?"
              checked={record.intoxication.intoxicated}
              onChange={checked => updateRecord(['intoxication', 'intoxicated'], checked)}
            />
            {record.intoxication.intoxicated && (
              <div className="mt-4">
                <SelectField
                  label="Tested By"
                  id="testedBy"
                  value={record.intoxication.testedBy ?? 'none'}
                  onChange={e => handleChange(e, ['intoxication', 'testedBy'])}
                  options={['none', 'police', 'medicalHelp']}
                />
              </div>
            )}
          </Section>

          {/* Section 7: State Authority Actions */}
          <Section title="7. State Authority Actions">{renderStateAuthorityActions}</Section>

          {/* Section 8: Medical Help */}
          <Section title="8. Medical Help & Consequences">{renderMedicalHelp}</Section>

          {/* Action Buttons */}
          <div className="mt-10 pt-6 border-t flex justify-end space-x-4 mr-3">
            <button
              type="button"
              onClick={handleReset}
              className="flex items-center px-6 py-3 text-sm font-semibold bg-gray-200 rounded-xl shadow-md hover:bg-gray-300 transition duration-150 ease-in-out"
            >
              <Eraser className="w-4 h-4 mr-2" /> Reset Form
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
