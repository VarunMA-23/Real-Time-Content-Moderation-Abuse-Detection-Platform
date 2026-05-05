import { useMemo } from 'react'
import ThresholdSlider from '../components/policies/ThresholdSlider'
import ToggleSwitch from '../components/policies/ToggleSwitch'
import usePolicies from '../hooks/usePolicies'

function Policies() {
  const { policies, setPolicies, savePolicies, loading, saving, saved, error } = usePolicies()
  const hasData = useMemo(() => !!policies && typeof policies.toxicityThreshold === 'number', [policies])

  if (loading || !hasData) return <p>Loading policies...</p>

  return (
    <section className="panel section-gap">
      <h3>Policies Configuration</h3>
      <ThresholdSlider label="Toxicity Threshold" value={policies.toxicityThreshold} onChange={(v) => setPolicies({ toxicityThreshold: v })} />
      <ThresholdSlider label="Spam Threshold" value={policies.spamThreshold} onChange={(v) => setPolicies({ spamThreshold: v })} />
      <ThresholdSlider label="Self-harm Threshold" value={policies.selfHarmThreshold} onChange={(v) => setPolicies({ selfHarmThreshold: v })} />
      <ThresholdSlider label="Hate Speech Threshold" value={policies.hateSpeechThreshold} onChange={(v) => setPolicies({ hateSpeechThreshold: v })} />
      <ToggleSwitch label="Auto-block" description="Automatically block high-risk messages without human review." checked={policies.autoBlock} onChange={(checked) => setPolicies({ autoBlock: checked })} />
      <ToggleSwitch label="LLM Review" description="Send flagged messages for additional language-model reasoning." checked={policies.llmReview} onChange={(checked) => setPolicies({ llmReview: checked })} />
      <button type="button" onClick={savePolicies} disabled={saving}>{saving ? 'Saving...' : 'Save Policies'}</button>
      {saved ? <p className="status allowed">? Policies saved</p> : null}
      {error ? <p className="status blocked">{error}</p> : null}
    </section>
  )
}

export default Policies
