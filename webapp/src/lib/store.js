import { writable, get } from "svelte/store";

// --- Constants ---
const ELO_DEFAULT = 1500;
const ELO_K = 32;
// Importance weights for computing job scores from macro ELOs
const WEIGHTS = { principal: 3, standard: 1, emergent: 0.5 };
// How much of a macro vote propagates to its children
const CHILD_PROPAGATION = 0.3;
const TOP_N = 100;
export const MIN_VOTES = 20;

// --- Loaded data (module-level, not reactive) ---
let macros = {}; // macro_code -> { libelle, enjeu }
let skillParent = {}; // child_skill_code -> macro_code
let jobs = {}; // job_code -> { libelle, principal, standard, emergent, contexts }
let ctxJobs = {}; // ctx_code -> [job_codes]
let jobContextMap = {}; // ctx_code -> { libelle, category }

// Derived at load time
let macroChildren = {}; // macro_code -> [child_skill_codes]
let jobMacroWeights = {}; // job_code -> { macro_code -> weight }
let macroJobs = {}; // macro_code -> [job_codes]

// --- Mutable state ---
let eloMap = {}; // macro_code | ctx_code -> float
let jobScoreCache = {}; // job_code -> float

// --- Svelte stores ---
export const view = writable("loading"); // 'loading' | 'comparing' | 'results'
export const voteCount = writable(0);
export const currentPair = writable(null);
export const rankedJobs = writable([]);
export const loadError = writable(null);

// --- ELO ---
function expected(ra, rb) {
  return 1 / (1 + Math.pow(10, (rb - ra) / 400));
}

function applyVote(codeA, codeB, outcome) {
  // outcome: +1 = A wins, -1 = B wins, 0 = draw
  const sa = outcome > 0 ? 1 : outcome < 0 ? 0 : 0.5;
  const ea = expected(
    eloMap[codeA] ?? ELO_DEFAULT,
    eloMap[codeB] ?? ELO_DEFAULT,
  );
  const delta = ELO_K * (sa - ea);
  eloMap[codeA] = (eloMap[codeA] ?? ELO_DEFAULT) + delta;
  eloMap[codeB] = (eloMap[codeB] ?? ELO_DEFAULT) - delta;

  // Propagate partially to children
  for (const child of macroChildren[codeA] ?? [])
    eloMap[child] = (eloMap[child] ?? ELO_DEFAULT) + delta * CHILD_PROPAGATION;
  for (const child of macroChildren[codeB] ?? [])
    eloMap[child] = (eloMap[child] ?? ELO_DEFAULT) - delta * CHILD_PROPAGATION;
}

function applyDelta(code, delta) {
  eloMap[code] = (eloMap[code] ?? ELO_DEFAULT) + delta;
  for (const child of macroChildren[code] ?? [])
    eloMap[child] = (eloMap[child] ?? ELO_DEFAULT) + delta * CHILD_PROPAGATION;
}

// --- Score ---
function computeJobScore(jobCode) {
  const job = jobs[jobCode];
  let score = 0;
  for (const [macroCode, w] of Object.entries(jobMacroWeights[jobCode] ?? {})) {
    score += (eloMap[macroCode] ?? ELO_DEFAULT) * w;
  }
  // Contexts contribute with weight 1
  for (const ctx of job.contexts ?? []) {
    score += eloMap[ctx.code] ?? ELO_DEFAULT;
  }
  return score;
}

function recomputeAffectedJobs(codes) {
  const affected = new Set();
  for (const code of codes) {
    for (const jc of macroJobs[code] ?? []) affected.add(jc);
    for (const jc of ctxJobs[code] ?? []) affected.add(jc);
  }
  for (const jc of affected) jobScoreCache[jc] = computeJobScore(jc);
}

function getTopJobCodes(n) {
  return Object.entries(jobScoreCache)
    .sort((a, b) => b[1] - a[1])
    .slice(0, n)
    .map(([code]) => code);
}

function computeRankedJobs(n = 10) {
  return getTopJobCodes(n).map((code) => ({
    code,
    libelle: jobs[code]?.libelle ?? code,
    score: Math.round(jobScoreCache[code]),
    url: `https://candidat.francetravail.fr/metierscope/#/fiche-metier/${code}`,
  }));
}

// --- Pair selection ---
function pickPair() {
  const top = getTopJobCodes(TOP_N);

  // Collect all unique macro codes across top jobs
  const allCodes = new Set();
  for (const jobCode of top) {
    for (const macroCode of Object.keys(jobMacroWeights[jobCode] ?? {}))
      allCodes.add(macroCode);
  }
  const codes = Array.from(allCodes);
  if (codes.length < 2) return null;

  for (let attempt = 0; attempt < 60; attempt++) {
    const idxA = Math.floor(Math.random() * codes.length);
    let idxB = Math.floor(Math.random() * (codes.length - 1));
    if (idxB >= idxA) idxB++;
    const codeA = codes[idxA];
    const codeB = codes[idxB];

    return {
      skillA: { code: codeA, ...macros[codeA] },
      skillB: { code: codeB, ...macros[codeB] },
    };
  }
  return null;
}

function initState() {
  eloMap = {};
  for (const code of Object.keys(macros)) eloMap[code] = ELO_DEFAULT;
  for (const code of Object.keys(jobContextMap)) eloMap[code] = ELO_DEFAULT;
  jobScoreCache = {};
  for (const code of Object.keys(jobs))
    jobScoreCache[code] = computeJobScore(code);
}

// --- Public API ---
export async function loadData() {
  try {
    const [m, sp, j] = await Promise.all([
      fetch("./data/macros.json").then((r) => r.json()),
      fetch("./data/skill_parent.json").then((r) => r.json()),
      fetch("./data/jobs.json").then((r) => r.json()),
    ]);
    macros = m;
    skillParent = sp;
    jobs = j;

    // Build macroChildren (inverse of skillParent)
    for (const [childCode, macroCode] of Object.entries(skillParent)) {
      if (!macroChildren[macroCode]) macroChildren[macroCode] = [];
      macroChildren[macroCode].push(childCode);
    }

    // Build jobMacroWeights: for each job, aggregate bucket weights per macro
    for (const [jobCode, job] of Object.entries(jobs)) {
      jobMacroWeights[jobCode] = {};
      for (const [bucket, weight] of Object.entries(WEIGHTS)) {
        for (const skillCode of job[bucket] ?? []) {
          const macroCode = skillParent[skillCode];
          if (!macroCode) continue;
          jobMacroWeights[jobCode][macroCode] =
            (jobMacroWeights[jobCode][macroCode] ?? 0) + weight;
        }
      }
    }

    // Build macroJobs reverse index
    for (const [jobCode, weights] of Object.entries(jobMacroWeights)) {
      for (const macroCode of Object.keys(weights)) {
        if (!macroJobs[macroCode]) macroJobs[macroCode] = [];
        macroJobs[macroCode].push(jobCode);
      }
    }

    // Build context reverse index and flat lookup
    for (const [jobCode, job] of Object.entries(jobs)) {
      for (const ctx of job.contexts ?? []) {
        if (!ctxJobs[ctx.code]) ctxJobs[ctx.code] = [];
        ctxJobs[ctx.code].push(jobCode);
        if (!jobContextMap[ctx.code])
          jobContextMap[ctx.code] = {
            libelle: ctx.libelle,
            category: ctx.category,
          };
      }
    }

    initState();
    currentPair.set(pickPair());
    rankedJobs.set(computeRankedJobs(10));
    view.set("comparing");
  } catch (e) {
    loadError.set(e.message);
    view.set("error");
  }
}

export function vote(value) {
  const pair = get(currentPair);
  if (!pair) return;
  applyVote(pair.skillA.code, pair.skillB.code, value);
  recomputeAffectedJobs([pair.skillA.code, pair.skillB.code]);
  voteCount.update((n) => n + 1);
  rankedJobs.set(computeRankedJobs(10));
  currentPair.set(pickPair());
}

export function voteBoth() {
  const pair = get(currentPair);
  if (!pair) return;
  applyDelta(pair.skillA.code, ELO_K * 0.5);
  applyDelta(pair.skillB.code, ELO_K * 0.5);
  recomputeAffectedJobs([pair.skillA.code, pair.skillB.code]);
  voteCount.update((n) => n + 1);
  rankedJobs.set(computeRankedJobs(10));
  currentPair.set(pickPair());
}

export function voteNeither() {
  const pair = get(currentPair);
  if (!pair) return;
  applyDelta(pair.skillA.code, -ELO_K * 0.5);
  applyDelta(pair.skillB.code, -ELO_K * 0.5);
  recomputeAffectedJobs([pair.skillA.code, pair.skillB.code]);
  voteCount.update((n) => n + 1);
  rankedJobs.set(computeRankedJobs(10));
  currentPair.set(pickPair());
}

export function skip() {
  currentPair.set(pickPair());
}

export function showResults() {
  view.set("results");
}

export function restart() {
  eloMap = {};
  macroChildren = {};
  jobMacroWeights = {};
  macroJobs = {};
  ctxJobs = {};
  jobContextMap = {};
  loadData();
  view.set("comparing");
  voteCount.set(0);
}
