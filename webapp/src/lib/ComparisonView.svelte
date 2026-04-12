<script>
  import { fly } from 'svelte/transition'
  import { currentPair, voteCount, vote, voteBoth, voteNeither, skip, showResults, MIN_VOTES } from './store.js'

  const TYPE_EMOJI = {
    'COMPETENCE-DETAILLEE': '🛠️',
    'MACRO-SAVOIR-FAIRE': '🧩',
    'MACRO-SAVOIR-ETRE-PROFESSIONNEL': '🧠',
    'SAVOIR': '📚',
  }

  const TYPE_LABEL = {
    'COMPETENCE-DETAILLEE': 'savoir-faire',
    'MACRO-SAVOIR-FAIRE': 'savoir-faire',
    'MACRO-SAVOIR-ETRE-PROFESSIONNEL': 'savoir-être',
    'SAVOIR': 'connaissance',
  }

  let selected = null

  function handle(fn, key) {
    selected = key
    setTimeout(() => { selected = null; fn() }, 180)
  }

  $: canShowResults = $voteCount >= MIN_VOTES
  $: pair = $currentPair
  $: progress = Math.min($voteCount / MIN_VOTES * 100, 100)
  $: remaining = Math.max(MIN_VOTES - $voteCount, 0)
</script>

<div class="wrapper">
  {#if !pair}
    <div class="no-pair">
      Plus de paires disponibles.
      <button on:click={showResults}>Voir les résultats</button>
    </div>
  {:else}
    <div class="meta">
      <div class="progress-track">
        <div class="progress-fill" style="width: {progress}%"></div>
      </div>
      <span class="counter">
        {#if canShowResults}
          prêt !
        {:else}
          encore {remaining} avant les résultats
        {/if}
      </span>
      {#if canShowResults}
        <button class="results-btn" on:click={showResults}>voir les résultats →</button>
      {/if}
    </div>

    <p class="question">Qu'est-ce qui vous attire le plus ?</p>

    {#key pair}
    <div class="choices-top" in:fly={{ y: 3, duration: 300, opacity: 0 }}>
      <button class="choice-btn" class:active={selected === 'A'} on:click={() => handle(() => vote(1), 'A')}>
        <span class="choice-tag">{TYPE_EMOJI[pair.skillA.type] ?? '•'} {TYPE_LABEL[pair.skillA.type] ?? pair.skillA.type}</span>
        <span class="choice-label">{pair.skillA.libelle}</span>
      </button>

      <button class="choice-btn" class:active={selected === 'B'} on:click={() => handle(() => vote(-1), 'B')}>
        <span class="choice-tag">{TYPE_EMOJI[pair.skillB.type] ?? '•'} {TYPE_LABEL[pair.skillB.type] ?? pair.skillB.type}</span>
        <span class="choice-label">{pair.skillB.libelle}</span>
      </button>
    </div>
    {/key}

    <div class="choices-bottom">
      <button class="secondary-btn" class:active={selected === 'both'}    on:click={() => handle(voteBoth, 'both')}>✌️ les deux, volontiers</button>
      <button class="secondary-btn" class:active={selected === 'neither'} on:click={() => handle(voteNeither, 'neither')}>😱 ni l'un ni l'autre</button>
      <button class="secondary-btn" class:active={selected === 'skip'}    on:click={() => handle(skip, 'skip')}>🤔 je passe</button>
    </div>
  {/if}
</div>

<style>
  .wrapper {
    width: 100%;
    max-width: 720px;
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
  }

  .meta {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .progress-track {
    flex: 1;
    height: 6px;
    background: var(--border);
    border-radius: 3px;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    background: var(--accent);
    border-radius: 3px;
    transition: width 0.3s ease;
  }

  .counter { font-size: 0.8rem; color: var(--text-muted); white-space: nowrap; }

  .question { font-size: 0.9rem; color: var(--text-muted); }

  /* Top row: A and B */
  .choices-top {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
  }

  .choice-btn {
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
    padding: 1.4rem;
    min-height: 140px;
    justify-content: flex-start;
    text-align: left;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    background: var(--surface);
    box-shadow: var(--shadow);
    cursor: pointer;
    transition: border-color 0.15s, background 0.15s, transform 0.12s;
  }

  .choice-btn:hover { border-color: #aaa; background: #f0efec; transform: translateY(-1px); }
  .choice-btn.active { border-color: #aaa; background: #f0efec; transform: scale(0.97); }

  .choice-tag {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-muted);
    letter-spacing: 0.03em;
    text-transform: uppercase;
  }

  .choice-label { font-size: 1.15rem; font-weight: 500; line-height: 1.4; color: var(--text); }

  /* Bottom row: les deux / aucun / sans avis */
  .choices-bottom {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 0.75rem;
  }

  .secondary-btn {
    padding: 0.75rem 1rem;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    background: var(--surface);
    box-shadow: var(--shadow);
    font-size: 1rem;
    font-weight: 500;
    color: var(--text);
    cursor: pointer;
    transition: border-color 0.15s, background 0.15s, transform 0.12s;
  }

  .secondary-btn:hover { border-color: #aaa; background: #f0efec; }
  .secondary-btn.active { background: #f0efec; border-color: #aaa; transform: scale(0.97); }


  /* Results button */
  .results-btn {
    background: var(--accent); color: white; border: none;
    border-radius: var(--radius); padding: 0.4rem 0.9rem;
    font-size: 0.85rem; font-weight: 600; cursor: pointer;
    transition: opacity 0.15s;
  }
  .results-btn:hover { opacity: 0.85; }

  .no-pair { color: var(--text-muted); font-size: 0.9rem; }
  .no-pair button { background: none; border: none; color: var(--accent); cursor: pointer; text-decoration: underline; }
</style>
