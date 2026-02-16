import './Slider.css';

type Props = {
  onChange: (value: number) => void;
  value: number;
};

export default function Slider({ onChange, value }: Props) {
  return (
    <input
      type="range"
      min={0.5}
      max={2}
      step={0.1}
      value={value}
      onChange={(e) => onChange(parseFloat(e.target.value))}
      style={{
        width: '100%',
        height: '6px',
        background: '#0a0a0a',
        outline: 'none',
        border: '1px solid #660000',
        borderRadius: '2px',
        appearance: 'none',
        WebkitAppearance: 'none',
      }}
      className="kitt-slider"
    />
  );
}
