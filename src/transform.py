import json
import yaml
import argparse
import pandas as pd
from pathlib import Path

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Transform")
    p.add_argument("--mode", choices=["full", "incremental"], default="full")
    return p

def TransformToCSV(base_dir: Path, raw_path: Path, config_path: Path, mode: str):
    normalized_name = "normalized.csv"

    with open(raw_path, "r") as json_file:
        data_dict = json.load(json_file)
    
    df = pd.DataFrame(data_dict["hourly"])
    with open(config_path, "r") as config_file:
        config = yaml.safe_load(config_file)
        df["city_id"] = config["entity"]["city_id"]

    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    df = df.dropna()
    df = df.drop_duplicates(subset=["time"])
    df = df.sort_values("time").reset_index(drop="True")

    normalized_path = base_dir / "data" / "normalized" / normalized_name
    normalized_path.parent.mkdir(parents=True, exist_ok=True)
    if mode == "incremental":
        df.to_csv(normalized_path, sep=",",mode= "a", header=False, index=False, encoding="utf-8")
    else:
        df.to_csv(normalized_path, sep=",", index=False, encoding="utf-8")

    return normalized_path

if __name__ == "__main__":
    base_dir = Path(__file__).parent.parent
    config_path = base_dir / "configs" / "variant_04.yml"
    raw_path = base_dir / "data" / "raw" / "raw.json"
    args = build_parser().parse_args()
    TransformToCSV(base_dir, raw_path, config_path, args.mode)
    
