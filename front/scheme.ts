type Address = string;

type Person = {
    pesel: string;
    idType: string,
    idNumber: string,
    birthDate: string,
    birthPlace: string,
    phoneNumber: string,
    address: Address,
    email: string,
}

type AccidentExplanationRecord = {
    personalData: Person;

    accidentDetails: {
        date: string;
        time: string;
        location: Address;
        plannedWorkStart: string;
        plannedWorkEnd: string;
    };

    workActivityBeforeAccident: string,

    accidentCircumstances: string;
    accidentCause: string;

    causedByMachineOrTool: false | {
        machineInfo: {
            name: string;
            type: string;
            productionDate: string;
        },
        wasFunctional?: boolean;
        usedAccordingToManual?: boolean;
        descriptionOfUse?: string;
    };

    machineryToolsInfo: {
        involved: boolean;
        machineOrToolName?: string;
        machineType?: string;
        productionDate?: string;
        wasFunctional?: boolean;
        usedAccordingToManual?: boolean;
        descriptionOfUse?: string;
    };

    usedProtectiveEquipment?: boolean | string[];
    usedSafetySupport?: boolean | {
        requiredMoreThanOnePerson: boolean;
    }

    bhpCompliance: boolean;
    hasProperPreparation: boolean;

    bhpTraining: {
        completedTraining: boolean;
        hasRiskAssessment: boolean;
        riskReductionMeasures?: string;
    };

    intoxication: {
        intoxicated: boolean;
        testedBy?: 'police' | 'medicalHelp' | 'none';
    };

    stateAuthorityActions: false | {
        name: string;
        address?: string;
        caseNumber?: string;
        status?: "finished" | "pending" | "rejected";
    }[];

    medicalHelp: false | {
        dateOfFirstAid?: string;
        healthcareFacilityName?: string;
        hospitalizationPeriod?: {
            from: string;
            to: string;
            address: Address;
        };
        diagnosedInjury?: string;
        incapacityPeriod?: {
            from: string;
            to: string;
        };
        sickLeaveOnAccidentDay: boolean;
    };

};
