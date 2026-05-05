function StatusBadge({ decision }) {
  return <span className={`badge badge-${decision}`}>{decision}</span>
}

export default StatusBadge
