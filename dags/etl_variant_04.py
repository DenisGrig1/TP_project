import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator

VARIANT = "04"
PROJECT_DIR = "/opt/project"

default_args = {
    "owner": "student",
    "retries": 1,
    "retry_delay": 30,
}

with DAG(
    dag_id=f"etl_variant_{VARIANT}",
    description=f"ETL pipeline (variant {VARIANT})",
    start_date=pendulum.datetime(2026, 3, 1, tz="UTC"),
    schedule="*/5 * * * *",
    catchup=False,
    default_args=default_args,
    tags=["semester2", "etl", f"variant_{VARIANT}"],
) as dag:
    extract = BashOperator(
        task_id = "extract",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            f"python src/extract.py "
            f"--mode full"
        ),
    )
    
    transform = BashOperator(
        task_id = "transform",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            f"python src/transform.py "
            f"--mode full"
        ),
    )

    dq = BashOperator(
        task_id = "dq",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            f"python src/dq.py"
        ),
    )

    mart = BashOperator(
        task_id = "mart",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            f"python src/mart.py"
        ),
    )
    
    load = BashOperator(
        task_id = "load",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            f"python src/load.py"
        ),
    )

    extract >> transform >> dq >> mart >> load
