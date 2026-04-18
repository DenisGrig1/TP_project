import requests
import yaml
import json
import pandas as pd
from pathlib import Path
from datetime import timedelta

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
