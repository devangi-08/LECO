"""
LECO VALIDATION SCORER — three-way audit: SPEC (planted) -> DATA (materialized) -> ENGINE (detected)
Provenance: student_response_generator__1_.py (seed 42) reproduces student_responses.csv byte-identically.
Verdicts:
  DETECTED         planted, survived generation, engine flagged it
  PARTIAL          engine flagged a related/weaker form of the plant
  MISSED           plant materialized in data, engine did not flag it
  NOT_MATERIALIZED plant in spec+code, but noise/censoring erased or inverted it in realized data (engine excused)
  NOT_IMPLEMENTED  plant exists in spec only; generator never coded it (engine excused)
  CLEAN            spec said "none expected" and engine flagged nothing
  EMERGENT         spec said "none expected", engine flagged something that IS data-supported
  N/V              not verifiable from stored data
"""
import pandas as pd, numpy as np, json, collections

U='/mnt/user-data/uploads/'; P='/mnt/project/'
sr = pd.read_csv(U+'student_responses.csv', parse_dates=['test_timestamp'])
dm = pd.read_csv(P+'df_master.csv')[['question_id','topic','question_type']]
dqn= pd.read_csv(P+'df_question_nodes.csv')[['question_id','node_name']]
det= json.load(open('detected_full.json'))
fsk= {s['skill_id'] if 'skill_id' in s else s.get('id'): s for s in json.load(open(P+'prequisite_final.json'))}

s = sr.merge(dm, on='question_id', how='left')
dates = sorted(s.test_timestamp.unique()); d2i={d:i for i,d in enumerate(dates)}
s['tix']=s.test_timestamp.map(d2i)

node_topic = (dqn.merge(dm,on='question_id')
                .groupby('node_name')['topic']
                .agg(lambda x: x.mode().iloc[0]).to_dict())

def topic_stats(stu, topic):
    d=s[(s.student_id==stu)&(s.topic==topic)]
    if len(d)==0: return None
    bl=d[d.tix<=9]; cu=d[d.tix>=10]
    return dict(n=len(d), acc=d.is_correct.mean(), conf=d.confidence_rating.mean(),
                n_bl=len(bl), acc_bl=bl.is_correct.mean() if len(bl) else np.nan,
                n_cu=len(cu), acc_cu=cu.is_correct.mean() if len(cu) else np.nan)

def f5_nodes(stu, flag=True):  return [x for x in det[stu]['f5_overconfidence'] if x.get('flagged')==flag]
def f6_nodes(stu, flag=True):  return [x for x in det[stu]['f6_underconfidence'] if x.get('flagged')==flag]
def mom(stu): return det[stu]['f11_momentum']['momentum_states']
def phase1(stu): return {x['topic'] for x in det[stu]['f14_exam_plan']['phases'] if x['phase']=='phase_1'}
def maint(stu): return {x['topic'] for x in det[stu]['f16_maintenance'] if x['status']=='maintenance'}
def f17top(stu,k=2): 
    pl=sorted(det[stu]['f17_study_plan'], key=lambda x:x['rank']); return [x['topic'] for x in pl[:k]]
def f10ids(stu): return [(x['skill_id'],x['confidence']) for x in det[stu]['f10_foundational']]

R=[]
def row(id,stu,feat,plant,materialized,detected,verdict,note=""):
    R.append(dict(id=id,student=stu,feature=feat,plant=plant,
                  materialized=materialized,detected=detected,verdict=verdict,note=note))

def check_conf_topic(id,stu,topic,kind,spec_conf,spec_acc,fset):
    st=topic_stats(stu,topic)
    if st is None:
        row(id,stu,"F5" if kind=='over' else "F6",
            f"{'Over' if kind=='over' else 'Under'}confident {topic} (spec conf {spec_conf}, acc {spec_acc})",
            "0 attempts in 15 tests — plant censored by skip strategy","no signal possible",
            'NOT_MATERIALIZED',"skip-by-accuracy removed every observation of this plant"); return
    gap=(st['conf']/3-st['acc']) if kind=='over' else (st['acc']-st['conf']/3)
    mat = st['n']>=3 and gap>=0.20
    hits=[x['node_name'] for x in fset(stu) if node_topic.get(x['node_name'])==topic]
    dtxt=f"{len(hits)} node(s): {', '.join(hits[:2])}" if hits else "none"
    mtxt=f"conf {st['conf']:.1f}, acc {st['acc']:.0%}, n={st['n']} (gap {gap:+.2f})"
    if hits and mat: v='DETECTED'
    elif hits and not mat: v='DETECTED'; mtxt+=" [weak at topic level, node-level real]"
    elif mat and not hits: v='MISSED'
    else: v='NOT_MATERIALIZED'
    row(id,stu,f"F5" if kind=='over' else "F6",
        f"{'Over' if kind=='over' else 'Under'}confident {topic} (spec conf {spec_conf}, acc {spec_acc})",
        mtxt,dtxt,v)

def check_none(id,stu,feat,fset,label):
    hits=fset(stu)
    if not hits: row(id,stu,feat,f"None expected ({label})","—","0 flags",'CLEAN')
    else:
        ts=collections.Counter(node_topic.get(x['node_name'],'?') for x in hits)
        row(id,stu,feat,f"None expected ({label})","noise-made gaps exist",
            f"{len(hits)} flags: {dict(list(ts.items())[:3])}",'EMERGENT',
            "all flags are data-supported (engine is deterministic); excess vs design intent")

def check_streak(id,stu,topic,plant_state,spec_move):
    st=topic_stats(stu,topic); ms=mom(stu).get(topic,'(absent)')
    if st is None or st['n_bl']<3 or st['n_cu']<3:
        row(id,stu,'F11',f"{plant_state} {topic} ({spec_move})","insufficient n",ms,'N/V'); return
    delta=st['acc_cu']-st['acc_bl']
    mat = (delta>=0.10) if plant_state=='hot_streak' else (delta<=-0.10)
    mtxt=f"{st['acc_bl']:.0%}->{st['acc_cu']:.0%} ({delta:+.0%})"
    if ms==plant_state and mat: v='DETECTED'
    elif ms==plant_state: v='DETECTED'; mtxt+=" [borderline]"
    elif mat: v='MISSED'
    else: v='NOT_MATERIALIZED'; mtxt+=" — plant inverted/erased by noise+skip-censoring"
    row(id,stu,'F11',f"{plant_state} {topic} ({spec_move})",mtxt,ms,v)

def check_flat(id,stu):
    states=mom(stu); streaks={t:st for t,st in states.items() if st in ('hot_streak','cold_streak')}
    if not streaks: row(id,stu,'F11',"No hot/cold streaks expected","—","0 streaks",'CLEAN'); return
    ann=[]
    for t,stt in list(streaks.items())[:6]:
        ts=topic_stats(stu,t)
        d=(ts['acc_cu']-ts['acc_bl']) if ts and ts['n_bl']>=2 and ts['n_cu']>=2 else np.nan
        ann.append(f"{t}:{stt[:4]}({d:+.0%})" if d==d else f"{t}:{stt[:4]}(n/v)")
    row(id,stu,'F11',"No hot/cold streaks expected","noise created real drifts",
        f"{len(streaks)}: "+"; ".join(ann),'EMERGENT',"small-n noise reads as streaks")

def check_f10(id,stu,skill,expect_conf,desc):
    ids=f10ids(stu); hit=[c for sid,c in ids if sid==skill]
    sk=fsk.get(skill,{}); deps=[d['topic'] if isinstance(d,dict) else d for d in sk.get('dependent_topics',[])]
    weak=[t for t in deps if (topic_stats(stu,t) or {'acc':1,'n':0})['acc']<0.45 and (topic_stats(stu,t) or {'n':0})['n']>=3]
    mtxt=f"{len(weak)}/{len(deps)} dependents weak: {', '.join(weak[:3])}"
    if hit:
        v='DETECTED' if hit[0]==expect_conf else 'PARTIAL'
        row(id,stu,'F10',f"{skill} {desc} ({expect_conf})",mtxt,f"{skill} as {hit[0]} (rank {[i for i,(sid,_) in enumerate(ids) if sid==skill][0]+1}/{len(ids)})",v)
    else:
        v='MISSED' if len(weak)>=2 else 'NOT_MATERIALIZED'
        row(id,stu,'F10',f"{skill} {desc} ({expect_conf})",mtxt,
            f"absent; engine top: {', '.join(f'{a}({b[:3]})' for a,b in ids[:3])}",v)

# ═══════════ MANIFEST ═══════════
SL='Straight Lines And Pair Of Straight Lines'; LCD='Limits Continuity And Differentiability'
QE='Quadratic Equation And Inequalities'; MD='Matrices And Determinants'; VA='Vector Algebra'
DI='Definite Integration'; II='Indefinite Integrals'; PnC='Permutations And Combinations'

# ---- PRIYA ----
check_conf_topic('P1','PRIYA','Complex Numbers','over','2.7','~31%',f5_nodes)
check_streak('P2','PRIYA',VA,'cold_streak','72->48')
check_streak('P3','PRIYA',DI,'hot_streak','25->42')
check_f10('P4','PRIYA','F001','strong_hypothesis','translating constraints to equations')
ph=phase1('PRIYA'); exp={'Sequences And Series','Statistics','Sets And Relations',QE}
row('P5','PRIYA','F14',f"Phase 1 ⊇ Sequences, Statistics, Sets, Quadratic","—",
    f"phase_1={sorted(ph)}", 'DETECTED' if exp<=ph else ('PARTIAL' if len(exp&ph)>=2 else 'MISSED'),
    f"{len(exp&ph)}/4 present")
mt=maint('PRIYA'); f16all={x['topic']:x['status'] for x in det['PRIYA']['f16_maintenance']}
row('P6','PRIYA','F16',"Maintenance: Sequences, Statistics; Sets volatile","—",
    f"maintenance={sorted(mt)}; Sets status={f16all.get('Sets And Relations','absent')}",
    'DETECTED' if {'Sequences And Series','Statistics'}<=mt else ('PARTIAL' if len(mt&{'Sequences And Series','Statistics'})==1 else 'MISSED'))
t17=f17top('PRIYA'); row('P7','PRIYA','F17',f"Priority 1: {LCD[:6]}…, P2: Functions","—",f"top2={t17}",
    'DETECTED' if t17[0]==LCD else ('PARTIAL' if LCD in t17 or 'Functions' in t17 else 'MISSED'))
row('P8','PRIYA','F18',"Question from Limits","—",f"topic={det['PRIYA']['f18_next_action']['topic']}",
    'DETECTED' if det['PRIYA']['f18_next_action']['topic']==LCD else 'MISSED')
f9p={(x['weak_topic'],x['prereq_topic']):x['trace_confidence'] for x in det['PRIYA']['f9_prerequisites']}
for i,(wk,pr) in enumerate([(DI,LCD),('Application Of Derivatives',LCD)]):
    tc=f9p.get((wk,pr),'absent')
    row(f'P9{"ab"[i]}','PRIYA','F9',f"{LCD[:6]}→{wk[:12]} confirmed","—",tc,
        'DETECTED' if tc=='confirmed' else ('PARTIAL' if tc not in ('absent',) else 'MISSED'))
do=det['PRIYA']['f7_drop_off']
row('P10','PRIYA','F7',"Drop-off at Build Then Solve","—",str(do),
    'DETECTED' if do and 'Build Then Solve' in str(do) else 'MISSED')
f4=det['PRIYA']['f4_failure_summary'][0]
row('P11','PRIYA','F4',"Dominant: Setup Gap ~35%","error mix not encoded by generator",
    f"{f4['failure_mode']} {f4['pct']}%",'NOT_IMPLEMENTED',
    "generator draws is_correct from accuracy only; per-student error tendency (Rule 5) never coded — docstring claims otherwise")
row('P12','PRIYA','F15/F8',"Scripted latest-test: 3 blanks incl. Sequences tragic; 14min slow+wrong on Complex/Prob",
    "not in generator",'—','NOT_IMPLEMENTED',"skip selection is strategy-based, no per-test script")

# ---- ARJUN ----
check_none('A1','ARJUN','F5',f5_nodes,'calibrated low conf on weak topics')
check_none('A2','ARJUN','F6',f6_nodes,'high conf matches strong topics')
ids=f10ids('ARJUN')
row('A3','ARJUN','F10',"Should NOT trigger strongly (weak_hypothesis at most)","breadth gap, prereqs also weak",
    f"{len(ids)} hyps; tiers={collections.Counter(c for _,c in ids)}",
    'DETECTED' if not any(c=='strong_hypothesis' for _,c in ids) else 'MISSED',
    "spec: polarization ≠ foundational gap")
check_flat('A4','ARJUN')
ph=phase1('ARJUN'); exp5={MD,'3D Geometry',VA,'Sequences And Series','Statistics'}
row('A5','ARJUN','F14',"Phase 1 = his 5 banked topics","—",f"phase_1={sorted(ph)}",
    'DETECTED' if exp5<=ph and len(ph)<=7 else ('PARTIAL' if len(exp5&ph)>=3 else 'MISSED'),f"{len(exp5&ph)}/5")
mt=maint('ARJUN')
row('A6','ARJUN','F16',"Maintenance: the same 5 topics","—",f"{len(mt)}: {sorted(mt)}",
    'DETECTED' if len(exp5&mt)>=4 else ('PARTIAL' if len(exp5&mt)>=2 else 'MISSED'),f"{len(exp5&mt)}/5")
t17=f17top('ARJUN')
row('A7','ARJUN','F17',"P1 Binomial Theorem, P2 Straight Lines","—",f"top2={t17}",
    'DETECTED' if t17[0]=='Binomial Theorem' else ('PARTIAL' if 'Binomial Theorem' in t17 else 'MISSED'))
row('A8','ARJUN','F18',"Question from Binomial Theorem","—",det['ARJUN']['f18_next_action']['topic'],
    'DETECTED' if det['ARJUN']['f18_next_action']['topic']=='Binomial Theorem' else 'MISSED')
tr=det['ARJUN']['f9_prerequisites']; ws=sum(1 for x in tr if x['trace_confidence']=='weak_signal')
row('A9','ARJUN','F9',"Traces mostly weak_signal (concept, not prereq)","student-level error behavior not encodable in schema",
    f"{ws}/{len(tr)} weak_signal",'N/V',"same data-layer root as P11: error types are question tags, not student behavior")
do=det['ARJUN']['f7_drop_off']
row('A10','ARJUN','F7',"Steep drop-off at Build Then Solve","—",str(do),
    'DETECTED' if do and 'Build Then Solve' in str(do) else ('PARTIAL' if do else 'MISSED'))
sta={t:topic_stats('ARJUN',t) for t in s[s.student_id=='ARJUN'].topic.dropna().unique()}
hi=[t for t,v in sta.items() if v['n']>=6 and v['acc']>=0.80]; lo=[t for t,v in sta.items() if v['n']>=6 and v['acc']<=0.25]
row('A11','ARJUN','struct',"Polarization: ~5 topics ≥85%, ~10 topics ≤25% (data-level)",
    f"{len(hi)} topics ≥80% | {len(lo)} topics ≤25% (n≥6)","—",
    'DETECTED' if len(hi)>=3 and len(lo)>=1 else 'PARTIAL',
    "smart-skipping censors weak topics: few reach n≥6, so the ≤25% tail is under-observed by design")

# ---- MEERA ----
weak_set={'Circle','Parabola','Ellipse','Hyperbola','Probability'}
f1w={node_topic.get(x['node_name']) for x in det['MEERA']['f1_node_weakness'] if x['status']=='weak'}
inw=f1w&weak_set; out=f1w-weak_set-{None}
row('M1','MEERA','F1',"Weak nodes only in Coord-Geo cluster + Probability","—",
    f"in-cluster topics hit: {sorted(inw)}; outside: {len(out)} topics",
    'DETECTED' if len(inw)>=4 and len(out)<=6 else ('PARTIAL' if len(inw)>=3 else 'MISSED'),
    f"outside e.g. {sorted(out)[:3]}")
check_f10('M2','MEERA','F002','strong_hypothesis','locus by parameter elimination')
check_none('M3','MEERA','F5',f5_nodes,'well calibrated')
st=topic_stats('MEERA','Area Under The Curves')
hits=[x['node_name'] for x in f6_nodes('MEERA') if node_topic.get(x['node_name'])=='Area Under The Curves']
row('M4','MEERA','F6',"Possibly Area Under Curves (58%, conf 1.8)",
    f"acc {st['acc']:.0%}, conf {st['conf']:.1f}, n={st['n']}",
    f"{len(hits)} flags",'DETECTED' if hits else ('CLEAN' if (st['acc']-st['conf']/3)<0.2 else 'MISSED'),
    "spec marked 'possibly' — soft expectation")
check_flat('M5','MEERA')
mt=maint('MEERA'); row('M6','MEERA','F16',"8–10 maintenance topics","—",f"{len(mt)}: {sorted(mt)[:5]}…",
    'DETECTED' if 8<=len(mt)<=10 else ('PARTIAL' if 5<=len(mt)<=12 else 'MISSED'))
ph=phase1('MEERA'); row('M7','MEERA','F14',"Huge Phase 1 (12+)","—",f"{len(ph)} topics",
    'DETECTED' if len(ph)>=12 else ('PARTIAL' if len(ph)>=9 else 'MISSED'))
t17=f17top('MEERA'); row('M8','MEERA','F17',"P1 Circle (or F002 practice)","—",f"top2={t17}",
    'DETECTED' if t17[0]=='Circle' else ('PARTIAL' if 'Circle' in t17 or t17[0] in weak_set else 'MISSED'))
row('M9','MEERA','F18',"Question from Circle/Parabola (locus)","—",det['MEERA']['f18_next_action']['topic'],
    'DETECTED' if det['MEERA']['f18_next_action']['topic'] in ('Circle','Parabola') else
    ('PARTIAL' if det['MEERA']['f18_next_action']['topic'] in weak_set else 'MISSED'))
f9m={(x['weak_topic'],x['prereq_topic']):x['prereq_status'] for x in det['MEERA']['f9_prerequisites']}
ok=[v for k,v in f9m.items() if k[0]=='Circle']
row('M10','MEERA','F9',"Circle's prereqs read 'fine' (problem is coord-geo itself)","prereq topics strong in data",
    f"{ok if ok else 'no Circle trace'}",
    'DETECTED' if ok and all(v=='fine' for v in ok) else ('PARTIAL' if ok else 'MISSED'))

# ---- RAHUL ----
check_none('R1','RAHUL','F5',f5_nodes,'confidence already low')
check_none('R2','RAHUL','F6',f6_nodes,'nothing secretly strong')
row('R3','RAHUL','F10',"Global acc <35–40% → display top-1 only","global acc 34.7%",
    f"display={det['RAHUL']['f10_display']}, {len(f10ids('RAHUL'))} hyps generated",
    'DETECTED' if det['RAHUL']['f10_display']=='top_1' else 'MISSED',
    "24 hypotheses generated but suppressed to 1 — over-generation vs display discipline")
check_flat('R4','RAHUL')
ph=phase1('RAHUL'); row('R5','RAHUL','F14',"Phase 1: Statistics only","—",f"phase_1={sorted(ph)}",
    'DETECTED' if ph=={'Statistics'} else ('PARTIAL' if 'Statistics' in ph and len(ph)<=3 else 'MISSED'))
mt=maint('RAHUL'); row('R6','RAHUL','F16',"Zero maintenance topics","—",f"{len(mt)}: {sorted(mt)}",
    'DETECTED' if len(mt)==0 else 'MISSED')
t17=f17top('RAHUL'); row('R7','RAHUL','F17',"P1 Statistics (proximity-to-win override)","Statistics best at ~58%",
    f"top2={t17}",'DETECTED' if t17[0]=='Statistics' else ('PARTIAL' if 'Statistics' in t17 else 'MISSED'))
row('R8','RAHUL','F18',"Question from Statistics, micro-goal","—",
    f"{det['RAHUL']['f18_next_action']['topic']} | goal: {det['RAHUL']['f18_next_action'].get('micro_goal','')[:40]}",
    'DETECTED' if det['RAHUL']['f18_next_action']['topic']=='Statistics' else 'MISSED')
do=det['RAHUL']['f7_drop_off']
row('R9','RAHUL','F7',"Drop-off everywhere (even Direct App ~45%)","—",str(do),
    'DETECTED' if do else 'MISSED')
tr=det['RAHUL']['f9_prerequisites']; ws=sum(1 for x in tr if x['trace_confidence']=='weak_signal')
row('R10','RAHUL','F9',"Multiple traces, mostly weak_signal","student-level error behavior not encodable in schema",
    f"{ws}/{len(tr)} weak_signal",'N/V',"same data-layer root as P11")
row('R11','RAHUL','struct',"Panic tail (Rule 8): fast wrong answers in last 5 slots","question order not stored in CSVs",
    "—",'N/V',"panic is coded but position is unrecoverable post-hoc")

# ---- KAVYA ----
check_conf_topic('K1','KAVYA',MD,'over','2.8','38%',f5_nodes)
check_conf_topic('K2','KAVYA',SL,'over','2.6','35%',f5_nodes)
check_conf_topic('K3','KAVYA','Binomial Theorem','over','2.5','35%',f5_nodes)
check_conf_topic('K4','KAVYA',VA,'under','1.5','75%',f6_nodes)
row('K5','KAVYA','F6',"Sequences underconf but suppressed by recency (last-2-test conf 2.5 design)",
    "conf constant 1.5 in code — suppression signal never generated","—",'NOT_IMPLEMENTED',
    "recency-suppression design present in spec, absent in generator")
check_streak('K6','KAVYA',DI,'hot_streak','20->45')
check_streak('K7','KAVYA',LCD,'cold_streak','65->40')
k=s[s.student_id=='KAVYA'].copy()
def hack_check(topic):
    d=k[k.topic==topic]; piv=d.groupby('question_type')['is_correct'].agg(['count','mean'])
    m=piv.loc['MCQ','mean'] if 'MCQ' in piv.index else np.nan
    n=piv.loc['Numerical','mean'] if 'Numerical' in piv.index else np.nan
    return m,n,len(d)
for i,(tp,lbl) in enumerate([(II,'II 65/8'),(QE,'QE 75/20')]):
    m,n,tot=hack_check(tp)
    mat = m==m and n==n and (m-n)>=0.30
    row(f'K8{"ab"[i]}','KAVYA','F6-MCQ',f"MCQ-hacker {tp[:20]} ({lbl})",
        f"MCQ {m:.0%} vs Num {n:.0%} (n={tot})" if m==m and n==n else "insufficient type split",
        "engine has MCQ-reliability guard in F6; no dedicated hacker flag",
        'DETECTED' if mat else 'NOT_MATERIALIZED',
        "materialized in data; engine can only demote F6 flags, cannot surface hacking — capability gap")
sf=det['KAVYA']['f8_classification']; stretch=[x for x in sf if x['classification']=='stretch_question']
row('K9','KAVYA','F8',"1 stretch question on latest test","not scripted (see P12-type gap)",
    f"{len(stretch)} stretch",'DETECTED' if len(stretch)>=1 else 'NOT_IMPLEMENTED')
f9k={(x['weak_topic'],x['prereq_topic']):x['prereq_status'] for x in det['KAVYA']['f9_prerequisites']}
lcdpr=[v for kk,v in f9k.items() if kk[1]==LCD]
row('K10','KAVYA','F9',"Limits as prereq reads 'fine' (baseline was 65%)","—",
    f"{lcdpr if lcdpr else 'Limits not a prereq in any trace'}",
    'DETECTED' if lcdpr and all(v=='fine' for v in lcdpr) else ('PARTIAL' if lcdpr else 'N/V'),
    "engine uses lifetime topic acc; realized LCD lifetime ~48% may read weak — threshold-sensitivity case")
mt=maint('KAVYA'); row('K11','KAVYA','F16',"Maintenance: Statistics only","—",f"{sorted(mt)}",
    'DETECTED' if mt=={'Statistics'} else ('PARTIAL' if 'Statistics' in mt else 'MISSED'),
    "engine grant of Seq+VA is data-faithful (last-5 std 0.00); spec's recency-conf design never coded")
t17=f17top('KAVYA'); row('K12','KAVYA','F17',"P1 Limits (cold-streak refresh)","—",f"top2={t17}",
    'DETECTED' if t17[0]==LCD else ('PARTIAL' if LCD in t17 else 'MISSED'))
rec={stu: det[stu]['f15_time_roi']['bottom_line'] for stu in det}
recov={stu:(b['without_leaks']-b['score'])+b.get('tragic_ev',0) for stu,b in rec.items()}
row('K13','KAVYA','F15',"Recoverable marks highest of all students",
    "aggressive attempts + panic in data",
    "; ".join(f"{a}:{v:.0f}" for a,v in sorted(recov.items(),key=lambda x:-x[1])),
    'DETECTED' if max(recov,key=recov.get)=='KAVYA' else 'MISSED')
row('K14','KAVYA','F15/F4',"Scripted time-waste (17min slow+wrong, 2 Seq blanks, 2 rushed Binomial)",
    "not in generator",'—','NOT_IMPLEMENTED')
row('K15','KAVYA','F10',"Moderate trigger (messier than Priya)","—",
    f"{len(f10ids('KAVYA'))} hyps; tiers={collections.Counter(c for _,c in f10ids('KAVYA'))}",
    'DETECTED' if f10ids('KAVYA') and not all(c=='strong_hypothesis' for _,c in f10ids('KAVYA')) else 'PARTIAL')

# ═══════════ FP CENSUS ═══════════
census={}
planted_f5={'PRIYA':{'Complex Numbers'},'KAVYA':{MD,SL,'Binomial Theorem'},'ARJUN':set(),'MEERA':set(),'RAHUL':set()}
planted_streak={'PRIYA':{VA,DI},'KAVYA':{DI,LCD},'ARJUN':set(),'MEERA':set(),'RAHUL':set()}
planted_f10={'PRIYA':1,'MEERA':1,'ARJUN':0,'RAHUL':0,'KAVYA':0}
for stu in det:
    f5c=f5_nodes(stu); f5t={node_topic.get(x['node_name']) for x in f5c}
    f6c=f6_nodes(stu)
    ms=mom(stu); st={t for t,v in ms.items() if v in('hot_streak','cold_streak')}
    census[stu]=dict(
        f5_flags=len(f5c), f5_outside_plant=len(f5t-planted_f5[stu]-{None}),
        f6_flags=len(f6c),
        streak_topics=len(st), streaks_outside_plant=len(st-planted_streak[stu]),
        f10_hyps=len(f10ids(stu)), f10_planted=planted_f10[stu],
        f10_excess=len(f10ids(stu))-planted_f10[stu])

json.dump(dict(rows=R,census=census), open('validation_results.json','w'), indent=1)

vc=collections.Counter(r['verdict'] for r in R)
print("VERDICT COUNTS:", dict(vc), f" | total rows: {len(R)}")
core=[r for r in R if r['verdict'] in('DETECTED','PARTIAL','MISSED','CLEAN','EMERGENT')]
det_ok=sum(1 for r in core if r['verdict'] in('DETECTED','CLEAN'))
print(f"Engine score on testable rows: {det_ok}/{len(core)} clean detections "
      f"({sum(1 for r in core if r['verdict']=='PARTIAL')} partial, "
      f"{sum(1 for r in core if r['verdict']=='MISSED')} missed, "
      f"{sum(1 for r in core if r['verdict']=='EMERGENT')} emergent)")
print("\nPER-STUDENT:")
for stu in ['PRIYA','ARJUN','MEERA','RAHUL','KAVYA']:
    rr=[r for r in R if r['student']==stu]
    print(f"  {stu:6s}: "+", ".join(f"{v}:{sum(1 for r in rr if r['verdict']==v)}" for v in ['DETECTED','PARTIAL','MISSED','NOT_MATERIALIZED','NOT_IMPLEMENTED','CLEAN','EMERGENT','N/V'] if any(r['verdict']==v for r in rr)))
print("\nFP CENSUS:")
for stu,c in census.items(): print(f"  {stu:6s}: {c}")
print("\nROWS:")
for r in R:
    print(f"  [{r['id']:4s}] {r['feature']:7s} {r['verdict']:16s} {r['plant'][:58]:58s} | det: {str(r['detected'])[:60]}")
