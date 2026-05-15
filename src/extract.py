import requests
import yaml
import json
import argparse
import pandas as pd
from pathlib import Path
from datetime import timedelta

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

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Extract")
    p.add_argument("--mode", choices=["full", "incremental"], default="full")
    return p

def ExtractData(config_path: Path, base_dir: Path, mode: str, state: dict):
    json_name = "raw.json"

    with open(config_path, "r", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)
    api = config["api"]

    if mode == "incremental" and state.get("last_successful_watermark"):
        wm = pd.to_datetime(state["last_successful_watermark"])
        if wm >= pd.to_datetime(api["params"]["end_date"]):
            return None
        else:
            api["params"]["start_date"] = (wm + timedelta(days=1)).strftime("%Y-%m-%d")
    
    try:
        r = requests.get(api["base_url"], params=api["params"])
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(f"HTTPError: {err}")
        return 0
    except requests.exceptions.Timeout:
        print("Timeout-error")
        return 0
    except requests.exceptions.RequestException as e:
        print(f"Unknown error: {e}")
        return 0
    
    data = r.json()
    raw_path = base_dir / "data" / "raw" / json_name
    raw_path.parent.mkdir(parents=True, exist_ok=True)

    with open(raw_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)

    return raw_path

if __name__ == "__main__":
    base_dir = Path(__file__).parent.parent
    config_path = base_dir / "configs" / "variant_04.yml"
    state_path = base_dir / "data" / "state" / "state.json"
    state = read_state(state_path)
    args = build_parser().parse_args()
    ExtractData(config_path, base_dir, args.mode, state)
    
    
