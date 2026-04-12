import { writable, derived, get } from 'svelte/store'
import { skills, jobs, generatePairs } from './mockData.js'

export const view = writable('comparing') // 'comparing' | 'results'

const initialScores = Object.fromEntries(skills.map(s => [s.id, 0]))
export const scores = writable({ ...initialScores })
export const voteCount = writable(0)

const TOTAL_PAIRS = 15
let pairs = generatePairs(TOTAL_PAIRS)
let pairIndex = 0

export const currentPair = writable(pairs[0])
export const totalPairs = TOTAL_PAIRS

export function vote(value) {
  const [idA, idB] = get(currentPair)
  scores.update(s => ({ ...s, [idA]: s[idA] + value, [idB]: s[idB] - value }))
  voteCount.update(n => n + 1)
  advance()
}

export function skip() {
  advance()
}

function advance() {
  pairIndex++
  if (pairIndex >= pairs.length) {
    view.set('results')
  } else {
    currentPair.set(pairs[pairIndex])
  }
}

export function showResults() {
  view.set('results')
}

export function restart() {
  pairs = generatePairs(TOTAL_PAIRS)
  pairIndex = 0
  scores.set({ ...initialScores })
  voteCount.set(0)
  currentPair.set(pairs[0])
  view.set('comparing')
}

export const rankedJobs = derived(scores, $scores =>
  jobs
    .map(job => ({
      ...job,
      score: job.skills.reduce((sum, sid) => sum + ($scores[sid] ?? 0), 0),
    }))
    .sort((a, b) => b.score - a.score)
)
