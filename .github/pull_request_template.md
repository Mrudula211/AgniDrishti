## What and why

<!-- Which requirement (FR/NFR) and which experiment (E0–E6) does this serve? -->

## Integrity checklist

- [ ] No fabricated metrics; unmeasured values read "TBD — experiment not yet executed."
- [ ] Every reported number links to a recorded run (config, data version, seed, commit).
- [ ] Data category (official / external / synthetic) stated for every result.
- [ ] Leakage considered: lot-grouped split, checkpoint feature availability, no `value_168h` in early features.
- [ ] No hard-coded absolute paths, thresholds or magic numbers (config instead).
- [ ] Tests added/updated for new logic, and they pass.
- [ ] No new dependency, or its necessity is explained below.
- [ ] Docs updated (requirements, experiment plan, claim register if claims changed).
- [ ] No unsupported claims (novelty, compliance, "guarantees", probabilities).
