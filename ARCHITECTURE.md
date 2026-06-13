# Architecture

End-to-end pipeline specification for the LECO diagnostic engine, covering data generation, the labeling pipeline, the diagnostic computation, and the output layer.

---

## Pipeline Overview

```mermaid
flowchart LR
    subgraph PA["Phase A — Data Acquisition & Labeling"]
        direction TB
        A1["🌐 Web Scraper\n(Playwright on ExamSIDE)"]
        A2["🧹 Text Cleaner\n(LaTeX standardization)"]
        A3["🤖 LLM Pass 1\n(Per-topic discovery)"]
        A4["🔀 LLM Pass 2\n(Cross-topic synthesis)"]
        A1 --> A2 --> A3 --> A4
    end

    subgraph PB["Phase B — Diagnostic Engine (Deterministic Python)"]
        direction TB
        B0["Stage 0: Pre-filter"]
        B12["Stages 1–2: Weakness + Confidence"]
        B34["Stages 3–4: Root Cause + Strategy"]
        B56["Stages 5–6: Study Plan + Next Action"]
        B0 --> B12 --> B34 --> B56
    end

    subgraph PC["Phase C — Output"]
        direction TB
        C1["📝 Report Generator\n(Reframe labels → student language)"]
        C2["💻 React Frontend\n(Planned)"]
        C1 --> C2
    end

    A4 -->|"4 CSV tables"| PB
    KG["📊 Knowledge Graph\nlayer_1_PN +\nprerequisite_final.json"] --> PB
    ST["👤 Student Data\nresponses +\ntest_composition"] --> PB
    PB -->|"DiagnosticReport"| PC
```

---

## Phase A: Data Acquisition & Labeling

### A1 — Web Scraping (Playwright)

```mermaid
flowchart LR
    URL["ExamSIDE\nTopic URL"] --> SCROLL["Lazy-scroll\n(50 cycles × 800px)"]
    SCROLL --> EXTRACT["Extract anchors\nwith overflow-y-hidden"]
    EXTRACT --> FILTER["Flag img/table/svg\n→ drop non-text"]
    FILTER --> QTYPE["Detect MCQ vs\nNumerical from H2"]
    QTYPE --> CSV["Raw CSV\n(per topic)"]
```

Key technical decisions:

- **Lazy-load handling:** Simulates human scroll behavior (800px increments with random 0.4–0.8s delays) to trigger all question loads, iterating up to 50 scroll cycles until `document.body.scrollHeight` stabilizes.
- **Fragment joining:** Questions on ExamSIDE are split across multiple `<p>` and `<span>` elements. The scraper joins them at the DOM level using `inner_text()` on the anchor container, which naturally concatenates child text.
- **Image flagging:** Questions containing `<img>`, `<table>`, or `<svg>` tags are flagged via a single DOM evaluation pass. These are filtered out before LLM processing since the engine handles text-only questions.

### A2 — Two-Pass LLM Discovery Pipeline

```mermaid
flowchart TD
    QS["~100 questions\nper topic"] --> P1["Pass 1: Topic-Level Extraction"]
    P1 --> |"Per-topic JSON"| NODES["Reasoning Archetypes\n(nodes)"]
    P1 --> ERRORS["Error Patterns"]
    P1 --> CONCEPTS["Concept Co-occurrences"]
    P1 --> DEMAND["Cognitive Demand\nClassification"]

    NODES --> P2["Pass 2: Cross-Topic Synthesis"]
    ERRORS --> P2
    CONCEPTS --> P2
    DEMAND --> P2

    P2 --> DQN["df_question_nodes\n(5,150 rows)"]
    P2 --> DQE["df_question_errors\n(5,522 rows)"]
    P2 --> DQC["df_question_concepts\n(11,784 rows)"]
    P2 --> DM["df_master\n(4,481 rows)"]

    style P1 fill:#e0e7ff,stroke:#4338ca
    style P2 fill:#e0e7ff,stroke:#4338ca
```

**Pass 1 — Topic-level extraction:** The LLM evaluates ~100 questions from a single topic to identify recurring reasoning archetypes, concept co-occurrences, classification dimensions (cognitive demand levels), and common error types. No hard numerical constraints (e.g., "find 3–6 archetypes") — the prompt emphasizes distinctness and lets the data dictate category counts.

**Pass 2 — Cross-topic synthesis:** The LLM evaluates all Pass 1 outputs for a subject to deduplicate nodes that appeared independently in multiple topics, extract universal cognitive operations, and produce the validated master vocabulary.

**Design reversal:** Error taxonomy and cognitive demand were initially nested inside individual archetypes. This was decoupled during validation because the same error type (e.g., *incorrect oxidation state assignment*) recurs across multiple distinct archetypes. In the final pipeline, errors are assigned independently of archetypes.

---

## Phase B: Diagnostic Computation

### Feature Dependency Graph

```mermaid
flowchart TD
    S0["Stage 0\nPre-filter eligible sets\n(items with ≥ 10 questions)"]

    S0 --> F1["F1 · Node Weakness"]
    S0 --> F3["F3 · Error Patterns"]
    S0 --> F4["F4 · Failure Modes"]
    S0 --> F7["F7 · Demand Profile"]
    S0 --> F8["F8 · Wrong Answer Triage"]
    S0 --> F11["F11 · Momentum"]

    F1 --> F2["F2 · Concept Precision"]
    F1 --> F5["F5 · Overconfidence"]
    F1 --> F6["F6 · Underconfidence"]

    F5 & F6 --> F9["F9 · Prereq Trace"]
    F5 & F6 --> F10["F10 · Foundational Skill"]

    F11 --> F14["F14 · Exam Plan"]
    F11 --> F16["F16 · Maintenance"]

    F5 & F9 & F11 & F14 & F16 --> F17["F17 · Study Plan"]

    F17 --> F15["F15 · Time ROI"]
    F17 --> F18["F18 · Next Action"]

    style S0 fill:#f3f4f6,stroke:#6b7280
    style F1 fill:#dbeafe,stroke:#2563eb
    style F2 fill:#dbeafe,stroke:#2563eb
    style F3 fill:#dbeafe,stroke:#2563eb
    style F4 fill:#fed7aa,stroke:#ea580c
    style F5 fill:#fed7aa,stroke:#ea580c
    style F6 fill:#fed7aa,stroke:#ea580c
    style F7 fill:#fed7aa,stroke:#ea580c
    style F8 fill:#fed7aa,stroke:#ea580c
    style F9 fill:#fecaca,stroke:#dc2626
    style F10 fill:#fecaca,stroke:#dc2626
    style F11 fill:#fecaca,stroke:#dc2626
    style F14 fill:#bbf7d0,stroke:#16a34a
    style F15 fill:#bbf7d0,stroke:#16a34a
    style F16 fill:#bbf7d0,stroke:#16a34a
    style F17 fill:#bbf7d0,stroke:#16a34a
    style F18 fill:#bbf7d0,stroke:#16a34a
```

> 🔵 Weakness Detection · 🟠 Failure Classification · 🔴 Root Cause · 🟢 Strategy & Action

---

### Feature Specifications with Math

#### F1 — Node-Level Weakness Map

For each reasoning node $n$, aggregate the student's accuracy across all tests:

$$
\text{acc}(n) = \frac{\sum_{q \in Q_n} \mathbb{1}[\text{correct}(q)]}{\lvert Q_n \rvert}
$$

where $Q_n$ is the set of all questions the student attempted that map to node $n$. A node is flagged as **weak** when:

$$
\text{acc}(n) < 0.50 \quad \text{and} \quad \lvert Q_n \rvert \geq 3
$$

The minimum-attempt threshold prevents false positives from small sample sizes.

---

#### F4 — Failure Mode Classification

Each wrong answer is classified into one of four failure modes using time-taken and confidence:

$$
\text{mode}(q) = \begin{cases}
\textbf{Rushed} & \text{if } t_q < 0.40 \cdot t_{\text{baseline}} \\[6pt]
\textbf{Concept Gap} & \text{if } e_q = \text{Conceptual} \\[4pt]
\textbf{Setup Gap} & \text{if } e_q = \text{Setup} \\[4pt]
\textbf{Execution Slip} & \text{if } e_q = \text{Procedural} \;\wedge\; c_q \geq 2 \\[4pt]
\textbf{Concept Gap} & \text{otherwise (low confidence procedural)}
\end{cases}
$$

where $t_q$ is time spent, $t_{\text{baseline}}$ is 90s for MCQ / 120s for Numerical, $e_q$ is the dominant error type, and $c_q$ is the confidence rating.

---

#### F8 — Wrong Answer Triage

For each wrong answer on the **latest test**, the engine checks the student's **lifetime historical accuracy** on that node and classifies the mistake:

$$
\text{class}(q) = \begin{cases}
\textbf{No Baseline} & \text{if } n_{\text{hist}} < 5 \\[6pt]
\textbf{Focus Area} & \text{if } \text{acc}_{\text{hist}}(n_q) \leq 0.35 \\[6pt]
\textbf{Stretch} & \text{if } \text{acc}_{\text{hist}}(n_q) \geq 0.65 \;\wedge\; d_q \geq 0.75 \\[6pt]
\textbf{Unexpected Slip} & \text{if } \text{acc}_{\text{hist}}(n_q) \geq 0.65 \;\wedge\; d_q < 0.75 \\[6pt]
\textbf{Developing} & \text{otherwise}
\end{cases}
$$

where $\text{acc}_{\text{hist}}(n_q)$ is the student's historical accuracy on the node(s) tied to question $q$, $n_{\text{hist}}$ is total historical attempts on those nodes, and $d_q$ is a difficulty proxy computed from the corpus.

The **difficulty proxy** for question $q$ is defined as:

$$
d_q = \frac{1}{\lvert N_q \rvert} \sum_{n \in N_q} \text{rank}(\text{demand}(n))
$$

where $\text{rank}$ maps cognitive demand levels to $[0, 1]$ across the five-tier spectrum.

---

#### F9 — Topic Prerequisite Trace

Given the prerequisite graph $G = (V, E)$ where vertices are topics and a directed edge $A \to B$ means "A is a prerequisite for B":

**Step 1.** Identify weak downstream topics:

$$
W = \{ t \in V \mid \text{acc}(t) < 0.40 \}
$$

**Step 2.** For each $t_{\text{down}} \in W$, find upstream prerequisites:

$$
\text{Prereqs}(t_{\text{down}}) = \{ t_{\text{up}} \mid (t_{\text{up}} \to t_{\text{down}}) \in E \}
$$

**Step 3.** Flag suspect upstream topics:

$$
\text{Suspects}(t_{\text{down}}) = \{ t_{\text{up}} \in \text{Prereqs}(t_{\text{down}}) \mid \text{acc}(t_{\text{up}}) < 0.40 \}
$$

**Step 4.** Confirm the trace with a cognitive demand cross-check. Let $W_q$ be the set of wrong answers in $t_{\text{down}}$, and let $H_q \subseteq W_q$ be those mapped to high cognitive demand nodes (Build Then Solve or above):

$$
\text{confidence} = \begin{cases}
\textbf{Confirmed} & \text{if } \dfrac{\lvert H_q \rvert}{\lvert W_q \rvert} \geq 0.60 \\[8pt]
\textbf{Suspect} & \text{otherwise}
\end{cases}
$$

The intuition: if a student's failures in the downstream topic are concentrated on structurally complex questions (not simple recall), it confirms that the prerequisite foundation — not the downstream topic's own content — is the root cause.

---

#### F10 — Foundational Skill Hypothesis

For each foundational skill $s$ with a set of dependent topics $D_s$:

**Step 1.** Compute the set of topics the student has attempted sufficiently:

$$
A = \{ t \mid \text{attempts}(t) \geq 10 \}
$$

**Step 2.** Compute overlap with weak topics:

$$
\text{overlap}(s) = \frac{\lvert W \cap D_s \cap A \rvert}{\lvert D_s \cap A \rvert}
$$

**Step 3.** Flag the skill as a suspect when:

$$
\lvert W \cap D_s \cap A \rvert \geq 2 \quad \text{and} \quad \text{overlap}(s) \geq 0.60
$$

**Step 4 (demand signature match).** Each foundational skill has a cognitive demand signature $\Sigma_s$ (e.g., skill F001 maps to *Build Then Solve* + *Build and Work Backwards*). If the student's wrong answers in the overlapping topics align with $\Sigma_s$, the hypothesis is strengthened to high priority.

**Step 5 (noise suppression).** If the student's global accuracy is below 35%, only the single strongest foundational hypothesis is displayed to prevent overwhelming them.

---

#### F17 — Study Focus Plan

Each non-maintenance topic receives a composite priority score:

$$
P(t) = 2.0 \cdot S(t) + 1.5 \cdot R(t) + 1.0 \cdot M(t) + 1.0 \cdot O(t) + 1.0 \cdot T(t)
$$

| Component | Weight | Definition |
|-----------|--------|------------|
| $S(t)$ — Severity | 2.0× | $1 - \text{acc}(t)$, normalized |
| $R(t)$ — Prerequisite Impact | 1.5× | Count of downstream weak topics that $t$ unlocks |
| $M(t)$ — Stagnation/Regression | 1.0× | 1 if cold streak or stagnant, 0 otherwise |
| $O(t)$ — Overconfidence | 1.0× | 1 if any node in $t$ is flagged overconfident, 0 otherwise |
| $T(t)$ — Tipping Point | 1.0× | 1 if $\text{acc}(t)$ is within 15% of the Phase 1 strength threshold |

Topics are ranked by $P(t)$ descending, and a 90-minute daily study budget is allocated proportionally.

---

### Key Thresholds (Configurable Constants)

| Constant | Value | Used By | Meaning |
|----------|-------|---------|---------|
| `MIN_QUESTIONS` | 10 | Pre-filter | Minimum questions in corpus for a node/concept/error to be eligible |
| `G1_MIN_ATTEMPTS` | 3 | F1, F2 | Minimum student attempts before flagging weakness |
| `G1_WEAK_THRESHOLD` | 0.50 | F1 | Accuracy below this = weak node |
| `G1_CONCEPT_FAIL_TH` | 0.60 | F2 | Concept failure rate above this = flagged leak |
| `G1_ERROR_FREQ_TH` | 5 | F3 | Error must recur 5+ times to be flagged as systemic |
| `G2_RUSHED_FRACTION` | 0.40 | F4 | Time below 40% of baseline = classified as "Rushed" |
| `G2_OVERCONF_GAP` | 0.20 | F5 | Confidence−accuracy gap threshold for overconfidence |
| `G2_MCQ_BASELINE` | 90s | F4 | Expected time per MCQ question |
| `G2_NUM_BASELINE` | 120s | F4 | Expected time per Numerical question |
| `G3_F8_MIN_ATTEMPTS` | 5 | F8 | Minimum historical attempts for triage classification |
| `G3_F9_WEAK_TOPIC` | 0.40 | F9 | Topic accuracy threshold for prerequisite trace |
| `G3_F10_OVERLAP_RATIO` | 0.60 | F10 | Minimum overlap ratio for foundational hypothesis |

---

### Synthetic Student Generation

For prototype demonstration, 5 synthetic students are generated, each with a defined learning personality:

| Student | Accuracy | Personality |
|---------|----------|-------------|
| PRIYA | 53% | Balanced weaknesses, setup gaps dominant |
| ARJUN | 65% | Strong overall but overconfident in specific nodes |
| MEERA | 64% | Good at pattern recognition, weak at abstract algebra |
| RAHUL | 35% | Broadly weak, many concept gaps |
| KAVYA | 45% | Improving trajectory, cold streak in specific topics |

Each student has 15 tests with ~25 questions per test. Question selection ensures archetype overlap across tests (critical for pattern detection).

---

## Phase C: Output Generation

### Report Reframing

Clinical labels are translated into student-friendly language:

| Clinical Label | Student-Facing Label | Student-Facing Explanation |
|---------------|---------------------|---------------------------|
| Concept Gap | Foundation moments | "You needed a stronger grip on the underlying idea" |
| Setup Gap | Starting line moments | "You knew the concept, but couldn't see the way in" |
| Execution Slip | Tiny moments | "You had it — small mistakes cost you" |
| Rushed | Clock moments | "Time pressure got to you" |

### Persona System (Planned)

The diagnostic data can be wrapped in different conversational personas: **The Coach** (direct, action-oriented), **The Gym Girly** (motivational, high-energy), **The Star Wars Sage** (metaphor-heavy, narrative). Same diagnostic data, different stylistic skin applied to the system prompt.

---

## Entity Relationship Diagram

```mermaid
erDiagram
    df_master ||--o{ df_question_nodes : "1 to many"
    df_master ||--o{ df_question_errors : "1 to many"
    df_master ||--o{ df_question_concepts : "1 to many"
    df_master ||--o{ student_responses : "1 per student per question"

    df_master {
        string question_id PK
        string topic
        string subject
        int year
        string question_type
        string question_text
        string correct_answer
        string solution_steps
        string wrong_options
    }

    df_question_nodes {
        string question_id FK
        string node_id
        string node_name
        string cognitive_operation
        string cognitive_demand
    }

    df_question_errors {
        string question_id FK
        string error_id
        string error_name
        string error_type
        string description
    }

    df_question_concepts {
        string question_id FK
        string topic
        string concept_name
    }

    student_responses {
        string student_id
        string question_id FK
        bool is_correct
        int time_taken_seconds
        int confidence_rating
        datetime test_timestamp
    }

    layer_1_PN {
        string source_topic
        string target_topic
    }

    prerequisite_final_json {
        string skill_id PK
        string skill_name
        string failure_signature
        list dependent_topics
    }
```

---

## What's Not In The Pipeline (And Why)

| Component | Status | Reason |
|-----------|--------|--------|
| Real-time LLM calls in the engine | Not used | All 16 features are deterministic Python. LLM is only used in the report generation layer |
| ChromaDB / vector search | Removed | Originally planned for question-to-question similarity. Unnecessary for prototype scope |
| 90K question corpus | Cleaned, not labeled | Cost/time constraints. The 4.5K PYQ corpus with solutions provides higher-fidelity signal |
| Digital pen / rough work capture | Dropped | Replaced by confidence tagging (1-click, 1–3 scale). Same signal, zero friction |
| NCERT RAG pipeline | Dropped | LLMs already know the curriculum. Direct classification is simpler and more accurate |
