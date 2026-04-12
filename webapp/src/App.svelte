<script>
  import { view } from './lib/store.js'
  import ComparisonView from './lib/ComparisonView.svelte'
  import ResultsView from './lib/ResultsView.svelte'
</script>

<header>
  <span class="title">Voyage à Rome</span>
  <span class="subtitle">Tous les chemins y mènent. Encore faut-il savoir lequel.</span>
</header>

<main>
  {#if $view === 'comparing'}
    <ComparisonView />
  {:else}
    <ResultsView />
  {/if}
</main>

<footer>
  données ROME 4.0 · France Travail · POC
</footer>

<style>
  :global(body) { display: flex; flex-direction: column; min-height: 100vh; }

  header {
    padding: 1.25rem 2rem;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: baseline;
    gap: 1rem;
    background: var(--surface);
  }

  .title {
    font-weight: 700;
    font-size: 1.1rem;
    letter-spacing: -0.01em;
  }

  .subtitle {
    color: var(--text-muted);
    font-size: 0.85rem;
  }

  main {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 2.5rem 1rem;
  }

  footer {
    text-align: center;
    padding: 1rem;
    font-size: 0.75rem;
    color: var(--text-muted);
    border-top: 1px solid var(--border);
  }
</style>
