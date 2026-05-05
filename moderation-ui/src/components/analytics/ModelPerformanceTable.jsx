function ModelPerformanceTable({ rows }) {
  return (
    <div className="panel"><h4>Model Performance</h4><table className="data-table"><thead><tr><th>Metric</th><th>Value</th></tr></thead><tbody>{rows.map((row) => <tr key={row.metric}><td>{row.metric}</td><td>{row.value}</td></tr>)}</tbody></table></div>
  )
}

export default ModelPerformanceTable
