export const MOCK_QUEUE = [
  {
    id: 'msg_101',
    text: 'You idiot, I will find you!',
    userId: 'u_42',
    timestamp: '2024-01-15T12:04:00Z',
    decision: 'blocked',
    scores: { toxicity: 0.91, spam: 0.05, selfHarm: 0.01 },
    llmExplanation: 'This message contains direct threats and harassment.',
    policyViolation: 'Hate Speech',
    history: [{ action: 'flagged', actor: 'system', time: '12:04' }],
  },
  {
    id: 'msg_102',
    text: 'Buy this now at huge discount!!!',
    userId: 'u_17',
    timestamp: '2024-01-15T11:58:00Z',
    decision: 'flagged',
    scores: { toxicity: 0.2, spam: 0.82, selfHarm: 0.01 },
    llmExplanation: 'Likely spam content due to promotional urgency patterns.',
    policyViolation: 'Spam',
    history: [{ action: 'flagged', actor: 'system', time: '11:58' }],
  },
]

export const MOCK_ANALYTICS = {
  totals: { totalMessages: 2380, blockedPercent: 12.4, flaggedPercent: 18.1, reviewedCount: 641 },
  timeline: [
    { date: 'Mon', total: 220, blocked: 24, flagged: 40, avgToxicity: 0.35, spamVolume: 61 },
    { date: 'Tue', total: 265, blocked: 32, flagged: 48, avgToxicity: 0.39, spamVolume: 66 },
    { date: 'Wed', total: 241, blocked: 28, flagged: 44, avgToxicity: 0.34, spamVolume: 59 },
    { date: 'Thu', total: 280, blocked: 38, flagged: 57, avgToxicity: 0.42, spamVolume: 73 },
    { date: 'Fri', total: 300, blocked: 41, flagged: 60, avgToxicity: 0.45, spamVolume: 80 },
  ],
  performance: [
    { metric: 'True Positives', value: '412' },
    { metric: 'False Positives', value: '23' },
    { metric: 'True Negatives', value: '1840' },
    { metric: 'False Negatives', value: '8' },
    { metric: 'Precision', value: '94.7%' },
    { metric: 'Recall', value: '98.1%' },
  ],
}
