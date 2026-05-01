import subprocess
import sys
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine

def RunDocker(base_dir: Path):
    result = subprocess.run([base_dir / "scripts" / "docker_run.bat"], shell=True)
    if result.returncode == 0:
        return 1
    else:
        return 0

def CheckSQL(table_name, engine):
    query = f"SELECT COUNT(*) FROM {table_name}"
    df_count = pd.read_sql_query(query, engine)
    row_count = df_count.iloc[0, 0]
    return row_count


def LoadToSQL(base_dir: Path, mart_path: Path):
    #result = RunDocker(base_dir)
    #if result == 0:
    #    print ("STOP LOADING TO SQL")
    #    return 0

    df = pd.read_csv(mart_path)
    table_name = "mart_sql"
    connection_url = "postgresql://denis:denis@localhost:5433/test_sql"
    engine = create_engine(connection_url)

    with engine.begin() as conn:
        df.to_sql(table_name, conn, if_exists="replace", index=False)
    row_count = CheckSQL(table_name, engine)

    return row_count
