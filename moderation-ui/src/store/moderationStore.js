import { create } from 'zustand'

const DEFAULT_POLICIES = {
  toxicityThreshold: 0.7,
  spamThreshold: 0.6,
  selfHarmThreshold: 0.5,
  hateSpeechThreshold: 0.7,
  autoBlock: false,
  llmReview: true,
}

const useModerationStore = create((set, get) => ({
  user: null,
  setUser: (user) => set({ user }),
  messages: [],
  addMessage: (msg) => set((state) => ({ messages: [msg, ...state.messages] })),
  updateMessage: (id, patch) => set((state) => ({ messages: state.messages.map((m) => (m.id === id ? { ...m, ...patch } : m)) })),
  queue: [],
  setQueue: (queue) => set({ queue }),
  selectedMessageId: null,
  setSelectedMessageId: (id) => set({ selectedMessageId: id }),
  resolveMessage: (id, decision) => set((state) => ({
    queue: state.queue.filter((m) => m.id !== id),
    messages: state.messages.map((m) => (m.id === id ? { ...m, status: decision } : m)),
    selectedMessageId: state.selectedMessageId === id ? state.queue.find((m) => m.id !== id)?.id ?? null : state.selectedMessageId,
  })),
  policies: DEFAULT_POLICIES,
  policiesLoaded: false,
  setPolicies: (patch) => set((state) => ({ 
    policies: { ...state.policies, ...patch },
    policiesLoaded: true 
  })),
  getSelectedMessage: () => {
    const state = get()
    return state.queue.find((m) => m.id === state.selectedMessageId) ?? null
  },
}))

export default useModerationStore
