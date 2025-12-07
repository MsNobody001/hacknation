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
