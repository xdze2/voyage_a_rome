<script>
  import { rankedJobs, voteCount, restart } from './store.js'

  $: top = $rankedJobs
  $: maxScore = Math.max(...top.map(j => j.score), 1)
</script>

<div class="wrapper">
  <div class="heading">
    <h1>Votre Rome personnalisée</h1>
    <p class="sub">Calculé sur {$voteCount} comparaison{$voteCount > 1 ? 's' : ''}. Non contractuel.</p>
  </div>

  <ol class="job-list">
    {#each top as job, i}
      <li class="job-row" class:podium={i < 3}>
        <span class="rank">{i + 1}</span>

        <div class="job-info">
          <a href={job.url} target="_blank" rel="noopener noreferrer" class="job-label">
            {job.label}
          </a>
          <div class="bar-wrap">
            <div
              class="bar"
              style="width: {Math.max(0, job.score / maxScore * 100)}%"
              class:negative-bar={job.score < 0}
            ></div>
          </div>
        </div>

        <span class="score" class:pos={job.score > 0} class:neg={job.score < 0}>
          {job.score > 0 ? '+' : ''}{job.score}
        </span>
      </li>
    {/each}
  </ol>

  <p class="disclaimer">
    Données fictives · <a href="https://candidat.francetravail.fr/metierscope/" target="_blank" rel="noopener noreferrer">Explorer sur France Travail →</a>
  </p>

  <button class="restart-btn" on:click={restart}>recommencer</button>
</div>

<style>
  .wrapper {
    width: 100%;
    max-width: 600px;
    display: flex;
    flex-direction: column;
    gap: 1.75rem;
  }

  .heading h1 {
    font-size: 1.3rem;
    font-weight: 700;
    letter-spacing: -0.02em;
  }

  .sub {
    font-size: 0.82rem;
    color: var(--text-muted);
    margin-top: 0.25rem;
  }

  .job-list {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .job-row {
    display: grid;
    grid-template-columns: 1.5rem 1fr 3rem;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
  }

  .job-row.podium {
    border-left: 3px solid var(--accent);
  }

  .rank {
    font-size: 0.8rem;
    font-weight: 700;
    color: var(--text-muted);
    text-align: right;
  }

  .job-info {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    min-width: 0;
  }

  .job-label {
    font-size: 0.95rem;
    font-weight: 500;
    color: var(--text);
    text-decoration: none;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .job-label:hover {
    color: var(--accent);
    text-decoration: underline;
    text-underline-offset: 3px;
  }

  .bar-wrap {
    height: 4px;
    background: var(--border);
    border-radius: 2px;
    overflow: hidden;
  }

  .bar {
    height: 100%;
    background: var(--accent);
    border-radius: 2px;
    transition: width 0.4s ease;
    min-width: 2px;
  }

  .bar.negative-bar { background: var(--border); }

  .score {
    font-size: 0.85rem;
    font-weight: 600;
    text-align: right;
    color: var(--text-muted);
  }

  .score.pos { color: var(--positive); }
  .score.neg { color: var(--negative); }

  .disclaimer {
    font-size: 0.78rem;
    color: var(--text-muted);
  }

  .disclaimer a {
    color: var(--text-muted);
  }

  .disclaimer a:hover { color: var(--accent); }

  .restart-btn {
    align-self: flex-start;
    background: none;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 0.45rem 0.9rem;
    font-size: 0.85rem;
    cursor: pointer;
    color: var(--text-muted);
    transition: border-color 0.15s, color 0.15s;
  }

  .restart-btn:hover {
    border-color: #aaa;
    color: var(--text);
  }
</style>
