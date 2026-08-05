# ═══════════════════════════════════════════════════════════════════════════════
# THREE DOORS — drop-in replacement for Section 4 of the narrative layer
# ═══════════════════════════════════════════════════════════════════════════════
# Paste this whole cell AFTER the narrative-layer cell in the notebook and re-run
# report generation. It redefines _section_4_what_to_do, so generate_student_report
# picks it up automatically.
#
# WHY THIS EXISTS
# The old closer ("Open this one question, right now") prescribed a single action
# without knowing the one thing that decides which action is right: the student's
# horizon. Exam in 4 days and exam in 4 months demand opposite plans. The engine
# never collects that context, so the honest final word is not a prescription —
# it is a set of doors, each priced, each labeled with who it is for. The student
# knows their horizon. They pick.
#
# DOOR 1 — REBUILD THE FOUNDATION   (F10 + F9: slowest path, biggest payoff)
# DOOR 2 — TAKE THE QUICK WIN       (nearest tipping-point topic: momentum this week)
# DOOR 3 — CHANGE NOTHING BUT STRATEGY (F15 + F16: marks without new learning)
#
# Honesty rules baked in (from VALIDATION.md):
#  · Door 1 speaks in the hypothesis's own confidence tier and ALWAYS ships a
#    self-verification step (validation showed F10 over-generates on weak
#    students: 24 hypotheses for one student against 0 planted).
#  · Door 1 states the negative honestly when F10 finds nothing (that IS the
#    diagnosis for a polarized student: no hidden skill, just unstudied topics).
#  · Door 2 computes the nearest win from the full F14 topic table (accuracy
#    closest below 65%, ≥8 attempts) instead of trusting F17's ordering, which
#    validation showed diverges from design intent in 4 of 5 students and lacks
#    the low-scorer proximity override.
#  · Door 3 promises only what F15 measured: leaked marks + tragic-skip value.
# ═══════════════════════════════════════════════════════════════════════════════

def _wrap(text, width=50):
    words=text.split(); out=[]; cur=""
    for w in words:
        if len(cur)+len(w)+1>width: out.append(cur); cur=w
        else: cur=f"{cur} {w}".strip()
    if cur: out.append(cur)
    return out


def _rows(x):
    """Normalize engine outputs: DataFrame -> records, list -> list, else []."""
    try:
        import pandas as _pd
        if isinstance(x, _pd.DataFrame):
            return x.to_dict('records')
    except Exception:
        pass
    return list(x) if isinstance(x, (list, tuple)) else []


TIER_PHRASE = {
    'strong_hypothesis':   "a strong pattern in your data",
    'moderate_hypothesis': "worth testing — not yet certain",
    'weak_hypothesis':     "a faint signal — treat it as a question, not a conclusion",
}


def _nearest_win(report):
    """Highest-accuracy topic still below 65%, ≥8 attempts, from the F14 table."""
    rows = _rows(report.f14_exam_plan.get('phases', []))
    cand = [r for r in rows
            if r.get('att', 0) >= 8 and r.get('acc', 1.0) < 0.65
            and r.get('phase') != 'skip']
    if not cand:
        return None
    return max(cand, key=lambda r: r['acc'])


def _door_1_foundation(report, lines):
    lines.append("  ┌─ DOOR 1 ─ REBUILD THE FOUNDATION ─────────────────────┐")
    lines.append("  │  For students with months. Slowest path, biggest payoff.")
    hyps = _rows(report.f10_foundational)
    if not hyps:
        lines.append("  │")
        lines.append("  │  Honest answer: this door is not your door. No single")
        lines.append("  │  hidden skill shows up behind your weak topics — they")
        lines.append("  │  fail independently, which usually means they simply")
        lines.append("  │  haven't been studied deeply yet. Skip to Door 2.")
        lines.append("  └────────────────────────────────────────────────────────┘")
        return
    h = hyps[0]
    shown = 1 if report.f10_display == 'top_1' else min(len(hyps), 2)
    overlap = h.get('weak_overlap', [])[:3]
    lines.append("  │")
    lines.append("  │  One skill may sit under several of your weak topics:")
    for k, seg in enumerate(_wrap(h['skill_name'], 46)):
        lines.append(f"  │    {'▸ ' if k == 0 else '  '}{seg}")
    lines.append(f"  │      ({TIER_PHRASE.get(h['confidence'], h['confidence'])})")
    if overlap:
        lines.append("  │    Topics it would unlock together:")
        for seg in _wrap(", ".join(overlap), 48):
            lines.append(f"  │      {seg}")
    if len(hyps) > 1:
        lines.append(f"  │    (Your data supports {len(hyps)} candidate skill{'s' if len(hyps)>1 else ''};")
        lines.append("  │     we show the strongest so the list doesn't bury you.)")
    lines.append("  │")
    lines.append("  │  VERIFY BEFORE YOU INVEST WEEKS — the pattern-finder is")
    lines.append("  │  eager, so make it prove itself. Take 3 fresh questions")
    lines.append("  │  that force you to BUILD the setup from words (not plug")
    lines.append(f"  │  a formula), from: {(overlap[0] if overlap else 'an affected topic')[:36]}")
    lines.append("  │    · 0–1 of 3 → hypothesis stands: drill this skill,")
    lines.append("  │      the topics move together.")
    lines.append("  │    · 3 of 3  → we retire it and your plan updates.")
    lines.append("  │  Cost: weeks.  Payoff: several topics rise at once.")
    lines.append("  └────────────────────────────────────────────────────────┘")


def _door_2_quick_win(report, lines):
    lines.append("  ┌─ DOOR 2 ─ TAKE THE QUICK WIN ─────────────────────────┐")
    lines.append("  │  For students who need momentum this week.")
    win = _nearest_win(report)
    if win is None:
        lines.append("  │")
        lines.append("  │  Nothing sits close to the 65% line right now — your")
        lines.append("  │  topics are either banked or far. Doors 1 and 3 are")
        lines.append("  │  where your marks are.")
        lines.append("  └────────────────────────────────────────────────────────┘")
        return
    acc = win['acc']; att = win.get('att', 0)
    per_test = att / 15.0
    gain = max(1, round((0.65 - acc) * per_test * 4 * 15) )  # marks over next 15 papers
    lines.append("  │")
    lines.append(f"  │  Closest topic to tipping into a strength:")
    lines.append(f"  │    ▸ {win['topic']}  — {acc:.0%} now, 65% is the line")
    lines.append("  │  One focused push (30–40 min/day, this week) flips it.")
    if gain >= 3:
        lines.append(f"  │  Payoff you can see: roughly +{gain} marks across your")
        lines.append("  │  next 15 papers from this topic alone — and the feeling")
        lines.append("  │  of a topic changing color on your map.")
    else:
        lines.append("  │  The number is small; the win is the flip itself —")
        lines.append("  │  one week turns a coin-flip topic into a banked one.")
    lines.append("  │  Cost: one week of focus.  Payoff: fast, visible.")
    lines.append("  └────────────────────────────────────────────────────────┘")


def _door_3_strategy(report, lines):
    b = report.f15_time_roi['bottom_line']
    leaked = int(b['without_leaks'] - b['score'])
    tragic = int(round(b.get('tragic_ev', 0)))
    total = leaked + tragic
    sw = _rows(report.f15_time_roi.get('sw_topics', []))
    unatt = _rows(report.f15_time_roi.get('unattempted', []))
    tragic_rows = [u for u in unatt if u.get('topic_acc', 0) >= 0.60]
    maint_n = 0
    try:
        m = report.f16_maintenance
        if 'status' in m.columns:
            maint_n = int((m['status'] == 'maintenance').sum())
    except Exception:
        pass
    lines.append("  ┌─ DOOR 3 ─ CHANGE NOTHING BUT STRATEGY ────────────────┐")
    lines.append("  │  For students days from the exam. No new learning.")
    lines.append("  │")
    lines.append(f"  │  On your latest paper, {total} marks were recoverable")
    lines.append("  │  without opening a textbook:")
    if leaked > 0 and sw:
        s0 = sw[0]
        lines.append(f"  │    ▸ {leaked} marks leaked to time traps — worst was")
        for seg in _wrap(f"{s0['topic']} ({s0['time_min']:.0f} min for {s0['marks']:+d} marks).", 48):
            lines.append(f"  │      {seg}")
        lines.append("  │      New rule: 2.5 minutes, no progress → skip, move on.")
    elif leaked > 0:
        lines.append(f"  │    ▸ {leaked} marks leaked to wrong answers on long attempts.")
    if tragic > 0 and tragic_rows:
        t0 = tragic_rows[0]
        lines.append(f"  │    ▸ {tragic} marks sat in questions you skipped from")
        for seg in _wrap(f"topics you're strong in (e.g. {t0['topic']}). Attempt these FIRST.", 48):
            lines.append(f"  │      {seg}")
    if maint_n:
        _s = "s" if maint_n > 1 else ""
        _v = "need" if maint_n > 1 else "needs"
        lines.append(f"  │    ▸ Plus: {maint_n} stable topic{_s} {_v} only 2 questions")
        lines.append("  │      a week — reclaim those study hours for the gaps.")
    lines.append("  │  Cost: zero new study.  Payoff: on the very next paper.")
    lines.append("  └────────────────────────────────────────────────────────┘")


def _section_4_what_to_do(report):
    """Section 4, rebuilt: three doors instead of one prescription."""
    lines = []
    lines.append("")
    lines.append("━" * 60)
    lines.append("  WHAT TO DO — THREE DOORS. YOU PICK.")
    lines.append("━" * 60)
    lines.append("")
    lines.append("  A diagnostic can tell you where you stand. It cannot know")
    lines.append("  how far your exam is, how many hours you have, or how")
    lines.append("  tired you are. You know. So instead of one instruction,")
    lines.append("  here are three doors — each priced honestly.")
    lines.append("")
    _door_1_foundation(report, lines)
    lines.append("")
    _door_2_quick_win(report, lines)
    lines.append("")
    _door_3_strategy(report, lines)
    lines.append("")
    lines.append("  Months out → Door 1.   Need momentum → Door 2.")
    lines.append("  Exam this week → Door 3.")
    lines.append("")
    lines.append("  Whichever you open, that's your whole job today.")
    lines.append("  The other doors will still be here tomorrow.")
    lines.append("")
    return "\n".join(lines)
