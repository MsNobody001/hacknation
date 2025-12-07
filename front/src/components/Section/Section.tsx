import { ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";

export interface SectionProps {
    title: string;
    children: React.ReactNode;
    defaultOpen?: boolean;
}

export const Section: React.FC<SectionProps> = ({ title, children, defaultOpen = false }) => {
    const [isOpen, setIsOpen] = useState(defaultOpen);

    return (
        <div className="bg-white shadow-xl rounded-xl overflow-hidden mb-6 border border-gray-200">
            <button
                type="button"
                className="flex justify-between items-center w-full p-5 text-lg font-semibold  bg-gray-50 hover:bg-gray-100 transition duration-150 ease-in-out focus:outline-none"
                onClick={() => setIsOpen(!isOpen)}
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
