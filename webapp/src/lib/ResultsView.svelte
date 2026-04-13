<script>
  import { rankedJobs, voteCount, restart, view } from './store.js'

  $: top = $rankedJobs
  $: minScore = Math.min(...top.map(j => j.score))
  $: maxScore = Math.max(...top.map(j => j.score))
  $: scoreRange = Math.max(maxScore - minScore, 1)
</script>

<div class="wrapper">
  <div class="heading">
    <h1>Votre Rome personnalisée</h1>
    <p class="sub">
      Calculé sur {$voteCount} comparaison{$voteCount !== 1 ? 's' : ''}.
      Non contractuel.
    </p>
  </div>

  <ol class="job-list">
    {#each top as job, i}
      <li class="job-row" class:podium={i < 3}>
        <span class="rank">{i + 1}</span>
        <div class="job-info">
          <a href={job.url} target="_blank" rel="noopener noreferrer" class="job-label">
            {job.libelle}
          </a>
          <span class="code">{job.code}</span>
          <div class="bar-wrap">
            <div class="bar" style="width: {Math.max(0, (job.score - minScore) / scoreRange * 100)}%"></div>
          </div>
        </div>
        <span class="score">{job.score - minScore > 0 ? '+' : ''}{job.score - minScore}</span>
      </li>
    {/each}
  </ol>

  <div class="actions">
    <button class="link-btn" on:click={() => view.set('comparing')}>← continuer à voter</button>
    <button class="restart-btn" on:click={restart}>recommencer</button>
  </div>

  <p class="disclaimer">
    <a href="https://candidat.francetravail.fr/metierscope/" target="_blank" rel="noopener noreferrer">
      Explorer toutes les fiches sur France Travail →
    </a>
  </p>
</div>

<style>
  .wrapper {
    width: 100%;
    max-width: 600px;
    display: flex;
    flex-direction: column;
    gap: 1.75rem;
  }

  .heading h1 { font-size: 1.3rem; font-weight: 700; letter-spacing: -0.02em; }
  .sub { font-size: 0.82rem; color: var(--text-muted); margin-top: 0.25rem; }

  .job-list { list-style: none; display: flex; flex-direction: column; gap: 0.5rem; }

  .job-row {
    display: grid;
    grid-template-columns: 1.5rem 1fr 3.5rem;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
  }

  .job-row.podium { border-left: 3px solid var(--accent); }

  .rank { font-size: 0.8rem; font-weight: 700; color: var(--text-muted); text-align: right; }

  .job-info { display: flex; flex-direction: column; gap: 0.2rem; min-width: 0; }

  .job-label {
    font-size: 0.95rem; font-weight: 500; color: var(--text);
    text-decoration: none; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  .job-label:hover { color: var(--accent); text-decoration: underline; text-underline-offset: 3px; }

  .code { font-size: 0.7rem; color: var(--text-muted); font-family: monospace; }

  .bar-wrap { height: 3px; background: var(--border); border-radius: 2px; overflow: hidden; margin-top: 0.2rem; }
  .bar { height: 100%; background: var(--accent); border-radius: 2px; transition: width 0.4s ease; min-width: 2px; }

  .score { font-size: 0.82rem; font-weight: 600; text-align: right; color: var(--text-muted); }

  .actions { display: flex; justify-content: space-between; align-items: center; }

  .link-btn {
    background: none; border: none; color: var(--text-muted);
    font-size: 0.85rem; cursor: pointer; padding: 0;
    text-decoration: underline; text-underline-offset: 3px;
  }
  .link-btn:hover { color: var(--text); }

  .restart-btn {
    background: none; border: 1px solid var(--border); border-radius: var(--radius);
    padding: 0.45rem 0.9rem; font-size: 0.85rem; cursor: pointer; color: var(--text-muted);
    transition: border-color 0.15s, color 0.15s;
  }
  .restart-btn:hover { border-color: #aaa; color: var(--text); }

  .disclaimer { font-size: 0.78rem; color: var(--text-muted); }
  .disclaimer a { color: var(--text-muted); }
  .disclaimer a:hover { color: var(--accent); }
</style>
