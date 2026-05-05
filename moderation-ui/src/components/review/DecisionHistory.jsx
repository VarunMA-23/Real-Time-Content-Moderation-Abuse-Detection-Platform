function DecisionHistory({ history }) {
  return (
    <div>
      <h4>Decision History</h4>
      <ul className="history-list">{history?.map((item, index) => <li key={`${item.action}-${index}`}>{item.action} by {item.actor} at {item.time}</li>)}</ul>
    </div>
  )
}

export default DecisionHistory
