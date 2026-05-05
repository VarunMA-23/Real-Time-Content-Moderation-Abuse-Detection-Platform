function RiskChip({ level }) {
  const icon = level === 'high' ? '??' : level === 'medium' ? '??' : '??'
  return <span className="risk-chip">{icon} {level}</span>
}

export default RiskChip
