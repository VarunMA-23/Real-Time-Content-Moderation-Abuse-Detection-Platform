import { http, HttpResponse } from 'msw'
import { MOCK_ANALYTICS, MOCK_QUEUE } from './messages'

export const handlers = [
  http.post('*/auth/login', async ({ request }) => {
    const { email } = await request.json()
    return HttpResponse.json({ id: 'mod_1', name: 'Moderator', email })
  }),
  http.post('*/moderate', async ({ request }) => {
    const { text } = await request.json()
    const lower = text.toLowerCase()
    const toxicity = lower.includes('idiot') || lower.includes('hate') ? 0.91 : 0.12
    const spam = lower.includes('buy') ? 0.82 : 0.06
    const decision = toxicity > 0.8 ? 'blocked' : spam > 0.7 ? 'flagged' : 'allowed'
    return HttpResponse.json({ messageId: crypto.randomUUID(), decision, scores: { toxicity, spam, selfHarm: 0.03 } })
  }),
  http.get('*/jobs/:jobId', () => HttpResponse.json({ status: 'completed', llmExplanation: 'Automated reasoning available for this message.', policyViolation: 'Potential harassment' })),
  http.get('*/review', () => HttpResponse.json({ queue: MOCK_QUEUE })),
  http.post('*/decision', () => HttpResponse.json({ success: true })),
  http.get('*/analytics', () => HttpResponse.json(MOCK_ANALYTICS)),
  http.get('*/policies', () => HttpResponse.json({ toxicityThreshold: 0.8, spamThreshold: 0.7, selfHarmThreshold: 0.5, hateSpeechThreshold: 0.75, autoBlock: true, llmReview: true })),
  http.put('*/policies', async ({ request }) => HttpResponse.json(await request.json())),
]
