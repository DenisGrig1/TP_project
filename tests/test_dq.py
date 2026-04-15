from pathlib import Path
import sys

import pandas as pd

# Добавляем путь к исходному коду
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from demo_pipeline.dq import check_not_null, check_unique_key, check_numeric_range

def test_check_not_null_pass():
    """Позитивный тест: проверка проходит, если NULL нет."""
    df = pd.DataFrame({"ts": ["2026-01-01 00:00:00", "2026-01-01 01:00:00"]})
    result = check_not_null(df, "ts")
    assert result["status"] == "PASS"

def test_check_not_null_fail():
    """Негативный тест: проверка падает, если есть NULL."""
    df = pd.DataFrame({"ts": ["2026-01-01 00:00:00", None]})
    result = check_not_null(df, "ts")
    assert result["status"] == "FAIL"
    assert result["details"]["null_count"] == 1

def test_check_unique_key_fail_on_duplicates():
    """Негативный тест: проверка уникальности находит дубликаты."""
    df = pd.DataFrame({
        "date": ["2026-03-01", "2026-03-01"],
        "city_id": ["GB_LON", "GB_LON"]
    })
    result = check_unique_key(df, ["date", "city_id"])
    assert result["status"] == "FAIL"
    assert result["details"]["duplicate_rows"] == 2

def test_check_numeric_range_boundary_passes():
    """Граничный тест: значения на границе диапазона проходят проверку."""
    df = pd.DataFrame({"temp": [-80, 0, 60]})
    result = check_numeric_range(df, "temp", min_value=-80, max_value=60, level="WARNING")
    assert result["status"] == "PASS"

def test_check_numeric_range_out_of_bounds_fails():
    """Негативный тест: значения вне диапазона не проходят проверку."""
    df = pd.DataFrame({"temp": [-81, 61]})
    result = check_numeric_range(df, "temp", min_value=-80, max_value=60, level="WARNING")
    assert result["status"] == "WARNING"
    assert result["details"]["bad_count"] == 2
