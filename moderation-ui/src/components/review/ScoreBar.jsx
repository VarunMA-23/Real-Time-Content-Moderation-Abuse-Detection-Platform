import { riskColor } from '../../utils/riskLevel'

function ScoreBar({ label, value }) {
  return (
    <div className="score-row"><span>{label}</span><div className="score-track"><div className="score-fill" style={{ width: `${value * 100}%`, backgroundColor: riskColor(value) }} /></div><span>{value.toFixed(2)}</span></div>
  )
}

export default ScoreBar
