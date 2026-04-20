# Treasury Regime Lab

Treasury Regime Lab is a regime-first research system for U.S. Treasury strategy.
It treats the latent economic regime path as the core state, uses the Treasury
market as the fastest observation surface, classifies shocks from official and
curated evidence, updates player response probabilities, and exports a
manager-facing daily dashboard for a GitHub Pages website.

## Core Design

- `Economic regime path` is the structural backbone.
- `Shock state` and `player response state` are stochastic drivers that bend or
  accelerate the regime path.
- `Treasury market data` is the main real-time inference channel.
- `Official sources` and `curated media notes` provide structured evidence
  rather than free-form narrative.
- `Curve math` includes Nelson-Siegel factors, butterfly structure, a rolling
  VAR-style term-premium decomposition, and cash-flow-based par-bond risk.
- `Daily, weekly, and monthly review` keeps score on scenarios, player paths,
  and source credibility.

## Project Layout

- `src/treasury_regime/agents`: multi-agent pipeline modules
- `src/treasury_regime/modeling`: regime dictionary, Bayesian updates, and
  market features
- `src/treasury_regime/sources`: public API and official source clients
- `src/treasury_regime/pipelines`: daily update and website export orchestration
- `data/raw`: downloaded market, auction, and official-source datasets
- `data/processed`: derived features and structured evidence
- `data/manual`: hand-curated media claims or source overrides
- `data/manual/research_upgrade_map.json`: version map, known problems, and upgrade queue
- `docs/V1_RESEARCH_MAP.md`: human-readable maintenance rule for the hierarchy
- `outputs`: reports, posteriors, archive tables, and website-ready JSON

## Daily Workflow

```bash
python3 run_daily_update.py
```

This runs:

1. `DataAgent`
2. `EvidenceAgent`
3. `ShockAgent`
4. `RegimeAgent`
5. `PlayerAgent`
6. `ReviewAgent`
7. `ReportAgent`
8. `Website export`

## Website Sync

The pipeline exports static JSON payloads to:

`/Users/jaeseokhwang/jaeseok_website/assets/data`

The website itself is a static GitHub Pages site that reads those payloads.

## Manual Evidence Notes

Optional curated notes can be added to:

`data/manual/manual_media_claims.json`

This is where Reuters/Bloomberg summaries should live if you want them included
without republishing proprietary text. Store your own summary, a citation URL,
and structured claim fields.

## Versioning And Research Maintenance

This build should be treated as `version 1`.
The hierarchy, known limitations, and next upgrades are tracked in:

`data/manual/research_upgrade_map.json`

When the system needs improvement, update the affected layer there first rather
than adding disconnected notes or ad hoc TODOs.
