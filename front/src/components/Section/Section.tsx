import { ChevronDown, ChevronUp } from "lucide-react";
import { useEffect, useState } from "react";

export interface SectionProps {
    title: string;
    children: React.ReactNode;
    defaultOpen?: boolean;
    isOpen?: boolean;
    onToggle?: (isOpen: boolean) => void;
}

export const Section: React.FC<SectionProps> = ({ title, children, defaultOpen = false, isOpen: controlledIsOpen, onToggle }) => {
    const [internalIsOpen, setInternalIsOpen] = useState(defaultOpen);
    
    const isOpen = controlledIsOpen !== undefined ? controlledIsOpen : internalIsOpen;
    
    useEffect(() => {
        if (controlledIsOpen !== undefined) {
            setInternalIsOpen(controlledIsOpen);
        }
    }, [controlledIsOpen]);

    const handleToggle = () => {
        const newState = !isOpen;
        if (onToggle) {
            onToggle(newState);
        } else {
            setInternalIsOpen(newState);
        }
    };

    return (
        <div className="bg-white shadow-xl rounded-xl overflow-hidden mb-6 border border-gray-200">
            <button
                type="button"
                className="flex justify-between items-center w-full p-5 text-lg font-semibold  bg-gray-50 hover:bg-gray-100 transition duration-150 ease-in-out focus:outline-none"
                onClick={handleToggle}
            >
                {title}
                {isOpen ? <ChevronUp className="w-5 h-5 text-blue-600" /> : <ChevronDown className="w-5 h-5" />}
            </button>
            <div className={`transition-all duration-300 ease-in-out ${isOpen ? 'max-h-[5000px] opacity-100' : 'max-h-0 opacity-0'} overflow-hidden`}>
                <div className="p-6">
                    {children}
                </div>
            </div>
        </div>
    );
};
