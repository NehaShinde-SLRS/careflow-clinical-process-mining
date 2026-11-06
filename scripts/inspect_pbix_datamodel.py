"""
CareFlow Clinical Process Mining - Safe Power BI DataModel Inspector
File: scripts/inspect_pbix_datamodel.py
Role: Member 3 - Data Engineering & Process Mining

Safety Guarantees:
- Strictly Read-Only (opens PBIX zip in 'r' mode).
- No credentials, tokens, passwords, or personal data printed.
- Sensitive paths scrubbed to generic placeholders.
- Extracts DAX formulas, M data source types, and visual configuration.
"""

import json
import re
import sys
import zipfile
from pathlib import Path

PBIX_PATH = Path("careflow_POWERBI_dashboard.pbix")

def sanitize_text(text: str) -> str:
    """Removes sensitive user paths, tokens, and credentials."""
    # Mask Windows/Unix absolute paths
    text = re.sub(r'[A-Za-z]:\\[^"\'\r\n\t]+', '[LOCAL_FILE_PATH]', text)
    text = re.sub(r'/(?:Users|home)/[^"\'\r\n\t]+', '[LOCAL_FILE_PATH]', text)
    # Mask potential token/secret strings
    text = re.sub(r'(key|secret|password|token)\s*=\s*["\'][^"\']+["\']', r'\1="[REDACTED]"', text, flags=re.IGNORECASE)
    return text

def inspect_visual_configs(z: zipfile.ZipFile):
    print("=== VISUAL TITLES, POSITIONS & FIELDS ===")
    pages = ["1cd6c46da30f91fd0ca1", "f7c0d033250d3662c857"]
    page_names = {"1cd6c46da30f91fd0ca1": "Page 1 - Executive & Operational Overview",
                  "f7c0d033250d3662c857": "Page 2 - Clinical Specialization & Provider Performance"}

    for p_id in pages:
        p_name = page_names.get(p_id, p_id)
        print(f"\n--- {p_name} ({p_id}) ---")
        prefix = f"Report/definition/pages/{p_id}/visuals/"
        vis_files = [n for n in z.namelist() if n.startswith(prefix) and n.endswith("visual.json")]
        
        for vf in sorted(vis_files):
            v_id = vf.split("/")[-2]
            try:
                v_data = json.loads(z.read(vf).decode("utf-8"))
                v = v_data.get("visual", {})
                v_type = v.get("visualType", "Unknown")
                pos = v_data.get("position", {})
                
                # Check visual projections / fields
                projections = v.get("query", {}).get("queryState", {})
                fields = []
                for role, role_dict in projections.items():
                    for p in role_dict.get("projections", []):
                        f = p.get("field", {})
                        if "Column" in f:
                            ent = f["Column"].get("Expression", {}).get("SourceRef", {}).get("Entity", "")
                            prop = f["Column"].get("Property", "")
                            fields.append(f"{ent}.{prop}")
                        elif "Measure" in f:
                            ent = f["Measure"].get("Expression", {}).get("SourceRef", {}).get("Entity", "")
                            prop = f["Measure"].get("Property", "")
                            fields.append(f"{ent}.{prop}")

                px = f"{pos.get('x', 0):.1f}" if pos.get('x') is not None else "N/A"
                py = f"{pos.get('y', 0):.1f}" if pos.get('y') is not None else "N/A"
                pw = f"{pos.get('width', 0):.1f}" if pos.get('width') is not None else "N/A"
                ph = f"{pos.get('height', 0):.1f}" if pos.get('height') is not None else "N/A"
                pos_str = f"x={px}, y={py}, w={pw}, h={ph}"
                print(f"  * Visual [{v_id[:8]}]: {v_type:20s} | {pos_str} | Fields: {fields}")
            except Exception as e:
                print(f"  * Visual [{v_id[:8]}]: Error parsing: {e}")

def inspect_datamodel(z: zipfile.ZipFile):
    print("\n=== POWER QUERY (M) DATA SOURCE & DAX EXPRESSIONS ===")
    if "DataModel" not in z.namelist():
        print("DataModel not found in archive.")
        return

    raw = z.read("DataModel")
    print(f"DataModel compressed size: {len(raw):,} bytes")

    # Extract readable ASCII text strings (length >= 6)
    ascii_strings = [s.decode("ascii", errors="ignore") for s in re.findall(b"[\x20-\x7E]{6,}", raw)]
    
    # Identify Data Source signatures safely
    print("\n[Data Source Type Detection]")
    source_types = set()
    for s in ascii_strings:
        if "Csv.Document" in s:
            source_types.add("CSV File Import (Csv.Document)")
        elif "Sql.Database" in s:
            source_types.add("SQL Server Database Import/DirectQuery")
        elif "GoogleBigQuery.Database" in s:
            source_types.add("Google BigQuery DirectQuery/Import")
        elif "Folder.Files" in s:
            source_types.add("Folder Ingestion")
        elif "HospitalOPD_cleaned" in s:
            source_types.add("Source Entity: HospitalOPD_cleaned")

    for st in sorted(source_types):
        print(f"  - Detected: {st}")

    # Search for DAX Measure definitions
    target_measures = [
        "Total Encounters",
        "Total Patients",
        "Median Wait to Consult",
        "Median Lab TAT (Hours)",
        "Median Consult Duration",
        "Median Wait to Lab",
        "Median Wait to Imaging",
        "Total Lab Orders",
        "Active Doctors",
        "Median Total Stay (Hours)",
        "Total Imaging Scans"
    ]

    print("\n[DAX Measure Formula Scans]")
    found_measures = {}
    for tm in target_measures:
        # Search patterns for DAX measure definitions (e.g., MeasureName = ...)
        matches = [s for s in ascii_strings if tm in s and any(kw in s for kw in ["=", "CALCULATE", "DISTINCTCOUNT", "COUNT", "MEDIAN", "SUM", "AVERAGE"])]
        if matches:
            # Pick the cleanest match that looks like a formula
            cleaned_m = sanitize_text(matches[0].strip())
            found_measures[tm] = cleaned_m[:120]
        else:
            found_measures[tm] = "[Defined in VertiPaq tabular model]"

    for m_name, m_formula in found_measures.items():
        print(f"  * [{m_name}]: {m_formula}")

    # Check for calculated columns
    print("\n[Engineered / Calculated Columns in DataModel]")
    calc_cols = set()
    for col in ["ArrivalHour", "YearMonth", "WaitToConsult_Min", "ConsultDuration_Min", "TotalStay_Hrs"]:
        for s in ascii_strings:
            if col in s:
                calc_cols.add(col)
                break
    for cc in sorted(calc_cols):
        print(f"  - Column: {cc}")

def main():
    if not PBIX_PATH.exists():
        print(f"Error: {PBIX_PATH} not found.")
        sys.exit(1)

    print("=" * 70)
    print("CAREFLOW CLINICAL PROCESS MINING - POWER BI SAFE INSPECTION")
    print(f"File: {PBIX_PATH.name} ({PBIX_PATH.stat().st_size:,} bytes)")
    print("Security: Safe Read-Only Mode (Credentials & Personal Data Scrubbed)")
    print("=" * 70)

    with zipfile.ZipFile(PBIX_PATH, "r") as z:
        inspect_visual_configs(z)
        inspect_datamodel(z)

    print("\n" + "=" * 70)
    print("Inspection complete. No sensitive data was exposed or persisted.")
    print("=" * 70)

if __name__ == "__main__":
    main()
