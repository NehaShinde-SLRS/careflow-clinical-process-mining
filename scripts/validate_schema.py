
import argparse
from pathlib import Path

import pandas as pd


def validate_schema(input_file):
    path = Path(input_file)

    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    # The supplied file is CSV-formatted text, even if its
    # filename ends in .xls.
    df = pd.read_csv(path, low_memory=False)

    print("\n=== HospitalOPD Schema Validation ===")
    print(f"Dataset file: {path.name}")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Exact duplicate rows: {df.duplicated().sum():,}")

    schema = pd.DataFrame({
        "column_name": df.columns,
        "data_type": [str(dtype) for dtype in df.dtypes],
        "non_null_count": df.notna().sum().values,
        "missing_count": df.isna().sum().values,
        "missing_percentage": (
            df.isna().mean().values * 100
        ).round(2),
        "unique_values": df.nunique(dropna=True).values,
    })

    print("\nColumn details:")
    print(schema.to_string(index=False))

    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / "schema_report.csv"
    schema.to_csv(report_path, index=False)

    print(f"\nSchema report saved to: {report_path}")
    print("Validation completed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Validate the HospitalOPD dataset schema."
    )
    parser.add_argument(
        "dataset",
        help="Path to the HospitalOPD CSV-formatted dataset"
    )
    args = parser.parse_args()

    validate_schema(args.dataset)
