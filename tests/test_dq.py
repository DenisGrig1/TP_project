from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dq import check_not_null, check_unique_key, check_numeric_range

def test_check_not_null_pass():
    df = pd.DataFrame({"x": [1, 2, 3]})
    result = check_not_null(df, "x")
    assert result["status"] == "PASS"

def test_check_unique_key_fail_on_duplicates():
    df = pd.DataFrame({
        "date": ["2026-03-01", "2026-03-01"],
        "city_id": ["RU_MOW", "RU_MOW"]
    })
    result = check_unique_key(df, ["date", "city_id"])
    assert result["status"] == "FAIL"
    assert result["details"]["duplicate_rows"] == 2

def test_check_numeric_range_boundary_passes():
    df = pd.DataFrame({"temp": [-60, 0, 60]})
    result = check_numeric_range(df, "temp", min_value=-60, max_value=60, level="WARNING")
    assert result["status"] == "PASS"
