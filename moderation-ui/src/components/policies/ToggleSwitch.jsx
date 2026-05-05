function ToggleSwitch({ label, description, checked, onChange }) {
  return <label className="toggle-field"><div><strong>{label}</strong><p>{description}</p></div><input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} /></label>
}

export default ToggleSwitch
