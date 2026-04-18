import yaml
import pandas as pd
from pathlib import Path

def ToMart(base_dir: Path, normalized_path: Path):
    mart_name = "mart_daily.csv"

    df = pd.read_csv(normalized_path, parse_dates=["time"])
    df["time"] = df["time"].dt.date
    df["rainy_hour"] = (df["precipitation"] > 0).astype(int)

    mart_df = df.groupby("time").agg({
        "temperature_2m" : "mean",
        "relative_humidity_2m" : "mean",
        "precipitation" : "sum",
        "wind_speed_10m" : "mean",
        "rainy_hour" : "sum"
    }).round(1).reset_index()
    mart_df["city_id"] = df["city_id"][0]
    mart_df = mart_df.rename(columns= {"time" : "date", "rainy_hour" : "rainy_hours"})
    
    ref_cities = pd.read_csv(base_dir / "configs" / "cities.csv")
    mart_df = mart_df.merge(
        ref_cities,
        on = "city_id",
        how = "left"
    )

    mart_path = base_dir / "data" / "mart" / mart_name
    mart_path.parent.mkdir(parents=True, exist_ok=True)
    mart_df.to_csv(mart_path, sep=",", index=False, encoding="utf-8")
    
    return mart_path
