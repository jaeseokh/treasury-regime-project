# Treasury Regime Lab

Regime-first Treasury market research for macro strategy, fixed-income decision
support, and hiring-manager-facing communication.

This repository models the `economic regime path` as the core latent state,
uses the Treasury market as the fastest observation mirror, classifies shocks
from official and curated evidence, updates five-player response paths, and
exports a daily dashboard for a public GitHub Pages site.

Public website:
[jaeseokh.github.io](https://jaeseokh.github.io/)

## Why this project exists

Most market dashboards describe what moved. This project is built to answer a
harder question:

`What changed in the economic regime path, which shock or player behavior bent
that path, and what does that imply for Treasury strategy?`

The intended audience is:

- macro research managers
- Treasury strategy heads
- buy-side and sell-side hiring teams
- researchers who need a disciplined regime-to-strategy workflow

## What Version 1 does

- defines a fixed `economic regime dictionary` and sparse transition graph
- updates regime probabilities daily with a `source-decomposed Bayesian update`
- treats the Treasury market as the main real-time inference layer
- classifies shocks from official and curated evidence
- estimates five-player response probabilities across short, mid, and long horizons
- computes curve math including:
  - Nelson-Siegel level, slope, and curvature
  - butterfly structure
  - breakeven and real-yield decomposition
  - rolling VAR-style term-premium proxy
  - cash-flow-based par-bond duration, convexity, and DV01
- exports a manager-facing dashboard payload for the website
- tracks versioned research limitations and the upgrade queue

## Research architecture

The system is intentionally hierarchical:

1. `Economic regime core`
2. `Treasury observation layer`
3. `Shock and evidence layer`
4. `Player response layer`
5. `Statistical and ML engine`
6. `Forecast review and memory`
7. `Website and communication layer`

The main design rule is simple:

- `regime path` is the structural backbone
- `shock` and `player behavior` are stochastic drivers
- `Treasuries` are the fastest mirror, not the regime itself

## Repository layout

- `src/treasury_regime/agents`
  Daily pipeline agents for data, evidence, shock, regime, player, review, and reporting
- `src/treasury_regime/modeling`
  Regime dictionary, Bayesian update logic, curve math, and market-feature engineering
- `src/treasury_regime/sources`
  Public API clients and official-source ingestion
- `src/treasury_regime/pipelines`
  Daily update and website export orchestration
- `data/manual`
  Manual media claims and the versioned research upgrade map
- `docs/V1_RESEARCH_MAP.md`
  Human-readable maintenance rule for versioned improvement

## Quick start

Create a Python environment, install the dependencies, then run the daily
pipeline.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
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

## Key outputs

- `outputs/daily_report.md`
  Daily Treasury regime note
- `outputs/daily_summary.json`
  Structured daily snapshot
- `outputs/posterior_history.csv`
  Regime posterior history
- `outputs/player_probabilities.csv`
  Player scenario probabilities
- `outputs/shock_history.csv`
  Shock classification history
- `outputs/research_upgrade_map.json`
  Versioned roadmap and known limitations

## Website sync

The pipeline exports static JSON payloads to:

`/Users/jaeseokhwang/jaeseok_website/assets/data`

The website is a separate GitHub Pages repository that reads those payloads and
renders the public dashboard.

## Evidence policy

Official sources and your own structured summaries belong in the system.
Reuters/Bloomberg text should be summarized and cited rather than republished
verbatim.

Optional curated notes live in:

`data/manual/manual_media_claims.json`

## Versioning and maintenance

This repository should be treated as `version 1`, not as a finished product.

The machine-readable source of truth for research maintenance is:

`data/manual/research_upgrade_map.json`

When the system needs improvement:

1. identify the affected layer
2. log the known problem
3. attach the planned change
4. define why it matters
5. define the success metric

That process is described in more detail in:

`docs/V1_RESEARCH_MAP.md`
