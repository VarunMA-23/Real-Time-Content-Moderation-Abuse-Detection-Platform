export function getRisk(decision) {
  return {
    allowed: { label: 'Allowed', color: 'var(--color-allowed)' },
    flagged: { label: 'Flagged', color: 'var(--color-flagged)' },
    blocked: { label: 'Blocked', color: 'var(--color-blocked)' },
  }[decision] || { label: 'Unknown', color: 'var(--color-text-muted)' }
}

export function riskColor(score) {
  if (score >= 0.7) return 'var(--color-blocked)'
  if (score >= 0.4) return 'var(--color-flagged)'
  return 'var(--color-allowed)'
}
