export interface InputProps {
    id: string;
    label: string;
    value: string | number | undefined;
    onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => void;
    type?: string;
    placeholder?: string;
    className?: string;
    required?: boolean;
    rows?: number;
}

export const InputField: React.FC<InputProps> = ({ id, label, value, onChange, type = 'text', placeholder, className = '', required = false, rows = 1 }) => (
    <div className={`flex flex-col space-y-1 ${className}`}>
        <label htmlFor={id} className="text-sm font-medium ">
            {label} {required && <span className="text-red-500">*</span>}
        </label>
        {rows > 1 ? (
            <textarea
                id={id}
                rows={rows}
                value={value as string}
                onChange={onChange}
                placeholder={placeholder}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 transition duration-150 ease-in-out"
            />
        ) : (
            <input
                id={id}
                type={type}
                value={value as string}
                onChange={onChange}
                placeholder={placeholder}
                required={required}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 transition duration-150 ease-in-out"
            />
        )}
    </div>
);
