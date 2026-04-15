#cd C:\Users\Denis\anaconda_projects\ddf91dc2-9e39-452c-92b7-90426cb2bede\project
#python src/pipeline.py --config configs/variant_4.yml --mode full

import argparse
import json
import logging
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import pandas as pd
import requests
import yaml
from sqlalchemy import create_engine, inspect, text

# --- Импорт функций DQ ---
from demo_pipeline.dq import run_dq_checks

# ------------------------------------------------------------
# 1. Настройка логирования
# ------------------------------------------------------------
def setup_logging(log_path: Path) -> logging.Logger:
    logger = logging.getLogger("week6_pipeline")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    log_path.parent.mkdir(parents=True, exist_ok=True)
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger

# ------------------------------------------------------------
# 2. Управление состоянием (State / Watermark)
# ------------------------------------------------------------
def read_state(state_path: Path) -> dict:
    if not state_path.exists():
        return {
            "variant_id": None,
            "last_successful_watermark": None,
            "last_run_at_utc": None,
            "last_mode": None,
        }
    with open(state_path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_state(state_path: Path, state: dict) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

# ------------------------------------------------------------
# 3. Извлечение данных (Extract)
# ------------------------------------------------------------
def extract(config: dict, state: dict, mode: str, base_dir: Path, logger: logging.Logger):
    params = config["api"]["params"].copy()
    
    if mode == "incremental" and state.get("last_successful_watermark"):
        start_date = datetime.strptime(state["last_successful_watermark"], "%Y-%m-%d") + timedelta(days=1)
        logger.info(f"Incremental mode: fetching data from {start_date.date()}")
    else:
        start_date = datetime.now() - timedelta(days=30)
        logger.info(f"Full mode (or no watermark): fetching data from {start_date.date()}")

    end_date = datetime.now()
    
    params["start_date"] = start_date.strftime("%Y-%m-%d")
    params["end_date"] = end_date.strftime("%Y-%m-%d")

    try:
        r = requests.get(config["api"]["base_url"], params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        logger.error(f"API request failed: {e}")
        raise

    run_tag = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
    raw_path = base_dir / "data" / "raw" / f"raw_{run_tag}.json"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Saved raw snapshot: {raw_path.name}")
    return raw_path, data

# ------------------------------------------------------------
# 4. Преобразование данных (Transform)
# ------------------------------------------------------------
def transform(raw_path: Path, config: dict, base_dir: Path, logger: logging.Logger) -> Path:
    with open(raw_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    df = pd.DataFrame(raw_data["hourly"])
    
    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    df["relative_humidity_2m"] = pd.to_numeric(df["relative_humidity_2m"], errors="coerce")
    df["city_id"] = config["entity"]["city_id"]

    df = df.dropna(subset=["time"])
    df = df.drop_duplicates(subset=["time"], keep="first")
    df = df.sort_values("time").reset_index(drop=True)

    df["precipitation"] = df["precipitation"].fillna(0)
    df = df.dropna(subset=["temperature_2m"])

    df.columns = [
        "Время, ГГГГ-ММ-ДД ЧЧ:ММ:СС",
        "Температура, °C",
        "Влажность, %",
        "Осадки, мм",
        "Скорость ветра, км/ч",
        "ID города"
    ]

    run_tag = raw_path.stem.replace("raw_", "")
    normalized_path = base_dir / "data" / "normalized" / f"normalized_{run_tag}.csv"
    normalized_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(normalized_path, index=False, encoding="utf-8")
    
    logger.info(f"Saved normalized dataset: {normalized_path.name}, rows={len(df)}")
    
    # --- Запуск DQ проверок ---
    logger.info("Running DQ checks on normalized data...")
    dq_results = run_dq_checks(df, config)
    
    # Сохраняем DQ отчеты в папку docs
    docs_dir = base_dir / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    dq_report_path = docs_dir / f"dq_report_{run_tag}.json"
    dq_md_path = docs_dir / f"dq_report_{run_tag}.md"
    
    with open(dq_report_path, "w", encoding="utf-8") as f:
        json.dump(dq_results, f, ensure_ascii=False, indent=2, default=str)
        
    # Генерируем Markdown отчет
    generate_dq_markdown_report(dq_results, dq_md_path, config['entity']['city_name'])
    
    # Логируем статус проверок
    for res in dq_results:
        if res['status'] != 'PASS':
            logger.warning(f"DQ Check '{res['check']}' status: {res['status']} - {res['message']}")
    
    return normalized_path

def generate_dq_markdown_report(results: list[dict], output_path: Path, dataset_name: str):
    """Генерирует Markdown отчет по результатам DQ проверок."""
    md_lines = [
        f"# DQ Report for {dataset_name}",
        f"Generated at: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "| Check | Status | Level | Message |",
        "|---|---|---|---|"
    ]
    for row in results:
        md_lines.append(f"| {row['check']} | **{row['status']}** | {row['level']} | {row['message']} |")
    
    md_lines.append("")
    md_lines.append("## Details")
    for row in results:
        if row['status'] != 'PASS':
            md_lines.append(f"### {row['check']}")
            md_lines.append(f"- **Status**: {row['status']}")
            md_lines.append(f"- **Level**: {row['level']}")
            md_lines.append(f"- **Message**: {row['message']}")
            md_lines.append(f"- **Details**:")
            for k, v in row['details'].items():
                md_lines.append(f"  - {k}: {v}")
            md_lines.append("")
            
    output_path.write_text("\n".join(md_lines), encoding="utf-8")
    return output_path

# ------------------------------------------------------------
# 5. Построение витрины (Build Mart)
# ------------------------------------------------------------
def build_mart(normalized_path: Path, config: dict, base_dir: Path, logger: logging.Logger) -> Path:
    # ... (код без изменений)
    df = pd.read_csv(normalized_path, parse_dates=['Время, ГГГГ-ММ-ДД ЧЧ:ММ:СС'])
    df.columns = ['Время', 'Температура', 'Влажность', 'Осадки', 'Скорость ветра', 'city_id']
    df['Дата'] = df['Время'].dt.date

    ref_cities = pd.read_csv(base_dir / "reference" / "cities.csv")

    kpi_df = df.groupby('Дата').agg(
        Средняя_температура=('Температура', 'mean'),
        Сумма_осадков=('Осадки', 'sum'),
        Колво_часов_с_осадками=('Осадки', lambda x: (x > 0).sum()),
        Скорость_ветра=('Скорость ветра', 'mean')
    ).reset_index()

    kpi_df['Средняя_температура'] = kpi_df['Средняя_температура'].round(1)
    kpi_df['Скорость_ветра'] = kpi_df['Скорость_ветра'].round(1)
    kpi_df['city_id'] = config["entity"]["city_id"]

    merged_kpi_df = kpi_df.merge(ref_cities, on="city_id", how="left")

    run_tag = normalized_path.stem.replace("normalized_", "")
    mart_path = base_dir / "data" / "mart" / f"mart_daily_{run_tag}.csv"
    mart_path.parent.mkdir(parents=True, exist_ok=True)
    merged_kpi_df.to_csv(mart_path, index=False, encoding='utf-8')
    
    logger.info(f"Saved mart dataset: {mart_path.name}, rows={len(merged_kpi_df)}")
    return mart_path

# ------------------------------------------------------------
# 6. Загрузка в БД (Load) с идемпотентностью
# ------------------------------------------------------------
def load_mart(mart_path: Path, config: dict, base_dir: Path, mode: str, logger: logging.Logger) -> int:
    # ... (код без изменений)
    table_name = "mart_variant_04"
    connection_url = "postgresql+psycopg2://denis:denis@localhost:5432/analytics"
    engine = create_engine(connection_url)

    mart_df = pd.read_csv(mart_path, parse_dates=['Дата'])
    mart_df['Дата'] = mart_df['Дата'].dt.strftime("%Y-%m-%d")

    with engine.begin() as conn:
        if mode == "full":
            mart_df.to_sql(table_name, conn, if_exists="replace", index=False)
            final_rows = len(mart_df)
            logger.info(f"Loaded table in FULL mode (replace). Rows: {final_rows}")
        else:
            try:
                existing_df = pd.read_sql_table(table_name, conn)
            except Exception:
                existing_df = pd.DataFrame(columns=mart_df.columns)

            combined_df = pd.concat([existing_df, mart_df], ignore_index=True)
            combined_df = combined_df.drop_duplicates(subset=["Дата", "city_id"], keep="last")
            combined_df = combined_df.reset_index(drop=True)
            
            combined_df.to_sql(table_name, conn, if_exists="replace", index=False)
            final_rows = len(combined_df)
            logger.info(
                f"Loaded table in INCREMENTAL mode (append+dedup). "
                f"New batch: {len(mart_df)}, Final rows: {final_rows}"
            )

    return final_rows

# ------------------------------------------------------------
# 7. Оркестрация пайплайна
# ------------------------------------------------------------
def run_pipeline(config_path: Path, mode: str) -> dict:
    base_dir = config_path.parent.parent
    log_path = base_dir / "logs" / "pipeline.log"
    logger = setup_logging(log_path)

    config = read_yaml(config_path)
    state_path = base_dir / "data" / "state.json"
    state = read_state(state_path)

    logger.info("=" * 60)
    logger.info(f"Pipeline started | Mode: {mode} | Config: {config_path.name}")
    logger.info(f"Current watermark: {state.get('last_successful_watermark')}")

    try:
        raw_path, raw_data = extract(config, state, mode, base_dir, logger)
        if not raw_data.get("hourly"):
            logger.warning("No hourly data found in API response. Pipeline stopped.")
            return {"status": "no_data", "rows_processed": 0}

        normalized_path = transform(raw_path, config, base_dir, logger)

        mart_path = build_mart(normalized_path, config, base_dir, logger)

        final_rows = load_mart(mart_path, config, base_dir, mode, logger)

        batch_max_date = pd.read_csv(mart_path)['Дата'].max()
        state = {
            "variant_id": config["variant_id"],
            "last_successful_watermark": batch_max_date,
            "last_run_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S"),
            "last_mode": mode,
        }
        write_state(state_path, state)
        logger.info(f"Watermark updated to: {batch_max_date}")

        logger.info("Pipeline finished successfully.")
        return {"status": "ok", "final_target_rows": final_rows}

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}

# ------------------------------------------------------------
# 8. Вспомогательные функции
# ------------------------------------------------------------
def read_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# ------------------------------------------------------------
# 9. Точка входа CLI
# ------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Week 6 Idempotent ETL Pipeline")
    parser.add_argument("--config", required=True, help="Path to YAML config file")
    parser.add_argument("--mode", choices=["full", "incremental"], default="full", help="ETL execution mode")
    args = parser.parse_args()

    result = run_pipeline(Path(args.config), mode=args.mode)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result.get("status") == "ok" else 1)

