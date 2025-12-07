import React, { useState } from 'react';
import { Save, Printer } from 'lucide-react';
import { Section } from '@/components/Section';
import { InputField } from '@/components/InputField/InputField';
import { SelectField } from '@/components/SelectField';
import { CheckboxField } from '@/components/CheckboxField';

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
  const [formData, setFormData] = useState<AccidentReportData>(initialData);

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
          <Section title="Opis ogoly" defaultOpen={true}>
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
          <Section title="Okolicznosci pracy">
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
                label="Work Arrangement"
                value={formData.work_solo_or_team}
                onChange={handleChange}
                options={['Solo', 'Team', 'Supervised Group']}
              />
              <InputField
                id="activity_before_accident"
                label="Activity Before Accident"
                value={formData.activity_before_accident}
                onChange={handleChange}
              />
              <InputField
                id="circumstances"
                label="Okolicznosci wypadku"
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
                label="Sequence of Events"
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
          <Section title="Machinery Involvement">
            <CheckboxField
              id="machines_involved"
              label="Were machines involved in the accident?"
              checked={formData.machines_involved}
              onChange={checked => handleCheckboxChange('machines_involved', checked)}
            />

            {formData.machines_involved && (
              <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-6 pl-4 border-l-4 border-blue-100 transition-all">
                <InputField
                  id="machine_name_type"
                  label="Machine Name/Type"
                  value={formData.machine_name_type}
                  onChange={handleChange}
                />
                <InputField
                  id="machine_production_date"
                  label="Data produckji maszyny"
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
                  label="Was it used properly?"
                  value={formData.proper_use}
                  onChange={handleChange}
                  placeholder="Yes/No, explain details"
                />
                <InputField
                  id="machine_description"
                  label="Additional Machine Details"
                  value={formData.machine_description}
                  onChange={handleChange}
                  rows={2}
                  className="md:col-span-2"
                />
              </div>
            )}
          </Section>

          {/* 4. Safety & Compliance */}
          <Section title="Safety & Compliance">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <h3 className="font-semibold text-gray-700 mb-2">Employee Readiness</h3>
                <CheckboxField
                  id="bhp_training"
                  label="Current HSE/BHP Training?"
                  checked={formData.bhp_training}
                  onChange={c => handleCheckboxChange('bhp_training', c)}
                />
                <CheckboxField
                  id="professional_preparation"
                  label="Professional Preparation?"
                  checked={formData.professional_preparation}
                  onChange={c => handleCheckboxChange('professional_preparation', c)}
                />
                <CheckboxField
                  id="bhp_compliance"
                  label="Compliance with HSE Rules?"
                  checked={formData.bhp_compliance}
                  onChange={c => handleCheckboxChange('bhp_compliance', c)}
                />
              </div>

              <div className="space-y-2">
                <h3 className="font-semibold text-gray-700 mb-2">Protective Equipment</h3>
                <CheckboxField
                  id="safety_equipment_used"
                  label="Was safety equipment used?"
                  checked={formData.safety_equipment_used}
                  onChange={c => handleCheckboxChange('safety_equipment_used', c)}
                />
                {formData.safety_equipment_used && (
                  <>
                    <InputField
                      id="safety_equipment_types"
                      label="Types Used"
                      value={formData.safety_equipment_types}
                      onChange={handleChange}
                    />
                    <InputField
                      id="safety_equipment_condition"
                      label="Condition of Equipment"
                      value={formData.safety_equipment_condition}
                      onChange={handleChange}
                    />
                  </>
                )}
              </div>

              <div className="md:col-span-2 pt-4 border-t border-gray-100">
                <h3 className="font-semibold text-gray-700 mb-2">Risk Management</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="flex flex-col gap-2">
                    <CheckboxField
                      id="risk_assessment"
                      label="Risk Assessment Conducted?"
                      checked={formData.risk_assessment}
                      onChange={c => handleCheckboxChange('risk_assessment', c)}
                    />
                    <CheckboxField
                      id="safety_measures"
                      label="Safety Measures in Place?"
                      checked={formData.safety_measures}
                      onChange={c => handleCheckboxChange('safety_measures', c)}
                    />
                  </div>
                  <InputField
                    id="risk_mitigation"
                    label="Mitigation Strategies"
                    value={formData.risk_mitigation}
                    onChange={handleChange}
                  />
                </div>
              </div>
            </div>
          </Section>

          {/* 5. Sobriety & Authorities */}
          <Section title="Investigation Details">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <h3 className="font-semibold text-gray-700">Sobriety</h3>
                <CheckboxField
                  id="sobriety_state"
                  label="Subject appeared sober?"
                  checked={formData.sobriety_state}
                  onChange={c => handleCheckboxChange('sobriety_state', c)}
                />
                <CheckboxField
                  id="sobriety_tested"
                  label="Was sobriety tested?"
                  checked={formData.sobriety_tested}
                  onChange={c => handleCheckboxChange('sobriety_tested', c)}
                />
                {formData.sobriety_tested && (
                  <InputField
                    id="sobriety_tested_by"
                    label="Tested By"
                    value={formData.sobriety_tested_by}
                    onChange={handleChange}
                  />
                )}
              </div>

              <div className="space-y-2">
                <h3 className="font-semibold text-gray-700">External Authorities</h3>
                <CheckboxField
                  id="investigation_authorities"
                  label="External authorities notified?"
                  checked={formData.investigation_authorities}
                  onChange={c => handleCheckboxChange('investigation_authorities', c)}
                />
                {formData.investigation_authorities && (
                  <div className="space-y-4 pt-2">
                    <InputField
                      id="authority_name"
                      label="Authority Name"
                      value={formData.authority_name}
                      onChange={handleChange}
                    />
                    <InputField
                      id="authority_address"
                      label="Address"
                      value={formData.authority_address}
                      onChange={handleChange}
                    />
                    <div className="grid grid-cols-2 gap-4">
                      <InputField
                        id="authority_case_number"
                        label="Case Number"
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
          <Section title="Medical & Consequences">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="md:col-span-2 space-y-4">
                <CheckboxField
                  id="first_aid_provided"
                  label="Was First Aid provided immediately?"
                  checked={formData.first_aid_provided}
                  onChange={c => handleCheckboxChange('first_aid_provided', c)}
                />
                {formData.first_aid_provided && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <InputField
                      id="first_aid_date"
                      label="Date/Time of First Aid"
                      type="datetime-local"
                      value={formData.first_aid_date}
                      onChange={handleChange}
                    />
                  </div>
                )}
              </div>

              <InputField
                id="medical_facility"
                label="Medical Facility"
                value={formData.medical_facility}
                onChange={handleChange}
              />
              <InputField
                id="diagnosed_injury"
                label="Diagnosed Injury"
                value={formData.diagnosed_injury}
                onChange={handleChange}
              />

              <InputField
                id="hospitalization_place"
                label="Place of Hospitalization"
                value={formData.hospitalization_place}
                onChange={handleChange}
              />
              <InputField
                id="hospitalization_period"
                label="Period (Days)"
                value={formData.hospitalization_period}
                onChange={handleChange}
              />

              <InputField
                id="work_incapacity_period"
                label="Incapacity Period"
                value={formData.work_incapacity_period}
                onChange={handleChange}
              />
              <div className="flex items-end pb-3">
                <CheckboxField
                  id="sick_leave_on_accident_day"
                  label="Sick leave issued on accident day?"
                  checked={formData.sick_leave_on_accident_day}
                  onChange={c => handleCheckboxChange('sick_leave_on_accident_day', c)}
                />
              </div>
            </div>
          </Section>

          <div className="flex justify-end gap-4 mt-8">
            <button
              type="submit"
              className="flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 shadow-lg"
            >
              <Save className="w-5 h-5 mr-2" />
              Zapisz
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
