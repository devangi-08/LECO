# Student Profile Spec Sheets — JEE Diagnostic Engine
## 5 Synthetic Profiles for Prototype Demonstration

---

## Global Baselines

These are the reference standards all students are compared against.

| Metric | Global Value | Notes |
|---|---|---|
| Average accuracy | 50% | Median JEE aspirant |
| Average net marks per test | ~40/100 | 25 questions × JEE scoring |
| Average confidence | 2.0 / 3 | Neutral self-assessment |
| MCQ time baseline | 90 seconds | Global standard |
| Numerical time baseline | 120 seconds | Global standard |
| Tests per student | 15 | Baseline = T1-10, Current = T11-15 |
| Questions per test | 25 | ~1 per topic, some topics 0 or 2 |
| Total attempts per student | 375 | 15 × 25 |

### Topic Difficulty Tiers (for interpreting accuracy)

| Tier | Topics | "Average" accuracy |
|---|---|---|
| Easier | Statistics, Sets & Relations, Sequences & Series, Vector Algebra, Straight Lines | 55-65% |
| Medium | Binomial Theorem, P&C, Matrices, Quadratic Eq, Functions, Circle | 45-55% |
| Hard | 3D Geometry, Definite Integration, App of Derivatives, Limits, Complex Numbers, Probability, Differential Eq, Area Under Curves | 35-50% |
| Specialist | Ellipse, Hyperbola, Parabola, Inverse Trig, Indefinite Integrals | 30-45% |

---

## Student 1 — PRIYA

### Narrative
Priya is the "textbook average" student. 50% overall accuracy. She has clear strengths (Algebra, Series) and clear weaknesses (Calculus chain). Her biggest hidden problem is a foundational skill gap — she can't translate word problems into equations (F001), which causes failures across Application of Derivatives, Probability, and Differential Equations simultaneously. She's overconfident on Complex Numbers (thinks she gets it, doesn't). She's been improving on Definite Integration but regressing on Vector Algebra.

### Objectives served
- Objective 1: Exercises every feature
- Objective 4: Clean story ("your real problem is one foundational skill")

### Overall stats
| Metric | Value |
|---|---|
| Overall accuracy | 50% |
| Net marks (current avg) | ~38/100 |
| Average confidence | 2.0 |
| Dominant failure mode | Setup Gap (~35%) |

### Topic Accuracy Table

| Topic | Baseline (T1-10) | Current (T11-15) | Delta | Momentum | Confidence | Avg Time | Error Tendency |
|---|---|---|---|---|---|---|---|
| Sequences And Series | 78% | 80% | +2 | stable | 2.5 | 75s | Procedural |
| Statistics | 72% | 75% | +3 | stable | 2.3 | 70s | Procedural |
| Sets And Relations | 68% | 70% | +2 | stable | 2.0 | 80s | Procedural |
| Quadratic Eq And Ineq | 62% | 65% | +3 | stable | 2.2 | 85s | Procedural |
| Vector Algebra | 72% | 48% | -24 | cold_streak | 2.5 | 85s | Procedural |
| Matrices And Det | 55% | 58% | +3 | stable | 2.0 | 100s | Procedural |
| Binomial Theorem | 48% | 55% | +7 | stable | 2.0 | 95s | Procedural |
| Functions | 52% | 55% | +3 | stable | 1.8 | 90s | Setup |
| Straight Lines | 50% | 52% | +2 | stable | 2.0 | 95s | Setup |
| Permutations And Comb | 45% | 48% | +3 | stable | 2.0 | 100s | Setup |
| Complex Numbers | 30% | 32% | +2 | stagnant | 2.7 | 110s | Conceptual |
| 3D Geometry | 42% | 45% | +3 | stable | 1.8 | 115s | Setup |
| Circle | 40% | 42% | +2 | stagnant | 1.8 | 105s | Setup |
| Limits Cont And Diff | 35% | 38% | +3 | stagnant | 1.7 | 120s | Setup |
| Application Of Deriv | 28% | 30% | +2 | stagnant | 1.5 | 130s | Setup |
| Definite Integration | 25% | 42% | +17 | hot_streak | 1.5 | 125s | Setup |
| Probability | 30% | 32% | +2 | stagnant | 1.8 | 120s | Setup |
| Differential Equations | 28% | 30% | +2 | stagnant | 1.5 | 135s | Setup |
| Area Under Curves | 25% | 28% | +3 | stagnant | 1.5 | 130s | Setup |
| Parabola | 35% | 38% | +3 | stagnant | 1.8 | 110s | Setup |
| Ellipse | 32% | 35% | +3 | stagnant | 1.7 | 115s | Setup |
| Hyperbola | 30% | 30% | 0 | stagnant | 1.7 | 120s | Conceptual |
| Indefinite Integrals | 30% | 35% | +5 | stable | 1.5 | 125s | Setup |
| Inverse Trig Functions | 35% | 38% | +3 | stagnant | 1.8 | 110s | Conceptual |
| Differentiation | 45% | 48% | +3 | stable | 2.0 | 95s | Procedural |
| Trig Ratio And Ident | 50% | 52% | +2 | stable | 2.0 | 85s | Procedural |

### Feature Triggers (what should fire)

| Feature | Expected Output |
|---|---|
| F1 | Weak nodes in: Limits, App of Derivatives, Probability, Def Integration, Diff Eq, Area Under Curves, Complex Numbers |
| F3 | Recurring error: "Missed constraint in setup" across multiple topics |
| F4 | Dominant mode: Setup Gap (~35%), then Concept Gap (~25%) |
| F5 | Overconfident on Complex Numbers (conf 2.7, acc 31%) |
| F6 | None expected (no hidden strengths with low confidence) |
| F7 | Drop-off at "Build Then Solve" |
| F8 | Latest test: 1-2 unexpected slips (Vector Algebra), 3-4 focus areas (Calculus topics) |
| F9 | Limits → Definite Integration (confirmed, setup errors dominate). Limits → App of Derivatives (confirmed). |
| F10 | F001 "Translating constraints to equations" — strong hypothesis (App of Derivatives + Probability + Diff Eq all weak, all dependent) |
| F11 | Hot streak: Definite Integration (+17pp). Cold streak: Vector Algebra (-24pp). Multiple stagnant. |
| F14 | Phase 1: Sequences, Statistics, Sets, Quadratic. Phase 3: Complex, Limits, Probability. |
| F15 | Slow+Wrong bucket heavy on Calculus topics. Tragic miss if Vector Algebra question left blank. |
| F16 | Maintenance: Sequences, Statistics. Not yet safe: Sets & Relations (volatile). |
| F17 | Priority 1: Limits (prereq to 2 topics + stagnant). Priority 2: Functions (tipping point). |
| F18 | Question from Limits topic. |

### Unattempted pattern (latest test)
Leave 3 questions blank: 1 from Sequences (tragic miss), 1 from Hyperbola (good skip), 1 from Differential Eq (borderline).

### Time waste pattern (latest test)
Spend 4+ minutes each on 3 Complex Numbers and Probability questions, all wrong. Total: ~14 min of Slow+Wrong.

---

## Student 2 — ARJUN

### Narrative
Arjun is the "polarized" student. Same 50% overall as Priya, completely different profile. He's exceptional at 5-6 topics (85%+) and terrible at 5-6 topics (15-25%). Nothing in between. His exam strategy is radically different from Priya's: he should spend 70% of his time on his strong topics (banking marks) and skip his weak ones entirely. His problem isn't a foundational skill gap — he simply hasn't studied half the syllabus deeply enough.

### Objectives served
- Objective 2: Same score as Priya, completely different diagnosis
- Objective 4: Contrast narrative ("two students, same score, different plans")

### Overall stats
| Metric | Value |
|---|---|
| Overall accuracy | 50% |
| Net marks (current avg) | ~38/100 |
| Average confidence | 2.1 |
| Dominant failure mode | Concept Gap (~45%) |

### Topic Accuracy Table

| Topic | Baseline (T1-10) | Current (T11-15) | Delta | Momentum | Confidence | Avg Time | Error Tendency |
|---|---|---|---|---|---|---|---|
| Matrices And Det | 88% | 90% | +2 | stable | 2.8 | 70s | Procedural |
| 3D Geometry | 85% | 88% | +3 | stable | 2.8 | 75s | Procedural |
| Vector Algebra | 82% | 85% | +3 | stable | 2.7 | 72s | Procedural |
| Sequences And Series | 80% | 82% | +2 | stable | 2.5 | 78s | Procedural |
| Statistics | 78% | 80% | +2 | stable | 2.5 | 72s | Procedural |
| Binomial Theorem | 55% | 60% | +5 | stable | 2.2 | 95s | Procedural |
| Straight Lines | 50% | 52% | +2 | stable | 2.0 | 90s | Setup |
| Quadratic Eq And Ineq | 48% | 50% | +2 | stable | 2.0 | 95s | Setup |
| Functions | 42% | 45% | +3 | stable | 1.8 | 100s | Setup |
| Permutations And Comb | 38% | 40% | +2 | stagnant | 1.8 | 105s | Conceptual |
| Complex Numbers | 22% | 25% | +3 | stagnant | 1.3 | 140s | Conceptual |
| Definite Integration | 18% | 20% | +2 | stagnant | 1.2 | 150s | Conceptual |
| Probability | 18% | 20% | +2 | stagnant | 1.3 | 145s | Conceptual |
| Application Of Deriv | 15% | 18% | +3 | stagnant | 1.2 | 155s | Conceptual |
| Limits Cont And Diff | 15% | 18% | +3 | stagnant | 1.2 | 150s | Conceptual |
| Differential Equations | 15% | 15% | 0 | stagnant | 1.0 | 160s | Conceptual |
| Area Under Curves | 12% | 15% | +3 | stagnant | 1.0 | 155s | Conceptual |
| Circle | 20% | 22% | +2 | stagnant | 1.3 | 130s | Conceptual |
| Parabola | 18% | 20% | +2 | stagnant | 1.2 | 140s | Setup |
| Ellipse | 15% | 18% | +3 | stagnant | 1.0 | 145s | Conceptual |
| Hyperbola | 12% | 15% | +3 | stagnant | 1.0 | 150s | Conceptual |
| Inverse Trig Functions | 20% | 22% | +2 | stagnant | 1.3 | 125s | Conceptual |
| Indefinite Integrals | 15% | 18% | +3 | stagnant | 1.0 | 150s | Conceptual |
| Differentiation | 20% | 22% | +2 | stagnant | 1.3 | 130s | Conceptual |
| Trig Ratio And Ident | 25% | 28% | +3 | stagnant | 1.5 | 120s | Conceptual |
| Sets And Relations | 55% | 58% | +3 | stable | 2.2 | 85s | Procedural |

### Feature Triggers

| Feature | Expected Output |
|---|---|
| F1 | Many weak nodes — but the story is topic-level, not node-level |
| F4 | Dominant mode: Concept Gap (45%) — he hasn't studied these topics |
| F5 | None — he's calibrated (low confidence where low accuracy) |
| F6 | None — his strong topics have matching high confidence |
| F7 | Steep drop-off at "Build Then Solve" (his weak topics are all high-demand) |
| F9 | Multiple prereq traces BUT mostly weak_signal (errors are Conceptual, not Setup — he hasn't learned the topics, not a prereq issue) |
| F10 | Should NOT trigger strongly — his weakness is breadth of study, not a foundational skill gap. If it triggers, confidence should be weak_hypothesis |
| F11 | No hot/cold streaks — everything is flat. Strong topics stable, weak topics stagnant. |
| F14 | Phase 1: 5 topics (Matrices, 3D, Vector, Sequences, Statistics). Phase 3/Skip: 10+ topics. Huge contrast with Priya. |
| F15 | Massive Slow+Wrong bucket — he spends time on topics he can't do. Biggest strategic gain is skipping. |
| F16 | Maintenance: Matrices, 3D Geometry, Vector Algebra, Sequences, Statistics (5 topics!) |
| F17 | Priority 1: Binomial Theorem (tipping point at 60%, almost Phase 1). Priority 2: Straight Lines. |
| F18 | Question from Binomial Theorem. |

### The demo contrast with Priya
Both score 50%. Priya's report says "fix one foundational skill and 3 topics unlock." Arjun's report says "you're brilliant at half the syllabus, study the other half — start with Binomial Theorem because it's closest to becoming a strength." Same score, completely different action plans.

---

## Student 3 — MEERA

### Narrative
Meera is the "almost there" student. 65% overall — above average. Strong everywhere except Coordinate Geometry (Circle, Parabola, Ellipse, Hyperbola) and Probability. Her report should be short and focused: "You're close to 80+. Fix these 2 problem areas." Most topics are in maintenance mode. Her F10 should trigger F002 "Setting up locus equations by parameter elimination" — because Circle, Parabola, Ellipse, and Hyperbola all depend on it, and she's weak at all four.

### Objectives served
- Objective 4: Shows system adds value for strong students too
- Objective 1: Tests maintenance mode at scale

### Overall stats
| Metric | Value |
|---|---|
| Overall accuracy | 65% |
| Net marks (current avg) | ~55/100 |
| Average confidence | 2.3 |
| Dominant failure mode | Setup Gap (~40%) |

### Topic Accuracy Table

| Topic | Baseline (T1-10) | Current (T11-15) | Delta | Momentum | Confidence | Avg Time | Error Tendency |
|---|---|---|---|---|---|---|---|
| Statistics | 85% | 88% | +3 | stable | 2.8 | 65s | Procedural |
| Sequences And Series | 82% | 85% | +3 | stable | 2.7 | 70s | Procedural |
| Sets And Relations | 80% | 82% | +2 | stable | 2.5 | 72s | Procedural |
| Vector Algebra | 78% | 80% | +2 | stable | 2.5 | 75s | Procedural |
| Matrices And Det | 75% | 78% | +3 | stable | 2.5 | 78s | Procedural |
| Quadratic Eq And Ineq | 72% | 75% | +3 | stable | 2.3 | 80s | Procedural |
| Binomial Theorem | 70% | 72% | +2 | stable | 2.3 | 82s | Procedural |
| Straight Lines | 68% | 70% | +2 | stable | 2.2 | 80s | Procedural |
| Functions | 68% | 70% | +2 | stable | 2.2 | 85s | Procedural |
| 3D Geometry | 65% | 68% | +3 | stable | 2.2 | 88s | Procedural |
| Permutations And Comb | 65% | 68% | +3 | stable | 2.2 | 85s | Procedural |
| Definite Integration | 62% | 65% | +3 | stable | 2.0 | 90s | Procedural |
| Application Of Deriv | 60% | 65% | +5 | stable | 2.0 | 92s | Setup |
| Limits Cont And Diff | 62% | 65% | +3 | stable | 2.0 | 88s | Procedural |
| Differential Equations | 58% | 62% | +4 | stable | 2.0 | 95s | Setup |
| Differentiation | 65% | 68% | +3 | stable | 2.2 | 82s | Procedural |
| Trig Ratio And Ident | 62% | 65% | +3 | stable | 2.0 | 80s | Procedural |
| Area Under Curves | 55% | 58% | +3 | stable | 1.8 | 95s | Setup |
| Indefinite Integrals | 58% | 60% | +2 | stable | 2.0 | 90s | Setup |
| Inverse Trig Functions | 55% | 58% | +3 | stable | 1.8 | 92s | Conceptual |
| Complex Numbers | 55% | 58% | +3 | stable | 2.0 | 90s | Setup |
| Probability | 32% | 35% | +3 | stagnant | 1.5 | 125s | Setup |
| Circle | 30% | 32% | +2 | stagnant | 1.5 | 120s | Setup |
| Parabola | 28% | 30% | +2 | stagnant | 1.5 | 125s | Setup |
| Ellipse | 25% | 28% | +3 | stagnant | 1.3 | 130s | Setup |
| Hyperbola | 22% | 25% | +3 | stagnant | 1.2 | 135s | Setup |

### Feature Triggers

| Feature | Expected Output |
|---|---|
| F1 | Weak nodes only in: Circle, Parabola, Ellipse, Hyperbola, Probability |
| F4 | Setup Gap dominant (~40%) — she can't construct locus/conic setups |
| F5 | None — well calibrated |
| F6 | Possibly on Area Under Curves (acc 58%, conf 1.8 — she's better than she thinks) |
| F9 | Circle → Straight Lines (fine), Circle → Quadratic (fine). Prereqs are strong — problem is in Coord Geo itself. |
| F10 | F002 "Setting up locus equations by parameter elimination" — Circle, Parabola, Ellipse, Hyperbola all depend on it and are all weak. Strong hypothesis. |
| F11 | No hot/cold streaks. Everything stable or stagnant. |
| F14 | Huge Phase 1 (12+ topics). Phase 3: only Coord Geo + Probability. |
| F16 | Maintenance: 8-10 topics. Very short active study list. |
| F17 | Priority 1: Circle (prereq to Parabola and Ellipse via coord geo chain). Or directly the F002 foundational skill practice. |
| F18 | Question from Circle or Parabola (locus-type). |

---

## Student 4 — RAHUL

### Narrative
Rahul is the "struggling" student. 35% overall accuracy. Weak at most things, strong at nothing. The system's job: don't overwhelm him. Show him ONE thing to start with. F10 should show top-1 only (global acc < 35%). F16 should show zero maintenance topics. The report should feel like a hand reaching out, not a list of 20 failures.

### Objectives served
- Objective 3: Graceful handling of a hard case
- Objective 4: Does the system help weak students or crush them?

### Overall stats
| Metric | Value |
|---|---|
| Overall accuracy | 35% |
| Net marks (current avg) | ~22/100 |
| Average confidence | 1.6 |
| Dominant failure mode | Concept Gap (~50%) |

### Topic Accuracy Table

| Topic | Baseline (T1-10) | Current (T11-15) | Delta | Momentum | Confidence | Avg Time | Error Tendency |
|---|---|---|---|---|---|---|---|
| Statistics | 55% | 58% | +3 | stable | 2.0 | 85s | Procedural |
| Sets And Relations | 50% | 52% | +2 | stable | 1.8 | 90s | Procedural |
| Sequences And Series | 48% | 50% | +2 | stable | 1.8 | 90s | Procedural |
| Straight Lines | 42% | 45% | +3 | stable | 1.8 | 95s | Setup |
| Quadratic Eq And Ineq | 40% | 42% | +2 | stable | 1.7 | 100s | Setup |
| Binomial Theorem | 35% | 38% | +3 | stagnant | 1.5 | 110s | Conceptual |
| Vector Algebra | 35% | 38% | +3 | stagnant | 1.5 | 105s | Setup |
| Matrices And Det | 32% | 35% | +3 | stagnant | 1.5 | 115s | Conceptual |
| Functions | 30% | 32% | +2 | stagnant | 1.5 | 110s | Conceptual |
| Permutations And Comb | 30% | 32% | +2 | stagnant | 1.5 | 110s | Conceptual |
| 3D Geometry | 28% | 30% | +2 | stagnant | 1.3 | 120s | Conceptual |
| Differentiation | 30% | 32% | +2 | stagnant | 1.5 | 110s | Setup |
| Trig Ratio And Ident | 30% | 32% | +2 | stagnant | 1.5 | 105s | Conceptual |
| Complex Numbers | 25% | 28% | +3 | stagnant | 1.3 | 125s | Conceptual |
| Circle | 25% | 28% | +3 | stagnant | 1.2 | 125s | Conceptual |
| Limits Cont And Diff | 22% | 25% | +3 | stagnant | 1.2 | 130s | Conceptual |
| Application Of Deriv | 20% | 22% | +2 | stagnant | 1.0 | 140s | Conceptual |
| Definite Integration | 18% | 20% | +2 | stagnant | 1.0 | 145s | Conceptual |
| Probability | 20% | 22% | +2 | stagnant | 1.2 | 135s | Conceptual |
| Differential Equations | 15% | 18% | +3 | stagnant | 1.0 | 150s | Conceptual |
| Area Under Curves | 15% | 18% | +3 | stagnant | 1.0 | 150s | Conceptual |
| Parabola | 18% | 20% | +2 | stagnant | 1.0 | 140s | Conceptual |
| Ellipse | 15% | 15% | 0 | stagnant | 1.0 | 145s | Conceptual |
| Hyperbola | 12% | 12% | 0 | stagnant | 1.0 | 150s | Conceptual |
| Indefinite Integrals | 18% | 20% | +2 | stagnant | 1.0 | 140s | Conceptual |
| Inverse Trig Functions | 20% | 22% | +2 | stagnant | 1.2 | 130s | Conceptual |

### Feature Triggers

| Feature | Expected Output |
|---|---|
| F1 | Almost everything is weak. The list is long. |
| F4 | Concept Gap dominant (50%). He doesn't know the theory. |
| F5 | None — his confidence is already low |
| F6 | None — nothing is secretly strong |
| F7 | Drop-off everywhere — even Direct Application is only ~45% |
| F9 | Multiple prereq traces but most are weak_signal (errors are Conceptual, not Setup) |
| F10 | Global acc ~35% → display top-1 only. Should surface the most foundational skill. |
| F11 | No hot/cold streaks. Everything stagnant. Trajectory: flat. |
| F14 | Phase 1: Statistics only. Phase 3: most topics. Skip: many. |
| F15 | Enormous Slow+Wrong bucket. But the "recoverable marks" message is still motivating. |
| F16 | Zero maintenance topics. |
| F17 | Priority 1: Statistics (closest to tipping, his best topic at 58%). Small daily minutes — achievable. |
| F18 | Question from Statistics. Micro-goal: "Get 4 right instead of 3." Achievable. |

### Key test: Does the system overwhelm him?
The report should NOT list 20 weak topics. It should focus on the 1-2 things he can actually do this week. F17 gives him Statistics as Priority 1. F18 gives him one question. That's the output. Everything else is available if he digs deeper, but the headline is one thing.

---

## Student 5 — KAVYA

### Narrative
Kavya is the stress test. 48% overall — close to average, but her patterns are complex. She's overconfident on 3 topics (thinks she's good, isn't). Underconfident on 2 (thinks she's bad, isn't). She hacks MCQs on 2 topics (high MCQ accuracy, zero Numerical accuracy — elimination strategy). Her time allocation is terrible — spends 40% of her time on weak topics. She has one dramatic hot streak and one cold streak happening simultaneously.

### Objectives served
- Objective 3: Stress tests every safety net (F5 min-conf, F6 MCQ-reliability, F6 recency, F10 cluster suppression)
- Objective 1: Exercises edge cases

### Overall stats
| Metric | Value |
|---|---|
| Overall accuracy | 48% |
| Net marks (current avg) | ~35/100 |
| Average confidence | 2.1 (misleading — highly variable) |
| Dominant failure mode | Mixed (Setup 30%, Concept 30%, Execution 25%, Rushed 15%) |

### Topic Accuracy Table

| Topic | Baseline (T1-10) | Current (T11-15) | Delta | Momentum | Confidence | Avg Time | Error Tendency | Special |
|---|---|---|---|---|---|---|---|---|
| Sequences And Series | 75% | 78% | +3 | stable | 1.5 | 80s | Procedural | UNDERCONFIDENT |
| Vector Algebra | 70% | 75% | +5 | stable | 1.5 | 78s | Procedural | UNDERCONFIDENT |
| Statistics | 65% | 68% | +3 | stable | 2.2 | 75s | Procedural | — |
| Matrices And Det | 35% | 38% | +3 | stagnant | 2.8 | 70s | Setup | OVERCONFIDENT |
| Straight Lines | 38% | 35% | -3 | stagnant | 2.6 | 85s | Setup | OVERCONFIDENT |
| Binomial Theorem | 32% | 35% | +3 | stagnant | 2.5 | 90s | Conceptual | OVERCONFIDENT |
| Functions | 55% | 58% | +3 | stable | 2.0 | 90s | Procedural | — |
| Quadratic Eq And Ineq | 55% | 58% | +3 | stable | 2.0 | 88s | Procedural | — |
| Sets And Relations | 50% | 55% | +5 | stable | 2.0 | 82s | Procedural | — |
| Permutations And Comb | 50% | 52% | +2 | stable | 2.0 | 95s | Setup | MCQ HACKER (MCQ: 70%, Num: 15%) |
| Complex Numbers | 45% | 48% | +3 | stable | 2.0 | 100s | Conceptual | MCQ HACKER (MCQ: 65%, Num: 10%) |
| 3D Geometry | 45% | 48% | +3 | stable | 1.8 | 105s | Setup | — |
| Definite Integration | 20% | 45% | +25 | hot_streak | 1.5 | 110s | Setup | Dramatic improvement |
| Limits Cont And Diff | 65% | 40% | -25 | cold_streak | 2.2 | 115s | Setup | Was strong, now slipping |
| Application Of Deriv | 30% | 32% | +2 | stagnant | 1.5 | 130s | Setup | — |
| Probability | 28% | 30% | +2 | stagnant | 1.5 | 135s | Setup | — |
| Differential Equations | 25% | 28% | +3 | stagnant | 1.3 | 140s | Conceptual | — |
| Circle | 30% | 32% | +2 | stagnant | 1.5 | 120s | Setup | — |
| Parabola | 28% | 28% | 0 | stagnant | 1.5 | 125s | Setup | — |
| Area Under Curves | 22% | 25% | +3 | stagnant | 1.2 | 140s | Setup | — |
| Ellipse | 20% | 22% | +2 | stagnant | 1.0 | 140s | Conceptual | — |
| Hyperbola | 18% | 20% | +2 | stagnant | 1.0 | 145s | Conceptual | — |
| Indefinite Integrals | 25% | 28% | +3 | stagnant | 1.3 | 135s | Setup | — |
| Inverse Trig Functions | 28% | 30% | +2 | stagnant | 1.5 | 120s | Conceptual | — |
| Differentiation | 40% | 42% | +2 | stable | 1.8 | 100s | Procedural | — |
| Trig Ratio And Ident | 38% | 40% | +2 | stable | 1.8 | 95s | Conceptual | — |

### Feature Triggers

| Feature | Expected Output |
|---|---|
| F5 | Overconfident on: Matrices (conf 2.8, acc 38%), Straight Lines (conf 2.6, acc 35%), Binomial (conf 2.5, acc 35%). All above min-conf floor (2.0). F5 should fire on all three. Error check: Setup errors on Matrices/Straight Lines → concept_overconfidence. Conceptual on Binomial → concept_overconfidence. |
| F6 | Underconfident on: Sequences (conf 1.5, acc 78%) → should check MCQ reliability, likely confident_strength. Vector Algebra (conf 1.5, acc 75%) → same. ALSO check recency: if last 2 tests on Sequences have conf ≥ 2.5, suppress (recently_corrected). Design: Sequences last 2 tests conf = 2.5 (suppressed). Vector Algebra last 2 tests conf = 1.5 (not suppressed, fires). |
| F6 (MCQ) | P&C (MCQ 70%, Num 15%) and Complex Numbers (MCQ 65%, Num 10%) — if F6 were to flag these, the MCQ reliability check should catch it. But their overall accuracy (52%, 48%) is borderline for F6 trigger anyway (gap needs to be >0.20). Design carefully. |
| F7 | Drop-off at Build Then Solve |
| F8 | Latest test should have 1 stretch question (strong node + hard question). |
| F9 | Limits was strong (65%) and dropped to 40% — cold streak BUT not a prereq trace issue (it was strong before). F9 should show "fine" on Limits as prereq since baseline was 65%. |
| F10 | Should trigger moderately. Not as clean as Priya's F001 because Kavya's weakness pattern is messier. |
| F11 | Hot streak: Definite Integration (+25pp). Cold streak: Limits (-25pp). Both dramatic. |
| F14 | Complex Phase 1/2/3 split — demonstrates the plan adapts to complex profiles. |
| F15 | Terrible time allocation. She spends time on weak topics (stagnant) and skips questions from strong topics (tragic misses). Recoverable marks should be highest of all students. |
| F16 | Maintenance: Statistics only (Sequences suppressed by recency? No — recency suppression is on F6, not F16. F16 checks stability. Sequences at 78% with stable last 5 → maintenance). |
| F17 | Priority 1: Limits (cold streak regression, was prerequisite, needs quick refresh). |

### Time waste pattern (latest test)
Spends 5 minutes each on 2 Differential Equations questions (wrong), 4 minutes on 1 Probability question (wrong), 3 minutes on 1 Area Under Curves question (wrong). Total Slow+Wrong: ~17 min.
Leaves 2 questions from Sequences And Series unattempted (tragic misses — she's 78% on these).
Rushes through 2 Binomial Theorem MCQs in <40 seconds each (Rushed failure mode).

---

## Data Generation Notes

### Test Composition Rules
All 5 students take the SAME 15 test papers (same questions in each test). Only their responses differ. This ensures fair comparison. Each test has 25 questions drawn from df_master with these constraints:
- Every topic appears in at least 10 of the 15 tests
- Top 15 topics (by question count) appear in every test
- Each test covers at least 18 of the 26 topics
- Archetype overlap: each eligible node (≥10 questions) appears in at least 3 of the 15 tests

### Response Generation Rules
For each student × each question:
1. Look up the question's topic
2. Use the student's accuracy for that topic (interpolated between baseline and current based on test index)
3. Set is_correct probabilistically from that accuracy
4. Set confidence_rating from the student's topic confidence value (with ±0.5 jitter, clamped to 1-3)
5. Set time_taken_seconds from the student's topic time value (with ±15s jitter, clamped to 30-300)
6. For "rushed" questions (Kavya's Binomial): override time to 30-40s
7. For "MCQ hacker" questions (Kavya's P&C, Complex): set MCQ accuracy high, Numerical accuracy low
8. For unattempted questions: do not add a row to student_responses, but keep the row in test_composition

### Adding Noise
After deterministic generation, randomly flip 5% of is_correct values. This prevents the data from looking artificially clean while preserving the designed patterns.


---

## APPENDIX — UPDATES (Final Revisions)

### Change 1: Kavya's MCQ Hacker Topics
Changed from P&C and Complex Numbers to:
- **Indefinite Integrals** (hack: differentiate the 4 MCQ options to find which matches)
- **Quadratic Equations** (hack: plug x=0 or x=1 into options)

Updated Kavya table rows:
| Indefinite Integrals | 25% | 28% | +3 | stagnant | 1.3 | 135s | Setup | MCQ HACKER (MCQ: 65%, Num: 8%) |
| Quadratic Eq And Ineq | 55% | 58% | +3 | stable | 2.0 | 88s | Procedural | MCQ HACKER (MCQ: 75%, Num: 20%) |

### Change 2: Test Format — 30 Questions Per Test
Each test has 30 questions (~22 MCQ + ~8 Numerical), matching JEE Mains format.
Students choose how many to attempt. Attempt rate is a personality trait:

| Student | Attempt Rate | Behavior |
|---|---|---|
| Priya | 22-24 | Average — skips a few she doesn't recognize |
| Arjun | 16-18 | Smart skipper — banks strong topics, ignores weak |
| Meera | 26-28 | Strong — attempts almost everything |
| Rahul | 20-22 | Over-attempts — tries things he can't do, bleeds marks |
| Kavya | 23-25 | Aggressive — attempts including questions she should skip |

### Change 3: Rahul's Priority Override
When global accuracy < 35%, the priority formula overrides prerequisite weight
and maximizes "proximity to win" weight. Template explicitly says:
"We usually recommend foundational topics. But right now, you need a confidence
boost. Statistics is your closest win — push it over 60% this week."

### Change 4: All 10 Noise Generation Rules

**Rule 1 — Accuracy noise (Good Day / Bad Day):**
Per test per topic: actual_accuracy = profile_accuracy + random.uniform(-0.10, +0.10)
Clamped to [0.05, 0.95].

**Rule 2 — Time noise (Tricky Question Effect):**
Per question: time = max(30, normal(base_time, 15))
Produces a realistic cloud, not a static point.

**Rule 3 — Attempt rate ceiling:**
Per student: attempt only N of 30 questions. Remaining are unattempted.
Unattempted questions: exist in test_composition but NOT in student_responses.
Selection of which to skip: prioritize skipping weak topics (smart skipping)
or random (Rahul — doesn't know what to skip).

**Rule 4 — Guessing noise:**
If topic accuracy < 30%: 20% of questions answered in <40s with Procedural error tag.
Simulates confused guessing, triggers F14 "Danger Zone" and F15 "Fast+Wrong."

**Rule 5 — Error type 70/30 distribution:**
If dominant error is "Setup": 70% of wrong answers tagged Setup, 15% Procedural, 15% Conceptual.
If dominant error is "Conceptual": 70% Conceptual, 15% Setup, 15% Procedural.
If dominant error is "Procedural": 70% Procedural, 15% Setup, 15% Conceptual.

**Rule 6 — Rushed error override:**
If time_taken < 45s AND wrong → force error_type = "Procedural" (careless).

**Rule 7 — Hard question error override:**
If difficulty_proxy > 0.75 AND wrong → force error_type = "Conceptual" (too hard).

**Rule 8 — Panic variable (last 5 questions):**
For Kavya and Rahul: if question_index >= 26 (out of 30):
- Increase Procedural error probability by 30%
- Reduce time to normal(40, 10) seconds
- Simulates end-of-exam panic.

**Rule 9 — Question difficulty interaction:**
adjusted_accuracy = topic_accuracy + (0.5 - difficulty_proxy) × 0.25
Easy question on weak topic → slightly better chance.
Hard question on strong topic → slightly worse chance.
Makes F8 "Stretch Question" trigger naturally.

**Rule 10 — Fatigue curve:**
time = base_time × (1 + 0.008 × question_index)
By question 25: time is 20% higher than question 1.
By question 30: 24% higher. Natural slowdown.
