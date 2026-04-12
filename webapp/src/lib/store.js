import { writable, get } from 'svelte/store'

// --- Constants ---
const ELO_DEFAULT = 1500
const ELO_K = 32
const WEIGHTS = { principal: 3, standard: 1, emergent: 0.5 }
const VOTING_TYPES = new Set([
  'COMPETENCE-DETAILLEE',
  'MACRO-SAVOIR-FAIRE',
  'MACRO-SAVOIR-ETRE-PROFESSIONNEL',
])
const TOP_N = 30
export const MIN_VOTES = 8

// --- Loaded data (module-level, not reactive) ---
let skills = {}     // code -> { libelle, type, freq }
let jobs = {}       // code -> { libelle, principal, standard, emergent }
let skillJobs = {}  // code -> [job_codes]
let jobSkillSets = {} // code -> Set<skill_code>

// --- Mutable state ---
let eloMap = {}         // skill_code -> float
let jobScoreCache = {}  // job_code -> float

// --- Svelte stores ---
export const view = writable('loading') // 'loading' | 'comparing' | 'results'
export const voteCount = writable(0)
export const currentPair = writable(null)
export const rankedJobs = writable([])
export const loadError = writable(null)

// --- ELO ---
function expected(ra, rb) {
  return 1 / (1 + Math.pow(10, (rb - ra) / 400))
}

function applyVote(codeA, codeB, value) {
  // value: -2..+2  positive = A preferred, 0 = draw
  // K-factor scaled by vote magnitude
  if (value === 0) {
    const ea = expected(eloMap[codeA], eloMap[codeB])
    eloMap[codeA] += ELO_K * (0.5 - ea)
    eloMap[codeB] += ELO_K * (0.5 - (1 - ea))
  } else {
    const [winner, loser, k] = value > 0
      ? [codeA, codeB, ELO_K * value]
      : [codeB, codeA, ELO_K * -value]
    const ea = expected(eloMap[winner], eloMap[loser])
    eloMap[winner] += k * (1 - ea)
    eloMap[loser]  += k * (0 - (1 - ea))
  }
}

// --- Score ---
function computeJobScore(jobCode) {
  const job = jobs[jobCode]
  let score = 0
  for (const [bucket, weight] of Object.entries(WEIGHTS)) {
    for (const skillCode of job[bucket] ?? []) {
      score += (eloMap[skillCode] ?? ELO_DEFAULT) * weight
    }
  }
  return score
}

function recomputeAffectedJobs(skillCodes) {
  const affected = new Set()
  for (const sc of skillCodes)
    for (const jc of skillJobs[sc] ?? [])
      affected.add(jc)
  for (const jc of affected)
    jobScoreCache[jc] = computeJobScore(jc)
}

function getTopJobCodes(n) {
  return Object.entries(jobScoreCache)
    .sort((a, b) => b[1] - a[1])
    .slice(0, n)
    .map(([code]) => code)
}

function computeRankedJobs(n = 10) {
  return getTopJobCodes(n).map(code => ({
    code,
    libelle: jobs[code]?.libelle ?? code,
    score: Math.round(jobScoreCache[code]),
    url: `https://candidat.francetravail.fr/metierscope/#/fiche-metier/${code}`,
  }))
}

// --- Pair selection (active learning) ---
function pickPair() {
  const top = getTopJobCodes(TOP_N)

  for (let attempt = 0; attempt < 60; attempt++) {
    const jobA = top[Math.floor(Math.random() * top.length)]
    const jobB = top[Math.floor(Math.random() * top.length)]
    if (jobA === jobB) continue

    const setA = jobSkillSets[jobA]
    const setB = jobSkillSets[jobB]

    // Skills exclusive to each job and of voteable type
    const candidatesA = [...setA].filter(s => !setB.has(s) && VOTING_TYPES.has(skills[s]?.type))
    const candidatesB = [...setB].filter(s => !setA.has(s) && VOTING_TYPES.has(skills[s]?.type))

    if (!candidatesA.length || !candidatesB.length) continue

    const codeA = candidatesA[Math.floor(Math.random() * candidatesA.length)]
    const codeB = candidatesB[Math.floor(Math.random() * candidatesB.length)]

    return { skillA: { code: codeA, ...skills[codeA] }, skillB: { code: codeB, ...skills[codeB] } }
  }
  return null
}

function initState() {
  for (const code of Object.keys(skills)) eloMap[code] = ELO_DEFAULT
  for (const code of Object.keys(jobs)) jobScoreCache[code] = computeJobScore(code)
}

// --- Public API ---
export async function loadData() {
  try {
    const [s, j, sj] = await Promise.all([
      fetch('./data/skills.json').then(r => r.json()),
      fetch('./data/jobs.json').then(r => r.json()),
      fetch('./data/skill_jobs.json').then(r => r.json()),
    ])
    skills = s
    jobs = j
    skillJobs = sj

    for (const [code, job] of Object.entries(jobs)) {
      jobSkillSets[code] = new Set([
        ...(job.principal ?? []),
        ...(job.standard ?? []),
        ...(job.emergent ?? []),
      ])
    }

    initState()
    currentPair.set(pickPair())
    rankedJobs.set(computeRankedJobs(10))
    view.set('comparing')
  } catch (e) {
    loadError.set(e.message)
    view.set('error')
  }
}

export function vote(value) {
  const pair = get(currentPair)
  if (!pair) return

  applyVote(pair.skillA.code, pair.skillB.code, value)
  recomputeAffectedJobs([pair.skillA.code, pair.skillB.code])
  voteCount.update(n => n + 1)
  rankedJobs.set(computeRankedJobs(10))
  currentPair.set(pickPair())
}

// Both skills liked equally — both go up
export function voteBoth() {
  const pair = get(currentPair)
  if (!pair) return
  const k = ELO_K * 0.5
  eloMap[pair.skillA.code] += k
  eloMap[pair.skillB.code] += k
  recomputeAffectedJobs([pair.skillA.code, pair.skillB.code])
  voteCount.update(n => n + 1)
  rankedJobs.set(computeRankedJobs(10))
  currentPair.set(pickPair())
}

// Neither skill liked — both go down
export function voteNeither() {
  const pair = get(currentPair)
  if (!pair) return
  const k = ELO_K * 0.5
  eloMap[pair.skillA.code] -= k
  eloMap[pair.skillB.code] -= k
  recomputeAffectedJobs([pair.skillA.code, pair.skillB.code])
  voteCount.update(n => n + 1)
  rankedJobs.set(computeRankedJobs(10))
  currentPair.set(pickPair())
}

export function skip() {
  currentPair.set(pickPair())
}

export function showResults() {
  view.set('results')
}

export function restart() {
  initState()
  voteCount.set(0)
  rankedJobs.set(computeRankedJobs(10))
  currentPair.set(pickPair())
  view.set('comparing')
}
