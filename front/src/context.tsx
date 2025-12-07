import { createContext, useContext, useState } from "react";
import { CollectedData } from "@/types";

export interface ContextType {
    collectedData: CollectedData;
    setCollectedData: (data: CollectedData) => void;
}

const Context = createContext<ContextType | undefined>(undefined);

export const ContextProvider = ({ children }: { children: React.ReactNode }) => {
    const [collectedData, setCollectedData] = useState<CollectedData>({
        accident_date: null,
        accident_time: null,
        location: null,
        work_start_time: null,
        work_end_time: null,
        injury_type: null,
        circumstances: null,
        cause: null,
        place_description: null,
        medical_help: null,
        investigation: null,
        machines_involved: null,
        machine_condition: null,
        proper_use: null,
        machine_description: null,
        machine_certification: null,
        machine_registry: null,
        witnesses: null,
        activity_before_accident: null,
        event_sequence: null,
        direct_cause: null,
        indirect_causes: null
    });

    return (
        <Context.Provider value= {{ collectedData, setCollectedData }
}>
    { children }
    </Context.Provider>
  );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useCtx = () => {
    const ctx = useContext(Context);
    if (!ctx) throw new Error("useChatContext must be used inside ChatProvider");
    return ctx;
};