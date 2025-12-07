import { InputProps } from "../InputField/InputField";

export interface SelectProps extends InputProps {
    options: string[];
}

export const SelectField: React.FC<SelectProps> = ({ id, label, value, onChange, options, className = '', required = false }) => (
    <div className={`flex flex-col space-y-1 ${className}`}>
        <label htmlFor={id} className="text-sm font-medium text-gray-700">
            {label} {required && <span className="text-red-500">*</span>}
        </label>
        <select
            id={id}
            value={value as string}
            onChange={onChange}
            required={required}
            className="w-full px-3 py-2 border border-gray-300 bg-white rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 transition duration-150 ease-in-out"
        >
            {options.map(option => (
                <option key={option} value={option}>{option}</option>
            ))}
        </select>
    </div>
);
