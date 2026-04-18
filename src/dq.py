import pandas as pd
from pathlib import Path

def build_result(check, status, level, message, details=None):
    return {
        "check": check,
        "status": status,
        "level": level,
        "message": message,
        "details": details or {}
    }

def check_non_empty(df, check_name="non_empty_dataset", level="FAIL", min_rows=1):
    row_count = len(df)
    ok = row_count >= min_rows
    return build_result(
        check_name,
        "PASS" if ok else level,
        level,
        f"row_count = {row_count}, min_rows = {min_rows}",
        {"row_count": int(row_count), "min_rows": int(min_rows)}
    )

def check_not_null(df, column, check_name=None, level="FAIL"):
    null_count = int(df[column].isna().sum())
    ok = null_count == 0
    return build_result(
        check_name or f"not_null_{column}",
        "PASS" if ok else level,
        level,
        f"{column}: null_count = {null_count}",
        {"column": column, "null_count": null_count}
    )

def check_unique_key(df, columns, check_name="unique_business_key", level="FAIL"):
    dup_mask = df.duplicated(subset=columns, keep=False)
    dup_count = int(dup_mask.sum())
    ok = dup_count == 0
    sample_dups = df.loc[dup_mask, columns].head(5).astype(str).to_dict(orient="records")
    return build_result(
        check_name,
        "PASS" if ok else level,
        level,
        f"duplicate_rows_on_key = {dup_count}",
        {"columns": columns, "duplicate_rows": dup_count, "sample": sample_dups}
    )

def check_numeric_range(df, column, min_value=None, max_value=None, check_name=None, level="WARNING"):
    s = pd.to_numeric(df[column], errors="coerce")
    mask = pd.Series(False, index=df.index)
    if min_value is not None:
        mask |= s < min_value
    if max_value is not None:
        mask |= s > max_value
    bad_count = int(mask.sum())
    ok = bad_count == 0
    sample = df.loc[mask, [column]].head(5).to_dict(orient="records")
    return build_result(
        check_name or f"range_{column}",
        "PASS" if ok else level,
        level,
        f"{column}: out_of_range = {bad_count}",
        {"column": column, "min": min_value, "max": max_value, "bad_count": bad_count, "sample": sample}
    )

def check_non_negative(df, column, check_name=None, level="FAIL"):
    s = pd.to_numeric(df[column], errors="coerce")
    mask = s < 0
    bad_count = int(mask.sum())
    ok = bad_count == 0
    sample = df.loc[mask, [column]].head(5).to_dict(orient="records")
    return build_result(
        check_name or f"non_negative_{column}",
        "PASS" if ok else level,
        level,
        f"{column}: negative_values = {bad_count}",
        {"column": column, "bad_count": bad_count, "sample": sample}
    )

def run_dq(normalized_path: Path, config: dict):
    df = pd.read_csv(normalized_path, parse_dates=["time"])
    rules = config["dq_rules"]
    results = []
    results.append(check_non_empty(df, min_rows=1))
    results.append(check_not_null(df, rules["not_null"]["collumn"]))
    results.append(check_unique_key(df, rules["unique_key"]["collumns"]))
    results.append(check_numeric_range(df, 
        column=rules["temperature_range"]["collumn"], 
        min_value=rules["temperature_range"]["min"], 
        max_value=rules["temperature_range"]["max"], 
        level="WARNING"))
    results.append(check_numeric_range(df, 
        column=rules["humidity_range"]["collumn"], 
        min_value=rules["humidity_range"]["min"], 
        max_value=rules["humidity_range"]["max"], 
        level="WARNING"))
    results.append(check_non_negative(df, rules["non_negative"]["collumn"]))
    
    return results

