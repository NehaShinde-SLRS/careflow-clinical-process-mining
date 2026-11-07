"""
CareFlow Clinical Process Mining — Petri Net Diagnostic Loop, Interleaving & In-Memory Conformance Test
File: scripts/test_petri_net_loops.py
Role: Member 3 — Data Engineering & Process Mining
Milestone: Day 12 — Process Conformance Verification
Date: 7 November 2026

Safety & Integrity Guarantees:
- Strictly Read-Only: Reads 'data/careflow_event_log.csv' in memory only.
- Zero File Writes: No files or outputs are created or modified on disk.
- Zero Cloud/Git Operations: Pure local Python execution.
- Zero Label Duplication: Every visible clinical activity corresponds to exactly ONE transition.
- Deterministic Sequence: Preserves verified 'event_order' when timestamps are identical.
- Assertion-Backed Verification: Fails immediately if any normative trace or ordering rule is violated.
"""

import time
import pandas as pd
import numpy as np
import pm4py
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.petri_net.utils import petri_utils
from pm4py.objects.log.obj import EventLog, Trace, Event

def build_normative_petri_net():
    """
    Constructs the Normative Reference Petri Net for CareFlow OPD.
    
    Architectural Principles:
    1. Zero Duplicate Labels: Exactly one transition per visible clinical activity name.
       - Appointment Registration: t_reg
       - Prescription Consultation Started: t_cs
       - Prescription Consultation Completed: t_cc
       - Lab Test Started: t_ls
       - Lab Test Completed: t_lc
       - Imaging Started: t_is
       - Imaging Completed: t_ic
       - Pharmacy Dispensation Started: t_ps
       - Pharmacy Dispensation Completed: t_pc
    
    2. Parallel Diagnostic Sub-process (AND-split / AND-join):
       - Branch 1: Lab (t_ls -> p_lab_active -> t_lc -> p_lab_out) OR skip (t_skip_lab)
         * Repeated cycles: silent loopback t_lab_cycle from p_lab_out to p_lab_in
       - Branch 2: Imaging (t_is -> p_img_active -> t_ic -> p_img_out) OR skip (t_skip_img)
         * Repeated cycles: silent loopback t_img_cycle from p_img_out to p_img_in
       - Synchronized at t_diag_join into p_post_diag.
       - Supports: Lab only, Imaging only, Both in either order, Neither.
       - Strictly enforces Start -> Complete cycles (Completed cannot occur without Started).
    
    3. Re-Consultation Review:
       - Modeled via silent loopback t_reconsult from p_post_diag back to p_reg.
       - Re-uses t_cs and t_cc without duplicate transition labels.
    
    4. Clean Pharmacy Paths:
       - Entry: p_pre_pharm -> t_enter_pharm (silent) -> p_pharm_in
       - Direct Skip: p_pre_pharm -> t_skip_pharm (silent) -> sink
       - Normal Cycle: p_pharm_in -> t_ps -> p_pharm_active -> t_pc -> p_pharm_out
       - Completion to Sink: p_pharm_out -> t_pharm_done (silent) -> sink
       - Repeated Cycles: p_pharm_out -> t_pharm_cycle (silent) -> p_pharm_in
    """
    net = PetriNet("CareFlow_Normative_Reference_Model")
    
    # 1. Places
    place_names = [
        'source', 'p_reg', 'p_cons_active', 'p_post_cons',
        'p_lab_in', 'p_lab_active', 'p_lab_out',
        'p_img_in', 'p_img_active', 'p_img_out',
        'p_post_diag', 'p_pre_pharm',
        'p_pharm_in', 'p_pharm_active', 'p_pharm_out',
        'sink'
    ]
    places = {p: PetriNet.Place(p) for p in place_names}
    for p in places.values():
        net.places.add(p)
        
    im = Marking({places['source']: 1})
    fm = Marking({places['sink']: 1})

    # 2. Transitions (Strictly Unique Visible Labels)
    transitions = {
        # Registration & Initial Consultation
        't_reg': PetriNet.Transition('t_reg', 'Appointment Registration'),
        't_cs': PetriNet.Transition('t_cs', 'Prescription Consultation Started'),
        't_cc': PetriNet.Transition('t_cc', 'Prescription Consultation Completed'),
        
        # Diagnostic Parallel Split & Join (Silent)
        't_diag_split': PetriNet.Transition('t_diag_split', None),
        't_diag_join': PetriNet.Transition('t_diag_join', None),
        
        # Lab Branch
        't_ls': PetriNet.Transition('t_ls', 'Lab Test Started'),
        't_lc': PetriNet.Transition('t_lc', 'Lab Test Completed'),
        't_skip_lab': PetriNet.Transition('t_skip_lab', None),
        't_lab_cycle': PetriNet.Transition('t_lab_cycle', None),
        
        # Imaging Branch
        't_is': PetriNet.Transition('t_is', 'Imaging Started'),
        't_ic': PetriNet.Transition('t_ic', 'Imaging Completed'),
        't_skip_img': PetriNet.Transition('t_skip_img', None),
        't_img_cycle': PetriNet.Transition('t_img_cycle', None),
        
        # Re-Consultation Review (Silent Loopback to p_reg)
        't_reconsult': PetriNet.Transition('t_reconsult', None),
        't_to_pharm': PetriNet.Transition('t_to_pharm', None),
        
        # Pharmacy Branch
        't_enter_pharm': PetriNet.Transition('t_enter_pharm', None),
        't_skip_pharm': PetriNet.Transition('t_skip_pharm', None),
        't_ps': PetriNet.Transition('t_ps', 'Pharmacy Dispensation Started'),
        't_pc': PetriNet.Transition('t_pc', 'Pharmacy Dispensation Completed'),
        't_pharm_cycle': PetriNet.Transition('t_pharm_cycle', None),
        't_pharm_done': PetriNet.Transition('t_pharm_done', None)
    }
    for t in transitions.values():
        net.transitions.add(t)

    # 3. Arcs
    # Registration & Initial Doctor Consultation
    petri_utils.add_arc_from_to(places['source'], transitions['t_reg'], net)
    petri_utils.add_arc_from_to(transitions['t_reg'], places['p_reg'], net)
    petri_utils.add_arc_from_to(places['p_reg'], transitions['t_cs'], net)
    petri_utils.add_arc_from_to(transitions['t_cs'], places['p_cons_active'], net)
    petri_utils.add_arc_from_to(places['p_cons_active'], transitions['t_cc'], net)
    petri_utils.add_arc_from_to(transitions['t_cc'], places['p_post_cons'], net)

    # Parallel Diagnostic Split (Concurrent Lab & Imaging)
    petri_utils.add_arc_from_to(places['p_post_cons'], transitions['t_diag_split'], net)
    petri_utils.add_arc_from_to(transitions['t_diag_split'], places['p_lab_in'], net)
    petri_utils.add_arc_from_to(transitions['t_diag_split'], places['p_img_in'], net)

    # Lab branch with complete cycle loopback
    petri_utils.add_arc_from_to(places['p_lab_in'], transitions['t_ls'], net)
    petri_utils.add_arc_from_to(transitions['t_ls'], places['p_lab_active'], net)
    petri_utils.add_arc_from_to(places['p_lab_active'], transitions['t_lc'], net)
    petri_utils.add_arc_from_to(transitions['t_lc'], places['p_lab_out'], net)
    petri_utils.add_arc_from_to(places['p_lab_in'], transitions['t_skip_lab'], net)
    petri_utils.add_arc_from_to(transitions['t_skip_lab'], places['p_lab_out'], net)
    # Complete Lab Cycle: p_lab_out -> t_lab_cycle -> p_lab_in
    petri_utils.add_arc_from_to(places['p_lab_out'], transitions['t_lab_cycle'], net)
    petri_utils.add_arc_from_to(transitions['t_lab_cycle'], places['p_lab_in'], net)

    # Imaging branch with complete cycle loopback
    petri_utils.add_arc_from_to(places['p_img_in'], transitions['t_is'], net)
    petri_utils.add_arc_from_to(transitions['t_is'], places['p_img_active'], net)
    petri_utils.add_arc_from_to(places['p_img_active'], transitions['t_ic'], net)
    petri_utils.add_arc_from_to(transitions['t_ic'], places['p_img_out'], net)
    petri_utils.add_arc_from_to(places['p_img_in'], transitions['t_skip_img'], net)
    petri_utils.add_arc_from_to(transitions['t_skip_img'], places['p_img_out'], net)
    # Complete Imaging Cycle: p_img_out -> t_img_cycle -> p_img_in
    petri_utils.add_arc_from_to(places['p_img_out'], transitions['t_img_cycle'], net)
    petri_utils.add_arc_from_to(transitions['t_img_cycle'], places['p_img_in'], net)

    # Diagnostic Join
    petri_utils.add_arc_from_to(places['p_lab_out'], transitions['t_diag_join'], net)
    petri_utils.add_arc_from_to(places['p_img_out'], transitions['t_diag_join'], net)
    petri_utils.add_arc_from_to(transitions['t_diag_join'], places['p_post_diag'], net)

    # Re-Consultation Review: Loops back to p_reg
    petri_utils.add_arc_from_to(places['p_post_diag'], transitions['t_reconsult'], net)
    petri_utils.add_arc_from_to(transitions['t_reconsult'], places['p_reg'], net)
    
    # Progress to Pharmacy stage
    petri_utils.add_arc_from_to(places['p_post_diag'], transitions['t_to_pharm'], net)
    petri_utils.add_arc_from_to(transitions['t_to_pharm'], places['p_pre_pharm'], net)

    # Pharmacy Paths
    # 1. Direct Skip (no pharmacy): p_pre_pharm -> t_skip_pharm -> sink
    petri_utils.add_arc_from_to(places['p_pre_pharm'], transitions['t_skip_pharm'], net)
    petri_utils.add_arc_from_to(transitions['t_skip_pharm'], places['sink'], net)
    
    # 2. Enter Pharmacy: p_pre_pharm -> t_enter_pharm -> p_pharm_in
    petri_utils.add_arc_from_to(places['p_pre_pharm'], transitions['t_enter_pharm'], net)
    petri_utils.add_arc_from_to(transitions['t_enter_pharm'], places['p_pharm_in'], net)
    
    # 3. Pharmacy Dispensation Cycle
    petri_utils.add_arc_from_to(places['p_pharm_in'], transitions['t_ps'], net)
    petri_utils.add_arc_from_to(transitions['t_ps'], places['p_pharm_active'], net)
    petri_utils.add_arc_from_to(places['p_pharm_active'], transitions['t_pc'], net)
    petri_utils.add_arc_from_to(transitions['t_pc'], places['p_pharm_out'], net)
    
    # 4. Pharmacy Completion: p_pharm_out -> t_pharm_done -> sink
    petri_utils.add_arc_from_to(places['p_pharm_out'], transitions['t_pharm_done'], net)
    petri_utils.add_arc_from_to(transitions['t_pharm_done'], places['sink'], net)
    
    # 5. Repeated Pharmacy Cycle: p_pharm_out -> t_pharm_cycle -> p_pharm_in
    petri_utils.add_arc_from_to(places['p_pharm_out'], transitions['t_pharm_cycle'], net)
    petri_utils.add_arc_from_to(transitions['t_pharm_cycle'], places['p_pharm_in'], net)

    return net, im, fm

def run_in_memory_trace_tests(net, im, fm):
    """
    Validates explicit in-memory test traces representing all normative clinical flows:
    1. Lab only
    2. Imaging only
    3. Both Lab and Imaging (Lab first)
    4. Both Lab and Imaging (Imaging first)
    5. Neither diagnostic branch (Consultation only)
    6. Repeated Lab cycles (Start -> Complete -> Start -> Complete)
    7. Repeated Imaging cycles (Start -> Complete -> Start -> Complete)
    8. Repeated Pharmacy cycles (Start -> Complete -> Start -> Complete)
    9. Post-diagnostic Re-consultation Review (Consult -> Lab -> Consult -> Pharmacy)
    """
    print("\n[Step 1/3] Running Explicit In-Memory Trace Validation Suite (9 Traces)...")
    
    test_cases = [
        ("1. Lab Only", [
            'Appointment Registration',
            'Prescription Consultation Started',
            'Prescription Consultation Completed',
            'Lab Test Started',
            'Lab Test Completed'
        ]),
        ("2. Imaging Only", [
            'Appointment Registration',
            'Prescription Consultation Started',
            'Prescription Consultation Completed',
            'Imaging Started',
            'Imaging Completed'
        ]),
        ("3. Both (Lab then Imaging)", [
            'Appointment Registration',
            'Prescription Consultation Started',
            'Prescription Consultation Completed',
            'Lab Test Started',
            'Lab Test Completed',
            'Imaging Started',
            'Imaging Completed'
        ]),
        ("4. Both (Imaging then Lab)", [
            'Appointment Registration',
            'Prescription Consultation Started',
            'Prescription Consultation Completed',
            'Imaging Started',
            'Imaging Completed',
            'Lab Test Started',
            'Lab Test Completed'
        ]),
        ("5. Neither (Consultation Only)", [
            'Appointment Registration',
            'Prescription Consultation Started',
            'Prescription Consultation Completed'
        ]),
        ("6. Repeated Lab Cycles", [
            'Appointment Registration',
            'Prescription Consultation Started',
            'Prescription Consultation Completed',
            'Lab Test Started',
            'Lab Test Completed',
            'Lab Test Started',
            'Lab Test Completed'
        ]),
        ("7. Repeated Imaging Cycles", [
            'Appointment Registration',
            'Prescription Consultation Started',
            'Prescription Consultation Completed',
            'Imaging Started',
            'Imaging Completed',
            'Imaging Started',
            'Imaging Completed'
        ]),
        ("8. Repeated Pharmacy Cycles", [
            'Appointment Registration',
            'Prescription Consultation Started',
            'Prescription Consultation Completed',
            'Pharmacy Dispensation Started',
            'Pharmacy Dispensation Completed',
            'Pharmacy Dispensation Started',
            'Pharmacy Dispensation Completed'
        ]),
        ("9. Post-Diagnostic Re-Consultation", [
            'Appointment Registration',
            'Prescription Consultation Started',
            'Prescription Consultation Completed',
            'Lab Test Started',
            'Lab Test Completed',
            'Prescription Consultation Started',
            'Prescription Consultation Completed',
            'Pharmacy Dispensation Started',
            'Pharmacy Dispensation Completed'
        ])
    ]
    
    all_passed = True
    for name, act_seq in test_cases:
        trace = Trace()
        for a in act_seq:
            e = Event()
            e['concept:name'] = a
            trace.append(e)
            
        test_log = EventLog()
        test_log.append(trace)
        
        replay_res = pm4py.conformance_diagnostics_token_based_replay(test_log, net, im, fm)[0]
        is_fit = replay_res['trace_is_fit']
        fitness = replay_res['trace_fitness']
        reached = replay_res['reached_marking']
        missing = replay_res['missing_tokens']
        remaining = replay_res['remaining_tokens']
        
        # Verify reached marking is sink:1
        reached_sink = (reached == fm)
        status = "PASS" if is_fit and missing == 0 and remaining == 0 and reached_sink else "FAIL"
        if status == "FAIL":
            all_passed = False
            
        print(f"  * {name:38s} | Status: {status:4s} | Fitness: {fitness:.2f} | Missing: {missing} | Remaining: {remaining} | Final: {reached}")

    assert all_passed, "Critical Assertion Failed: One or more normative clinical pathways failed replay!"
    print("\n  >>> All 9 normative clinical pathway test traces PASSED with 100% Token Replay Fitness and sink reachability!")

def verify_timestamp_and_event_order():
    """
    Verifies that explicit event_order is strictly preserved after PM4Py conversion,
    especially when events share identical timestamps.
    """
    print("\n[Step 2/3] Verifying Clinical Sequence Preservation on Real Co-Occurring Timestamps...")
    df = pd.read_csv("data/careflow_event_log.csv")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # 1. Validate event_order integrity (Nulls, Duplicates, and Non-negative Bound)
    null_order_count = int(df['event_order'].isnull().sum())
    print(f"  * Total Rows Inspected: {len(df):,}")
    print(f"  * Null 'event_order' count: {null_order_count} (Must be exactly 0)")
    assert null_order_count == 0, f"Assertion Error: Found {null_order_count} null event_order records!"
    
    dup_order_count = int(df.duplicated(subset=['case_id', 'event_order']).sum())
    print(f"  * Duplicate 'event_order' within same case: {dup_order_count} (Must be exactly 0)")
    assert dup_order_count == 0, f"Assertion Error: Found {dup_order_count} duplicate event_order within cases!"
    
    min_order = int(df['event_order'].min())
    print(f"  * Min 'event_order' value:   {min_order} (Must be >= 0)")
    assert min_order >= 0, f"Assertion Error: Minimum event_order ({min_order}) is negative (< 0)!"

    # 2. Sort strictly by case_id, timestamp, and event_order
    df = df.sort_values(by=['case_id', 'timestamp', 'event_order'], ascending=[True, True, True])
    
    # 3. Validate Microsecond Tie-Breaker Assumptions:
    # Proof of Preservation:
    # - Original timestamps are at minute resolution (delta >= 60,000,000 us for distinct timestamps).
    # - Maximum event_order is < 100 (delta <= 100 us).
    # - 100 us << 60,000,000 us, so chronological ordering between distinct minutes is 100% preserved.
    # - For equal timestamps (delta = 0 us), microsecond ordering strictly follows event_order.
    
    # Assumption A: Timestamp resolution is at least 1 minute (no sub-minute seconds or microseconds)
    sub_minute_count = int(((df['timestamp'].dt.second != 0) | (df['timestamp'].dt.microsecond != 0)).sum())
    print(f"  * Sub-minute Timestamps:     {sub_minute_count} (Must be exactly 0)")
    assert sub_minute_count == 0, f"Assertion Error: Found {sub_minute_count} timestamps with sub-minute resolution!"
    
    # Assumption B: Minimum positive delta between distinct timestamps within cases is >= 60s (60,000,000 us)
    raw_case_diffs = df.groupby('case_id')['timestamp'].diff().dropna()
    pos_deltas = raw_case_diffs[raw_case_diffs > pd.Timedelta(0)]
    assert not pos_deltas.empty, "Assertion Error: 'pos_deltas' is empty (no positive timestamp progression found within cases); timestamp-gap assumption cannot be verified!"
    min_delta_us = int(pos_deltas.min().total_seconds() * 1_000_000)
    print(f"  * Min Distinct Timestamp Gap:{min_delta_us:,} us ({pos_deltas.min()}) (Must be >= 60,000,000 us)")
    assert min_delta_us >= 60_000_000, f"Assertion Error: Minimum positive timestamp delta ({min_delta_us} us) < 60,000,000 us!"
    
    # Assumption C: Maximum event_order is < 100 and strictly less than min_delta_us
    max_order = int(df['event_order'].max())
    print(f"  * Max 'event_order' value:   {max_order} (Must be < 100 and < {min_delta_us:,} us)")
    assert max_order < 100, f"Assertion Error: Maximum event_order ({max_order}) exceeds assumed bound (< 100)!"
    assert max_order < min_delta_us, f"Assertion Error: Maximum event_order ({max_order} us) >= min timestamp delta ({min_delta_us} us)!"
    
    # Apply monotonic microsecond tie-breaker
    df['timestamp_monotonic'] = df['timestamp'] + pd.to_timedelta(df['event_order'], unit='us')
    
    # Verify non-decreasing monotonicity within each case
    diffs = df.groupby('case_id')['timestamp_monotonic'].diff()
    neg_diffs = int((diffs < pd.Timedelta(0)).sum())
    print(f"  * Monotonic Inversion Check: {neg_diffs} negative timestamp diffs detected (Must be 0)")
    assert neg_diffs == 0, "Assertion Error: Negative timestamp difference detected after monotonic adjustment!"

    dup_mask = df.duplicated(subset=['case_id', 'timestamp'], keep=False)
    dup_cases = df[dup_mask]['case_id'].nunique()
    print(f"  * Total Cases: {df['case_id'].nunique():,}")
    print(f"  * Cases with co-occurring identical timestamps: {dup_cases:,} ({dup_cases/df['case_id'].nunique()*100:.2f}%)")
    
    # Safe check before accessing sample
    sample_dup = df[dup_mask & (df['activity'] == 'Prescription Consultation Started')]
    if not sample_dup.empty:
        sample_case = sample_dup['case_id'].iloc[0]
        case_rows = df[df['case_id'] == sample_case].sort_values('event_order')
        print(f"\n  [Sample Verification: Case {sample_case}]")
        for _, r in case_rows.iterrows():
            print(f"    - Order #{r['event_order']}: {r['activity']:36s} | Raw: {r['timestamp']} | Monotonic: {r['timestamp_monotonic']}")
            
        # Convert case to PM4Py log and verify activity order
        pm_df = pm4py.format_dataframe(case_rows, case_id='case_id', activity_key='activity', timestamp_key='timestamp_monotonic')
        log = pm4py.convert_to_event_log(pm_df)
        log_activities = [e['concept:name'] for e in log[0]]
        expected_activities = list(case_rows['activity'])
        
        assert log_activities == expected_activities, f"Sequence Mismatch! Log: {log_activities} vs Expected: {expected_activities}"
        print(f"  * Conversion Verification: PM4Py Trace Activity Sequence exactly matches clinical event_order!")
    else:
        print("  * Notice: No co-occurring 'Prescription Consultation Started' sample found for demonstration.")

def run_cohort_conformance_benchmark(net, im, fm):
    """
    Runs a rapid smoke test on the first 5,000 cases to verify algorithmic
    stability and token convergence. Zero hardcoded fallbacks.
    
    Note: This is a smoke test on an initial subset, not the final full-cohort metric.
    Full-cohort (49,912 cases) metrics are computed in the production pipeline.
    """
    t0 = time.time()
    df = pd.read_csv("data/careflow_event_log.csv")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(by=['case_id', 'timestamp', 'event_order'], ascending=[True, True, True])
    df['timestamp_monotonic'] = df['timestamp'] + pd.to_timedelta(df['event_order'], unit='us')
    
    # Sample first 5,000 cases for smoke testing
    sample_cases = df['case_id'].drop_duplicates().head(5000)
    sample_df = df[df['case_id'].isin(sample_cases)]
    
    print(f"\n[Step 3/3] Running Quick Smoke Test (First {len(sample_cases):,} Cases - Algorithmic Sanity Check Only)...")
    
    pm_df = pm4py.format_dataframe(sample_df, case_id='case_id', activity_key='activity', timestamp_key='timestamp_monotonic')
    log = pm4py.convert_to_event_log(pm_df)
    
    fit_res = pm4py.fitness_token_based_replay(log, net, im, fm)
    prec_val = pm4py.precision_token_based_replay(log, net, im, fm)
    
    print(f"  * Smoke Test Subset Size:    {len(sample_cases):,} cases ({len(sample_df):,} events)")
    print(f"  * Smoke Test Log Fitness:    {fit_res['log_fitness']:.4f} ({fit_res['log_fitness']*100:.2f}%)")
    print(f"  * Smoke Test Trace Fitness:  {fit_res['average_trace_fitness']:.4f} ({fit_res['average_trace_fitness']*100:.2f}%)")
    print(f"  * Smoke Test % Fit Traces:   {fit_res['perc_fit_traces']:.2f}%")
    print(f"  * Smoke Test Precision:      {prec_val:.4f} ({prec_val*100:.2f}%)")
    print(f"  * Smoke Test Execution Time: {time.time() - t0:.2f}s")
    print("  * Notice: Full-cohort execution (49,912 cases) will follow in scripts/process_conformance_analysis.py.")

def main():
    print("=" * 80)
    print("CAREFLOW CLINICAL PROCESS MINING — PETRI NET REPLAY & CONFORMANCE VERIFICATION")
    print("Mode: Strictly Read-Only (Memory Execution, Zero Disk Writes)")
    print("=" * 80)
    
    # 1. Build the validated normative reference Petri net
    net, im, fm = build_normative_petri_net()
    
    # 2. Validate all 9 normative in-memory test traces
    run_in_memory_trace_tests(net, im, fm)
    
    # 3. Validate timestamp monotonicity and event_order preservation
    verify_timestamp_and_event_order()
    
    # 4. Run rapid smoke test on 5,000 cases
    run_cohort_conformance_benchmark(net, im, fm)
    
    print("\n" + "=" * 80)
    print("VERIFICATION SUITE COMPLETE — 100% ASSERTIONS PASSED")
    print("=" * 80)

if __name__ == "__main__":
    main()
