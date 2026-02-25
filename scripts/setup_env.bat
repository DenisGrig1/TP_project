where python
pause
py -m venv .venv
pause
.\.venv\Scripts\Activate.ps1
pause
pip install -r requirements.txt
pause
python -c "import sem2_de; print('ok')"
pause
conda run -n broken_env.py
pause
