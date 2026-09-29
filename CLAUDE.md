# CLAUDE.md

# AgniDrishti — SIH 2026 PS 26170

This file is the permanent engineering and research governance document for
this repository. Every Claude Code session (and every human contributor) must
follow it. If an instruction in a chat conflicts with this file, point out the
conflict before acting.

## Project

AgniDrishti is an engineering and ML research project for:

SIH 2026 — Problem Statement 26170
AI-Driven Anomaly Detection in Component Burn-In & Screening

The goal is to develop an explainable, experimentally validated reliability
screening framework for detecting abnormal component behavior and identifying
potential future degradation.

---

# 0. Current Phase (read first)

**Phase: DEPLOYABLE PROTOTYPE BUILT — awaiting team review** (P2–P7 completed 2026-09-26;
deployable screening service, site calibration and audit trail added 2026-09-28 at the team's
request, [ADR-006](docs/decisions/ADR-006-deployable-service.md); results in
`docs/research/experiments/ablation-plan.md` §3–§5; v1 test split spent — changes need a
new pre-registered config and fresh data). Authorisation record: P2–P7 authorised by the team 2026-09-26 (
"do everything as per you", end product in 2 days). P1 data foundation is done.
Experiment values are pre-registered in `configs/experiments/pipeline_v1.yaml`.

Build one layer per change, in this order, each with tests and its recorded
experiment on validation lots: L1 + metrics (E1) → L2 lot-relative level/drift
(E2, E3) → L4 168h prediction + safety-slope rule (E4) → L5 interval (E5) → L6
decision rules (E6) → L7 explanations → one final test-lot evaluation →
prototype CLI + demo built only from recorded outputs.

Earlier P1 scope (kept for record):

Scope of P1 (narrow, in this order):

- `pyproject.toml` with minimal, justified dependencies.
- Canonical schema + raw→canonical column mapping (FR-01).
- Data-quality gate (FR-02) with unit tests, including checkpoint-availability
  (leakage) tests.

Still NOT allowed in P1 until their gates are met:

- ~~Synthetic data generator~~ — gate met 2026-09-26 (families sealed, grids
  pre-registered); development generator + E0 audit implemented (FR-17–FR-19).
  Never create or reconstruct held-out families 19–20.
- ~~Experiments E1–E6~~ — gate met 2026-09-26 (pre-registration above).
- Still not allowed: advanced / black-box models (CLAUDE §4), a database,
  notebooks with production logic, any number in the demo that does not come
  from a recorded run. (The web service is allowed since 2026-09-28, ADR-006.)

No implementation may begin without a documented requirement in
`docs/requirements/requirements-specification.md` and a planned experiment in
`docs/research/experiments/experiment-plan.md`.

The phase changes only when the team explicitly says so. When it changes,
update this section, `README.md`, `docs/project-state.md` and
`docs/roadmap/implementation-plan.md` in the same change.

---

# 1. Core Engineering Principle

Prefer:

Simple + Validated + Explainable

over:

Complex + Impressive + Unvalidated

The objective is NOT to build the largest AI system.

The objective is to build a technically defensible, reproducible,
explainable and useful solution to PS 26170.

---

# 2. Current Candidate Pipeline

Burn-in Data
↓
Data Quality Gate
↓
Absolute Specification Check
↓
Lot-Relative Analysis (level + drift / trajectory)
↓
168h Prediction
↓
Uncertainty Estimation (conditional — kept only if E5 supports it)
↓
Ordered Decision Rules (incl. safety-slope rule; no fused risk score)
↓
PASS / REVIEW / REJECT (+ binary flag)
↓
Engineer-Readable Explanation

This is a PROVISIONAL architecture (see `docs/decisions/ADR-001-initial-architecture.md`,
Revision 1 of 2026-09-26).
It must be validated experimentally before being treated as final.
Every layer after the specification check must earn its place in the ablation study.

---

# 3. Baseline-First Rule

Always begin with simple baselines. Required progression:

1. Static specification threshold
2. Lot-relative robust statistics
3. Trajectory features
4. Simple 168h prediction
5. Advanced prediction only if justified
6. Uncertainty
7. Risk decision
8. Full system

Never jump directly to the most complex model.

Development loop:

BASELINE → MEASURE → EXTEND → MEASURE → ABLATE → VALIDATE

---

# 4. No Unnecessary AI

Do not use a technology simply because it is popular. Do not automatically introduce:

- LSTM, GRU, Transformer, CNN, Autoencoder, GNN
- Large neural networks
- Reinforcement learning
- LLMs / generative AI
- "Digital twin" framing

The burn-in data is expected to be **sparse in time** (reported checkpoints:
0h, 24h, 96h, 168h). Do not assume dense time series.

An advanced model may only be introduced when ALL of these hold:

1. There is a clear technical reason.
2. The baseline has been evaluated.
3. The limitation of the baseline is documented.
4. The advanced model plausibly addresses that limitation.
5. The required data volume is available and documented.
6. An experiment is defined in the experiment plan.
7. The experiment demonstrates measurable value over the baseline.

---

# 5. No Fake Results

Never fabricate: accuracy, precision, recall, F1, PR-AUC, false-negative rate,
false-positive rate, MAE, RMSE, calibration, interval coverage, interval width,
review rate, latency, throughput, scalability, dataset size, failure counts,
benchmark results, or "illustrative" numbers that look like results.

If an experiment has not been run, write exactly:

`TBD — experiment not yet executed.`

Never generate realistic-looking numbers as placeholders. Numeric examples in
documentation (e.g. "50 µA limit") must be labelled as illustrative and must not
be phrased as an outcome.

The research PDFs contain unmeasured ablation numbers (e.g. "catches 20% / 65%
/ 92%", "zero false negatives", "review queue under 8%"). These are NOT results
and must never be reused. See `docs/research/claim-register.md`.

---

# 6. Dataset Integrity

Always distinguish:

- Official SIH/PS data
- External public datasets (e.g. NASA PCoE)
- Synthetic PS-shaped datasets
- Simulated/illustrative examples

Never represent synthetic data as real. Never represent NASA/public datasets as
SIH or ISRO datasets. Never fabricate failure labels or physics.

Every dataset must have an entry in `docs/research/datasets/data-sources.md`
with: source, access, license/usage conditions (where known), variables,
units, temporal resolution, component identifiers, lot identifiers, labels,
missing values, limitations, intended use.

Rules for `data/`:

- `data/raw/` — original files, never modified in place, never overwritten.
- `data/external/` — third-party public datasets, as downloaded.
- `data/synthetic/` — generated data; every file must be reproducible from a
  committed generator + config + seed, and its name must contain `synthetic`.
- `data/interim/`, `data/processed/` — derived; must be regenerable by a script.
- Do not auto-download large datasets. Downloading is a deliberate, documented step.

---

# 7. Data Leakage Prevention

Data leakage is unacceptable.

For early 168h prediction, features may only use information available at the
decision checkpoint. Do not leak:

- `Value_168h` (or any later checkpoint) into features for an earlier checkpoint
- future labels or labels derived from future measurements
- future-derived features (e.g. slopes computed with a later point)
- post-prediction observations
- statistics fitted on test lots (scalers, thresholds, calibration quantiles)

Prevent:

- component leakage (same component in train and test)
- lot leakage (split by `Lot_ID`, not by row)
- temporal leakage (see above)
- duplicate samples across train/validation/calibration/test

Lot-relative statistics computed from peers in the same lot at the same
checkpoint are allowed (this is how a lot is screened in practice), but peer
labels and peer future values are not.

The split strategy is defined in `docs/research/experiments/evaluation-protocol.md`.
A final test set must stay untouched until final evaluation.

Leakage checks must be automated as tests once code exists.

---

# 8. Experiment Reproducibility

Every meaningful experiment records:

- Experiment ID (matching `experiment-plan.md`)
- Dataset name + version/hash + data category (official/external/synthetic)
- Configuration file
- Features
- Model / method
- Train/validation/calibration/test split and grouping key
- Random seed(s)
- Metrics
- Result
- Observations and limitations
- Git commit

Experiments must be reproducible from a config and a command. Never silently
overwrite previous experiment results; write to a new run directory.

---

# 9. Required Evaluation

Anomaly / screening: recall, precision, F1, PR-AUC, false-negative rate, false-positive rate.

Prediction: MAE, RMSE, error on the decision-relevant tail, appropriate trajectory metrics.

Uncertainty: prediction-interval coverage (overall and per lot / per scenario),
interval width, calibration.

Operational: defect escape rate, false rejection rate, review rate,
automatically cleared percentage, latency where applicable.

Accuracy alone is insufficient and must never be the headline metric
(defects are expected to be rare).

---

# 10. Mandatory Ablation

1. Static specification
2. Static + lot statistics
3. Static + lot + trajectory
4. Static + lot + trajectory + 168h prediction
5. Previous + uncertainty
6. Full decision rules (the "risk engine": ordered rules, no fused score — ADR-001 Rev. 1)

If a component does not improve the evidence, consider removing it.
Do not keep complexity for presentation value.

---

# 11. Explainability

A flagged component must have a human-readable, quantitative explanation that answers:

- Why was it flagged?
- How abnormal is it relative to its lot?
- What happened to its trajectory?
- What is the predicted future state?
- How uncertain is the prediction?
- Why was PASS / REVIEW / REJECT selected (which rule fired)?

Avoid generic statements such as "The AI thinks this component is risky."

---

# 12. Decision Logic

Use PASS / REVIEW / REJECT only when supported by implemented decision logic.
REVIEW exists to handle uncertainty and suspicious cases without forcing a binary decision.
When inputs are missing or invalid, the default is REVIEW, never PASS.
Do not claim elimination of false negatives unless validated, and even then
state the dataset and conditions.

---

# 13. Statistical Terminology

Be precise. See `docs/glossary.md`.

- A 95% **prediction interval** is NOT "95% probability that the component will fail".
- A **confidence interval** (for a parameter) is not a **prediction interval** (for a new observation).
- Conformal coverage is **marginal** and assumes exchangeability; it is not a per-component guarantee.
- A risk score is not a probability unless it has been calibrated and the
  calibration has been measured on held-out data.
- A robust z-score is a distance, not a probability.

If terminology is uncertain, verify it before writing it.

---

# 14. Novelty Claims

Do not claim: first, world's first, completely novel, no existing solution,
patent-pending, standard-compliant (e.g. "AEC-Q001 compliant"), or
"physics-informed" unless the physics is actually encoded and validated.

Prefer: proposed framework, proposed integration, PS-specific implementation,
engineering differentiation, "informed by lot-relative screening practice".

See `docs/research/prior-art/novelty-boundaries.md`.

---

# 15. Research Rule and Claim Labels

Research documentation must distinguish the following. Use these labels:

| Label | Meaning |
|---|---|
| `[SF]` | Source-supported fact — stated by a cited source (note which) |
| `[PA]` | Prior-art finding |
| `[EI]` | Engineering interpretation / inference |
| `[PR]` | Proposal (our design choice) |
| `[AS]` | Assumption |
| `[UV]` | Unverified claim / hypothesis |
| `[GAP]` | Research gap / not established by the available research |
| `[NC]` | Must NOT be claimed in the presentation |

Never silently upgrade an assumption into a fact. When the research does not
establish something, write: "Not established by the available research."

Source IDs used throughout the docs:

- `R0` — **Official PS 26170 text**, SIH portal (https://sih.gov.in/sih2026PS),
  retrieved 2026-09-26, preserved in `docs/research/ps-analysis/`
  (`official-ps-26170.md` + unmodified HTML extract). Authoritative; overrides R1–R4.
- `R1` — `Comprehensive Guide to Deep Web Research.pdf` (methodology only)
- `R2` — `Deep Research Report.pdf`
- `R3` — `SIH_26170_Comprehensive_Research_Report.pdf`
- `R4` — Research assessment text pasted into the Claude Code chat (2026-09-26)

None of R1–R4 is the official PS text; use R0 for any statement about what the PS requires.
Verified external primary sources use IDs `S-01`… (registry: `docs/research/prior-art/literature-review.md`).
No official PS dataset exists (verified 2026-09-26: `docs/research/datasets/official-dataset-verification.md`).

---

# 16. Code Quality (for future implementation)

Use professional Python (3.11+ assumed; confirm when `pyproject.toml` is created).

Prefer: type hints, small pure functions, clear modules, meaningful names,
explicit configuration, `logging` (not `print`) in library code, docstrings on
public functions stating units and assumptions, deterministic seeds, tests.

Avoid: giant scripts, magic numbers, hidden global state, hard-coded paths,
duplicate code, unnecessary abstractions, unused classes, dead code,
commented-out code.

Numerical code must state units and must handle degenerate cases explicitly
(e.g. MAD = 0, lot size too small, missing checkpoint).

---

# 17. Naming Conventions

- Python package: `agnidrish` (ASCII only; import as `import agnidrish`).
- Modules/functions/variables: `snake_case`. Classes: `PascalCase`. Constants: `UPPER_SNAKE_CASE`.
- Checkpoint columns: `value_0h`, `value_24h`, `value_96h`, `value_168h`
  (the reports use `Value_0h` etc.; map raw names to canonical names in one place).
- Identifiers: `component_id`, `lot_id`, `wafer_id`, `device_family`.
- Experiments: `E1` … `E6` as in the experiment plan; run directories
  `artifacts/<kind>/<experiment_id>/<YYYYMMDD-HHMMSS>_<short_sha>/`.
- Configs: `configs/<area>/<name>.yaml`.
- Docs: lowercase kebab-case `.md`; ADRs `ADR-NNN-title.md`.
- Synthetic data files must contain `synthetic` in the filename.

---

# 18. Repository Rules

```
docs/        Research, requirements, architecture, decisions, presentation
data/        raw / external / synthetic / interim / processed (see §6)
notebooks/   Exploration and analysis only
src/         Reusable production code (src/agnidrish/)
tests/       unit / integration / fixtures
configs/     Configuration (thresholds, paths relative to repo root, seeds)
scripts/     Repeatable command-line workflows
artifacts/   models / metrics / plots / predictions (generated, git-ignored)
app/         Final application/demo (not before P7)
.github/     PR template and, later, CI
```

The three research PDFs in the repository root are original source material.
Do not delete, overwrite or edit them.

---

# 19. Notebook Rule

Notebooks are for exploration, visualization, experiments.
Production logic belongs in `src/agnidrish/`.
Do not duplicate production logic across notebooks. Notebooks import from the package.
Name notebooks `NN-short-description.ipynb`. Clear large outputs before committing.

---

# 20. Path and Configuration Rule

Never hard-code absolute paths (e.g. the local Windows project path) in source
code, configs, notebooks or docs meant to be executed.
Use project-relative paths resolved from the repository root.
Thresholds, model parameters, dataset locations and seeds live in `configs/`.

---

# 21. Dependency Rule

Do not install packages unless required. Before adding one:

1. Check whether the standard library is sufficient.
2. Check whether an existing dependency already solves the problem.
3. Add only what is necessary, pin a compatible version range, and note why.

No dependency may be added for a component that has not passed its baseline experiment.

---

# 22. File Creation, Cleanup and Deletion Rule

The repository must remain clean, minimal, purposeful and maintainable.

## Before creating a file

Before creating any file, ask:

"Does this file have a current, concrete purpose in the present project phase?"

If NO:
- DO NOT CREATE IT.
- Do not create speculative files.
- Do not create placeholder implementations.
- Do not create duplicate documentation.
- Do not create files merely because they may be useful later.

Do not generate:
- speculative modules
- empty classes
- fake implementations
- placeholder APIs
- unused configuration files
- duplicate research reports
- duplicate READMEs
- unnecessary notebooks
- unnecessary scripts
- unnecessary test files
- unnecessary abstraction layers
- temporary files that should not remain in the repository

`.gitkeep` files are allowed only when required to preserve the agreed
directory structure.

## Repository cleanup

Claude Code MUST periodically inspect the repository for unnecessary files.

If a file is demonstrably:
- obsolete
- duplicated
- superseded
- temporary
- accidentally generated
- unrelated to the project
- empty without a structural purpose
- created during an earlier phase and no longer required
- contradicted by a newer authoritative document
- redundant with another document

then Claude Code SHOULD DELETE it rather than leaving repository clutter.

Do not keep unnecessary files "just in case."

The goal is:

    Minimum necessary files + Maximum useful evidence

## Before deleting a file

NEVER delete a file blindly.

Before deletion:

1. Inspect the file.
2. Determine its purpose.
3. Search the repository for references to it.
4. Check whether another document depends on it.
5. Check whether it contains unique research evidence, source material,
   requirements, decisions, provenance or experiment information.
6. Identify whether another file has superseded it.
7. If it is duplicated, identify the authoritative version.
8. If deletion is safe, delete the unnecessary file.
9. Update references, indexes, README files or documentation affected by
   the deletion.
10. Report the deletion in the final change summary.

## Safe deletion categories

Claude Code may delete without asking for separate confirmation when the
file is clearly:

- a temporary generated file
- an accidental duplicate
- an empty file with no structural purpose
- a broken/generated artifact that is not a source of truth
- an obsolete intermediate document
- a redundant copy of an authoritative document
- an implementation placeholder prohibited by the current project phase

## Protected files

The following must NOT be deleted, overwritten or modified merely for cleanup:

- official source datasets
- original source documents
- verified external datasets
- research PDFs supplied as source material
- accepted ADRs
- experiment evidence
- provenance records
- dataset hashes/checksums
- files explicitly marked as authoritative
- files required by the current repository structure

The three original research PDFs in the repository root are source material
and must remain untouched.

## Superseded documentation

Do not accumulate multiple competing versions of the same document.

When a document is superseded:

- preserve the authoritative historical record when it has research,
  decision or provenance value;
- mark it `Superseded` where appropriate;
- create/update the authoritative replacement;
- remove redundant copies;
- update references to point to the authoritative document.

Do NOT silently delete historical evidence merely because a newer document exists.

## Phase-aware cleanup

At the beginning of each major project phase, inspect the repository and
remove files that are no longer appropriate for the new phase.

For example:

Research phase:
- remove accidental implementation files
- remove unused notebooks
- remove temporary downloads
- remove duplicate research notes

Implementation phase:
- remove obsolete planning placeholders
- remove temporary experiments
- consolidate duplicate implementation documentation

Experiment phase:
- remove invalid or accidental outputs
- preserve reproducible experiment evidence
- never delete results merely because they are poor

Presentation phase:
- remove obsolete presentation drafts when they have no historical value
- retain the final evidence-backed presentation source

## Never delete evidence to improve appearance

Do NOT delete:
- failed experiments
- negative results
- poor-performing models
- evidence that contradicts the preferred approach
- inconvenient measurements
- documented limitations

if they are legitimate research evidence.

Instead, preserve them and document their status.

## Final cleanup check

Before completing a significant task, check:

- Are there duplicate files?
- Are there obsolete files?
- Are there temporary files?
- Are there empty files that serve no purpose?
- Are there files belonging to a future phase that were created prematurely?
- Are there documents that contradict the current authoritative documentation?
- Are there unused generated artifacts?
- Are there stale references to deleted or renamed files?

Delete unnecessary files and update references where safe.

The repository should never grow simply because Claude Code generated files.
 

# 23. Implementation Rule (when implementation begins)

Requirement → Minimal implementation → Test → Experiment → Measure → Document → Extend

Never implement the entire architecture in one operation. One layer per change.

---

# 24. Testing Expectations

Tests go in `tests/unit/`, `tests/integration/`, with small hand-written
fixtures in `tests/fixtures/` (fixtures are test data, not datasets; keep tiny).

Prioritise tests for: data validation, leakage prevention (split disjointness,
feature availability per checkpoint), feature calculations (robust z, MAD = 0
handling, drift/slope with unequal spacing), decision logic (every rule, missing
inputs → REVIEW), evaluation metrics (against hand-computed values).

Do not generate dozens of trivial tests. Every test must be able to fail for a real bug.

---

# 25. Documentation Standards

- Every doc starts with a status line: `Status: Draft | Proposed | Accepted | Superseded` and a last-updated date.
- Use the claim labels in §15 for research content.
- Cite sources by ID (R1–R4) with section/part, or by full reference.
- Record decisions as ADRs in `docs/decisions/`. Do not rewrite an accepted ADR; supersede it.
- When a result exists, link to the run directory / metrics file that produced it.

---

# 26. Git Hygiene

- Small, focused commits with imperative messages (`Add lot-relative robust z-score`).
- Work on branches; do not commit directly to `main` once collaboration starts.
- Never commit: secrets, credentials, large datasets, model binaries, generated
  artifacts, notebook outputs with large embedded data.
- `.gitignore` excludes data and artifacts except `.gitkeep` and READMEs.
- Every PR fills in `.github/pull_request_template.md` (integrity checklist).

---

# 27. Presentation Integrity

Every number in the SIH presentation must be traceable to an actual experiment run.
Every graph must come from actual data, and the data category (official /
external / synthetic) must be visible on the slide.
If something is not implemented, mark it **Proposed** or **Future Work**.
Never present simulated component behaviour as real ISRO hardware data.

---

# 28. Change Management

Before modifying existing code or docs:

1. Inspect it.
2. Understand dependencies.
3. Identify affected components.
4. Make the smallest necessary change.
5. Run relevant tests.
6. Report what changed.
7. Check whether the change makes any existing files obsolete or redundant.
8. Delete unnecessary files and update affected references.

Do not rewrite unrelated code.

Do not leave obsolete files merely because they were previously generated.

---

# 29. Development Priority

P0 Research and requirements  (done 2026-09-26)
P1 Dataset strategy and data validation  (done 2026-09-26)
P2 Baselines  (done 2026-09-26; P2–P7 authorised together, one layer per change)
P3 Lot-relative and trajectory analysis  (done 2026-09-26)
P4 168h prediction  (done 2026-09-26)
P5 Uncertainty and risk engine  (done 2026-09-26)
P6 Explainability  (done 2026-09-26)
P7 Application/demo  (done 2026-09-26; deployable service 2026-09-28)
P8 Presentation  ← next (needs a team decision)

Do not skip directly to P7.

---

# 30. Definition of Done

A feature is complete only when:

- Code works
- Relevant tests pass
- Leakage has been considered
- Configuration is reproducible
- Results are recorded
- Documentation is updated
- Limitations are known
- Evidence supports its usefulness

"Code runs" is not sufficient.

---

# 31. Most Important Rule

Do not optimize for "How much code can be generated?"

Optimize for "How little code is required to produce reliable evidence?"

AgniDrishti must remain: Professional, Reproducible, Explainable,
Experiment-driven, Research-backed, Maintainable.

