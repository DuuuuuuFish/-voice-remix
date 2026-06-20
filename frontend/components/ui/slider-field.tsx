interface SliderFieldProps {
  label: string;
  min: number;
  max: number;
  step?: number;
  value: number;
  displayValue?: string;
  onChange: (value: number) => void;
}

export function SliderField({
  label,
  min,
  max,
  step = 1,
  value,
  displayValue,
  onChange,
}: SliderFieldProps) {
  return (
    <label className="block space-y-2">
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium text-slate-700">{label}</span>
        <span className="text-slate-500">{displayValue ?? value}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
        className="h-2 w-full cursor-pointer appearance-none rounded-full bg-slate-200 accent-indigo-600"
      />
    </label>
  );
}
