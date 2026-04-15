# src/demo_pipeline/dq.py
from __future__ import annotations

import pandas as pd

def build_result(check: str, status: str, level: str, message: str, details: dict | None = None) -> dict:
    return {
        "check": check,
        "status": status,
        "level": level,
        "message": message,
        "details": details or {}
    }

def check_non_empty(df: pd.DataFrame, check_name: str = "non_empty_dataset", level: str = "FAIL", min_rows: int = 1) -> dict:
    row_count = len(df)
    ok = row_count >= min_rows
    return build_result(
        check_name,
        "PASS" if ok else level,
        level,
        f"row_count = {row_count}, min_rows = {min_rows}",
        {"row_count": int(row_count), "min_rows": int(min_rows)}
    )

def check_not_null(df: pd.DataFrame, column: str, check_name: str | None = None, level: str = "FAIL") -> dict:
    null_count = int(df[column].isna().sum())
    ok = null_count == 0
    return build_result(
        check_name or f"not_null__{column}",
        "PASS" if ok else level,
        level,
        f"{column}: null_count = {null_count}",
        {"column": column, "null_count": null_count}
    )

def check_unique_key(df: pd.DataFrame, columns: list[str], check_name: str = "unique_business_key", level: str = "FAIL") -> dict:
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

def check_numeric_range(df: pd.DataFrame, column: str, min_value: float | None = None, max_value: float | None = None, check_name: str | None = None, level: str = "WARNING") -> dict:
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
        check_name or f"range__{column}",
        "PASS" if ok else level,
        level,
        f"{column}: out_of_range = {bad_count}",
        {"column": column, "min": min_value, "max": max_value, "bad_count": bad_count, "sample": sample}
    )

def check_non_negative(df: pd.DataFrame, column: str, check_name: str | None = None, level: str = "FAIL") -> dict:
    s = pd.to_numeric(df[column], errors="coerce")
    mask = s < 0
    bad_count = int(mask.sum())
    ok = bad_count == 0
    sample = df.loc[mask, [column]].head(5).to_dict(orient="records")
    return build_result(
        check_name or f"non_negative__{column}",
        "PASS" if ok else level,
        level,
        f"{column}: negative_values = {bad_count}",
        {"column": column, "bad_count": bad_count, "sample": sample}
    )

def check_monotonic_increasing(df: pd.DataFrame, column: str, check_name: str | None = None, level: str = "WARNING") -> dict:
    s = pd.to_datetime(df[column], errors="coerce")
    # Проверяем, что нет NA и что разница между соседними значениями >= 0
    if s.isna().any():
        return build_result(
            check_name or f"monotonic__{column}",
            "FAIL",
            "FAIL",
            f"{column}: contains NA values, cannot check monotonicity",
            {"column": column}
        )
    is_increasing = (s.diff().dropna() >= pd.Timedelta(0)).all()
    ok = is_increasing
    return build_result(
        check_name or f"monotonic__{column}",
        "PASS" if ok else level,
        level,
        f"{column}: is_monotonic_increasing = {is_increasing}",
        {"column": column, "is_monotonic_increasing": bool(is_increasing)}
    )

def run_dq_checks(df: pd.DataFrame, config: dict) -> list[dict]:
    results = []
    rules = config['dq_rules']
    
    rules_dict = {rule['name']: rule for rule in rules}

    results.append(check_non_empty(df, level="FAIL"))

    results.append(check_not_null(df, "Время, ГГГГ-ММ-ДД ЧЧ:ММ:СС", check_name="ts_not_null", level="FAIL"))

    results.append(check_monotonic_increasing(df, "Время, ГГГГ-ММ-ДД ЧЧ:ММ:СС", check_name="ts_monotonic", level="WARNING"))

    rule_temp = rules_dict.get('temperature_range', {})
    results.append(check_numeric_range(
        df, "Температура, °C", 
        min_value=rule_temp.get('min', -80), 
        max_value=rule_temp.get('max', 60), 
        check_name="temperature_range", 
        level=rule_temp.get('level', 'WARNING')
    ))

    rule_hum = rules_dict.get('humidity_range', {})
    results.append(check_numeric_range(
        df, "Влажность, %", 
        min_value=rule_hum.get('min', 0), 
        max_value=rule_hum.get('max', 100), 
        check_name="humidity_range", 
        level=rule_hum.get('level', 'WARNING')
    ))

    rule_prec = rules_dict.get('precipitation_non_negative', {})
    results.append(check_non_negative(
        df, "Осадки, мм", 
        check_name="precipitation_non_negative", 
        level=rule_prec.get('level', 'FAIL')
    ))

    rule_dup = rules_dict.get('unique_city_ts', {})
    results.append(check_unique_key(
        df, ["ID города", "Время, ГГГГ-ММ-ДД ЧЧ:ММ:СС"], 
        check_name="unique_city_ts", 
        level=rule_dup.get('level', 'FAIL')
    ))

    return results
