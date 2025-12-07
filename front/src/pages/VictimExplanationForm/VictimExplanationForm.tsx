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
import { convertDate } from '@/utils';

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
  const [openSections, setOpenSections] = useState<Record<string, boolean>>({
    personalData: true,
    accidentDetails: false,
    machineRelated: false,
    otherMachinery: false,
    safety: false,
    intoxication: false,
    authorities: false,
    medicalHelp: false,
  });

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

    const sectionsToOpen: Record<string, boolean> = {};

    // Accident Details
    if (ctx.collectedData.accident_date) {
      updateRecord(['accidentDetails', 'date'], convertDate(ctx.collectedData.accident_date));
      sectionsToOpen.accidentDetails = true;
    }
    if (ctx.collectedData.accident_time) {
      updateRecord(['accidentDetails', 'time'], ctx.collectedData.accident_time);
      sectionsToOpen.accidentDetails = true;
    }
    if (ctx.collectedData.location) {
      updateRecord(['accidentDetails', 'location'], ctx.collectedData.location);
      sectionsToOpen.accidentDetails = true;
    }
    if (ctx.collectedData.work_start_time) {
      updateRecord(['accidentDetails', 'plannedWorkStart'], ctx.collectedData.work_start_time);
      sectionsToOpen.accidentDetails = true;
    }
    if (ctx.collectedData.work_end_time) {
      updateRecord(['accidentDetails', 'plannedWorkEnd'], ctx.collectedData.work_end_time);
      sectionsToOpen.accidentDetails = true;
    }
    
    if (ctx.collectedData.activity_before_accident) {
      updateRecord(['workActivityBeforeAccident'], ctx.collectedData.activity_before_accident);
      sectionsToOpen.accidentDetails = true;
    }
    if (ctx.collectedData.circumstances) {
      updateRecord(['accidentCircumstances'], ctx.collectedData.circumstances);
      sectionsToOpen.accidentDetails = true;
    }
    if (ctx.collectedData.cause || ctx.collectedData.direct_cause) {
      const causeText = [ctx.collectedData.cause, ctx.collectedData.direct_cause].filter(Boolean).join(' | ');
      updateRecord(['accidentCause'], causeText);
      sectionsToOpen.accidentDetails = true;
    }

    if (ctx.collectedData.machines_involved) {
      sectionsToOpen.machineRelated = true;
    }

    if (ctx.collectedData.injury_type || ctx.collectedData.medical_help) {
      if (ctx.collectedData.injury_type) {
        updateRecord(['medicalHelp', 'diagnosedInjury'], ctx.collectedData.injury_type);
      }
      sectionsToOpen.medicalHelp = true;
    }

    if (ctx.collectedData.investigation) {
      sectionsToOpen.authorities = true;
    }

    if (Object.keys(sectionsToOpen).length > 0) {
      setOpenSections(prev => ({ ...prev, ...sectionsToOpen }));
    }
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
          label="Numer serii"
          id="idNumber"
          value={record.personalData.idNumber}
          onChange={e => handleChange(e, ['personalData', 'idNumber'])}
          required
        />
        <InputField
          label="Data urodzenia"
          id="birthDate"
          type="date"
          value={record.personalData.birthDate}
          onChange={e => handleChange(e, ['personalData', 'birthDate'])}
        />
        <InputField
          label="Miejsce urodzenia"
          id="birthPlace"
          value={record.personalData.birthPlace}
          onChange={e => handleChange(e, ['personalData', 'birthPlace'])}
        />
        <InputField
          label="Numer telefonu"
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
          label="Adres"
          id="adres"
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
          label="Miejsce wypadku"
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
          label="Czy służby porządkowe były zaangażowane?"
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
            <Plus className="w-4 h-4 mr-2" /> Dodaj akcję nadzorczą
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
          label="Czy osoba poszkodowana uzyskała pomoc medyczną?"
          checked={isDetails}
          onChange={checked => updateRecord(['medicalHelp'], checked ? { sickLeaveOnAccidentDay: false } : false)}
        />

        {isDetails && (
          <div className="mt-4 p-4 border border-gray-300 rounded-lg bg-gray-50 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InputField
                label="Data pierwszej pomocy"
                id="firstAidDate"
                type="date"
                value={medicalHelp.dateOfFirstAid}
                onChange={e => handleChange(e, ['medicalHelp', 'dateOfFirstAid'])}
              />
              <InputField
                label="Nazwa placówki medycznej"
                id="facilityName"
                value={medicalHelp.healthcareFacilityName}
                onChange={e => handleChange(e, ['medicalHelp', 'healthcareFacilityName'])}
              />
              <InputField
                label="Zdiagnozowana kontuzja"
                id="injury"
                value={medicalHelp.diagnosedInjury}
                onChange={e => handleChange(e, ['medicalHelp', 'diagnosedInjury'])}
                className="md:col-span-2"
              />

              <CheckboxField
                id="sickLeaveAccidentDay"
                label="Otrzymano zwolnienie lekarskie na dzień wypadku?"
                checked={medicalHelp.sickLeaveOnAccidentDay}
                onChange={checked => updateRecord(['medicalHelp', 'sickLeaveOnAccidentDay'], checked)}
              />
            </div>

            <h5 className="text-md font-semibold mt-4 bg-green border-b pb-1">
              Okres hospitalizacji (opcjonalnie)
            </h5>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <InputField
                label="Od"
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
                label="Do"
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
                label="Adres szpitala"
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

            <h5 className="text-md font-semibold mt-4 bg-green border-b pb-1">Okres niezdolności do pracy (opcjonalnie)</h5>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InputField
                label="Od"
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
                label="Do"
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
    <div className="min-h-screen flex justify-center">
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
          <Section 
            title="1. Dane osobowe" 
            isOpen={openSections.personalData}
            onToggle={(isOpen) => setOpenSections(prev => ({ ...prev, personalData: isOpen }))}
          >
            {renderPersonSection}
          </Section>

          {/* Section 2: Accident Details */}
          <Section 
            title="2. Szczegóły wypadku"
            isOpen={openSections.accidentDetails}
            onToggle={(isOpen) => setOpenSections(prev => ({ ...prev, accidentDetails: isOpen }))}
          >
            {renderAccidentDetails}
            <div className="space-y-4 mt-6">
              <InputField
                label="Czynność wykonywana przed wypadkiem"
                id="activityBefore"
                value={record.workActivityBeforeAccident}
                onChange={e => handleChange(e, ['workActivityBeforeAccident'])}
                rows={3}
              />
              <InputField
                label="Okoliczności wypadku"
                id="circumstances"
                value={record.accidentCircumstances}
                onChange={e => handleChange(e, ['accidentCircumstances'])}
                rows={3}
              />
              <InputField
                label="Przyczyna wypadku"
                id="cause"
                value={record.accidentCause}
                onChange={e => handleChange(e, ['accidentCause'])}
                rows={3}
              />
            </div>
          </Section>

          {/* Section 3: Machine/Tool Related Accident */}
          <Section 
            title="3. Wypadek spowodowany przez maszynę/narzędzie"
            isOpen={openSections.machineRelated}
            onToggle={(isOpen) => setOpenSections(prev => ({ ...prev, machineRelated: isOpen }))}
          >
            <CheckboxField
              id="causedByMachine"
              label="Sprawdź czy wypadek był spowodowany bezpośrednio przez maszynę lub urządzenie."
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
          <Section 
            title="4. Inne maszyny i narzędzia biorące udział w zdarzeniu"
            isOpen={openSections.otherMachinery}
            onToggle={(isOpen) => setOpenSections(prev => ({ ...prev, otherMachinery: isOpen }))}
          >
            <CheckboxField
              id="otherMachineryInvolved"
              label="Czy jakieś inne maszyny lub urządzenia miały udział w zdarzeniu (nie bezpośrednio)"
              checked={record.machineryToolsInfo.involved}
              onChange={checked => updateRecord(['machineryToolsInfo', 'involved'], checked)}
            />
            {record.machineryToolsInfo.involved && (
              <div className="mt-4">{renderMachineryToolsInfo(record.machineryToolsInfo, ['machineryToolsInfo'])}</div>
            )}
          </Section>

          {/* Section 5: Safety and Compliance */}
          <Section 
            title="5. Bezpieczeństwo i zgodność z procedurami"
            isOpen={openSections.safety}
            onToggle={(isOpen) => setOpenSections(prev => ({ ...prev, safety: isOpen }))}
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Protective Equipment */}
              <div>
                <h3 className="font-semibold mb-2">Noszone ubrania ochronne</h3>
                <SelectField
                  label="Czy w trakcie zdarzenia noszono ubrania ochronne?"
                  id="protectiveEquipment"
                  value={
                    typeof record.usedProtectiveEquipment === 'boolean'
                      ? record.usedProtectiveEquipment
                        ? 'Tak'
                        : 'Nie'
                      : 'List Provided'
                  }
                  onChange={e => {
                    const val = e.target.value;
                    if (val === 'Tak') updateRecord(['usedProtectiveEquipment'], ['']);
                    if (val === 'Nie') updateRecord(['usedProtectiveEquipment'], false);
                  }}
                  options={['Nie', 'Tak']} // Simplification: 'Tak' means provide list
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
                <h3 className="font-semibold mb-2">Wsparcie ochronne</h3>
                <SelectField
                  label="Czy wsparcie ochronne było używane?"
                  id="safetySupport"
                  value={
                    typeof record.usedSafetySupport === 'boolean'
                      ? record.usedSafetySupport
                        ? 'Tak'
                        : 'No'
                      : 'Details Provided'
                  }
                  onChange={e => {
                    const val = e.target.value;
                    if (val === 'Tak') updateRecord(['usedSafetySupport'], { requiredMoreThanOnePerson: false });
                    if (val === 'Nie') updateRecord(['usedSafetySupport'], false);
                  }}
                  options={['Nie', 'Tak']}
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
                label="Czy ukończono szkolenie BHP?"
                checked={record.bhpCompliance}
                onChange={checked => updateRecord(['bhpCompliance'], checked)}
              />
              <CheckboxField
                id="properPreparation"
                label="Czy zrealizowano odpowiednie przygotowanie?"
                checked={record.hasProperPreparation}
                onChange={checked => updateRecord(['hasProperPreparation'], checked)}
              />
            </div>

            <div className="mt-6 border-t pt-6 bg-yellow-50/50 p-4 rounded-lg">
              <h3 className="font-semibold mb-3">Szkolenie BHP i zarządzanie ryzykiem</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <CheckboxField
                  id="completedTraining"
                  label="Czy ukończono szkolenie BHP?"
                  checked={record.bhpTraining.completedTraining}
                  onChange={checked => updateRecord(['bhpTraining', 'completedTraining'], checked)}
                />
                <CheckboxField
                  id="hasRiskAssessment"
                  label="Czy posiadane dokumenty zarządzania ryzykiem?"
                  checked={record.bhpTraining.hasRiskAssessment}
                  onChange={checked => updateRecord(['bhpTraining', 'hasRiskAssessment'], checked)}
                />
                <InputField
                  label="Środki zmniejszenia ryzyka (Opcjonalne)"
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
          <Section 
            title="6. Stan trzeźwości"
            isOpen={openSections.intoxication}
            onToggle={(isOpen) => setOpenSections(prev => ({ ...prev, intoxication: isOpen }))}
          >
            <CheckboxField
              id="intoxicated"
              label="Czy poszkodowany/a był/a pod wpływem (alkohol / inne używki)?"
              checked={record.intoxication.intoxicated}
              onChange={checked => updateRecord(['intoxication', 'intoxicated'], checked)}
            />
            {record.intoxication.intoxicated && (
              <div className="mt-4">
                <SelectField
                  label="Testowane przez"
                  id="testedBy"
                  value={record.intoxication.testedBy ?? 'none'}
                  onChange={e => handleChange(e, ['intoxication', 'testedBy'])}
                  options={['Nikt', 'police', 'medicalHelp']}
                />
              </div>
            )}
          </Section>

          {/* Section 7: State Authority Actions */}
          <Section 
            title="7. Akcje nadzorcze"
            isOpen={openSections.authorities}
            onToggle={(isOpen) => setOpenSections(prev => ({ ...prev, authorities: isOpen }))}
          >
            {renderStateAuthorityActions}
          </Section>

          {/* Section 8: Medical Help */}
          <Section 
            title="8. Udzielona pomoc medyczna"
            isOpen={openSections.medicalHelp}
            onToggle={(isOpen) => setOpenSections(prev => ({ ...prev, medicalHelp: isOpen }))}
          >
            {renderMedicalHelp}
          </Section>

          {/* Action Buttons */}
          <div className="mt-10 pt-6 border-t flex justify-end space-x-4 mr-3">
            <button
              type="button"
              onClick={handleReset}
              className="flex items-center px-6 py-3 text-sm font-semibold bg-gray-200 rounded-xl shadow-md hover:bg-gray-300 transition duration-150 ease-in-out"
            >
              <Eraser className="w-4 h-4 mr-2" /> Resetuj formularz
            </button>
            <button
              type="submit"
              className="flex items-center px-6 py-3 text-sm font-semibold text-white bg-primary rounded-xl shadow-lg hover:bg-green-700 transition duration-150 ease-in-out transform hover:scale-105"
            >
              <Save className="w-4 h-4 mr-2" /> Zapisz zmiany
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export { VictimExplanationForm };
