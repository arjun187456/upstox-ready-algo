python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
python -m upstox_ready_algo.cli --mode live --data-source upstox --iterations 1000000
