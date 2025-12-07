import React, { useState, useEffect } from 'react';
import { Save, Printer, Eraser } from 'lucide-react';
import { Section } from '@/components/Section';
import { InputField } from '@/components/InputField/InputField';
import { SelectField } from '@/components/SelectField';
import { CheckboxField } from '@/components/CheckboxField';
import { useCtx } from '@/context';
import { convertDate } from '@/utils';

// --- Types based on Schema ---

interface AccidentReportData {
  accident_date: string;
  accident_time: string;
  location: string;
  work_start_time: string;
  work_end_time: string;
  activity_before_accident: string;
  circumstances: string;
  cause: string;
  place_description: string;

  // Machinery
  machines_involved: boolean;
  machine_name_type: string;
  machine_production_date: string;
  machine_condition: string;
  proper_use: string;
  machine_description: string;

  // Safety
  safety_equipment_used: boolean;
  safety_equipment_types: string;
  safety_equipment_condition: string;
  bhp_compliance: boolean;
  professional_preparation: boolean;
  bhp_training: boolean;
  risk_assessment: boolean;
  risk_mitigation: string;
  safety_measures: boolean;

  // Work Context
  work_solo_or_team: string;

  // Sobriety & Investigation
  sobriety_state: boolean;
  sobriety_tested: boolean;
  sobriety_tested_by: string;
  investigation_authorities: boolean;
  authority_name: string;
  authority_address: string;
  authority_case_number: string;
  authority_case_status: string;

  // Medical
  first_aid_provided: boolean;
  first_aid_date: string;
  medical_facility: string;
  hospitalization_period: string;
  hospitalization_place: string;
  diagnosed_injury: string;
  work_incapacity_period: string;
  sick_leave_on_accident_day: boolean;

  // Narrative
  witnesses: string;
  event_sequence: string;
}

const initialData: AccidentReportData = {
  accident_date: '',
  accident_time: '',
  location: '',
  work_start_time: '',
  work_end_time: '',
  activity_before_accident: '',
  circumstances: '',
  cause: '',
  place_description: '',
  machines_involved: false,
  machine_name_type: '',
  machine_production_date: '',
  machine_condition: '',
  proper_use: '',
  machine_description: '',
  safety_equipment_used: false,
  safety_equipment_types: '',
  safety_equipment_condition: '',
  bhp_compliance: false,
  professional_preparation: false,
  bhp_training: false,
  risk_assessment: false,
  risk_mitigation: '',
  safety_measures: false,
  work_solo_or_team: 'Solo',
  sobriety_state: true,
  sobriety_tested: false,
  sobriety_tested_by: '',
  investigation_authorities: false,
  authority_name: '',
  authority_address: '',
  authority_case_number: '',
  authority_case_status: '',
  first_aid_provided: false,
  first_aid_date: '',
  medical_facility: '',
  hospitalization_period: '',
  hospitalization_place: '',
  diagnosed_injury: '',
  work_incapacity_period: '',
  sick_leave_on_accident_day: false,
  witnesses: '',
  event_sequence: '',
};

export const AccidentReportForm = () => {
  const ctx = useCtx();
  const [formData, setFormData] = useState<AccidentReportData>(initialData);
  const [openSections, setOpenSections] = useState<Record<string, boolean>>({
    general: true,
    workDetails: false,
    machinery: false,
    safety: false,
    investigation: false,
    medical: false,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { id, value } = e.target;
    setFormData(prev => ({ ...prev, [id]: value }));
  };

  const handleCheckboxChange = (id: keyof AccidentReportData, checked: boolean) => {
    setFormData(prev => ({ ...prev, [id]: checked }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Form Submitted:', formData);
    alert('Report saved to console!');
  };

  const handleReset = () => {
    setFormData(initialData);
    setOpenSections({
      general: true,
      workDetails: false,
      machinery: false,
      safety: false,
      investigation: false,
      medical: false,
    });
  };


  useEffect(() => {
    if (!ctx.collectedData) return;

    const sectionsToOpen: Record<string, boolean> = {};
    const updates: Partial<AccidentReportData> = {};

    // General Information
    if (ctx.collectedData.accident_date) {
      updates.accident_date = convertDate(ctx.collectedData.accident_date);
      sectionsToOpen.general = true;
    }
    if (ctx.collectedData.accident_time) {
      updates.accident_time = ctx.collectedData.accident_time;
      sectionsToOpen.general = true;
    }
    if (ctx.collectedData.location) {
      updates.location = ctx.collectedData.location;
      sectionsToOpen.general = true;
    }
    if (ctx.collectedData.place_description) {
      updates.place_description = ctx.collectedData.place_description;
      sectionsToOpen.general = true;
    }

    // Work Details
    if (ctx.collectedData.work_start_time) {
      updates.work_start_time = ctx.collectedData.work_start_time;
      sectionsToOpen.workDetails = true;
    }
    if (ctx.collectedData.work_end_time) {
      updates.work_end_time = ctx.collectedData.work_end_time;
      sectionsToOpen.workDetails = true;
    }
    if (ctx.collectedData.activity_before_accident) {
      updates.activity_before_accident = ctx.collectedData.activity_before_accident;
      sectionsToOpen.workDetails = true;
    }
    if (ctx.collectedData.circumstances) {
      updates.circumstances = ctx.collectedData.circumstances;
      sectionsToOpen.workDetails = true;
    }
    if (ctx.collectedData.cause) {
      updates.cause = ctx.collectedData.cause;
      sectionsToOpen.workDetails = true;
    }
    if (ctx.collectedData.event_sequence) {
      updates.event_sequence = ctx.collectedData.event_sequence;
      sectionsToOpen.workDetails = true;
    }
    if (ctx.collectedData.witnesses) {
      updates.witnesses = ctx.collectedData.witnesses;
      sectionsToOpen.workDetails = true;
    }

    // Machinery
    if (ctx.collectedData.machines_involved) {
      updates.machines_involved = true;
      updates.machine_description = ctx.collectedData.machines_involved;
      sectionsToOpen.machinery = true;
    }
    if (ctx.collectedData.machine_condition) {
      updates.machine_condition = ctx.collectedData.machine_condition;
      sectionsToOpen.machinery = true;
    }
    if (ctx.collectedData.proper_use) {
      updates.proper_use = ctx.collectedData.proper_use;
      sectionsToOpen.machinery = true;
    }

    // Medical
    if (ctx.collectedData.injury_type) {
      updates.diagnosed_injury = ctx.collectedData.injury_type;
      sectionsToOpen.medical = true;
    }
    if (ctx.collectedData.medical_help) {
      updates.first_aid_provided = true;
      updates.medical_facility = ctx.collectedData.medical_help;
      sectionsToOpen.medical = true;
    }

    // Investigation
    if (ctx.collectedData.investigation) {
      updates.investigation_authorities = true;
      updates.authority_name = ctx.collectedData.investigation;
      sectionsToOpen.investigation = true;
    }

    // Apply updates
    if (Object.keys(updates).length > 0) {
      setFormData(prev => ({ ...prev, ...updates }));
    }

    // Open sections
    if (Object.keys(sectionsToOpen).length > 0) {
      setOpenSections(prev => ({ ...prev, ...sectionsToOpen }));
    }
  }, [ctx.collectedData]);

  return (
    <div className="min-h-screen bg-gray-100 py-8 px-4 sm:px-6 lg:px-8 font-sans">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">Zawiadomienie o wypadku</h1>
            <p className="mt-2 text-gray-600">
              Proszę wypełnić wszystkie odpowiednie sekcje dotyczące wypadku przy pracy.
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          {/* 1. General Information */}
          <Section 
            title="Opis ogólny" 
            isOpen={openSections.general}
            onToggle={(isOpen) => setOpenSections(prev => ({ ...prev, general: isOpen }))}
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <InputField
                id="accident_date"
                label="Data wypadku"
                type="date"
                value={formData.accident_date}
                onChange={handleChange}
                required
              />
              <InputField
                id="accident_time"
                label="Godzina wypadku"
                type="time"
                value={formData.accident_time}
                onChange={handleChange}
                required
              />
              <InputField
                id="location"
                label="Lokalizacja wypadku"
                value={formData.location}
                onChange={handleChange}
                className="md:col-span-2"
              />
              <InputField
                id="place_description"
                label="Opis lokalizacji"
                value={formData.place_description}
                onChange={handleChange}
                rows={2}
                className="md:col-span-2"
              />
            </div>
          </Section>

          {/* 2. Work Details */}
          <Section 
            title="Okoliczności pracy"
            isOpen={openSections.workDetails}
            onToggle={(isOpen) => setOpenSections(prev => ({ ...prev, workDetails: isOpen }))}
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <InputField
                id="work_start_time"
                label="Planowa godzina rozpoczecia pracy"
                type="time"
                value={formData.work_start_time}
                onChange={handleChange}
              />
              <InputField
                id="work_end_time"
                label="Planowa godzina zakonczenia pracy"
                type="time"
                value={formData.work_end_time}
                onChange={handleChange}
              />
              <SelectField
                id="work_solo_or_team"
                label="Organizacja pracy"
                value={formData.work_solo_or_team}
                onChange={handleChange}
                options={['Indywidualnie', 'Zespół', 'Grupa nadzorowana']}
              />
              <InputField
                id="activity_before_accident"
                label="Czynność przed wypadkiem"
                value={formData.activity_before_accident}
                onChange={handleChange}
              />
              <InputField
                id="circumstances"
                label="Okoliczności wypadku"
                value={formData.circumstances}
                onChange={handleChange}
                rows={3}
                className="md:col-span-2"
              />
              <InputField
                id="cause"
                label="Przyczyna wypadku"
                value={formData.cause}
                onChange={handleChange}
                rows={2}
                className="md:col-span-2"
              />
              <InputField
                id="event_sequence"
                label="Kolejność zdarzeń"
                value={formData.event_sequence}
                onChange={handleChange}
                rows={3}
                className="md:col-span-2"
              />
              <InputField
                id="witnesses"
                label="Świadkowie"
                value={formData.witnesses}
                onChange={handleChange}
                rows={2}
                className="md:col-span-2"
              />
            </div>
          </Section>

          {/* 3. Machinery */}
          <Section 
            title="Udział maszyn"
            isOpen={openSections.machinery}
            onToggle={(isOpen) => setOpenSections(prev => ({ ...prev, machinery: isOpen }))}
          >
            <CheckboxField
              id="machines_involved"
              label="Czy w wypadku brały udział maszyny?"
              checked={formData.machines_involved}
              onChange={checked => handleCheckboxChange('machines_involved', checked)}
            />

            {formData.machines_involved && (
              <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-6 pl-4 border-l-4 border-blue-100 transition-all">
                <InputField
                  id="machine_name_type"
                  label="Nazwa/Typ maszyny"
                  value={formData.machine_name_type}
                  onChange={handleChange}
                />
                <InputField
                  id="machine_production_date"
                  label="Data produkcji maszyny"
                  type="date"
                  value={formData.machine_production_date}
                  onChange={handleChange}
                />
                <InputField
                  id="machine_condition"
                  label="Stan maszyny"
                  value={formData.machine_condition}
                  onChange={handleChange}
                />
                <InputField
                  id="proper_use"
                  label="Czy była używana prawidłowo?"
                  value={formData.proper_use}
                  onChange={handleChange}
                  placeholder="Tak/Nie, wyjaśnij szczegóły"
                />
                <InputField
                  id="machine_description"
                  label="Dodatkowe szczegóły maszyny"
                  value={formData.machine_description}
                  onChange={handleChange}
                  rows={2}
                  className="md:col-span-2"
                />
              </div>
            )}
          </Section>

          {/* 4. Safety & Compliance */}
          <Section 
            title="Bezpieczeństwo i zgodność"
            isOpen={openSections.safety}
            onToggle={(isOpen) => setOpenSections(prev => ({ ...prev, safety: isOpen }))}
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <h3 className="font-semibold text-gray-700 mb-2">Przygotowanie pracownika</h3>
                <CheckboxField
                  id="bhp_training"
                  label="Aktualne szkolenie BHP?"
                  checked={formData.bhp_training}
                  onChange={c => handleCheckboxChange('bhp_training', c)}
                />
                <CheckboxField
                  id="professional_preparation"
                  label="Przygotowanie zawodowe?"
                  checked={formData.professional_preparation}
                  onChange={c => handleCheckboxChange('professional_preparation', c)}
                />
                <CheckboxField
                  id="bhp_compliance"
                  label="Zgodność z zasadami BHP?"
                  checked={formData.bhp_compliance}
                  onChange={c => handleCheckboxChange('bhp_compliance', c)}
                />
              </div>

              <div className="space-y-2">
                <h3 className="font-semibold text-gray-700 mb-2">Środki ochronne</h3>
                <CheckboxField
                  id="safety_equipment_used"
                  label="Czy używano środków ochronnych?"
                  checked={formData.safety_equipment_used}
                  onChange={c => handleCheckboxChange('safety_equipment_used', c)}
                />
                {formData.safety_equipment_used && (
                  <>
                    <InputField
                      id="safety_equipment_types"
                      label="Użyte typy"
                      value={formData.safety_equipment_types}
                      onChange={handleChange}
                    />
                    <InputField
                      id="safety_equipment_condition"
                      label="Stan środków"
                      value={formData.safety_equipment_condition}
                      onChange={handleChange}
                    />
                  </>
                )}
              </div>

              <div className="md:col-span-2 pt-4 border-t border-gray-100">
                <h3 className="font-semibold text-gray-700 mb-2">Zarządzanie ryzykiem</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="flex flex-col gap-2">
                    <CheckboxField
                      id="risk_assessment"
                      label="Czy przeprowadzono ocenę ryzyka?"
                      checked={formData.risk_assessment}
                      onChange={c => handleCheckboxChange('risk_assessment', c)}
                    />
                    <CheckboxField
                      id="safety_measures"
                      label="Czy środki bezpieczeństwa były na miejscu?"
                      checked={formData.safety_measures}
                      onChange={c => handleCheckboxChange('safety_measures', c)}
                    />
                  </div>
                  <InputField
                    id="risk_mitigation"
                    label="Strategie ograniczania ryzyka"
                    value={formData.risk_mitigation}
                    onChange={handleChange}
                  />
                </div>
              </div>
            </div>
          </Section>

          {/* 5. Sobriety & Authorities */}
          <Section 
            title="Szczegóły dochodzenia"
            isOpen={openSections.investigation}
            onToggle={(isOpen) => setOpenSections(prev => ({ ...prev, investigation: isOpen }))}
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <h3 className="font-semibold text-gray-700">Trzeźwość</h3>
                <CheckboxField
                  id="sobriety_state"
                  label="Osoba wydawała się trzeźwa?"
                  checked={formData.sobriety_state}
                  onChange={c => handleCheckboxChange('sobriety_state', c)}
                />
                <CheckboxField
                  id="sobriety_tested"
                  label="Czy przeprowadzono test trzeźwości?"
                  checked={formData.sobriety_tested}
                  onChange={c => handleCheckboxChange('sobriety_tested', c)}
                />
                {formData.sobriety_tested && (
                  <InputField
                    id="sobriety_tested_by"
                    label="Testowane przez"
                    value={formData.sobriety_tested_by}
                    onChange={handleChange}
                  />
                )}
              </div>

              <div className="space-y-2">
                <h3 className="font-semibold text-gray-700">Służby zewnętrzne</h3>
                <CheckboxField
                  id="investigation_authorities"
                  label="Czy powiadomiono służby zewnętrzne?"
                  checked={formData.investigation_authorities}
                  onChange={c => handleCheckboxChange('investigation_authorities', c)}
                />
                {formData.investigation_authorities && (
                  <div className="space-y-4 pt-2">
                    <InputField
                      id="authority_name"
                      label="Nazwa służby"
                      value={formData.authority_name}
                      onChange={handleChange}
                    />
                    <InputField
                      id="authority_address"
                      label="Adres"
                      value={formData.authority_address}
                      onChange={handleChange}
                    />
                    <div className="grid grid-cols-2 gap-4">
                      <InputField
                        id="authority_case_number"
                        label="Numer sprawy"
                        value={formData.authority_case_number}
                        onChange={handleChange}
                      />
                      <InputField
                        id="authority_case_status"
                        label="Status"
                        value={formData.authority_case_status}
                        onChange={handleChange}
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>
          </Section>

          {/* 6. Medical & Consequences */}
          <Section 
            title="Medyczne i konsekwencje"
            isOpen={openSections.medical}
            onToggle={(isOpen) => setOpenSections(prev => ({ ...prev, medical: isOpen }))}
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="md:col-span-2 space-y-4">
                <CheckboxField
                  id="first_aid_provided"
                  label="Czy natychmiast udzielono pierwszej pomocy?"
                  checked={formData.first_aid_provided}
                  onChange={c => handleCheckboxChange('first_aid_provided', c)}
                />
                {formData.first_aid_provided && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <InputField
                      id="first_aid_date"
                      label="Data/Godzina pierwszej pomocy"
                      type="datetime-local"
                      value={formData.first_aid_date}
                      onChange={handleChange}
                    />
                  </div>
                )}
              </div>

              <InputField
                id="medical_facility"
                label="Placówka medyczna"
                value={formData.medical_facility}
                onChange={handleChange}
              />
              <InputField
                id="diagnosed_injury"
                label="Zdiagnozowana kontuzja"
                value={formData.diagnosed_injury}
                onChange={handleChange}
              />

              <InputField
                id="hospitalization_place"
                label="Miejsce hospitalizacji"
                value={formData.hospitalization_place}
                onChange={handleChange}
              />
              <InputField
                id="hospitalization_period"
                label="Okres (dni)"
                value={formData.hospitalization_period}
                onChange={handleChange}
              />

              <InputField
                id="work_incapacity_period"
                label="Okres niezdolności do pracy"
                value={formData.work_incapacity_period}
                onChange={handleChange}
              />
              <div className="flex items-end pb-3">
                <CheckboxField
                  id="sick_leave_on_accident_day"
                  label="Czy zwolnienie lekarskie wystawiono w dniu wypadku?"
                  checked={formData.sick_leave_on_accident_day}
                  onChange={c => handleCheckboxChange('sick_leave_on_accident_day', c)}
                />
              </div>
            </div>
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
