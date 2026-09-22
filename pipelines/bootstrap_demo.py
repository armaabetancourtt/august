from __future__ import annotations

from pathlib import Path

import duckdb

from august.synthetic.demo import generate_macro_history, generate_properties

ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC = ROOT / "data" / "synthetic"
PROCESSED = ROOT / "data" / "processed"


def main() -> None:
    SYNTHETIC.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)

    macro = generate_macro_history()
    properties = generate_properties()

    macro_path = SYNTHETIC / "macro_demo.csv"
    properties_path = SYNTHETIC / "properties_demo.csv"
    warehouse_path = PROCESSED / "august.duckdb"

    macro.to_csv(macro_path, index=False)
    properties.to_csv(properties_path, index=False)

    con = duckdb.connect(str(warehouse_path))
    con.execute(
        "CREATE OR REPLACE TABLE macro_observations AS SELECT * FROM read_csv_auto(?)",
        [str(macro_path)],
    )
    con.execute(
        "CREATE OR REPLACE TABLE properties AS SELECT * FROM read_csv_auto(?)",
        [str(properties_path)],
    )
    con.close()

    print(f"SYNTHETIC DATA created: {macro_path}")
    print(f"SYNTHETIC DATA created: {properties_path}")
    print(f"DuckDB warehouse created: {warehouse_path}")


if __name__ == "__main__":
    main()
