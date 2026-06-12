# LECO - Learning Engine for Cognitive Optimization

A deterministic diagnostic engine that analyzes JEE exam performance at the micro-skill level, traces failure to its root cause through a prerequisite knowledge graph, and produces a single, targeted next-action recommendation instead of an overwhelming dashboard of weaknesses.

Built on a labeled corpus of 4,481 JEE Mathematics PYQs (2015–2026) enriched with reasoning archetypes, error taxonomies, and concept tags — all extracted through a two-pass unsupervised LLM discovery pipeline.


The Problem 

Every test-prep platform tells students the same thing: "You're weak at Calculus." That's useless. A student staring at 15 weak topics doesn't know where to start. They re-read textbooks they already understand, practice random questions, and stay stuck — because the real problem is three layers deeper than "Calculus."

LECO asks a different question: Why is this student failing, and what single action will move their score the most right now?

What Makes This Different

Micro-skill resolution, not topic-level. Questions aren't tagged as "Calculus" — they're tagged with atomic reasoning nodes like Piecewise Dissection via Absolute Value or Tangent-at-a-Point with External Constraint. A student failing "Calculus" might actually be fine at integration but broken at a single setup pattern.

Root-cause tracing, not symptom listing. A directed prerequisite graph (75 topic-level edges + 42 below-syllabus foundational skills) lets the engine trace a failure in Definite Integration back to a gap in Limits — and tell the student to fix Limits first, because more Integration practice will keep failing until the foundation is repaired.

Behavioral diagnosis from metadata. Without requiring students to log their work, the engine infers failure modes from time-taken, confidence ratings, and error patterns: distinguishing concept gaps from setup gaps from execution slips from rushed guesses. A student who "needs to study more" might actually need to slow down on setup.

One question with a reason. The output isn't a dashboard. It's a single, specific question selected from the corpus at the student's ideal difficulty level, with an LLM-generated explanation of exactly why that question was chosen based on their diagnostic profile.
