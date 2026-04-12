<script>
  import { onMount } from 'svelte'
  import { view, loadError, loadData } from './lib/store.js'
  import ComparisonView from './lib/ComparisonView.svelte'
  import ResultsView from './lib/ResultsView.svelte'

  onMount(loadData)
</script>

<div class="page">
  <header>
    <span class="title">🏛️ Voyage à <span class="rome">ROME</span></span>
    <p class="subtitle">Répertoire Opérationnel des Métiers et des Emplois (ROME) — trouvez le vôtre en classant des compétences.</p>
  </header>

  <main>
    {#if $view === 'loading'}
      <div class="status">Chargement des données ROME…</div>

    {:else if $view === 'error'}
      <div class="status error">
        <p>Impossible de charger les données.</p>
        <code>{$loadError}</code>
        <p class="hint">Vérifiez que <code>webapp/public/data/</code> contient les JSON générés par <code>build_json.py</code>.</p>
      </div>

    {:else if $view === 'comparing'}
      <ComparisonView />

    {:else}
      <ResultsView />
    {/if}
  </main>

  <footer>
    <span>données ROME 4.0 · France Travail · POC</span>
    <span>Aucune donnée collectée — tout reste dans votre navigateur.</span>
  </footer>
</div>

<style>
  .page {
    max-width: 720px;
    margin: 0 auto;
    padding: 0 1rem;
    display: flex;
    flex-direction: column;
  }

  header {
    padding: 2rem 0 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
  }

  .title {
    font-family: 'Playfair Display', Georgia, serif;
    font-weight: 700;
    font-size: 2rem;
    letter-spacing: -0.01em;
    line-height: 1;
  }

  .rome { letter-spacing: 0.08em; }

  .subtitle { color: var(--text-muted); font-size: 0.82rem; line-height: 1.4; max-width: 55ch; }

  main {
    display: flex;
    flex-direction: column;
    padding: 1.5rem 0 0;
    width: 100%;
  }

  footer {
    padding: 3rem 0 2rem;
    font-size: 0.75rem;
    color: var(--text-muted);
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
  }

  .status { color: var(--text-muted); font-size: 0.9rem; margin-top: 4rem; }

  .status.error {
    color: var(--negative);
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    max-width: 480px;
  }

  .hint { color: var(--text-muted); font-size: 0.8rem; }
</style>
