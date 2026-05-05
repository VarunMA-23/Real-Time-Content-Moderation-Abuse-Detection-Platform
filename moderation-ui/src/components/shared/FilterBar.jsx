function FilterBar({ filters, onChange }) {
  return (
    <div className="filter-bar">
      <select value={filters.risk} onChange={(e) => onChange({ ...filters, risk: e.target.value })}>
        <option value="all">All Risks</option><option value="high">High</option><option value="medium">Medium</option>
      </select>
      <select value={filters.dateRange} onChange={(e) => onChange({ ...filters, dateRange: e.target.value })}>
        <option value="today">Today</option><option value="last7">Last 7 days</option><option value="all">All time</option>
      </select>
      <select value={filters.category} onChange={(e) => onChange({ ...filters, category: e.target.value })}>
        <option value="all">All categories</option><option value="toxicity">Toxicity</option><option value="spam">Spam</option><option value="selfHarm">Self-harm</option><option value="hateSpeech">Hate speech</option>
      </select>
    </div>
  )
}

export default FilterBar
