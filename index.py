"""
Vercel Serverless Function Entrypoint for Soconie CRM - Lê Minh Ngọc
Exposes WSGI app for @vercel/python runtime.
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ["VERCEL"] = "1"

from crm.database import init_db
from crm.seed import seed_crm_data
from run_crm import create_app

try:
    init_db()
    seed_crm_data()
except Exception as _e:
    print(f"Serverless DB init: {_e}")

app = create_app()
handler = app

if __name__ == "__main__":
    app.run()
