export interface CheckboxProps {
    id: string;
    label: string;
    checked: boolean;
    onChange: (checked: boolean) => void;
}

export const CheckboxField: React.FC<CheckboxProps> = ({ id, label, checked, onChange }) => (
    <div className="flex items-center space-x-2">
        <input
            id={id}
            type="checkbox"
            checked={checked}
            onChange={(e) => onChange(e.target.checked)}
            className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
        />
        <label htmlFor={id} className="text-sm font-medium select-none">
            {label}
        </label>
    </div>
);