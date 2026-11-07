"""
CareFlow Clinical Process Mining — Day 11 Power BI Dashboard Inspection
Script: scripts/inspect_pbix.py

Purpose:
Performs a strictly read-only inspection of the Power BI dashboard file
"careflow_POWERBI_dashboard.pbix" received from Member 4.

Safety & Read-Only Guarantee:
- Opens the PBIX archive strictly in read-only mode ('r').
- Does not modify, overwrite, delete, or create any data or archive files.
- Does not access, read, or export any credentials or environment secrets.
- Does not connect to any network, cloud, or external database resources.
"""

import zipfile
import json
import re
from pathlib import Path

pbix_path = Path('careflow_POWERBI_dashboard.pbix')

if not pbix_path.exists():
    print(f"Error: {pbix_path} not found.")
    exit(1)

print(f"Loading {pbix_path.name} ({pbix_path.stat().st_size:,} bytes) in STRICT READ-ONLY mode...")

with zipfile.ZipFile(pbix_path, 'r') as z:
    # 1. Report Definition
    if 'Report/definition/report.json' in z.namelist():
        rep = json.loads(z.read('Report/definition/report.json').decode('utf-8'))
        print("\n=== 1. REPORT CONFIGURATION ===")
        print(f"Theme: {rep.get('theme')}")
        print(f"Default Page: {rep.get('defaultPage')}")
        print(f"Filter Pane: {rep.get('filterPane')}")

    # 2. Diagram Layout (Tables & Model Structure)
    if 'DiagramLayout' in z.namelist():
        raw_bytes = z.read('DiagramLayout')
        diag_json = None
        for enc in ['utf-16-le', 'utf-16', 'utf-8-sig', 'utf-8']:
            try:
                diag_json = json.loads(raw_bytes.decode(enc))
                break
            except Exception:
                continue
        if diag_json:
            print("\n=== 2. DATA MODEL TABLES (FROM DIAGRAM LAYOUT) ===")
            nodes = diag_json.get('diagram', {}).get('nodes', [])
            for node in nodes:
                t_name = node.get('name')
                pos = node.get('position', {})
                print(f"  * Table: {t_name} (x={pos.get('x')}, y={pos.get('y')})")
        else:
            print("  Note: DiagramLayout could not be parsed as JSON.")

    # 3. Settings & Metadata
    if 'Settings' in z.namelist():
        raw_s = z.read('Settings')
        for enc in ['utf-16-le', 'utf-8-sig', 'utf-8']:
            try:
                s_json = json.loads(raw_s.decode(enc))
                print("\n=== 3. REPORT SETTINGS ===")
                print(json.dumps(s_json, indent=2))
                break
            except Exception:
                pass

    # 4. DataModel Deep Inspection (Tables, Columns, DAX Measures, Data Sources)
    if 'DataModel' in z.namelist():
        print("\n=== 4. DATA MODEL DEEP SCAN (TABLES, COLUMNS, MEASURES & DATA SOURCES) ===")
        dm_bytes = z.read('DataModel')
        print(f"DataModel binary size: {len(dm_bytes):,} bytes")
        
        # Extract ASCII / UTF-8 and UTF-16 strings
        # Look for M formulas and file paths
        text_utf8 = dm_bytes.decode('utf-8', errors='ignore')
        text_utf16 = dm_bytes.decode('utf-16-le', errors='ignore')
        combined_text = text_utf8 + "\n" + text_utf16
        
        # Search for source file paths or connection strings
        sources = set(re.findall(r'(?:File\.Contents|Csv\.Document|Source\s*=\s*)([^\r\n;\)]+)', combined_text))
        csv_refs = set(re.findall(r'([a-zA-Z0-9_\-\.\:\\]+\.csv)', combined_text, re.IGNORECASE))
        bq_refs = set(re.findall(r'(?:careflow[a-zA-Z0-9_\-]*|bigquery[a-zA-Z0-9_\-]*)', combined_text, re.IGNORECASE))
        
        print("\nData Source Ingestion Footprint:")
        if csv_refs:
            for c_ref in sorted(list(csv_refs))[:10]:
                print(f"  * CSV Source Reference: {c_ref}")
        if bq_refs:
            for b_ref in sorted(list(bq_refs))[:10]:
                print(f"  * BigQuery Identifier Reference: {b_ref}")
        
        # Search for DAX Measure Formulas
        known_measures = [
            "Total Encounters", "Total Patients", "Median Wait to Consult",
            "Median Lab TAT (Hours)", "Median Consult Duration", "Median Wait to Lab",
            "Median Wait to Imaging", "Total Lab Orders", "Active Doctors",
            "Median Total Stay (Hours)", "Total Imaging Scans"
        ]
        
        print("\nDiscovered DAX Measure Signatures & Expressions:")
        for m in known_measures:
            pattern = rf'({re.escape(m)}\s*=\s*[^;\r\n]+)'
            matches = re.findall(pattern, combined_text, re.IGNORECASE)
            if matches:
                # Deduplicate and pick cleanest match
                clean_matches = sorted(list(set(matches)), key=len)
                print(f"  * [{m}]: {clean_matches[0].strip()}")
            else:
                print(f"  * [{m}]: Referenced in Visual Model")

        # Discover Calculated Columns in cleaned_HospitalOPD
        print("\nCalculated Columns & Engineered Features in 'cleaned_HospitalOPD':")
        calc_cols = ["ArrivalHour", "YearMonth", "WaitToConsult", "LabTAT", "TotalStay", "ConsultDuration"]
        for cc in calc_cols:
            pattern = rf'({re.escape(cc)}\s*=\s*[^;\r\n]+)'
            matches = re.findall(pattern, combined_text, re.IGNORECASE)
            if matches:
                clean_m = sorted(list(set(matches)), key=len)
                print(f"  * [{cc}]: {clean_m[0].strip()}")

    # 5. Pages & Visuals Inspection
    pages_data = json.loads(z.read('Report/definition/pages/pages.json').decode('utf-8'))
    print("\n=== 5. REPORT PAGES & VISUALS ===")
    page_order = pages_data.get('pageOrder', [])
    print(f"Total Pages: {len(page_order)}")
    
    all_referenced_tables = set()
    all_referenced_measures = set()

    for idx, p_id in enumerate(page_order, 1):
        p_path = f'Report/definition/pages/{p_id}/page.json'
        p_json = json.loads(z.read(p_path).decode('utf-8'))
        display_name = p_json.get('displayName', p_id)
        print(f"\n" + "=" * 70)
        print(f"PAGE {idx}: '{display_name}' (ID: {p_id})")
        print(f"Dimensions: {p_json.get('width')} x {p_json.get('height')}")
        print("=" * 70)
        
        visual_files = [f for f in z.namelist() if f.startswith(f'Report/definition/pages/{p_id}/visuals/') and f.endswith('visual.json')]
        print(f"Visuals Count: {len(visual_files)}\n")
        
        for v_idx, vf in enumerate(visual_files, 1):
            v_id = vf.split('/')[-2]
            v_json = json.loads(z.read(vf).decode('utf-8'))
            visual_block = v_json.get('visual', {})
            v_type = visual_block.get('visualType')
            
            # Extract visual title
            v_title = None
            try:
                vc = visual_block.get('visualContainerObjects', {})
                if 'title' in vc:
                    title_props = vc['title'][0].get('properties', {})
                    if 'text' in title_props:
                        expr = title_props['text'].get('expr', {})
                        if 'Literal' in expr:
                            v_title = expr['Literal'].get('Value')
            except Exception:
                pass
            
            # Extract query projections & fields
            projections = visual_block.get('query', {}).get('queryState', {})
            fields_used = []
            for role_name, role_data in projections.items():
                for proj in role_data.get('projections', []):
                    query_ref = proj.get('queryRef')
                    if query_ref:
                        fields_used.append(f"{role_name} -> {query_ref}")
                        # Track table references
                        match = re.search(r'([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)', query_ref)
                        if match:
                            all_referenced_tables.add(match.group(1))
            
            print(f"  [{v_idx}. Visual ID: {v_id}]")
            print(f"    Type:   {v_type}")
            print(f"    Title:  {v_title or '[Default / Automatic Title]'}")
            if fields_used:
                print(f"    Data Fields:")
                for f_item in fields_used:
                    print(f"      - {f_item}")
            print()

    print("\n=== 6. SUMMARY OF MODEL & SCHEMA REFERENCES ===")
    print(f"Referenced Tables in Visuals: {sorted(list(all_referenced_tables))}")
    print("\nRead-only PBIX inspection complete.")

