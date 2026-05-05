function ThresholdSlider({ label, value, onChange, min = 0, max = 1, step = 0.01 }) {
  return <label className="slider-field"><span>{label}: {value.toFixed(2)}</span><input type="range" min={min} max={max} step={step} value={value} onChange={(e) => onChange(Number(e.target.value))} /></label>
}

export default ThresholdSlider
