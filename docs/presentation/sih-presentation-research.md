# SIH Presentation Research

Status: Draft · Last updated: 2026-09-26

Labels: **OFFICIAL** (S-16 guidelines / S-17 template / R0) · **OBSERVED** (secondary source; low reliability) · **RECOMMENDATION** (ours).

## 1. Official requirements — idea stage (due 30 Sep 2026)

| # | Requirement | Source |
|---|---|---|
| O-1 | Idea presentation uploaded as **PDF only** ("No PPT, Word Doc or any other format will be supported") | S-17 slide 7 |
| O-2 | **Maximum 6 slides including the title slide** | S-17 slide 7 |
| O-3 | Use the provided template **without changing the idea detail pointers** | S-17 slide 7 |
| O-4 | Slide headings: (1) Title page (PS ID, PS title, theme, category, team ID, team name); (2) Idea title — proposed solution, how it addresses the problem, innovation and uniqueness; (3) Technical approach — technologies, methodology (flow charts / images / working prototype); (4) Feasibility and viability — feasibility, challenges and risks, strategies; (5) Impact and benefits; (6) Research and references | S-17 slides 1–6 |
| O-5 | "Try to avoid paragraphs … points / diagrams / infographics / pictures"; "precise and easy to understand"; "Idea should be unique and novel" | S-17 slide 7 |
| O-6 | Portal fields: idea title, idea description, idea presentation (PDF); max 2 PSs per team; 500-idea cap per PS (31/500 at R0 retrieval) | S-16 p. 10–11; R0 |
| O-7 | Deadline for team nomination and idea submission: **30 Sep 2026**; "No request will be entertained after the deadline" | S-16 p. 10 |
| O-8 | Idea selection criteria: "novelty of the idea, complexity, clarity and details in the prescribed format, feasibility, practicability, sustainability, scale of impact, user experience and potential for future work progression" | S-16 p. 13 (confirms claim D-17 for 2026) |
| O-9 | 4–5 teams per PS may reach the Grand Finale; the PS organisation "isn't obligated to declare a winner unless student proposals meet their expectations" | S-16 p. 12, 18 |
| O-10 | Grand Finale offline at nodal centres, proposed December 2026; mentors help build "a working prototype" | S-16 p. 13–15 |
| O-11 | Ideas "must be new and must not have been present in any previous event/program" | S-16 p. 17 |
| O-12 | PS-specific evaluation: Anomaly Detection Score, MAE on Value_168h, Explainability | R0 |

Not found officially: finale judging rubric for 2026, demo rules, a video
requirement for idea submission (a secondary blog mentions a video; not in S-16/S-17).

## 2. Observed patterns (secondary / weak evidence)

| # | Observation | Source | Reliability |
|---|---|---|---|
| P-1 | SIH 2025 software finale ran as a 36-hour hackathon at ~60 nodal centres | News article (hybiz.tv) | Low–medium |
| P-2 | Public SIH26170 team repositories already implement lot-relative PAT outliers + 24h→168h prediction + a percentile safety slope | Search-result snippets; repositories not opened | Low; shows the basic Module A/B pipeline is **common**, not distinctive |
| P-3 | Past winners' decks are not officially published; only blog posts and college notices exist | Search 2026-09-26 | — |

We found **no** reliable evidence for claims like "winners always do X"; none are made here.

## 3. What judges are likely to question (derived from O-8, O-12, prior art)

| Criterion (O-8 / O-12) | Likely question | Where we answer |
|---|---|---|
| Novelty | "DPAT and drift limits already exist — what's new?" | novelty-boundaries §2 (prediction at 24h + allowance + interval + review) |
| Complexity / technical depth | "Is this just a z-score?" | Why simple is correct for 2–4 points; ablation plan |
| Feasibility | "Where is your data?" | Dataset categories; synthetic design; NASA methodology check |
| Practicability | "How does a QA engineer use it?" | decision-flow; evidence card |
| Anomaly Detection Score | "How do you avoid escapes?" | REVIEW + conservative binary mapping |
| MAE | "What MAE do you get?" | Idea stage: **TBD — experiment not yet executed**; plan E4 |
| Explainability | "Show me why part X was rejected" | Evidence-card template |
| Future work | "Deployment at ISRO?" | Batch per lot, advisory, audit log (proposed) |

Full list: [judge-questions.md](judge-questions.md).

## 4. Recommendations

1. **Two decks, not one.** (a) the 6-slide idea PDF due 30 Sep 2026 — proposals
   and plan only, no results exist; (b) the finale deck from recorded
   experiments ([slide-plan.md](slide-plan.md)).
2. **Idea PDF mapping to the fixed template** — built 2026-09-26 after team
   approval (Decision 2): text in [idea-submission-content.md](idea-submission-content.md),
   deck in [sih2026-idea-agnidrishti.pptx](sih2026-idea-agnidrishti.pptx):

   | Template slide | Content |
   |---|---|
   | 2 Idea | Static limits vs lot + drift; PS modules A/B; REVIEW state; innovation stated as "proposed integration" (novelty-boundaries §2) |
   | 3 Technical approach | Pipeline diagram; T24 Module B; robust lot statistics (AEC-style); drift allowance (ESCC-style); prediction interval; Python stack (proposed) |
   | 4 Feasibility | No official data → synthetic + NASA; leakage-safe lot splits; risks from drawbacks-and-risks |
   | 5 Impact | Fewer escapes, earlier decisions, auditable — all as **aims**, no numbers |
   | 6 References | S-01, S-02, S-04, S-05, S-06, S-10, S-11, S-13, NASA datasets |

3. Never put a performance number in the idea PDF; write the experiment that
   will measure it.
4. Show the data category on every future chart (CLAUDE §27).
5. Ask organisers the GAP-01/03/05/10 questions early (sih@aicte-india.org).
