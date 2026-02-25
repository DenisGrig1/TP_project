py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -c "import sem2_de; print('ok')"
python -m sem2_de.cli --help
python -m sem2_de.cli extract --config
