export type Address = string;

export interface Person {
    pesel: string;
    idType: string;
    idNumber: string;
    birthDate: string;
    birthPlace: string;
    phoneNumber: string;
    address: Address;
    email: string;
}

export interface AccidentDetails {
    date: string;
    time: string;
    location: Address;
    plannedWorkStart: string;
    plannedWorkEnd: string;
}

export interface MachineInfo {
    name: string;
    type: string;
    productionDate: string;
}

export interface CausedByMachine {
    machineInfo: MachineInfo;
    wasFunctional?: boolean;
    usedAccordingToManual?: boolean;
    descriptionOfUse?: string;
}

export interface MachineryToolsInfo {
    involved: boolean;
    machineOrToolName?: string;
    machineType?: string;
    productionDate?: string;
    wasFunctional?: boolean;
    usedAccordingToManual?: boolean;
    descriptionOfUse?: string;
}

export interface BHPCompliance {
    completedTraining: boolean;
    hasRiskAssessment: boolean;
    riskReductionMeasures?: string;
}

export interface Intoxication {
    intoxicated: boolean;
    testedBy?: 'police' | 'medicalHelp' | 'notTested';
}

export interface StateAuthorityAction {
    name: string;
    address?: string;
    caseNumber?: string;
    status?: "finished" | "pending" | "rejected";
}

export interface HospitalizationPeriod {
    from: string;
    to: string;
    address: Address;
}

export interface IncapacityPeriod {
    from: string;
    to: string;
}

export interface MedicalHelpDetails {
    dateOfFirstAid?: string;
    healthcareFacilityName?: string;
    hospitalizationPeriod?: HospitalizationPeriod;
    diagnosedInjury?: string;
    incapacityPeriod?: IncapacityPeriod;
    sickLeaveOnAccidentDay: boolean;
}

export interface UsedSafetySupport {
    requiredMoreThanOnePerson: boolean;
}

export interface AccidentExplanationRecord {
    personalData: Person;
    accidentDetails: AccidentDetails;
    workActivityBeforeAccident: string;
    accidentCircumstances: string;
    accidentCause: string;
    causedByMachineOrTool: false | CausedByMachine;
    machineryToolsInfo: MachineryToolsInfo;
    usedProtectiveEquipment?: boolean | string[];
    usedSafetySupport?: boolean | UsedSafetySupport;
    bhpCompliance: boolean;
    hasProperPreparation: boolean;
    bhpTraining: BHPCompliance;
    intoxication: Intoxication;
    stateAuthorityActions: false | StateAuthorityAction[];
    medicalHelp: false | MedicalHelpDetails;
}

export interface Message {
    id: string;
    text: string;
    sender: 'user' | 'agent' | 'system';
}

export interface CollectedData {
        accident_date: string | null,
        accident_time: string | null,
        location: string | null,
        work_start_time: string | null,
        work_end_time: string | null,
        injury_type: string | null,
        circumstances: string | null,
        cause: string | null,
        place_description: string | null,
        medical_help: string | null,
        investigation: string | null,
        machines_involved: string | null,
        machine_condition: string | null,
        proper_use: string | null,
        machine_description: string | null,
        machine_certification: string | null,
        machine_registry: string | null,
        witnesses: string | null,
        activity_before_accident: string | null,
        event_sequence: string | null,
        direct_cause: string | null,
        indirect_causes: string | null
}

export interface SendChatMsgResponse {
    response: string;
    session_id: string;
    collected_data: CollectedData,
}

export type FileStatus = 'pending' | 'uploading' | 'complete' | 'error';

export interface UploadFile {
  id: string;
  name: string;
  size: number;
  status: FileStatus;
  progress: number; // 0 to 100
  file: File; // Reference to the actual File object
}