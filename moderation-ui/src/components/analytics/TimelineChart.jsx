import { ResponsiveContainer, Line, LineChart, Tooltip, XAxis, YAxis } from 'recharts'

function TimelineChart({ data, dataKeys, title }) {
  return (
    <div className="panel chart-panel">
      <h4>{title}</h4>
      <ResponsiveContainer width="100%" height={260}><LineChart data={data}><XAxis dataKey="date" stroke="#6b7280" /><YAxis stroke="#6b7280" /><Tooltip />{dataKeys.map((key) => <Line key={key.key} type="monotone" dataKey={key.key} stroke={key.color} strokeWidth={2} dot={false} />)}</LineChart></ResponsiveContainer>
    </div>
  )
}

export default TimelineChart
