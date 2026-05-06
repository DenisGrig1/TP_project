import extract
import transform
import mart
import load
import dq
import json
import yaml
import sys
import argparse
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone, timedelta

def read_state(path: Path) -> dict:
    if not path.exists():
        return {
            "variant_id": None,
            "last_successful_watermark": None,
            "last_run_at_utc": None,
            "last_mode": None,
        }
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def utc_now_tag() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def write_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Pipeline")
    p.add_argument("--mode", choices=["full", "incremental"], default="full")
    p.add_argument("--fail-after", choices=["none", "extract", "transform", "load"], default="none")
    return p

def run_pipeline(mode, fail_after="none"):
    curr_file = Path(__file__)
    base_dir = curr_file.parent.parent
    config_path = base_dir  / "configs" / "variant_04.yml"
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    state_path = base_dir / "data"/ "state" / "state.json"
    state = read_state(state_path)
    
    changed = config
    changed["api"]["params"]["start_date"] = start_date
    changed["api"]["params"]["end_date"] = end_date
    with open(config_path, "w") as cfg:
        yaml.dump(changed, cfg)

    raw_path = extract.ExtractData(config_path, base_dir, mode, state)
    if raw_path is None:
        print("Pipeline finished: nothing new to process.")
        return {
            "status": "no_new_data",
            "rows_in_batch": 0,
            "state": state,
        }
    print(f"Raw JSON-file was saved at: {raw_path}")

    normalized_path = transform.TransformToCSV(base_dir, raw_path, config_path, mode)
    print(f"Normalized CSV-file was saved at: {normalized_path}")

    dq_results = dq.run_dq(normalized_path, config)
    dq_path = base_dir / "docs" / f"dq_report_{utc_now_tag()}.json"
    dq_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dq_path, "w", encoding="utf-8") as f:
        json.dump(dq_results, f, ensure_ascii=False, indent=2, default=str)
    print(f"DQ checks were saved at: {dq_path}")

    mart_path = mart.ToMart(base_dir, normalized_path)
    print(f"Daily mart CSV-file was saved at: {mart_path}")

    row_count = load.LoadToSQL(base_dir, mart_path)
    print(f"Loaded to SQL, number of rows: {row_count}")

    with open(mart_path, "r") as mart_file:
        data = pd.read_csv(mart_file)
    data_max_date = pd.to_datetime(max(data["date"])).strftime("%Y-%m-%d")
    state = {
        "variant_id": config["variant_id"],
        "last_successful_watermark": data_max_date,
        "last_run_at_utc": utc_now_tag(),
        "last_mode": mode,
    }
    write_state(state_path, state)

    return {
        "status": "ok",
        "rows_in_batch": int(len(data)),
        "num_of_rows": int(row_count),
        "state": state,
    }

if __name__ == "__main__":
    args = build_parser().parse_args()
    result = run_pipeline(args.mode, args.fail_after)
    print(json.dumps(result, ensure_ascii=False, indent=2))
