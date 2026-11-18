"""
Soconie CRM - Lê Minh Ngọc
Server WSGI Entrypoint for Local & Cloud Deployments (Vercel, Render, Railway).
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from crm.database import init_db
from crm.seed import seed_crm_data
from run_crm import create_app

# Khởi tạo schema và nạp dữ liệu mẫu ban đầu
try:
    init_db()
    seed_crm_data()
except Exception as _e:
    print(f"Khởi tạo database: {_e}")

# Expose WSGI application instance
app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
