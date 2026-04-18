import sys
import importlib.util

def main():
    print("=" * 50)
    print("SMOKE TEST - DIAGNOSTIC")
    print("=" * 50)
    
    # Информация о Python
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    
    # Проверка импортов
    packages = ["pandas", "numpy", "requests", "pyyaml", "json", 
        "sqlalchemy", "psycopg2-binary", "matplotlib", "pytest", "scikit-learn",
        "argparse", "datetime", "pathlib", "ipynbname"]
    print("\nChecking required packages:")
    
    missing = []
    for pkg in packages:
        spec = importlib.util.find_spec(pkg)
        if spec is None:
            print(f"  ✗ {pkg} - NOT FOUND")
            missing.append(pkg)
        else:
            # Попробуем импортировать и получить версию
            try:
                module = importlib.import_module(pkg)
                version = getattr(module, "__version__", "unknown")
                print(f"  ✓ {pkg} - {version}")
            except ImportError:
                print(f"  ✗ {pkg} - IMPORT ERROR")
                missing.append(pkg)
    
    print("\n" + "=" * 50)
    if missing:
        print(f"ERROR: Missing packages: {missing}")
        print("=" * 50)
        sys.exit(1)
    else:
        print("SMOKE TEST: OK")
        print("=" * 50)
        sys.exit(0)

if __name__ == "__main__":
    main()
