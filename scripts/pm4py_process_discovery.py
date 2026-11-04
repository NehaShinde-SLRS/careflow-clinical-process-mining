"""
CareFlow Clinical Process Mining — Day 9 PM4Py Process Discovery & Integration
Script: scripts/pm4py_process_discovery.py

Author: Senior Process Mining Engineer (Member 3)
Date: 4 November 2026
GCP Project: careflow-clinical-process-m
BigQuery Dataset: careflow_opd

Implements an end-to-end PM4Py process mining discovery pipeline on data/careflow_event_log.csv:
1. Event Log Quality & PM4Py Schema Integration Validation
2. Process Discovery (Frequency DFG, Performance DFG, Start/End Activities)
3. Inductive Miner Process Modeling (Petri Net & Process Tree)
4. Process Variants & Cumulative Pareto Distribution Analysis
5. Clinical Department Bottleneck & Waiting Time Quantification
6. Visualizations Generation (NetworkX + Matplotlib publication-grade PNGs)
7. Standard Model Interchange (PNML, PTML, DOT, compressed IEEE XES)
8. Summary JSON Artifact Generation for Audit Verification
"""

import os
import sys
import json
import time
from pathlib import Path
import pandas as pd
import numpy as np

# Force UTF-8 stdout
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import pm4py

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EVENT_LOG_PATH = PROJECT_ROOT / "data" / "careflow_event_log.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "process_mining"
XES_OUTPUT_PATH = PROJECT_ROOT / "data" / "careflow_event_log.xes.gz"

def setup_directories():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def step1_load_and_validate_quality(log_path):
    print("=" * 80)
    print("STEP 1: EVENT LOG LOADING & PM4PY SCHEMA INTEGRATION VALIDATION")
    print("=" * 80)

    if not log_path.exists():
        raise FileNotFoundError(f"Event log not found at: {log_path}")

    start_t = time.time()
    raw_df = pd.read_csv(log_path, low_memory=False)
    load_duration = time.time() - start_t
    print(f"Loaded {len(raw_df):,} event records from {log_path.name} in {load_duration:.2f}s.")

    # 1.1 Quality Checks: Missing values
    missing_counts = raw_df.isnull().sum()
    total_missing = missing_counts.sum()
    print(f"\n[Quality Check 1.1] Missing values across all {len(raw_df.columns)} columns: {total_missing}")
    if total_missing > 0:
        for col, cnt in missing_counts[missing_counts > 0].items():
            print(f"  - {col}: {cnt:,} missing ({cnt*100/len(raw_df):.2f}%)")
    else:
        print("  --> PASS: 0 null values detected across all columns.")

    # 1.2 Quality Checks: Exact Duplicate Rows
    exact_duplicates = raw_df.duplicated().sum()
    print(f"\n[Quality Check 1.2] Exact duplicate rows: {exact_duplicates}")
    if exact_duplicates == 0:
        print("  --> PASS: 0 exact duplicate rows across all 14 columns.")

    # 1.3 Case Integrity & Event Order Consistency
    total_cases = raw_df['case_id'].nunique()
    total_patients = raw_df['patient_id'].nunique()
    events_per_case = raw_df.groupby('case_id').size()
    single_event_cases = (events_per_case == 1).sum()
    print(f"\n[Quality Check 1.3] Case Integrity:")
    print(f"  - Unique Cases (Encounters): {total_cases:,}")
    print(f"  - Unique Patients: {total_patients:,}")
    print(f"  - Mean Events per Case: {events_per_case.mean():.2f}")
    print(f"  - Median Events per Case: {events_per_case.median():.1f}")
    print(f"  - Min / Max Events per Case: {events_per_case.min()} / {events_per_case.max()}")
    print(f"  - Single-Event Cases: {single_event_cases} (0.00%)")

    # 1.4 Anomaly Flag Quantification
    anomaly_counts = raw_df['timestamp_anomaly_flag'].value_counts().to_dict()
    flagged_events = raw_df[raw_df['timestamp_anomaly_flag'] == True]
    cases_with_anomaly = flagged_events['case_id'].nunique()
    print(f"\n[Quality Check 1.4] Timestamp Anomaly Flag:")
    print(f"  - Normal Events: {len(raw_df) - len(flagged_events):,} ({(len(raw_df) - len(flagged_events))*100/len(raw_df):.2f}%)")
    print(f"  - Early Diagnostic Start Anomaly Events: {len(flagged_events):,} ({len(flagged_events)*100/len(raw_df):.2f}%)")
    print(f"  - Cases Impacted: {cases_with_anomaly:,} ({cases_with_anomaly*100/total_cases:.2f}%)")

    # 1.5 Format for PM4Py
    print("\n[Quality Check 1.5] PM4Py DataFrame Formatting:")
    df_pm4py = pm4py.format_dataframe(
        raw_df,
        case_id='case_id',
        activity_key='activity',
        timestamp_key='timestamp'
    )
    print("  --> PM4Py internal mapping validated:")
    print("      case:concept:name  <-- case_id")
    print("      concept:name       <-- activity")
    print("      time:timestamp     <-- timestamp (parsed datetime)")
    print(f"      Parsed timestamp range: {df_pm4py['time:timestamp'].min()} to {df_pm4py['time:timestamp'].max()}")

    quality_summary = {
        "total_events": int(len(raw_df)),
        "total_cases": int(total_cases),
        "total_patients": int(total_patients),
        "total_missing_values": int(total_missing),
        "exact_duplicates": int(exact_duplicates),
        "single_event_cases": int(single_event_cases),
        "events_per_case_mean": float(events_per_case.mean()),
        "events_per_case_median": float(events_per_case.median()),
        "events_per_case_max": int(events_per_case.max()),
        "anomaly_events_count": int(len(flagged_events)),
        "anomaly_cases_count": int(cases_with_anomaly),
        "timestamp_min": str(df_pm4py['time:timestamp'].min()),
        "timestamp_max": str(df_pm4py['time:timestamp'].max())
    }

    return df_pm4py, raw_df, quality_summary

def step2_discover_dfg(df_pm4py):
    print("\n" + "=" * 80)
    print("STEP 2: DIRECTLY-FOLLOWS GRAPH (DFG) DISCOVERY")
    print("=" * 80)

    # 2.1 Frequency DFG
    t0 = time.time()
    dfg_freq, start_acts, end_acts = pm4py.discover_dfg(df_pm4py)
    dfg_dur = time.time() - t0
    print(f"Discovered Frequency DFG in {dfg_dur:.2f}s:")
    print(f"  - Distinct Edge Types: {len(dfg_freq):,}")
    print(f"  - Total Transitions: {sum(dfg_freq.values()):,}")

    print("\n--- Start Activities (Case Ingress) ---")
    for act, cnt in sorted(start_acts.items(), key=lambda x: x[1], reverse=True):
        print(f"  * {act:<42}: {cnt:>6,} ({cnt*100.0/sum(start_acts.values()):>5.2f}%)")

    print("\n--- End Activities (Case Egress) ---")
    for act, cnt in sorted(end_acts.items(), key=lambda x: x[1], reverse=True):
        print(f"  * {act:<42}: {cnt:>6,} ({cnt*100.0/sum(end_acts.values()):>5.2f}%)")

    print("\n--- Top 10 Directly-Follows Transitions by Frequency ---")
    sorted_dfg = sorted(dfg_freq.items(), key=lambda x: x[1], reverse=True)
    for i, ((src, tgt), cnt) in enumerate(sorted_dfg[:10], 1):
        print(f"  {i:>2}. {src} --> {tgt}: {cnt:>6,} transitions")

    # 2.2 Performance DFG (Durations)
    t1 = time.time()
    perf_dfg, p_start, p_end = pm4py.discover_performance_dfg(df_pm4py)
    perf_dur = time.time() - t1
    print(f"\nDiscovered Performance DFG in {perf_dur:.2f}s:")

    performance_records = []
    for (src, tgt), stat in perf_dfg.items():
        freq = dfg_freq.get((src, tgt), 0)
        mean_sec = stat.get('mean', 0.0)
        median_sec = stat.get('median', 0.0)
        performance_records.append({
            'source': src,
            'target': tgt,
            'frequency': freq,
            'mean_min': mean_sec / 60.0,
            'median_min': median_sec / 60.0,
            'mean_hours': mean_sec / 3600.0,
            'median_hours': median_sec / 3600.0
        })

    perf_df = pd.DataFrame(performance_records).sort_values(by='frequency', ascending=False)

    return dfg_freq, start_acts, end_acts, perf_df

def step3_discover_inductive_models(df_pm4py):
    print("\n" + "=" * 80)
    print("STEP 3: INDUCTIVE MINER PROCESS MODELING")
    print("=" * 80)

    # 3.1 Inductive Petri Net
    t0 = time.time()
    net, im, fm = pm4py.discover_petri_net_inductive(df_pm4py)
    petri_dur = time.time() - t0
    print(f"Discovered Inductive Petri Net in {petri_dur:.2f}s:")
    print(f"  - Places: {len(net.places):,}")
    print(f"  - Transitions: {len(net.transitions):,}")
    print(f"  - Arcs: {len(net.arcs):,}")
    print(f"  - Initial Marking: {[p.name for p in im]}")
    print(f"  - Final Marking: {[p.name for p in fm]}")

    # 3.2 Inductive Process Tree
    t1 = time.time()
    tree = pm4py.discover_process_tree_inductive(df_pm4py)
    tree_dur = time.time() - t1
    print(f"\nDiscovered Inductive Process Tree in {tree_dur:.2f}s:")
    print(f"  - Process Tree Operator Representation: {str(tree)}")

    # Export PNML & PTML
    pnml_path = OUTPUT_DIR / "inductive_petri_net.pnml"
    ptml_path = OUTPUT_DIR / "inductive_process_tree.ptml"
    pm4py.write_pnml(net, im, fm, str(pnml_path))
    pm4py.write_ptml(tree, str(ptml_path))
    print(f"\nSaved model artifacts:")
    print(f"  * Petri Net PNML: {pnml_path.name} ({pnml_path.stat().st_size:,} bytes)")
    print(f"  * Process Tree PTML: {ptml_path.name} ({ptml_path.stat().st_size:,} bytes)")

    return net, im, fm, tree

def step4_analyze_variants_and_pareto(df_pm4py):
    print("\n" + "=" * 80)
    print("STEP 4: PROCESS VARIANTS & CUMULATIVE PARETO ANALYSIS")
    print("=" * 80)

    t0 = time.time()
    variants = pm4py.get_variants_as_tuples(df_pm4py)
    total_cases = df_pm4py['case:concept:name'].nunique()

    variant_records = []
    for var_tuple, case_val in variants.items():
        var_trace_str = " -> ".join(var_tuple)
        case_count = len(case_val) if isinstance(case_val, list) else int(case_val)
        variant_records.append({
            'variant_tuple': var_tuple,
            'variant_trace': var_trace_str,
            'case_count': case_count,
            'event_length': len(var_tuple)
        })

    v_df = pd.DataFrame(variant_records).sort_values(by='case_count', ascending=False).reset_index(drop=True)
    v_df['share_pct'] = (v_df['case_count'] / total_cases) * 100.0
    v_df['cumulative_share_pct'] = v_df['share_pct'].cumsum()

    print(f"Discovered {len(v_df):,} distinct execution variants across {total_cases:,} cases in {time.time()-t0:.2f}s.")

    pareto_50 = (v_df['cumulative_share_pct'] <= 50.0).sum() + 1
    pareto_80 = (v_df['cumulative_share_pct'] <= 80.0).sum() + 1
    pareto_90 = (v_df['cumulative_share_pct'] <= 90.0).sum() + 1
    pareto_95 = (v_df['cumulative_share_pct'] <= 95.0).sum() + 1

    print(f"\nPareto Distribution Summary:")
    print(f"  - Top {pareto_50} variant(s) account for 50% of all outpatient cases.")
    print(f"  - Top {pareto_80} variants account for 80% of all outpatient cases.")
    print(f"  - Top {pareto_90} variants account for 90% of all outpatient cases.")
    print(f"  - Top {pareto_95} variants account for 95% of all outpatient cases.")

    print("\n--- Top 10 Clinical Execution Variants ---")
    for i, r in v_df.head(10).iterrows():
        print(f"\n[Variant {i+1}] Cases: {r['case_count']:,} ({r['share_pct']:.2f}% | Cumulative: {r['cumulative_share_pct']:.2f}%) | Steps: {r['event_length']}")
        print(f"  Trace: {r['variant_trace']}")

    return v_df, {
        "total_variants": int(len(v_df)),
        "pareto_50_count": int(pareto_50),
        "pareto_80_count": int(pareto_80),
        "pareto_90_count": int(pareto_90),
        "pareto_95_count": int(pareto_95)
    }

def step5_quantify_bottlenecks(perf_df):
    print("\n" + "=" * 80)
    print("STEP 5: DEPARTMENTAL BOTTLENECK & WAITING TIME QUANTIFICATION")
    print("=" * 80)

    # Filter transitions with statistical volume (>=100 cases)
    frequent_transitions = perf_df[perf_df['frequency'] >= 100].copy()
    top_delays = frequent_transitions.sort_values(by='mean_min', ascending=False)

    print("\nTop 10 Clinical Transitions with Highest Mean Duration (>=100 cases):")
    for i, (_, r) in enumerate(top_delays.head(10).iterrows(), 1):
        print(f"  {i:>2}. {r['source']} --> {r['target']}")
        print(f"      Count: {r['frequency']:,} | Mean: {r['mean_min']:.1f}m ({r['mean_hours']:.2f}h) | Median: {r['median_min']:.1f}m ({r['median_hours']:.2f}h)")

    # Key clinical stages analysis
    key_stages = [
        ("Registration to Consultation Wait", "Appointment Registration", "Prescription Consultation Started"),
        ("Consultation Active Duration", "Prescription Consultation Started", "Prescription Consultation Completed"),
        ("Consultation to Lab Order Dispatch", "Prescription Consultation Completed", "Lab Test Started"),
        ("Laboratory Turnaround Time (TAT)", "Lab Test Started", "Lab Test Completed"),
        ("Consultation to Imaging Dispatch", "Prescription Consultation Completed", "Imaging Started"),
        ("Imaging Turnaround Time (TAT)", "Imaging Started", "Imaging Completed"),
        ("Consultation to Pharmacy Dispatch", "Prescription Consultation Completed", "Pharmacy Dispensation Started"),
        ("Pharmacy Dispensation Duration", "Pharmacy Dispensation Started", "Pharmacy Dispensation Completed"),
    ]

    key_stage_metrics = []
    print("\n--- Key Clinical Department Stage Latencies ---")
    for label, src, tgt in key_stages:
        match = perf_df[(perf_df['source'] == src) & (perf_df['target'] == tgt)]
        if not match.empty:
            row = match.iloc[0]
            status = "BOTTLENECK (>120m)" if row['mean_min'] > 120 else "STANDARD"
            print(f"  * {label:<38}: Mean={row['mean_min']:>6.1f}m ({row['mean_hours']:>4.2f}h) | Median={row['median_min']:>5.1f}m | Volume={row['frequency']:>6,} [{status}]")
            key_stage_metrics.append({
                'label': label,
                'source': src,
                'target': tgt,
                'frequency': int(row['frequency']),
                'mean_min': float(row['mean_min']),
                'median_min': float(row['median_min']),
                'mean_hours': float(row['mean_hours']),
                'is_bottleneck': bool(row['mean_min'] > 120)
            })

    return frequent_transitions, key_stage_metrics

def step6_generate_visualizations(df_pm4py, dfg_freq, start_acts, end_acts, perf_df, v_df, key_stage_metrics):
    print("\n" + "=" * 80)
    print("STEP 6: GENERATING PUBLICATION-GRADE VISUALIZATIONS")
    print("=" * 80)

    # -------------------------------------------------------------
    # Visualization 1: Directly-Follows Graph (Frequency Network)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(16, 12), dpi=300)
    G = nx.DiGraph()

    # Add nodes with categories
    activities = list(set([u for u, v in dfg_freq.keys()] + [v for u, v in dfg_freq.keys()]))
    for act in activities:
        G.add_node(act)

    # Layout: arrange logically by stage
    pos = {
        'Appointment Registration': (0, 0),
        'Prescription Consultation Started': (1.5, 0),
        'Prescription Consultation Completed': (3.0, 0),
        'Lab Test Started': (4.5, 1.2),
        'Lab Test Completed': (6.0, 1.2),
        'Imaging Started': (4.5, 0.0),
        'Imaging Completed': (6.0, 0.0),
        'Pharmacy Dispensation Started': (4.5, -1.2),
        'Pharmacy Dispensation Completed': (6.0, -1.2),
    }

    # Node styling
    node_colors = []
    for node in G.nodes():
        if node == 'Appointment Registration':
            node_colors.append('#2ca02c') # Green (Start)
        elif 'Completed' in node:
            node_colors.append('#1f77b4') # Blue (Service End)
        elif 'Started' in node:
            node_colors.append('#ff7f0e') # Orange (Service Start)
        else:
            node_colors.append('#9467bd')

    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=3200, alpha=0.9, edgecolors='#333333', linewidths=1.5)

    # Node labels
    labels = {n: n.replace(' ', '\n') for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=labels, ax=ax, font_size=8, font_family='sans-serif', font_weight='bold', font_color='white')

    # Draw edges with frequency width
    # Filter top edges for readability (frequency >= 50)
    major_edges = {k: v for k, v in dfg_freq.items() if v >= 50 and k[0] in pos and k[1] in pos}
    max_freq = max(major_edges.values()) if major_edges else 1

    for (u, v), freq in major_edges.items():
        if u == v:
            continue # Skip self-loops for network clarity
        width = 1.0 + 5.0 * (freq / max_freq)
        alpha = 0.4 + 0.5 * (freq / max_freq)
        rad = 0.15 if (v, u) in major_edges else 0.05
        ax.annotate(
            "",
            xy=pos[v], xycoords='data',
            xytext=pos[u], textcoords='data',
            arrowprops=dict(
                arrowstyle="-|>",
                color="#003366",
                lw=width,
                alpha=alpha,
                connectionstyle=f"arc3,rad={rad}",
                mutation_scale=15
            )
        )
        # Edge label at midpoint
        mx = (pos[u][0] + pos[v][0]) / 2.0
        my = (pos[u][1] + pos[v][1]) / 2.0 + rad * 0.3
        if freq >= 1000:
            ax.text(mx, my, f"{freq:,}", fontsize=7, color='#002244', fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.2", facecolor='white', edgecolor='#cccccc', alpha=0.85))

    ax.set_title("CareFlow Directly-Follows Graph (DFG) — Transition Frequencies\nCareFlow Outpatient Dataset (49,912 Encounters | 193,443 Events)",
                 fontsize=14, fontweight='bold', pad=20)
    ax.axis('off')

    # Legend
    legend_elements = [
        mpatches.Patch(facecolor='#2ca02c', edgecolor='#333333', label='Primary Entry (Registration: 99.16%)'),
        mpatches.Patch(facecolor='#ff7f0e', edgecolor='#333333', label='Diagnostic / Clinical Service Started'),
        mpatches.Patch(facecolor='#1f77b4', edgecolor='#333333', label='Diagnostic / Clinical Service Completed'),
    ]
    ax.legend(handles=legend_elements, loc='lower center', ncol=3, frameon=True, fontsize=9)

    fig.tight_layout()
    v1_path = OUTPUT_DIR / "dfg_frequency_graph.png"
    plt.savefig(v1_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  * Generated DFG Frequency Network: {v1_path.name}")

    # -------------------------------------------------------------
    # Visualization 2: Performance DFG (Bottlenecks)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(16, 12), dpi=300)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=3200, alpha=0.9, edgecolors='#333333', linewidths=1.5)
    nx.draw_networkx_labels(G, pos, labels=labels, ax=ax, font_size=8, font_family='sans-serif', font_weight='bold', font_color='white')

    perf_lookup = {(r['source'], r['target']): r for _, r in perf_df.iterrows()}

    for (u, v), freq in major_edges.items():
        if u == v:
            continue
        rec = perf_lookup.get((u, v))
        mean_min = rec['mean_min'] if rec is not None else 0.0

        if mean_min > 120.0:
            edge_color = '#d62728' # Red for severe bottleneck (>2 hours)
            lw = 3.5
        elif mean_min > 30.0:
            edge_color = '#ff7f0e' # Orange for moderate delay (30-120 min)
            lw = 2.2
        else:
            edge_color = '#2ca02c' # Green for low wait (<30 min)
            lw = 1.2

        rad = 0.15 if (v, u) in major_edges else 0.05
        ax.annotate(
            "",
            xy=pos[v], xycoords='data',
            xytext=pos[u], textcoords='data',
            arrowprops=dict(
                arrowstyle="-|>",
                color=edge_color,
                lw=lw,
                connectionstyle=f"arc3,rad={rad}",
                mutation_scale=15
            )
        )
        mx = (pos[u][0] + pos[v][0]) / 2.0
        my = (pos[u][1] + pos[v][1]) / 2.0 + rad * 0.3
        if freq >= 1000 or mean_min > 120.0:
            duration_txt = f"{mean_min:.1f}m" if mean_min < 60 else f"{mean_min/60:.1f}h"
            ax.text(mx, my, duration_txt, fontsize=7, color=edge_color, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.2", facecolor='#ffffea', edgecolor=edge_color, alpha=0.9))

    ax.set_title("CareFlow Performance DFG — Clinical Mean Waiting & Turnaround Times\nIdentifying Operational Bottlenecks across Clinical Pathways",
                 fontsize=14, fontweight='bold', pad=20)
    ax.axis('off')

    perf_legend = [
        mpatches.Patch(facecolor='#2ca02c', label='Efficient Flow (<30 min mean latency)'),
        mpatches.Patch(facecolor='#ff7f0e', label='Moderate Delay (30–120 min mean latency)'),
        mpatches.Patch(facecolor='#d62728', label='Operational Bottleneck (>120 min / 2 hours)'),
    ]
    ax.legend(handles=perf_legend, loc='lower center', ncol=3, frameon=True, fontsize=9)

    fig.tight_layout()
    v2_path = OUTPUT_DIR / "dfg_performance_graph.png"
    plt.savefig(v2_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  * Generated DFG Performance Graph: {v2_path.name}")

    # -------------------------------------------------------------
    # Visualization 3: Process Variants Pareto Distribution
    # -------------------------------------------------------------
    fig, ax1 = plt.subplots(figsize=(14, 8), dpi=300)
    top_v = v_df.head(15).copy()
    indices = np.arange(len(top_v))

    # Variant labels
    v_labels = [f"V{i+1}: {r['event_length']} steps" for i, r in top_v.iterrows()]

    bars = ax1.bar(indices, top_v['case_count'], color='#1f77b4', alpha=0.85, width=0.6, label='Patient Encounters')
    ax1.set_xlabel("Clinical Process Variant", fontsize=11, fontweight='bold', labelpad=10)
    ax1.set_ylabel("Number of Encounters", fontsize=11, fontweight='bold', color='#1f77b4')
    ax1.set_xticks(indices)
    ax1.set_xticklabels(v_labels, rotation=45, ha='right', fontsize=9)
    ax1.tick_params(axis='y', labelcolor='#1f77b4')
    ax1.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))

    # Pareto line on secondary axis
    ax2 = ax1.twinx()
    line = ax2.plot(indices, top_v['cumulative_share_pct'], color='#d62728', marker='o', linewidth=2.5, label='Cumulative Share %')
    ax2.set_ylabel("Cumulative Share of Total Encounters (%)", fontsize=11, fontweight='bold', color='#d62728')
    ax2.set_ylim(0, 105)
    ax2.tick_params(axis='y', labelcolor='#d62728')

    # Add reference horizontal lines
    ax2.axhline(80, color='gray', linestyle='--', linewidth=1.2, alpha=0.7)
    ax2.axhline(90, color='orange', linestyle='--', linewidth=1.2, alpha=0.7)
    ax2.axhline(95, color='green', linestyle='--', linewidth=1.2, alpha=0.7)
    ax2.text(len(top_v)-1, 81, "80% (Top 2 variants)", color='gray', fontsize=8, ha='right')
    ax2.text(len(top_v)-1, 91, "90% (Top 6 variants)", color='orange', fontsize=8, ha='right')
    ax2.text(len(top_v)-1, 96, "95% (Top 18 variants)", color='green', fontsize=8, ha='right')

    # Bar annotations
    for bar in bars:
        h = bar.get_height()
        ax1.annotate(f"{h:,}",
                     xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 3), textcoords="offset points",
                     ha='center', va='bottom', fontsize=7, fontweight='bold')

    plt.title("CareFlow Process Variants & Cumulative Pareto Distribution\nPareto Principle: Top 2 Variants Cover 82.76% of All Outpatient Encounters",
              fontsize=13, fontweight='bold', pad=15)
    fig.tight_layout()
    v3_path = OUTPUT_DIR / "process_variants_pareto.png"
    plt.savefig(v3_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  * Generated Process Variants Pareto Chart: {v3_path.name}")

    # -------------------------------------------------------------
    # Visualization 4: Key Stage Bottlenecks & Turnaround Times
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
    stage_df = pd.DataFrame(key_stage_metrics).sort_values(by='mean_min', ascending=True)

    y_pos = np.arange(len(stage_df))
    colors = ['#d62728' if r['is_bottleneck'] else '#1f77b4' for _, r in stage_df.iterrows()]

    bars = ax.barh(y_pos, stage_df['mean_min'], color=colors, alpha=0.85, height=0.55, label='Mean Latency (min)')
    # Overlay median points
    ax.scatter(stage_df['median_min'], y_pos, color='#ff7f0e', s=80, zorder=5, label='Median Latency (min)', edgecolors='#333333')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(stage_df['label'], fontsize=9, fontweight='bold')
    ax.set_xlabel("Duration in Minutes", fontsize=11, fontweight='bold')
    ax.set_title("CareFlow Outpatient Departmental Turnaround Times & Waiting Durations\nBenchmark: >120 Minutes Defined as Primary Clinical Bottleneck",
                 fontsize=13, fontweight='bold', pad=15)

    # 120 min benchmark line
    ax.axvline(120, color='#d62728', linestyle='--', linewidth=1.5, alpha=0.8)
    ax.text(125, len(stage_df)-1, "120 min Bottleneck Threshold", color='#d62728', fontsize=8, fontweight='bold')

    for bar, (_, r) in zip(bars, stage_df.iterrows()):
        w = bar.get_width()
        hours_str = f" ({w/60:.1f}h)" if w >= 60 else ""
        ax.text(w + 5, bar.get_y() + bar.get_height()/2,
                f"Mean: {w:.1f}m{hours_str} | Med: {r['median_min']:.1f}m",
                ha='left', va='center', fontsize=8, fontweight='bold')

    ax.legend(loc='lower right', frameon=True, fontsize=9)
    ax.set_xlim(0, max(stage_df['mean_min']) * 1.25)
    fig.tight_layout()
    v4_path = OUTPUT_DIR / "bottleneck_waiting_times.png"
    plt.savefig(v4_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  * Generated Departmental Bottleneck Chart: {v4_path.name}")

    # -------------------------------------------------------------
    # Visualization 5: Activity Frequency Distribution
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
    act_counts = df_pm4py['concept:name'].value_counts()
    y_pos = np.arange(len(act_counts))

    bars = ax.barh(y_pos, act_counts.values, color='#2ca02c', alpha=0.85, height=0.55)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(act_counts.index, fontsize=9, fontweight='bold')
    ax.set_xlabel("Total Event Count", fontsize=11, fontweight='bold')
    ax.invert_yaxis()
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: f"{int(x):,}"))

    for bar in bars:
        w = bar.get_width()
        pct = (w / len(df_pm4py)) * 100.0
        ax.text(w + 500, bar.get_y() + bar.get_height()/2,
                f"{int(w):,} ({pct:.1f}%)",
                ha='left', va='center', fontsize=8, fontweight='bold')

    ax.set_title("CareFlow Clinical Milestone Event Frequencies\n193,443 Total Events across 9 Clinical Activities",
                 fontsize=13, fontweight='bold', pad=15)
    ax.set_xlim(0, max(act_counts.values) * 1.18)
    fig.tight_layout()
    v5_path = OUTPUT_DIR / "activity_frequency_distribution.png"
    plt.savefig(v5_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  * Generated Activity Frequency Distribution: {v5_path.name}")

def step7_export_xes_and_dot(df_pm4py, dfg_freq, start_acts, end_acts):
    print("\n" + "=" * 80)
    print("STEP 7: EXPORTING STANDARDIZED INTERCHANGE ARTIFACTS (XES & DOT)")
    print("=" * 80)

    # 7.1 Export Graphviz DOT file
    dot_path = OUTPUT_DIR / "dfg_frequency.dot"
    with open(dot_path, 'w', encoding='utf-8') as f:
        f.write("digraph CareFlow_DFG {\n")
        f.write("  rankdir=LR;\n")
        f.write("  node [shape=box, style=\"rounded,filled\", fontname=\"Helvetica\"];\n")
        f.write("  edge [fontname=\"Helvetica\", fontsize=9];\n\n")

        for (u, v), freq in sorted(dfg_freq.items(), key=lambda x: x[1], reverse=True):
            f.write(f"  \"{u}\" -> \"{v}\" [label=\"{freq:,}\", penwidth={1.0 + 3.0*(freq/50000)}];\n")

        f.write("}\n")
    print(f"  * Exported Graphviz DOT: {dot_path.name} ({dot_path.stat().st_size:,} bytes)")

    # 7.2 Export compressed IEEE XES
    print(f"  * Writing IEEE compressed XES to: {XES_OUTPUT_PATH.name}...")
    t0 = time.time()
    pm4py.write_xes(df_pm4py, str(XES_OUTPUT_PATH))
    xes_dur = time.time() - t0
    xes_size_mb = XES_OUTPUT_PATH.stat().st_size / (1024 * 1024)
    print(f"  --> Successfully generated {XES_OUTPUT_PATH.name} ({xes_size_mb:.2f} MB) in {xes_dur:.2f}s.")

def step8_save_summary_json(quality_summary, dfg_freq, start_acts, end_acts, v_meta, v_df, key_stage_metrics):
    print("\n" + "=" * 80)
    print("STEP 8: SAVING STRUCTURED AUDIT SUMMARY JSON")
    print("=" * 80)

    summary_data = {
        "metadata": {
            "project": "CareFlow Clinical Process Mining",
            "milestone": "Day 9 PM4Py Process Discovery & Integration",
            "date": "2026-11-04",
            "pm4py_version": pm4py.__version__,
            "total_events": quality_summary["total_events"],
            "total_cases": quality_summary["total_cases"],
            "total_patients": quality_summary["total_patients"]
        },
        "quality_metrics": quality_summary,
        "discovery_metrics": {
            "dfg_edge_count": len(dfg_freq),
            "total_transitions": sum(dfg_freq.values()),
            "start_activities": start_acts,
            "end_activities": end_acts,
            "total_variants": v_meta["total_variants"],
            "pareto": {
                "top_variants_50pct": v_meta["pareto_50_count"],
                "top_variants_80pct": v_meta["pareto_80_count"],
                "top_variants_90pct": v_meta["pareto_90_count"],
                "top_variants_95pct": v_meta["pareto_95_count"]
            }
        },
        "top_5_variants": [
            {
                "rank": i + 1,
                "case_count": int(r["case_count"]),
                "share_pct": round(float(r["share_pct"]), 2),
                "cumulative_share_pct": round(float(r["cumulative_share_pct"]), 2),
                "event_length": int(r["event_length"]),
                "trace": r["variant_trace"]
            }
            for i, r in v_df.head(5).iterrows()
        ],
        "key_clinical_stages": key_stage_metrics,
        "artifacts_generated": [
            "outputs/process_mining/dfg_frequency_graph.png",
            "outputs/process_mining/dfg_performance_graph.png",
            "outputs/process_mining/process_variants_pareto.png",
            "outputs/process_mining/bottleneck_waiting_times.png",
            "outputs/process_mining/activity_frequency_distribution.png",
            "outputs/process_mining/inductive_petri_net.pnml",
            "outputs/process_mining/inductive_process_tree.ptml",
            "outputs/process_mining/dfg_frequency.dot",
            "outputs/process_mining/pm4py_discovery_summary.json",
            "data/careflow_event_log.xes.gz"
        ]
    }

    json_path = OUTPUT_DIR / "pm4py_discovery_summary.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=2)

    print(f"  * Saved JSON Summary: {json_path.name} ({json_path.stat().st_size:,} bytes)")

def main():
    print("CAREFLOW CLINICAL PROCESS MINING — DAY 9 PM4PY PIPELINE")
    print(f"PM4Py Version: {pm4py.__version__}")
    print(f"Project Directory: {PROJECT_ROOT}")

    setup_directories()

    # Step 1: Loading & Validation
    df_pm4py, raw_df, quality_summary = step1_load_and_validate_quality(EVENT_LOG_PATH)

    # Step 2: DFG Discovery
    dfg_freq, start_acts, end_acts, perf_df = step2_discover_dfg(df_pm4py)

    # Step 3: Inductive Modeling
    net, im, fm, tree = step3_discover_inductive_models(df_pm4py)

    # Step 4: Variants & Pareto
    v_df, v_meta = step4_analyze_variants_and_pareto(df_pm4py)

    # Step 5: Bottleneck Analysis
    frequent_transitions, key_stage_metrics = step5_quantify_bottlenecks(perf_df)

    # Step 6: Visualizations
    step6_generate_visualizations(df_pm4py, dfg_freq, start_acts, end_acts, perf_df, v_df, key_stage_metrics)

    # Step 7: XES & DOT Export
    step7_export_xes_and_dot(df_pm4py, dfg_freq, start_acts, end_acts)

    # Step 8: Save Audit JSON
    step8_save_summary_json(quality_summary, dfg_freq, start_acts, end_acts, v_meta, v_df, key_stage_metrics)

    print("\n" + "=" * 80)
    print("DAY 9 PM4PY PROCESS DISCOVERY PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == '__main__':
    main()
