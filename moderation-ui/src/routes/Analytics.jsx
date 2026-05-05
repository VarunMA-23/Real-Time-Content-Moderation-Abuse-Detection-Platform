import MetricCard from '../components/analytics/MetricCard'
import ModelPerformanceTable from '../components/analytics/ModelPerformanceTable'
import TimelineChart from '../components/analytics/TimelineChart'
import useAnalytics from '../hooks/useAnalytics'

function Analytics() {
  const { data, loading, error } = useAnalytics({ from: '', to: '' })

  if (loading) return <p>Loading analytics...</p>
  if (error) return <p className="status blocked">{error}</p>
  if (!data) return null

  return (
    <div className="section-gap">
      <div className="metrics-grid"><MetricCard label="Total Messages" value={data.totals.totalMessages} /><MetricCard label="Blocked %" value={`${data.totals.blockedPercent}%`} /><MetricCard label="Flagged %" value={`${data.totals.flaggedPercent}%`} /><MetricCard label="Reviewed Count" value={data.totals.reviewedCount} /></div>
      <div className="charts-grid"><TimelineChart title="Messages Over Time" data={data.timeline} dataKeys={[{ key: 'total', color: '#6366f1' }, { key: 'blocked', color: '#ef4444' }, { key: 'flagged', color: '#f59e0b' }]} /><TimelineChart title="Toxicity Trend" data={data.timeline} dataKeys={[{ key: 'avgToxicity', color: '#22c55e' }]} /></div>
      <ModelPerformanceTable rows={data.performance} />
    </div>
  )
}

export default Analytics
