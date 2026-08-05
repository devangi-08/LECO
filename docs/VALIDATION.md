# Validation — Scoring the Engine Against Designed Ground Truth

Every pattern in LECO's five synthetic students was put there on purpose. That makes this prototype scoreable in a way most solo projects are not: the design spec says what should be found, the generator says what was actually encoded, the data says what survived noise, and the engine says what it detected. This chapter runs that four-link chain end to end and reports every result, including the misses.

**Provenance.** `student_response_generator.py` (seed 42) regenerates `student_responses.csv` **byte-identically** — 1,637/1,637 rows match on every field. The engine outputs scored here were reproduced from that same CSV and match the archived Colab run exactly. Nothing in this chapter is scored against a moving target.

## Method

Each expectation from the profile spec sheets became one row in a machine-readable manifest (61 rows). Each row is checked twice: once against the *realized data* (did the plant survive generation noise?) and once against the *engine output* (did the feature fire?). The two checks are independent, which is what separates engine failures from generator failures.

| Verdict | Meaning |
|---|---|
| DETECTED | Planted, survived generation, engine flagged it |
| PARTIAL | Engine flagged a weaker or adjacent form |
| MISSED | Plant is present in the realized data; engine did not flag it |
| NOT_MATERIALIZED | Plant exists in spec and code, but noise or censoring erased/inverted it — engine excused |
| NOT_IMPLEMENTED | Plant exists in the spec only; the generator never coded it — engine excused |
| CLEAN | Spec said "none expected" and the engine flagged nothing |
| EMERGENT | Spec said "none expected"; the engine flagged something that *is* supported by the realized data |
| N/V | Not verifiable from stored data |

Conventions: momentum windows mirror the spec (tests 1–10 vs 11–15); a streak counts as materialized at |Δ| ≥ 10pp with ≥3 attempts per window; a confidence plant counts as materialized at topic level when |conf/3 − accuracy| ≥ 0.20 with n ≥ 3 (the engine's own gap constant); nodes map to topics by modal question-topic. Engine constants cited from code: F5 fires only when attempts ≥ 5, gap > 0.20, accuracy < 0.60, and avg confidence ≥ 2.0.

## Scoreboard

Of **48 testable expectations**, the engine cleanly satisfied **19** (DETECTED + CLEAN), partially satisfied **6**, and **missed 18**. **5** "none expected" rows drew flags that the data genuinely supports. Outside the testable set, **5** plants never survived generation, **5** were specified but never coded, and **3** cannot be checked from stored data.

| Student | DETECTED | PARTIAL | MISSED | NOT_MATERIALIZED | NOT_IMPLEMENTED | CLEAN | EMERGENT | N/V |
|---|---|---|---|---|---|---|---|---|
| PRIYA | 1 | 1 | 6 | 3 | 2 | · | · | · |
| ARJUN | 3 | 1 | 3 | · | · | 1 | 2 | 1 |
| MEERA | 2 | 3 | 2 | · | · | 1 | 2 | · |
| RAHUL | 2 | 1 | 3 | · | · | 2 | 1 | 2 |
| KAVYA | 7 | · | 4 | 2 | 3 | · | · | · |

Read the two Kavya lines first: she was designed as the stress test, and she is where the engine earned the most (7 clean detections, including both MCQ-hacker plants and the Limits cold streak) and where its sharpest architectural blind spot shows (two of three overconfidence plants missed — see Finding 3).

## What the engine got right

The detections that matter most are the ones that required the engine to disagree with surface impressions. It ranked Kavya's recoverable marks highest of all five students (22 vs 11, 11, 9, 7) — exactly the designed "terrible time allocation" story. It produced **zero** foundational hypotheses for Arjun, correctly reading polarization as breadth-of-study rather than a hidden skill gap, while banking his exact five strong topics into Phase 1 (5/5). It held Rahul to a single displayed hypothesis (`top_1`) despite generating 24 internally — display discipline working as designed. It caught Priya's Vector Algebra collapse and Kavya's Limits collapse as cold streaks, confined Meera's weak nodes to the planted Coordinate-Geometry cluster and surfaced F002 for her, read Kavya's Limits-as-prerequisite as `fine` (baseline-aware, not lifetime-fooled), and its F6 MCQ-reliability guard had real work to do: both hacker plants materialized hard (Indefinite Integrals MCQ 100% vs Numerical 0%).

## Five findings, with mechanisms

**Finding 1 — The censoring paradox: the generator's skip strategy erased its own plants.** Priya is scripted to skip her weakest topics. Her overconfidence plant lives on Complex Numbers (conf 2.7, acc ~31%) — a weak topic — so she attempted it **zero times in fifteen tests**. The same censoring gutted her flagship F001 plant: two of five dependent topics have n = 0 (Application of Derivatives, Differential Equations) and one has n = 2 (Probability). The engine's "wrong" answer — F038 as strong hypothesis — is the *data-faithful* answer: its visible dependents (Straight Lines 38%, Parabola 17%, P&C 33%) really are weak. Design lesson for any future generator: an overconfident persona must *attempt* the topics she is deluded about; skip-by-accuracy contradicts the psychology it is meant to encode.

**Finding 2 — Plant survival under noise is a coin flip at this sample size.** Per-test ±10% accuracy noise, a 5% answer flip, and difficulty interaction sit on top of ~15–20 attempts per topic. Of the four momentum plants, two survived (Priya VA −24pp, Kavya Limits −25pp) and two died: Priya's Definite Integration *hot* plant inverted into an 87%→13% observed *collapse* (small-n luck early, censoring, bad draws late), and Kavya's DI hot plant flattened to 31%→25%. The engine tracked the realized data correctly in all four cases. A separate casualty: Meera's Quadratic plant (72→75%) realized at **33%** — an improbable flip cluster — which is why her Circle prerequisite trace read `also_weak`. The uncomfortable arithmetic: a +17–25pp designed swing is roughly the same magnitude as the noise envelope.

**Finding 3 — Granularity mismatch: topic-level plants, node-level gates.** Kavya's Matrices overconfidence (conf 2.8, planted acc 38%) materialized clearly at topic level (26 attempts, realized acc 54%, gap +0.36). The engine still missed it, mechanically: those 26 attempts fragment across **10 nodes**; the two nodes with n ≥ 5 drifted to 60% and 67% accuracy — above F5's 0.60 accuracy ceiling — and the one node at 0% accuracy had only 3 attempts, below the n ≥ 5 floor. Binomial missed the same way. Straight Lines was caught only because a single node (Triangle Center Extraction) happened to accumulate 5 attempts at 40%. The fix is architectural, not a threshold nudge: F5 needs a topic-level companion check, or node evidence pooling.

**Finding 4 — The policy layer diverges from design intent even when detection succeeds.** F17/F18 disagreed with the spec's priority in four of five students, all resolving to Quadratic Equations or Functions: the priority formula's "unlocks N weak topics" component dominates every other signal. Rahul's case is stricter: the spec's Change-3 proximity-to-win override (global acc < 35% → recommend the nearest win) **does not exist in the engine** — zero matches in code — so his plan leads with Functions instead of Statistics even though F14 and F18-adjacent logic know Statistics is his banked topic. F16's stability gate is erratic at n≈5 windows: Priya's two designed maintenance topics both read `not_yet_safe` (std ≈ 0.40), Rahul got one maintenance topic where the spec expected zero, and Kavya's grant of Sequences + Vector Algebra (std 0.00) is data-faithful but spec-divergent. None of these are detection failures; all are calibration decisions this validation now makes visible and arguable.

**Finding 5 — The spec-vs-code drift ledger.** Five designed behaviors were never implemented: Priya's scripted latest-test (tragic blanks, 14-minute slow-wrong block), Kavya's scripted time-waste and her recency-based F6 suppression signal, the per-test stretch-question setup, and — most consequentially — **Rule 5**. The generator's docstring claims error-type tendencies are "encoded via which questions are wrong"; the code never references error tags when drawing correctness. Student-level error behavior therefore does not exist in this dataset, which is why F4's dominant-mode expectations (Priya "Setup ~35%" vs engine "Concept 32%") and both F9 weak-signal expectations are scored N/V or NOT_IMPLEMENTED rather than MISSED: the schema cannot express what the spec asked the engine to find. Any future generator must select *which* questions a student gets wrong using the error taxonomy, not just how many.

## Emergent flags and the horoscope metric

The project's recurring fear was the horoscope effect — an engine that finds patterns everywhere. Two numbers bound it. Upstream, F10 over-generates on weak students: 24 hypotheses for Rahul and 17 for Kavya against 0 planted, versus 0 for Arjun, 1 excess for Priya, 4 for Meera — hypothesis count tracks weakness breadth, not truth. Downstream, display gating contains it (Rahul sees exactly one). The census also shows F11 naming 7–11 streak topics per student where 0–2 were planted; audit of all 44 streak states found every window had ≥4 attempts and real ≥10pp swings — these are *noise-real* patterns, honestly detected, which is precisely why streak language reaching a student should be conservative.

| Student | F5 flags | F5 outside plant | F6 flags | Streak topics | Streaks outside plant | F10 hypotheses | F10 planted | F10 excess |
|---|---|---|---|---|---|---|---|---|
| PRIYA | 3 | 2 | 2 | 9 | 7 | 2 | 1 | 1 |
| ARJUN | 1 | 1 | 0 | 8 | 8 | 0 | 0 | 0 |
| MEERA | 2 | 2 | 0 | 11 | 11 | 5 | 1 | 4 |
| RAHUL | 0 | 0 | 0 | 7 | 7 | 24 | 0 | 24 |
| KAVYA | 2 | 1 | 0 | 9 | 8 | 17 | 0 | 17 |


## What this validation cannot establish

It cannot break the circularity of synthetic data: the engine was scored on patterns whose encoding conventions it shares. It does not calibrate thresholds — it *nominates* miscalibration candidates (the 0.60 F5 ceiling, the F16 std gate, the F17 unlock weight, the absent Change-3 override) but five students on one seed cannot set values. It says nothing about real students, real confidence self-reports, or real error behavior — the one question a first pilot must answer remains whether an F10 hypothesis survives contact with a student actually attempting its diagnostic question.

## Appendix — all 61 rows

| ID | Student | Feature | Planted / expected | Materialized in data | Engine detected | Verdict | Note |
|---|---|---|---|---|---|---|---|
| P1 | PRIYA | F5 | Overconfident Complex Numbers (spec conf 2.7, acc ~31%) | 0 attempts in 15 tests — plant censored by skip strategy | no signal possible | NOT_MATERIALIZED | skip-by-accuracy removed every observation of this plant |
| P2 | PRIYA | F11 | cold_streak Vector Algebra (72->48) | 77%->60% (-17%) | cold_streak | DETECTED |  |
| P3 | PRIYA | F11 | hot_streak Definite Integration (25->42) | 83%->30% (-53%) — plant inverted/erased by noise+skip-censoring | cold_streak | NOT_MATERIALIZED |  |
| P4 | PRIYA | F10 | F001 translating constraints to equations (strong_hypothesis) | 1/5 dependents weak: Straight Lines And Pair Of Straight Lines | absent; engine top: F038(str), F002(mod) | NOT_MATERIALIZED |  |
| P5 | PRIYA | F14 | Phase 1 ⊇ Sequences, Statistics, Sets, Quadratic | — | phase_1=['Functions', 'Sequences And Series', 'Statistics', 'Vector Algebra'] | PARTIAL | 2/4 present |
| P6 | PRIYA | F16 | Maintenance: Sequences, Statistics; Sets volatile | — | maintenance=[]; Sets status=not_yet_safe | MISSED |  |
| P7 | PRIYA | F17 | Priority 1: Limits…, P2: Functions | — | top2=['Quadratic Equation And Inequalities', 'Straight Lines And Pair Of Straigh | MISSED |  |
| P8 | PRIYA | F18 | Question from Limits | — | topic=Quadratic Equation And Inequalities | MISSED |  |
| P9a | PRIYA | F9 | Limits→Definite Int confirmed | — | absent | MISSED |  |
| P9b | PRIYA | F9 | Limits→Application  confirmed | — | absent | MISSED |  |
| P10 | PRIYA | F7 | Drop-off at Build Then Solve | — | None | MISSED |  |
| P11 | PRIYA | F4 | Dominant: Setup Gap ~35% | error mix not encoded by generator | Concept Gap 32.1% | NOT_IMPLEMENTED | generator draws is_correct from accuracy only; per-student error tendency (Rule 5) never coded — docstring cla |
| P12 | PRIYA | F15/F8 | Scripted latest-test: 3 blanks incl. Sequences tragic; 14min slow+wrong on Complex/Prob | not in generator | — | NOT_IMPLEMENTED | skip selection is strategy-based, no per-test script |
| A1 | ARJUN | F5 | None expected (calibrated low conf on weak topics) | noise-made gaps exist | 1 flags: {'Sets And Relations': 1} | EMERGENT | all flags are data-supported (engine is deterministic); excess vs design intent |
| A2 | ARJUN | F6 | None expected (high conf matches strong topics) | — | 0 flags | CLEAN |  |
| A3 | ARJUN | F10 | Should NOT trigger strongly (weak_hypothesis at most) | breadth gap, prereqs also weak | 0 hyps; tiers=Counter() | DETECTED | spec: polarization ≠ foundational gap |
| A4 | ARJUN | F11 | No hot/cold streaks expected | noise created real drifts | 8: Sets And Relations:hot_(+24%); Functions:hot_(+20%); Quadratic Equation And I | EMERGENT | small-n noise reads as streaks |
| A5 | ARJUN | F14 | Phase 1 = his 5 banked topics | — | phase_1=['3D Geometry', 'Functions', 'Matrices And Determinants', 'Sequences And | DETECTED | 5/5 |
| A6 | ARJUN | F16 | Maintenance: the same 5 topics | — | 1: ['Functions'] | MISSED | 0/5 |
| A7 | ARJUN | F17 | P1 Binomial Theorem, P2 Straight Lines | — | top2=['Quadratic Equation And Inequalities', 'Logarithm'] | MISSED |  |
| A8 | ARJUN | F18 | Question from Binomial Theorem | — | Quadratic Equation And Inequalities | MISSED |  |
| A9 | ARJUN | F9 | Traces mostly weak_signal (concept, not prereq) | student-level error behavior not encodable in schema | 0/8 weak_signal | N/V | same data-layer root as P11: error types are question tags, not student behavior |
| A10 | ARJUN | F7 | Steep drop-off at Build Then Solve | — | Formula with Judgment | PARTIAL |  |
| A11 | ARJUN | struct | Polarization: ~5 topics ≥85%, ~10 topics ≤25% (data-level) | 5 topics ≥80% / 2 topics ≤25% (n≥6) | — | DETECTED | smart-skipping censors weak topics: few reach n≥6, so the ≤25% tail is under-observed by design |
| M1 | MEERA | F1 | Weak nodes only in Coord-Geo cluster + Probability | — | in-cluster topics hit: ['Circle', 'Ellipse', 'Hyperbola', 'Parabola', 'Probabili | DETECTED | outside e.g. ['Application Of Derivatives', 'Area Under The Curves', 'Differential Equations'] |
| M2 | MEERA | F10 | F002 locus by parameter elimination (strong_hypothesis) | 4/6 dependents weak: Circle, Parabola, Ellipse | F002 as moderate_hypothesis (rank 2/5) | PARTIAL |  |
| M3 | MEERA | F5 | None expected (well calibrated) | noise-made gaps exist | 2 flags: {'Matrices And Determinants': 1, 'Differential Equations': 1} | EMERGENT | all flags are data-supported (engine is deterministic); excess vs design intent |
| M4 | MEERA | F6 | Possibly Area Under Curves (58%, conf 1.8) | acc 60%, conf 1.5, n=15 | 0 flags | CLEAN | spec marked 'possibly' — soft expectation |
| M5 | MEERA | F11 | No hot/cold streaks expected | noise created real drifts | 11: Permutations And Combinations:hot_(+44%); Vector Algebra:hot_(+31%); Limits  | EMERGENT | small-n noise reads as streaks |
| M6 | MEERA | F16 | 8–10 maintenance topics | — | 4: ['Permutations And Combinations', 'Sets And Relations', 'Statistics', 'Vector | MISSED |  |
| M7 | MEERA | F14 | Huge Phase 1 (12+) | — | 16 topics | DETECTED |  |
| M8 | MEERA | F17 | P1 Circle (or F002 practice) | — | top2=['Quadratic Equation And Inequalities', 'Circle'] | PARTIAL |  |
| M9 | MEERA | F18 | Question from Circle/Parabola (locus) | — | Quadratic Equation And Inequalities | MISSED |  |
| M10 | MEERA | F9 | Circle's prereqs read 'fine' (problem is coord-geo itself) | prereq topics strong in data | ['fine', 'also_weak', 'also_weak'] | PARTIAL |  |
| R1 | RAHUL | F5 | None expected (confidence already low) | — | 0 flags | CLEAN |  |
| R2 | RAHUL | F6 | None expected (nothing secretly strong) | — | 0 flags | CLEAN |  |
| R3 | RAHUL | F10 | Global acc <35–40% → display top-1 only | global acc 34.7% | display=top_1, 24 hyps generated | DETECTED | 24 hypotheses generated but suppressed to 1 — over-generation vs display discipline |
| R4 | RAHUL | F11 | No hot/cold streaks expected | noise created real drifts | 7: Sets And Relations:hot_(+46%); Statistics:hot_(+43%); Binomial Theorem:hot_(+ | EMERGENT | small-n noise reads as streaks |
| R5 | RAHUL | F14 | Phase 1: Statistics only | — | phase_1=['Logarithm', 'Statistics'] | PARTIAL |  |
| R6 | RAHUL | F16 | Zero maintenance topics | — | 1: ['Statistics'] | MISSED |  |
| R7 | RAHUL | F17 | P1 Statistics (proximity-to-win override) | Statistics best at ~58% | top2=['Functions', 'Straight Lines And Pair Of Straight Lines'] | MISSED |  |
| R8 | RAHUL | F18 | Question from Statistics, micro-goal | — | Functions / goal: Get 4 right instead of your usual 3 (out | MISSED |  |
| R9 | RAHUL | F7 | Drop-off everywhere (even Direct App ~45%) | — | Direct Application to Formula with Judgment | DETECTED |  |
| R10 | RAHUL | F9 | Multiple traces, mostly weak_signal | student-level error behavior not encodable in schema | 4/44 weak_signal | N/V | same data-layer root as P11 |
| R11 | RAHUL | struct | Panic tail (Rule 8): fast wrong answers in last 5 slots | question order not stored in CSVs | — | N/V | panic is coded but position is unrecoverable post-hoc |
| K1 | KAVYA | F5 | Overconfident Matrices And Determinants (spec conf 2.8, acc 38%) | conf 2.7, acc 55%, n=22 (gap +0.35) | none | MISSED |  |
| K2 | KAVYA | F5 | Overconfident Straight Lines And Pair Of Straight Lines (spec conf 2.6, acc 35%) | conf 2.6, acc 15%, n=13 (gap +0.72) | 1 node(s): Triangle Center Extraction | DETECTED |  |
| K3 | KAVYA | F5 | Overconfident Binomial Theorem (spec conf 2.5, acc 35%) | conf 2.6, acc 29%, n=14 (gap +0.57) | none | MISSED |  |
| K4 | KAVYA | F6 | Underconfident Vector Algebra (spec conf 1.5, acc 75%) | conf 1.7, acc 71%, n=14 (gap +0.14) | none | NOT_MATERIALIZED |  |
| K5 | KAVYA | F6 | Sequences underconf but suppressed by recency (last-2-test conf 2.5 design) | conf constant 1.5 in code — suppression signal never generated | — | NOT_IMPLEMENTED | recency-suppression design present in spec, absent in generator |
| K6 | KAVYA | F11 | hot_streak Definite Integration (20->45) | 31%->29% (-2%) — plant inverted/erased by noise+skip-censoring | stagnant | NOT_MATERIALIZED |  |
| K7 | KAVYA | F11 | cold_streak Limits Continuity And Differentiability (65->40) | 83%->38% (-46%) | cold_streak | DETECTED |  |
| K8a | KAVYA | F6-MCQ | MCQ-hacker Indefinite Integrals (II 65/8) | MCQ 100% vs Num 0% (n=10) | engine has MCQ-reliability guard in F6; no dedicated hacker flag | DETECTED | materialized in data; engine can only demote F6 flags, cannot surface hacking — capability gap |
| K8b | KAVYA | F6-MCQ | MCQ-hacker Quadratic Equation A (QE 75/20) | MCQ 67% vs Num 25% (n=14) | engine has MCQ-reliability guard in F6; no dedicated hacker flag | DETECTED | materialized in data; engine can only demote F6 flags, cannot surface hacking — capability gap |
| K9 | KAVYA | F8 | 1 stretch question on latest test | not scripted (see P12-type gap) | 0 stretch | NOT_IMPLEMENTED |  |
| K10 | KAVYA | F9 | Limits as prereq reads 'fine' (baseline was 65%) | — | ['fine', 'fine'] | DETECTED | engine uses lifetime topic acc; realized LCD lifetime ~48% may read weak — threshold-sensitivity case |
| K11 | KAVYA | F16 | Maintenance: Statistics only | — | ['Sequences And Series', 'Vector Algebra'] | MISSED | engine grant of Seq+VA is data-faithful (last-5 std 0.00); spec's recency-conf design never coded |
| K12 | KAVYA | F17 | P1 Limits (cold-streak refresh) | — | top2=['Functions', 'Quadratic Equation And Inequalities'] | MISSED |  |
| K13 | KAVYA | F15 | Recoverable marks highest of all students | aggressive attempts + panic in data | KAVYA:22; MEERA:11; RAHUL:11; PRIYA:9; ARJUN:7 | DETECTED |  |
| K14 | KAVYA | F15/F4 | Scripted time-waste (17min slow+wrong, 2 Seq blanks, 2 rushed Binomial) | not in generator | — | NOT_IMPLEMENTED |  |
| K15 | KAVYA | F10 | Moderate trigger (messier than Priya) | — | 17 hyps; tiers=Counter({'strong_hypothesis': 9, 'moderate_hypothesis': 6, 'weak_ | DETECTED |  |

*Generated by `validation_scoring.py` against `detected_full.json`; both ship alongside this document. Reproduce with: run the engine notebook's feature cell on `student_responses.csv`, then `python validation_scoring.py`.*
