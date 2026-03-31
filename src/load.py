from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, inspect

def main():
    mart_path = Path("mart_daily_2026-03-19_17-13-07.csv")
    table_name = "mart_variant_05"

    connection_url = "postgresql+psycopg2://denis:denis@localhost:5432/analytics"
    engine = create_engine(connection_url)

    print(f"[INFO] reading file: {mart_path.resolve()}")
    df = pd.read_csv(mart_path)

    print(f"[INFO] rows={len(df)}, cols={len(df.columns)}")
    print(f"[INFO] loading to table: {table_name}")

    with engine.begin() as conn:
        df.to_sql(table_name, conn, if_exists="replace", index=False)

    print("[OK] load finished successfully")


    
    # Проверить существование таблицы
    inspector = inspect(engine)
    if 'mart_variant_05' in inspector.get_table_names():
        print("Таблица существует!")
        
        # Показать структуру
        columns = inspector.get_columns('mart_variant_05')
        print("\nСтруктура таблицы:")
        for col in columns:
            print(f"  {col['name']}: {col['type']}")
        
        # Подсчет строк
        df_count = pd.read_sql("SELECT COUNT(*) as count FROM mart_variant_05", engine)
        print(f"\nВсего строк: {df_count['count'][0]}")
        
        # Показать первые 5 строк
        df_sample = pd.read_sql("SELECT * FROM mart_variant_05 LIMIT 5", engine)
        print("\nПервые 5 строк:")
        print(df_sample)
    else:
        print("Таблица не найдена")

if __name__ == "__main__":
    main()
