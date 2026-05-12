import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.append('/opt/project/src')

VARIANT = "04"
PROJECT_DIR = Path("/opt/project")
CONFIG_PATH = PROJECT_DIR / "configs" / f"variant_{VARIANT}.yml"
DATA_DIR = PROJECT_DIR / "data"

default_args = {
    'owner': 'student',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    dag_id=f"etl_variant_{VARIANT}",
    default_args=default_args,
    description='ETL Pipeline: Extract -> Transform -> Load -> DQ',
    schedule_interval='*/5 * * * *',
    start_date=pendulum.datetime(2026, 3, 1, tz="UTC"),
    catchup=False,
    tags=['semester2', 'etl', f'variant_{VARIANT}'],
    doc_md=__doc__,
) as dag:

    extract_task = BashOperator(
        task_id='extract',
        bash_command=(
            f"cd /opt/project && "
            f"python -c \""
            f"import sys; sys.path.append('/opt/project/src'); "
            f"from extract import ExtractData; "
            f"from pathlib import Path; "
            f"import json; "
            f"state_file = Path('/opt/project/data/state/state.json'); "
            f"state = json.loads(state_file.read_text()) if state_file.exists() else {{}}; "
            f"result = ExtractData(config_path=Path('/opt/project/configs/variant_{VARIANT}.yml'), base_dir=Path('/opt/project'), mode='full', state=state); "
            f"print(f'Extract completed: {{result}}')\""
        ),
        dag=dag,
    )

    transform_task = BashOperator(
        task_id='transform',
        bash_command=(
            f"cd /opt/project && "
            f"python -c \""
            f"import sys; sys.path.append('/opt/project/src'); "
            f"from transform import TransformToCSV; "
            f"from pathlib import Path; "
            f"result = TransformToCSV(base_dir=Path('/opt/project'), raw_path=Path('/opt/project/data/raw/raw.json'), config_path=Path('/opt/project/configs/variant_{VARIANT}.yml'), mode='full'); "
            f"print(f'Transform completed: {{result}}')\""
        ),
        dag=dag,
    )

    mart_task = BashOperator(
        task_id='build_mart',
        bash_command=(
            f"cd /opt/project && "
            f"python -c \""
            f"import sys; sys.path.append('/opt/project/src'); "
            f"from mart import ToMart; "
            f"from pathlib import Path; "
            f"result = ToMart(base_dir=Path('/opt/project'), normalized_path=Path('/opt/project/data/normalized/normalized.csv')); "
            f"import pandas as pd; "
            f"df = pd.read_csv(result); "
            f"print(f'Mart completed: {{len(df)}} rows')\""
        ),
        dag=dag,
    )

    load_task = BashOperator(
        task_id='load_to_sql',
        bash_command=(
            f"cd /opt/project && "
            f"python -c \""
            f"import sys; sys.path.append('/opt/project/src'); "
            f"from load import LoadToSQL; "
            f"from pathlib import Path; "
            f"row_count = LoadToSQL(base_dir=Path('/opt/project'), mart_path=Path('/opt/project/data/mart/mart_daily.csv')); "
            f"print(f'Load completed: {{row_count}} rows')\""
        ),
        dag=dag,
    )

    dq_task = BashOperator(
        task_id='data_quality',
        bash_command=(
            f"cd /opt/project && "
            f"python -c \""
            f"import sys; sys.path.append('/opt/project/src'); "
            f"from dq import run_dq; "
            f"from pathlib import Path; "
            f"import yaml; import json; "
            f"config = yaml.safe_load(Path('/opt/project/configs/variant_{VARIANT}.yml').read_text()); "
            f"results = run_dq(normalized_path=Path('/opt/project/data/normalized/normalized.csv'), config=config); "
            f"dq_path = Path('/opt/project/docs/dq_report_{datetime.now()}.json'); "
            f"dq_path.parent.mkdir(parents=True, exist_ok=True); "
            f"dq_path.write_text(json.dumps(results, indent=2, default=str)); "
            f"pass_count = sum(1 for r in results if r['status'] == 'PASS'); "
            f"fail_count = sum(1 for r in results if r['status'] == 'FAIL'); "
            f"warn_count = sum(1 for r in results if r['status'] == 'WARNING'); "
            f"print(f'DQ completed: PASS={{pass_count}}, WARNING={{warn_count}}, FAIL={{fail_count}}')\""
        ),
        dag=dag,
    )

    extract_task >> transform_task >> mart_task >> load_task >> dq_task
