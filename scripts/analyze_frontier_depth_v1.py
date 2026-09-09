#!/usr/bin/env python3
"""Deep, non-destructive diagnostics for frozen PUR-FRONTIER V1.

This script never changes the frozen FRONTIER V1 decision. It analyzes the
already-frozen frontier table to quantify decision phase boundaries, robustness
cliffs, objective-structure sensitivity, weight-stability basins, and a Pareto
set. All results remain algorithmic properties of synthetic PUR_SIM_V1.
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
import numpy as np
import pandas as pd

CID='cid'
BROAD={'eta80':(.85,10.0),'eta120':(.16,.80),'ratio':(6.0,13.0)}
PREF={'eta80':(2.2,5.5),'eta120':(.30,.60),'ratio':(7.0,9.5)}
Q={'eta80':1.0,'eta120':1.0,'ratio':2.0}
CENTER={k:math.sqrt(a*b) for k,(a,b) in PREF.items()}


def mdi_phase(df: pd.DataFrame, robust: bool, lo=.30, hi=.40) -> pd.DataFrame:
    point_cols=['check_nco_oh','check_eta80_broad','check_eta120_broad','check_ratio_broad',
                'check_eta80_preferred','check_eta120_preferred','check_ratio_preferred',
                'check_chemistry_in_domain']
    base=df[point_cols].all(axis=1) & (df.mdi_fraction<=.49)
    score='robust_score' if robust else 'property_score'
    if robust:
        base &= df.robust_check_interval_inside_broad & df.robust_check_domain_ratio_max
    cur=lo; out=[]
    while cur <= hi + 1e-12:
        cand=df[base & (df.mdi_fraction>=cur)]
        if cand.empty: break
        win=cand.sort_values([score,CID]).iloc[0]
        upper=min(float(win.mdi_fraction),hi)
        out.append({'floor_lo':cur,'floor_hi_inclusive':upper,'winner':win[CID],
                    'blend':win.blend,'nco_oh':float(win.nco_oh),
                    'mdi_fraction':float(win.mdi_fraction),'score':float(win[score])})
        if upper >= hi-1e-12: break
        cur=np.nextafter(upper,np.inf)
    return pd.DataFrame(out)


def broad_smax(row: pd.Series) -> tuple[float,str]:
    vals=[]
    for k in ('eta80','eta120','ratio'):
        y=float(row[k]); r=float(row.unc_radius); q=Q[k]; lo,hi=BROAD[k]
        s=min((math.log10(y)-math.log10(lo))/(q*r),
              (math.log10(hi)-math.log10(y))/(q*r))
        vals.append((s,k))
    return min(vals)


def preferred_smax(row: pd.Series) -> tuple[float,str]:
    vals=[]
    for k in ('eta80','eta120','ratio'):
        y=float(row[k]); r=float(row.unc_radius); q=Q[k]; lo,hi=PREF[k]
        s=min((math.log10(y)-math.log10(lo))/(q*r),
              (math.log10(hi)-math.log10(y))/(q*r))
        vals.append((s,k))
    return min(vals)


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--frontier',default='results/frontier_v1/frontier_table.csv')
    ap.add_argument('--out',default='results/frontier_depth_v1')
    ap.add_argument('--weight-samples',type=int,default=50000)
    ap.add_argument('--seed',type=int,default=20260909)
    args=ap.parse_args()
    df=pd.read_csv(args.frontier)
    out=Path(args.out); out.mkdir(parents=True,exist_ok=True)

    l0=df.sort_values(['property_score',CID]).iloc[0]
    l1=df[df.feasible_nominal].sort_values(['property_score',CID]).iloc[0]
    l2=df[df.feasible_robust].sort_values(['robust_score',CID]).iloc[0]

    rankset=df[df.feasible_robust].copy()
    rankset['nominal_rank_recalc']=rankset.property_score.rank(method='min')
    rankset['robust_rank_recalc']=rankset.robust_score.rank(method='min')
    rho=float(rankset[['nominal_rank_recalc','robust_rank_recalc']].corr(method='spearman').iloc[0,1])
    tau=float(rankset[['nominal_rank_recalc','robust_rank_recalc']].corr(method='kendall').iloc[0,1])
    a=rankset.sort_values('nominal_rank_recalc').robust_rank_recalc.to_numpy()
    inversions=int(sum(np.sum(a[i+1:]<a[i]) for i in range(len(a)-1)))
    total_pairs=len(a)*(len(a)-1)//2

    mdi_phase(df,False).to_csv(out/'mdi_floor_phase_nominal.csv',index=False)
    mdi_phase(df,True).to_csv(out/'mdi_floor_phase_robust.csv',index=False)

    U=df[df.feasible_nominal & (df.domain_ratio<=1.0)].copy()
    absd={k:np.abs(np.log10(U[k]/CENTER[k])) for k in ('eta80','eta120','ratio')}
    U['A']=sum(absd[k]**2 for k in absd)
    U['B']=sum(2*absd[k]*Q[k]*U.unc_radius for k in absd)
    U['C']=sum((Q[k]*U.unc_radius)**2 for k in absd)
    sx=U.apply(broad_smax,axis=1,result_type='expand')
    U['smax_broad']=sx[0].astype(float); U['bottleneck_broad']=sx[1]
    phase=[]
    for s in np.arange(0,2.20001,.0025):
        v=U[U.smax_broad>=s-1e-12]
        if v.empty:
            phase.append({'scale':s,'winner':None,'n_admissible':0,'winner_score':np.nan})
        else:
            score=v.A+v.B*s+v.C*s*s; idx=score.idxmin()
            phase.append({'scale':s,'winner':v.loc[idx,CID],'n_admissible':len(v),'winner_score':float(score.loc[idx])})
    phase=pd.DataFrame(phase); phase.to_csv(out/'uncertainty_scale_sweep.csv',index=False)
    seg=[]
    for r in phase.itertuples(index=False):
        if seg and seg[-1]['winner']==r.winner: seg[-1]['s_hi']=r.scale
        else: seg.append({'s_lo':r.scale,'s_hi':r.scale,'winner':r.winner})
    pd.DataFrame(seg).to_csv(out/'uncertainty_scale_phase.csv',index=False)

    def qcoef(id_):
        z=U[U[CID]==id_].iloc[0]; return float(z.A),float(z.B),float(z.C),float(z.smax_broad)
    qa=qcoef(str(l1[CID])); qb=qcoef(str(l2[CID]))
    roots=np.roots([qa[2]-qb[2],qa[1]-qb[1],qa[0]-qb[0]])
    cross=[float(x.real) for x in roots if abs(x.imag)<1e-10 and x.real>=0]

    strict=[]
    for _,row in df[df.feasible_nominal].iterrows():
        s,b=preferred_smax(row)
        strict.append({CID:row[CID],'strict_smax':s,'strict_bottleneck':b,
                       'blend':row.blend,'nco_oh':row.nco_oh,'mdi_fraction':row.mdi_fraction})
    strict=pd.DataFrame(strict).sort_values('strict_smax',ascending=False)
    strict.to_csv(out/'strict_preferred_certification.csv',index=False)

    h120=.5*math.log10(PREF['eta120'][1]/PREF['eta120'][0])
    hr=.5*math.log10(PREF['ratio'][1]/PREF['ratio'][0])
    d120=np.log10(df.eta120/CENTER['eta120']); dr=np.log10(df.ratio/CENTER['ratio'])
    df['state_score']=(d120/h120)**2+(dr/hr)**2
    df['state_robust_score']=((np.abs(d120)+df.unc_radius)/h120)**2+((np.abs(dr)+2*df.unc_radius)/hr)**2
    state_l0=df.sort_values(['state_score',CID]).iloc[0]
    state_l1=df[df.feasible_nominal].sort_values(['state_score',CID]).iloc[0]
    state_l2=df[df.feasible_robust].sort_values(['state_robust_score',CID]).iloc[0]
    sr=df[df.feasible_robust].copy()
    sr['state_nominal_rank']=sr.state_score.rank(method='min')
    sr['state_robust_rank']=sr.state_robust_score.rank(method='min')
    sr[[CID,'blend','nco_oh','mdi_fraction','property_score','robust_score','state_score','state_robust_score','state_nominal_rank','state_robust_rank']].sort_values('state_robust_rank').to_csv(out/'rheology_state_rank.csv',index=False)

    rng=np.random.default_rng(args.seed); W=rng.dirichlet(np.ones(3),size=args.weight_samples)
    def weight_counts(mask,robust):
        x=df[mask]
        if robust:
            rr=x.unc_radius.to_numpy()
            D=np.column_stack(((np.abs(np.log10(x.eta80/CENTER['eta80']))+rr)**2,
                               (np.abs(np.log10(x.eta120/CENTER['eta120']))+rr)**2,
                               (np.abs(np.log10(x.ratio/CENTER['ratio']))+2*rr)**2))
        else:
            D=np.column_stack((np.log10(x.eta80/CENTER['eta80'])**2,
                               np.log10(x.eta120/CENTER['eta120'])**2,
                               np.log10(x.ratio/CENTER['ratio'])**2))
        ids=x[CID].to_numpy(); winners=[]
        for i in range(0,len(W),5000): winners.extend(ids[np.argmin(W[i:i+5000]@D.T,axis=1)])
        c=pd.Series(winners).value_counts().rename_axis('winner').reset_index(name='count')
        c['fraction']=c['count']/len(W); return c
    wc_nom=weight_counts(df.feasible_nominal,False); wc_rob=weight_counts(df.feasible_robust,True)
    wc_nom.to_csv(out/'objective_weight_stability_nominal.csv',index=False)
    wc_rob.to_csv(out/'objective_weight_stability_robust.csv',index=False)

    P=df[df.feasible_robust].copy()
    vals=np.column_stack((np.abs(np.log10(P.eta80/CENTER['eta80'])),
                          np.abs(np.log10(P.eta120/CENTER['eta120'])),
                          np.abs(np.log10(P.ratio/CENTER['ratio'])),P.unc_radius,P.domain_ratio))
    nd=np.ones(len(P),dtype=bool)
    for i in range(len(P)):
        dom=np.all(vals<=vals[i]+1e-15,axis=1)&np.any(vals<vals[i]-1e-15,axis=1); dom[i]=False
        if dom.any(): nd[i]=False
    P['pareto5']=nd
    P[[CID,'blend','nco_oh','mdi_fraction','eta80','eta120','ratio','unc_radius','domain_ratio','pareto5','property_score','robust_score']].to_csv(out/'pareto5_frontier.csv',index=False)

    delta=math.log10(CENTER['eta120']*CENTER['ratio']/CENTER['eta80'])
    summary={
      'frozen_reproduction':{'L0':l0[CID],'L1':l1[CID],'L2':l2[CID],
        'n_nominal_feasible':int(df.feasible_nominal.sum()),'n_robust_admissible':int(df.feasible_robust.sum())},
      'ranking_propagation':{'n':len(rankset),'spearman':rho,'kendall':tau,'pairwise_inversions':inversions,'total_pairs':total_pairs,'inversion_fraction':inversions/total_pairs},
      'uncertainty_scale':{'L1_L2_score_crossover_roots':cross,'global_max_broad_scale':float(U.smax_broad.max()),'last_candidate':U.loc[U.smax_broad.idxmax(),CID],'last_bottleneck':U.loc[U.smax_broad.idxmax(),'bottleneck_broad']},
      'strict_preferred_certification':{'n_at_scale_1':int((strict.strict_smax>=1).sum()),'n_nominal':len(strict),'best_candidate':strict.iloc[0][CID],'best_scale':float(strict.iloc[0].strict_smax),'required_uncertainty_reduction_fraction':float(1-strict.iloc[0].strict_smax),'bottleneck_counts':strict.strict_bottleneck.value_counts().to_dict()},
      'objective_geometry':{'constraint':'eta80 = eta120 * ratio','center_inconsistency_delta_log10':delta,'J3_induced_metric_on_eta120_ratio':[[2,1],[1,2]],'metric_eigenvalues':[3,1],'principal_weight_ratio':3.0,'normalized_state_halfwidths':{'eta120':h120,'ratio':hr},'state_winners':{'L0':state_l0[CID],'L1':state_l1[CID],'L2':state_l2[CID]}},
      'weight_stability':{'samples':len(W),'seed':args.seed,'nominal_top':wc_nom.head(12).to_dict('records'),'robust_top':wc_rob.head(15).to_dict('records')},
      'pareto5':{'n_non_dominated':int(nd.sum()),'n_robust_admissible':len(P)},
      'claim_boundary':'All FRONTIER-DEPTH outputs are decision-geometry properties of synthetic PUR_SIM_V1, not experimental polyurethane laws.'
    }
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
