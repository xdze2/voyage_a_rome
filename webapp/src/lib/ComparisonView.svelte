<script>
  import { currentPair, voteCount, totalPairs, vote, skip, showResults } from './store.js'
  import { skills } from './mockData.js'

  const byId = Object.fromEntries(skills.map(s => [s.id, s]))

  $: [idA, idB] = $currentPair
  $: skillA = byId[idA]
  $: skillB = byId[idB]

  const options = [
    { value: -2, label: '−2', hint: 'nettement B' },
    { value: -1, label: '−1', hint: 'plutôt B' },
    { value:  0, label:  '0', hint: 'égalité' },
    { value: +1, label: '+1', hint: 'plutôt A' },
    { value: +2, label: '+2', hint: 'nettement A' },
  ]

  let selected = null

  function handleVote(value) {
    selected = value
    setTimeout(() => { selected = null; vote(value) }, 150)
  }

  $: progress = Math.round(($voteCount / totalPairs) * 100)
  $: canShowResults = $voteCount >= 8
</script>

<div class="wrapper">
  <div class="meta">
    <span class="counter">comparaison {$voteCount + 1} / {totalPairs}</span>
    <div class="progress-bar"><div class="fill" style="width: {progress}%"></div></div>
  </div>

  <p class="question">Laquelle de ces activités vous attire le plus ?</p>

  <div class="arena">
    <div class="card" class:highlight={selected > 0}>
      <span class="tag">A</span>
      <p>{skillA?.label}</p>
    </div>

    <span class="vs">vs</span>

    <div class="card" class:highlight={selected < 0}>
      <span class="tag">B</span>
      <p>{skillB?.label}</p>
    </div>
  </div>

  <div class="vote-row">
    <span class="hint-left">← B</span>
    <div class="buttons">
      {#each options as opt}
        <button
          class="vote-btn"
          class:active={selected === opt.value}
          class:negative={opt.value < 0}
          class:neutral={opt.value === 0}
          class:positive={opt.value > 0}
          on:click={() => handleVote(opt.value)}
          title={opt.hint}
        >
          {opt.label}
        </button>
      {/each}
    </div>
    <span class="hint-right">A →</span>
  </div>

  <div class="actions">
    <button class="link-btn" on:click={skip}>passer</button>
    {#if canShowResults}
      <button class="results-btn" on:click={showResults}>voir les résultats →</button>
    {/if}
  </div>
</div>

<style>
  .wrapper {
    width: 100%;
    max-width: 680px;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .meta {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .counter {
    font-size: 0.8rem;
    color: var(--text-muted);
    white-space: nowrap;
  }

  .progress-bar {
    flex: 1;
    height: 4px;
    background: var(--border);
    border-radius: 2px;
    overflow: hidden;
  }

  .fill {
    height: 100%;
    background: var(--accent);
    border-radius: 2px;
    transition: width 0.3s ease;
  }

  .question {
    font-size: 0.9rem;
    color: var(--text-muted);
  }

  .arena {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: 1rem;
    align-items: center;
  }

  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem;
    min-height: 110px;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    box-shadow: var(--shadow);
    transition: border-color 0.15s, background 0.15s;
  }

  .card.highlight {
    border-color: var(--accent);
    background: var(--accent-light);
  }

  .tag {
    font-size: 0.7rem;
    font-weight: 700;
    color: var(--text-muted);
    letter-spacing: 0.05em;
  }

  .card p {
    font-size: 0.95rem;
    line-height: 1.4;
  }

  .vs {
    font-size: 0.8rem;
    color: var(--text-muted);
    font-style: italic;
  }

  .vote-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .hint-left, .hint-right {
    font-size: 0.75rem;
    color: var(--text-muted);
    white-space: nowrap;
  }

  .buttons {
    flex: 1;
    display: flex;
    gap: 0.4rem;
    justify-content: center;
  }

  .vote-btn {
    flex: 1;
    max-width: 60px;
    padding: 0.6rem 0;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    background: var(--surface);
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.12s, border-color 0.12s, color 0.12s;
  }

  .vote-btn:hover { border-color: #aaa; }

  .vote-btn.negative  { color: var(--negative); }
  .vote-btn.neutral   { color: var(--neutral); }
  .vote-btn.positive  { color: var(--positive); }

  .vote-btn.active.negative { background: #fdf0ee; border-color: var(--negative); }
  .vote-btn.active.neutral  { background: #f0f0f0; border-color: #888; }
  .vote-btn.active.positive { background: #edfaf3; border-color: var(--positive); }

  .actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .link-btn {
    background: none;
    border: none;
    color: var(--text-muted);
    font-size: 0.85rem;
    cursor: pointer;
    padding: 0;
    text-decoration: underline;
    text-underline-offset: 3px;
  }

  .link-btn:hover { color: var(--text); }

  .results-btn {
    background: var(--accent);
    color: white;
    border: none;
    border-radius: var(--radius);
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
    transition: opacity 0.15s;
  }

  .results-btn:hover { opacity: 0.85; }
</style>
