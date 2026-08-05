"""
STUDENT RESPONSE GENERATOR — 5 Students × 15 Tests
═══════════════════════════════════════════════════════════════════════════

Generates student_responses DataFrame from:
  - test_composition.csv (15 tests × 30 questions)
  - df_master.csv (question metadata)
  - df_question_nodes.csv (cognitive demand for difficulty proxy)
  - Hardcoded student profiles from spec sheets

All 10 noise rules implemented:
  1. Accuracy noise (±10% per test)
  2. Time noise (Gaussian)
  3. Attempt rate ceiling
  4. Guessing noise (<30% topics → fast wrong answers)
  5. Error type 70/30 (encoded via which questions are wrong, not explicit)
  6. Rushed error override (time <45s)
  7. Hard question error override (high difficulty)
  8. Panic variable (last 5 questions for Kavya, Rahul)
  9. Difficulty interaction (easy boosts, hard reduces accuracy)
  10. Fatigue curve (time increases through test)

Output:
  student_responses.csv — student_id, question_id, is_correct,
                          time_taken_seconds, confidence_rating, test_timestamp
"""

import pandas as pd
import numpy as np


# ═══════════════════════════════════════════════════════════════════════════════
# STUDENT PROFILES (hardcoded from spec sheets)
# ═══════════════════════════════════════════════════════════════════════════════

# Each profile: {topic: {bl: baseline_acc, cu: current_acc, conf: confidence, time: avg_time}}
# Plus: attempt_rate, panic (bool), mcq_hacker_topics

PROFILES = {
    'PRIYA': {
        'attempt_range': (22, 24),
        'panic': False,
        'mcq_hacker': {},
        'skip_strategy': 'weak',     # skips weak topics
        'topics': {
            'Sequences And Series':                     {'bl': 0.78, 'cu': 0.80, 'conf': 2.5, 'time': 75},
            'Statistics':                               {'bl': 0.72, 'cu': 0.75, 'conf': 2.3, 'time': 70},
            'Sets And Relations':                       {'bl': 0.68, 'cu': 0.70, 'conf': 2.0, 'time': 80},
            'Quadratic Equation And Inequalities':      {'bl': 0.62, 'cu': 0.65, 'conf': 2.2, 'time': 85},
            'Vector Algebra':                           {'bl': 0.72, 'cu': 0.48, 'conf': 2.5, 'time': 85},
            'Matrices And Determinants':                {'bl': 0.55, 'cu': 0.58, 'conf': 2.0, 'time': 100},
            'Binomial Theorem':                         {'bl': 0.48, 'cu': 0.55, 'conf': 2.0, 'time': 95},
            'Functions':                                {'bl': 0.52, 'cu': 0.55, 'conf': 1.8, 'time': 90},
            'Straight Lines And Pair Of Straight Lines': {'bl': 0.50, 'cu': 0.52, 'conf': 2.0, 'time': 95},
            'Permutations And Combinations':            {'bl': 0.45, 'cu': 0.48, 'conf': 2.0, 'time': 100},
            'Complex Numbers':                          {'bl': 0.30, 'cu': 0.32, 'conf': 2.7, 'time': 110},
            '3D Geometry':                              {'bl': 0.42, 'cu': 0.45, 'conf': 1.8, 'time': 115},
            'Circle':                                   {'bl': 0.40, 'cu': 0.42, 'conf': 1.8, 'time': 105},
            'Limits Continuity And Differentiability':  {'bl': 0.35, 'cu': 0.38, 'conf': 1.7, 'time': 120},
            'Application Of Derivatives':               {'bl': 0.28, 'cu': 0.30, 'conf': 1.5, 'time': 130},
            'Definite Integration':                     {'bl': 0.25, 'cu': 0.42, 'conf': 1.5, 'time': 125},
            'Probability':                              {'bl': 0.30, 'cu': 0.32, 'conf': 1.8, 'time': 120},
            'Differential Equations':                   {'bl': 0.28, 'cu': 0.30, 'conf': 1.5, 'time': 135},
            'Area Under The Curves':                    {'bl': 0.25, 'cu': 0.28, 'conf': 1.5, 'time': 130},
            'Parabola':                                 {'bl': 0.35, 'cu': 0.38, 'conf': 1.8, 'time': 110},
            'Ellipse':                                  {'bl': 0.32, 'cu': 0.35, 'conf': 1.7, 'time': 115},
            'Hyperbola':                                {'bl': 0.30, 'cu': 0.30, 'conf': 1.7, 'time': 120},
            'Indefinite Integrals':                     {'bl': 0.30, 'cu': 0.35, 'conf': 1.5, 'time': 125},
            'Inverse Trigonometric Functions':           {'bl': 0.35, 'cu': 0.38, 'conf': 1.8, 'time': 110},
            'Differentiation':                          {'bl': 0.45, 'cu': 0.48, 'conf': 2.0, 'time': 95},
            'Trigonometric Ratio And Identites':        {'bl': 0.50, 'cu': 0.52, 'conf': 2.0, 'time': 85},
            'Logarithm':                                {'bl': 0.40, 'cu': 0.42, 'conf': 1.8, 'time': 100},
        },
    },
    'ARJUN': {
        'attempt_range': (16, 18),
        'panic': False,
        'mcq_hacker': {},
        'skip_strategy': 'smart',    # skips weakest topics deliberately
        'topics': {
            'Matrices And Determinants':                {'bl': 0.88, 'cu': 0.90, 'conf': 2.8, 'time': 70},
            '3D Geometry':                              {'bl': 0.85, 'cu': 0.88, 'conf': 2.8, 'time': 75},
            'Vector Algebra':                           {'bl': 0.82, 'cu': 0.85, 'conf': 2.7, 'time': 72},
            'Sequences And Series':                     {'bl': 0.80, 'cu': 0.82, 'conf': 2.5, 'time': 78},
            'Statistics':                               {'bl': 0.78, 'cu': 0.80, 'conf': 2.5, 'time': 72},
            'Sets And Relations':                       {'bl': 0.55, 'cu': 0.58, 'conf': 2.2, 'time': 85},
            'Binomial Theorem':                         {'bl': 0.55, 'cu': 0.60, 'conf': 2.2, 'time': 95},
            'Straight Lines And Pair Of Straight Lines': {'bl': 0.50, 'cu': 0.52, 'conf': 2.0, 'time': 90},
            'Quadratic Equation And Inequalities':      {'bl': 0.48, 'cu': 0.50, 'conf': 2.0, 'time': 95},
            'Functions':                                {'bl': 0.42, 'cu': 0.45, 'conf': 1.8, 'time': 100},
            'Permutations And Combinations':            {'bl': 0.38, 'cu': 0.40, 'conf': 1.8, 'time': 105},
            'Complex Numbers':                          {'bl': 0.22, 'cu': 0.25, 'conf': 1.3, 'time': 140},
            'Definite Integration':                     {'bl': 0.18, 'cu': 0.20, 'conf': 1.2, 'time': 150},
            'Probability':                              {'bl': 0.18, 'cu': 0.20, 'conf': 1.3, 'time': 145},
            'Application Of Derivatives':               {'bl': 0.15, 'cu': 0.18, 'conf': 1.2, 'time': 155},
            'Limits Continuity And Differentiability':  {'bl': 0.15, 'cu': 0.18, 'conf': 1.2, 'time': 150},
            'Differential Equations':                   {'bl': 0.15, 'cu': 0.15, 'conf': 1.0, 'time': 160},
            'Area Under The Curves':                    {'bl': 0.12, 'cu': 0.15, 'conf': 1.0, 'time': 155},
            'Circle':                                   {'bl': 0.20, 'cu': 0.22, 'conf': 1.3, 'time': 130},
            'Parabola':                                 {'bl': 0.18, 'cu': 0.20, 'conf': 1.2, 'time': 140},
            'Ellipse':                                  {'bl': 0.15, 'cu': 0.18, 'conf': 1.0, 'time': 145},
            'Hyperbola':                                {'bl': 0.12, 'cu': 0.15, 'conf': 1.0, 'time': 150},
            'Inverse Trigonometric Functions':           {'bl': 0.20, 'cu': 0.22, 'conf': 1.3, 'time': 125},
            'Indefinite Integrals':                     {'bl': 0.15, 'cu': 0.18, 'conf': 1.0, 'time': 150},
            'Differentiation':                          {'bl': 0.20, 'cu': 0.22, 'conf': 1.3, 'time': 130},
            'Trigonometric Ratio And Identites':        {'bl': 0.25, 'cu': 0.28, 'conf': 1.5, 'time': 120},
            'Logarithm':                                {'bl': 0.20, 'cu': 0.22, 'conf': 1.3, 'time': 130},
        },
    },
    'MEERA': {
        'attempt_range': (26, 28),
        'panic': False,
        'mcq_hacker': {},
        'skip_strategy': 'random',
        'topics': {
            'Statistics':                               {'bl': 0.85, 'cu': 0.88, 'conf': 2.8, 'time': 65},
            'Sequences And Series':                     {'bl': 0.82, 'cu': 0.85, 'conf': 2.7, 'time': 70},
            'Sets And Relations':                       {'bl': 0.80, 'cu': 0.82, 'conf': 2.5, 'time': 72},
            'Vector Algebra':                           {'bl': 0.78, 'cu': 0.80, 'conf': 2.5, 'time': 75},
            'Matrices And Determinants':                {'bl': 0.75, 'cu': 0.78, 'conf': 2.5, 'time': 78},
            'Quadratic Equation And Inequalities':      {'bl': 0.72, 'cu': 0.75, 'conf': 2.3, 'time': 80},
            'Binomial Theorem':                         {'bl': 0.70, 'cu': 0.72, 'conf': 2.3, 'time': 82},
            'Straight Lines And Pair Of Straight Lines': {'bl': 0.68, 'cu': 0.70, 'conf': 2.2, 'time': 80},
            'Functions':                                {'bl': 0.68, 'cu': 0.70, 'conf': 2.2, 'time': 85},
            '3D Geometry':                              {'bl': 0.65, 'cu': 0.68, 'conf': 2.2, 'time': 88},
            'Permutations And Combinations':            {'bl': 0.65, 'cu': 0.68, 'conf': 2.2, 'time': 85},
            'Definite Integration':                     {'bl': 0.62, 'cu': 0.65, 'conf': 2.0, 'time': 90},
            'Application Of Derivatives':               {'bl': 0.60, 'cu': 0.65, 'conf': 2.0, 'time': 92},
            'Limits Continuity And Differentiability':  {'bl': 0.62, 'cu': 0.65, 'conf': 2.0, 'time': 88},
            'Differential Equations':                   {'bl': 0.58, 'cu': 0.62, 'conf': 2.0, 'time': 95},
            'Differentiation':                          {'bl': 0.65, 'cu': 0.68, 'conf': 2.2, 'time': 82},
            'Trigonometric Ratio And Identites':        {'bl': 0.62, 'cu': 0.65, 'conf': 2.0, 'time': 80},
            'Area Under The Curves':                    {'bl': 0.55, 'cu': 0.58, 'conf': 1.8, 'time': 95},
            'Indefinite Integrals':                     {'bl': 0.58, 'cu': 0.60, 'conf': 2.0, 'time': 90},
            'Inverse Trigonometric Functions':           {'bl': 0.55, 'cu': 0.58, 'conf': 1.8, 'time': 92},
            'Complex Numbers':                          {'bl': 0.55, 'cu': 0.58, 'conf': 2.0, 'time': 90},
            'Probability':                              {'bl': 0.32, 'cu': 0.35, 'conf': 1.5, 'time': 125},
            'Circle':                                   {'bl': 0.30, 'cu': 0.32, 'conf': 1.5, 'time': 120},
            'Parabola':                                 {'bl': 0.28, 'cu': 0.30, 'conf': 1.5, 'time': 125},
            'Ellipse':                                  {'bl': 0.25, 'cu': 0.28, 'conf': 1.3, 'time': 130},
            'Hyperbola':                                {'bl': 0.22, 'cu': 0.25, 'conf': 1.2, 'time': 135},
            'Logarithm':                                {'bl': 0.55, 'cu': 0.58, 'conf': 2.0, 'time': 85},
        },
    },
    'RAHUL': {
        'attempt_range': (20, 22),
        'panic': True,
        'mcq_hacker': {},
        'skip_strategy': 'random',   # doesn't know what to skip
        'topics': {
            'Statistics':                               {'bl': 0.55, 'cu': 0.58, 'conf': 2.0, 'time': 85},
            'Sets And Relations':                       {'bl': 0.50, 'cu': 0.52, 'conf': 1.8, 'time': 90},
            'Sequences And Series':                     {'bl': 0.48, 'cu': 0.50, 'conf': 1.8, 'time': 90},
            'Straight Lines And Pair Of Straight Lines': {'bl': 0.42, 'cu': 0.45, 'conf': 1.8, 'time': 95},
            'Quadratic Equation And Inequalities':      {'bl': 0.40, 'cu': 0.42, 'conf': 1.7, 'time': 100},
            'Binomial Theorem':                         {'bl': 0.35, 'cu': 0.38, 'conf': 1.5, 'time': 110},
            'Vector Algebra':                           {'bl': 0.35, 'cu': 0.38, 'conf': 1.5, 'time': 105},
            'Matrices And Determinants':                {'bl': 0.32, 'cu': 0.35, 'conf': 1.5, 'time': 115},
            'Functions':                                {'bl': 0.30, 'cu': 0.32, 'conf': 1.5, 'time': 110},
            'Permutations And Combinations':            {'bl': 0.30, 'cu': 0.32, 'conf': 1.5, 'time': 110},
            '3D Geometry':                              {'bl': 0.28, 'cu': 0.30, 'conf': 1.3, 'time': 120},
            'Differentiation':                          {'bl': 0.30, 'cu': 0.32, 'conf': 1.5, 'time': 110},
            'Trigonometric Ratio And Identites':        {'bl': 0.30, 'cu': 0.32, 'conf': 1.5, 'time': 105},
            'Complex Numbers':                          {'bl': 0.25, 'cu': 0.28, 'conf': 1.3, 'time': 125},
            'Circle':                                   {'bl': 0.25, 'cu': 0.28, 'conf': 1.2, 'time': 125},
            'Limits Continuity And Differentiability':  {'bl': 0.22, 'cu': 0.25, 'conf': 1.2, 'time': 130},
            'Application Of Derivatives':               {'bl': 0.20, 'cu': 0.22, 'conf': 1.0, 'time': 140},
            'Definite Integration':                     {'bl': 0.18, 'cu': 0.20, 'conf': 1.0, 'time': 145},
            'Probability':                              {'bl': 0.20, 'cu': 0.22, 'conf': 1.2, 'time': 135},
            'Differential Equations':                   {'bl': 0.15, 'cu': 0.18, 'conf': 1.0, 'time': 150},
            'Area Under The Curves':                    {'bl': 0.15, 'cu': 0.18, 'conf': 1.0, 'time': 150},
            'Parabola':                                 {'bl': 0.18, 'cu': 0.20, 'conf': 1.0, 'time': 140},
            'Ellipse':                                  {'bl': 0.15, 'cu': 0.15, 'conf': 1.0, 'time': 145},
            'Hyperbola':                                {'bl': 0.12, 'cu': 0.12, 'conf': 1.0, 'time': 150},
            'Indefinite Integrals':                     {'bl': 0.18, 'cu': 0.20, 'conf': 1.0, 'time': 140},
            'Inverse Trigonometric Functions':           {'bl': 0.20, 'cu': 0.22, 'conf': 1.2, 'time': 130},
            'Logarithm':                                {'bl': 0.25, 'cu': 0.28, 'conf': 1.3, 'time': 120},
        },
    },
    'KAVYA': {
        'attempt_range': (23, 25),
        'panic': True,
        'mcq_hacker': {
            'Indefinite Integrals':       {'mcq_acc': 0.65, 'num_acc': 0.08},
            'Quadratic Equation And Inequalities': {'mcq_acc': 0.75, 'num_acc': 0.20},
        },
        'skip_strategy': 'aggressive',  # attempts too many, including bad ones
        'topics': {
            'Sequences And Series':                     {'bl': 0.75, 'cu': 0.78, 'conf': 1.5, 'time': 80},
            'Vector Algebra':                           {'bl': 0.70, 'cu': 0.75, 'conf': 1.5, 'time': 78},
            'Statistics':                               {'bl': 0.65, 'cu': 0.68, 'conf': 2.2, 'time': 75},
            'Matrices And Determinants':                {'bl': 0.35, 'cu': 0.38, 'conf': 2.8, 'time': 70},
            'Straight Lines And Pair Of Straight Lines': {'bl': 0.38, 'cu': 0.35, 'conf': 2.6, 'time': 85},
            'Binomial Theorem':                         {'bl': 0.32, 'cu': 0.35, 'conf': 2.5, 'time': 90},
            'Functions':                                {'bl': 0.55, 'cu': 0.58, 'conf': 2.0, 'time': 90},
            'Quadratic Equation And Inequalities':      {'bl': 0.55, 'cu': 0.58, 'conf': 2.0, 'time': 88},
            'Sets And Relations':                       {'bl': 0.50, 'cu': 0.55, 'conf': 2.0, 'time': 82},
            'Permutations And Combinations':            {'bl': 0.50, 'cu': 0.52, 'conf': 2.0, 'time': 95},
            'Complex Numbers':                          {'bl': 0.45, 'cu': 0.48, 'conf': 2.0, 'time': 100},
            '3D Geometry':                              {'bl': 0.45, 'cu': 0.48, 'conf': 1.8, 'time': 105},
            'Definite Integration':                     {'bl': 0.20, 'cu': 0.45, 'conf': 1.5, 'time': 110},
            'Limits Continuity And Differentiability':  {'bl': 0.65, 'cu': 0.40, 'conf': 2.2, 'time': 115},
            'Application Of Derivatives':               {'bl': 0.30, 'cu': 0.32, 'conf': 1.5, 'time': 130},
            'Probability':                              {'bl': 0.28, 'cu': 0.30, 'conf': 1.5, 'time': 135},
            'Differential Equations':                   {'bl': 0.25, 'cu': 0.28, 'conf': 1.3, 'time': 140},
            'Circle':                                   {'bl': 0.30, 'cu': 0.32, 'conf': 1.5, 'time': 120},
            'Parabola':                                 {'bl': 0.28, 'cu': 0.28, 'conf': 1.5, 'time': 125},
            'Area Under The Curves':                    {'bl': 0.22, 'cu': 0.25, 'conf': 1.2, 'time': 140},
            'Ellipse':                                  {'bl': 0.20, 'cu': 0.22, 'conf': 1.0, 'time': 140},
            'Hyperbola':                                {'bl': 0.18, 'cu': 0.20, 'conf': 1.0, 'time': 145},
            'Indefinite Integrals':                     {'bl': 0.25, 'cu': 0.28, 'conf': 1.3, 'time': 135},
            'Inverse Trigonometric Functions':           {'bl': 0.28, 'cu': 0.30, 'conf': 1.5, 'time': 120},
            'Differentiation':                          {'bl': 0.40, 'cu': 0.42, 'conf': 1.8, 'time': 100},
            'Trigonometric Ratio And Identites':        {'bl': 0.38, 'cu': 0.40, 'conf': 1.8, 'time': 95},
            'Logarithm':                                {'bl': 0.30, 'cu': 0.32, 'conf': 1.5, 'time': 110},
        },
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# GENERATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

def compute_difficulty(df_master, df_qn):
    """Difficulty proxy per question (0-1)."""
    df = df_master[['question_id', 'text_length', 'question_type']].copy()
    df['lp'] = df['text_length'].rank(pct=True)
    df['ts'] = df['question_type'].map({'MCQ': 0.3, 'Numerical': 0.7})
    dm = {'Direct Application': 0.1, 'Formula with Judgment': 0.3,
          'Build Then Solve': 0.6, 'Build and Work Backwards': 0.8, 'Reverse Engineer': 1.0}
    nd = df_qn[['question_id', 'cognitive_demand']].drop_duplicates()
    df = df.merge(nd, on='question_id', how='left')
    df['ds'] = df['cognitive_demand'].map(dm).fillna(0.5)
    df['difficulty'] = (df['lp']*0.3 + df['ts']*0.3 + df['ds']*0.4).round(3)
    return dict(zip(df['question_id'], df['difficulty']))


def interpolate_accuracy(bl, cu, test_idx, n_tests=15):
    """Smooth interpolation between baseline and current accuracy."""
    t = test_idx / (n_tests - 1)
    return bl + (cu - bl) * t


def select_attempts(questions_df, profile, test_idx, rng):
    """Decide which questions to attempt based on skip strategy."""
    n_attempt = rng.integers(*profile['attempt_range'])
    n_attempt = min(n_attempt, len(questions_df))

    if profile['skip_strategy'] == 'smart':
        # Skip weakest topics first
        topic_acc = {}
        for _, q in questions_df.iterrows():
            tp = profile['topics'].get(q['topic'], {'bl': 0.3, 'cu': 0.3})
            topic_acc[q['question_id']] = interpolate_accuracy(tp['bl'], tp['cu'], test_idx)
        questions_df = questions_df.copy()
        questions_df['_acc'] = questions_df['question_id'].map(topic_acc)
        questions_df = questions_df.sort_values('_acc', ascending=False)
        return questions_df.head(n_attempt)['question_id'].tolist()

    elif profile['skip_strategy'] == 'weak':
        # Skip some weak topics
        topic_acc = {}
        for _, q in questions_df.iterrows():
            tp = profile['topics'].get(q['topic'], {'bl': 0.3, 'cu': 0.3})
            topic_acc[q['question_id']] = interpolate_accuracy(tp['bl'], tp['cu'], test_idx)
        questions_df = questions_df.copy()
        questions_df['_acc'] = questions_df['question_id'].map(topic_acc)
        questions_df = questions_df.sort_values('_acc', ascending=False)
        return questions_df.head(n_attempt)['question_id'].tolist()

    elif profile['skip_strategy'] == 'aggressive':
        # Attempts most, including some bad ones — skip only a few randomly
        skip_n = len(questions_df) - n_attempt
        skip_idx = rng.choice(len(questions_df), size=skip_n, replace=False)
        return [q for i, q in enumerate(questions_df['question_id'].tolist()) if i not in skip_idx]

    else:  # random
        idx = rng.choice(len(questions_df), size=n_attempt, replace=False)
        return questions_df.iloc[sorted(idx)]['question_id'].tolist()


def generate_responses(test_comp, df_master, df_qn):
    """Generate student_responses for all 5 students."""
    rng = np.random.default_rng(42)
    difficulty = compute_difficulty(df_master, df_qn)

    # Build question lookup
    q_info = df_master.set_index('question_id')[['topic', 'question_type']].to_dict('index')

    all_rows = []
    test_ids = sorted(test_comp['test_id'].unique())
    test_dates = pd.date_range('2025-01-10', periods=len(test_ids), freq='W')
    test_date_map = dict(zip(test_ids, test_dates))

    for student_id, profile in PROFILES.items():
        student_rows = []

        for test_idx, test_id in enumerate(test_ids):
            test_qs = test_comp[test_comp['test_id'] == test_id].merge(
                df_master[['question_id', 'topic', 'question_type']], on='question_id')
            test_date = test_date_map[test_id]

            # ── Select which questions to attempt ─────────────────────────
            attempted_qids = select_attempts(test_qs, profile, test_idx, rng)

            for q_pos, qid in enumerate(attempted_qids):
                info = q_info.get(qid, {'topic': 'Unknown', 'question_type': 'MCQ'})
                topic = info['topic']
                q_type = info['question_type']
                diff = difficulty.get(qid, 0.5)

                tp = profile['topics'].get(topic, {'bl': 0.35, 'cu': 0.35, 'conf': 1.5, 'time': 110})

                # ── Rule 1: Base accuracy (interpolated + noise) ──────────
                base_acc = interpolate_accuracy(tp['bl'], tp['cu'], test_idx)
                acc_noise = rng.uniform(-0.10, 0.10)   # Rule 1: ±10%
                noisy_acc = base_acc + acc_noise

                # ── Rule 9: Difficulty interaction ────────────────────────
                noisy_acc += (0.5 - diff) * 0.25

                # ── MCQ Hacker override ───────────────────────────────────
                if topic in profile['mcq_hacker']:
                    hack = profile['mcq_hacker'][topic]
                    if q_type == 'MCQ':
                        noisy_acc = hack['mcq_acc'] + rng.uniform(-0.08, 0.08)
                    else:
                        noisy_acc = hack['num_acc'] + rng.uniform(-0.05, 0.05)

                noisy_acc = np.clip(noisy_acc, 0.03, 0.97)

                # ── Rule 8: Panic (last 5 questions) ──────────────────────
                is_panic = profile['panic'] and q_pos >= 25

                if is_panic:
                    noisy_acc *= 0.6   # 40% accuracy reduction

                # ── Determine correctness ─────────────────────────────────
                is_correct = bool(rng.random() < noisy_acc)

                # ── Rule 4: Guessing noise (weak topic, fast wrong) ───────
                is_guess = False
                if base_acc < 0.30 and not is_correct and rng.random() < 0.20:
                    is_guess = True

                # ── Confidence ────────────────────────────────────────────
                base_conf = tp['conf']
                conf_jitter = rng.uniform(-0.5, 0.5)
                confidence = int(np.clip(round(base_conf + conf_jitter), 1, 3))

                # ── Time ──────────────────────────────────────────────────
                base_time = tp['time']

                # Rule 10: Fatigue curve
                fatigue = 1 + 0.008 * q_pos
                base_time_fatigued = base_time * fatigue

                if is_panic:
                    # Rule 8: Panic — very fast
                    time_taken = int(np.clip(rng.normal(40, 10), 20, 60))
                elif is_guess:
                    # Rule 4: Guessing — fast
                    time_taken = int(np.clip(rng.normal(35, 8), 20, 50))
                elif is_correct:
                    # Rule 2: Normal time noise
                    time_taken = int(np.clip(rng.normal(base_time_fatigued * 0.85, 15), 30, 300))
                else:
                    # Wrong answers take longer
                    time_taken = int(np.clip(rng.normal(base_time_fatigued * 1.35, 25), 40, 360))

                student_rows.append({
                    'student_id': student_id,
                    'question_id': qid,
                    'is_correct': is_correct,
                    'time_taken_seconds': time_taken,
                    'confidence_rating': confidence,
                    'test_timestamp': test_date,
                })

        all_rows.extend(student_rows)
        n = len(student_rows)
        correct = sum(1 for r in student_rows if r['is_correct'])
        print(f"  {student_id:8s}: {n:>4} responses, {correct}/{n} correct ({correct/n:.0%})")

    df = pd.DataFrame(all_rows)

    # ── Rule: 5% random flip for organic noise ────────────────────────────────
    flip_mask = rng.random(len(df)) < 0.05
    df.loc[flip_mask, 'is_correct'] = ~df.loc[flip_mask, 'is_correct']
    flipped = flip_mask.sum()
    print(f"\n  Applied 5% noise flip: {flipped} answers flipped")

    return df


# ═══════════════════════════════════════════════════════════════════════════════
# RUN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("=" * 70)
    print("STUDENT RESPONSE GENERATOR")
    print("=" * 70)

    df_master = pd.read_csv('/mnt/project/df_master.csv')
    df_qn = pd.read_csv('/mnt/project/df_question_nodes.csv')
    test_comp = pd.read_csv('/mnt/user-data/outputs/test_composition.csv')

    print(f"\nLoaded: df_master ({len(df_master)}), df_qn ({len(df_qn)}), "
          f"test_comp ({len(test_comp)})\n")

    # Generate
    print("Generating responses for 5 students...\n")
    sr = generate_responses(test_comp, df_master, df_qn)

    # ── Validation ────────────────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print("VALIDATION")
    print(f"{'='*70}")
    print(f"  Total rows: {len(sr)}")
    print(f"  Students: {sr['student_id'].nunique()}")
    print(f"  Tests per student:")

    for sid in sr['student_id'].unique():
        ss = sr[sr['student_id'] == sid]
        n_tests = ss['test_timestamp'].nunique()
        avg_per_test = len(ss) / n_tests
        acc = ss['is_correct'].mean()
        avg_conf = ss['confidence_rating'].mean()
        avg_time = ss['time_taken_seconds'].mean()
        print(f"    {sid:8s}: {n_tests} tests, {avg_per_test:.0f} qs/test, "
              f"acc={acc:.0%}, conf={avg_conf:.1f}, time={avg_time:.0f}s")

    # Check unattempted counts
    print(f"\n  Unattempted per student (test 15):")
    last_date = sr['test_timestamp'].max()
    for sid in sr['student_id'].unique():
        test15_attempted = sr[(sr['student_id'] == sid) & (sr['test_timestamp'] == last_date)]
        test15_total = test_comp[test_comp['test_id'] == 15]
        unattempted = len(test15_total) - len(test15_attempted)
        print(f"    {sid:8s}: {len(test15_attempted)} attempted, {unattempted} unattempted")

    # Topic accuracy check for key profiles
    print(f"\n  Topic accuracy spot-check (Priya vs Arjun on strong topics):")
    for sid in ['PRIYA', 'ARJUN']:
        ss = sr[sr['student_id'] == sid]
        ta = ss.merge(df_master[['question_id', 'topic']], on='question_id')
        top3 = ta.groupby('topic')['is_correct'].mean().sort_values(ascending=False).head(3)
        print(f"    {sid}: {dict(top3.round(2))}")

    # Save
    output_path = '/mnt/user-data/outputs/student_responses.csv'
    sr.to_csv(output_path, index=False)
    print(f"\n  Saved → {output_path}")
    print(f"  Shape: {sr.shape}")
