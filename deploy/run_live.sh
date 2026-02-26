#!/usr/bin/env bash
set -e

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
python -m upstox_ready_algo.cli --mode live --data-source upstox --iterations 1000000
