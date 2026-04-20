# Treasury Regime Lab V1 Research Map

This document defines how the project should be maintained as it evolves beyond
the current version.

## Why this exists

The project is intentionally being built as `version 1`, not as a final system.
That means each weakness should be attached to the right layer of the research
stack instead of being handled as an isolated patch.

## Maintenance Rule

When a new problem appears:

1. identify the affected layer
2. describe the problem in plain language
3. attach the planned change
4. define why it matters for Treasury strategy research
5. define the success metric

The machine-readable source of truth for this process is:

`data/manual/research_upgrade_map.json`

## Current Layer Order

1. Economic regime core
2. Treasury observation layer
3. Shock and evidence layer
4. Player response layer
5. Statistical and ML engine
6. Forecast review and memory
7. Website and communication layer

## Update Discipline

- `Daily`: note data failures, suspicious posterior jumps, export problems, or
  obvious interpretation issues.
- `Weekly`: review model calibration, player logic, and communication gaps.
- `Monthly`: re-rank upgrade priorities and decide whether changes are still
  within v1 or justify a version step.

## Current Version Objective

Version 1 should remain:

- regime-first
- Treasury-specific
- manager-facing
- explicit about uncertainty
- explicit about known limitations

The roadmap is not just a backlog. It is the control surface for how the
research system improves over time.
