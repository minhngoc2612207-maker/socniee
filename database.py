"""
Database layer for Minh Ngọc Enterprise CRM.
Provides SQLite connection management, table initialization, and query utilities.
"""
import sqlite3
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional
from crm.config import DB_PATH

_local = threading.local()


def get_db() -> sqlite3.Connection:
    """Gets thread-local SQLite connection with dictionary-like row factory."""
    if not hasattr(_local, "conn") or _local.conn is None:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        _local.conn = conn
    return _local.conn


def query_db(query: str, args=(), one: bool = False):
    """Executes a query and returns list of dictionaries or single dictionary."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    if one:
        return dict(rv[0]) if rv else None
    return [dict(r) for r in rv]


def execute_db(query: str, args=()) -> int:
    """Executes a write query and returns lastrowid."""
    conn = get_db()
    cur = conn.execute(query, args)
    conn.commit()
    last_id = cur.lastrowid
    cur.close()
    return last_id


def init_db():
    """Initializes all CRM database schemas."""
    conn = get_db()
    cursor = conn.cursor()

    # 1. Departments (Phòng ban)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS departments (
        id TEXT PRIMARY KEY,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        manager_user_id TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        deleted_at TEXT
    )
    """)

    # 2. Roles (Vai trò người dùng)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS roles (
        id TEXT PRIMARY KEY,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        is_system INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        deleted_at TEXT
    )
    """)

    # 3. Permissions (Danh mục quyền)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS permissions (
        id TEXT PRIMARY KEY,
        code TEXT UNIQUE NOT NULL,
        module TEXT NOT NULL,
        action TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT
    )
    """)

    # 4. Role Permissions (Ma trận phân quyền)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS role_permissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role_id TEXT NOT NULL,
        permission_code TEXT NOT NULL,
        scope TEXT DEFAULT 'all', -- 'all' (toàn công ty), 'department' (phòng ban), 'own' (cá nhân)
        FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
    )
    """)

    # 5. Users (Người dùng / Nhân viên)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE,
        phone TEXT,
        avatar_url TEXT,
        role_id TEXT,
        department_id TEXT,
        status TEXT DEFAULT 'active', -- 'active', 'inactive'
        is_superadmin INTEGER DEFAULT 0,
        last_login_at TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        deleted_at TEXT,
        created_by TEXT,
        FOREIGN KEY (role_id) REFERENCES roles(id),
        FOREIGN KEY (department_id) REFERENCES departments(id)
    )
    """)

    # 6. Audit Logs (Nhật ký kiểm toán)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        user_name TEXT,
        action TEXT NOT NULL,       -- CREATE, UPDATE, DELETE, EXPORT, LOGIN
        module TEXT NOT NULL,       -- users, customers, deals, kanban, orders...
        record_id TEXT,
        before_data TEXT,
        after_data TEXT,
        ip_address TEXT,
        user_agent TEXT,
        created_at TEXT NOT NULL
    )
    """)

    # 7. Notifications (Thông báo)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        category TEXT DEFAULT 'system',
        link TEXT,
        is_read INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # 8. Settings (Cấu hình hệ thống)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        category TEXT DEFAULT 'general',
        description TEXT,
        updated_at TEXT NOT NULL
    )
    """)

    # 9. Customers (Khách hàng)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id TEXT PRIMARY KEY,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        tax_id TEXT,
        phone TEXT,
        email TEXT,
        address TEXT,
        group_type TEXT DEFAULT 'THUONG', -- 'VIP', 'THUONG', 'TIEM_NANG'
        status TEXT DEFAULT 'HOAT_DONG',
        assigned_user_id TEXT,
        industry TEXT,
        website TEXT,
        notes TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        deleted_at TEXT,
        created_by TEXT,
        FOREIGN KEY (assigned_user_id) REFERENCES users(id)
    )
    """)

    # 10. Leads (Khách hàng tiềm năng)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id TEXT PRIMARY KEY,
        full_name TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        company TEXT,
        source TEXT DEFAULT 'Website', -- 'Website', 'Facebook', 'Zalo', 'Gioi_thieu'
        lead_score REAL DEFAULT 50.0,
        status TEXT DEFAULT 'MOI',     -- 'MOI', 'DANG_CHAM', 'CHUYEN_DOI', 'HUY'
        assigned_user_id TEXT,
        converted_customer_id TEXT,
        notes TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        deleted_at TEXT,
        created_by TEXT,
        FOREIGN KEY (assigned_user_id) REFERENCES users(id),
        FOREIGN KEY (converted_customer_id) REFERENCES customers(id)
    )
    """)

    # 11. Pipeline Stages & Deals (Cơ hội bán hàng)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pipeline_stages (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        color TEXT DEFAULT '#4F46E5',
        order_index INTEGER DEFAULT 0,
        probability REAL DEFAULT 20.0,
        is_won INTEGER DEFAULT 0,
        is_lost INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS deals (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        expected_revenue REAL DEFAULT 0,
        stage_id TEXT NOT NULL,
        customer_id TEXT,
        assigned_user_id TEXT,
        expected_close_date TEXT,
        loss_reason TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        deleted_at TEXT,
        created_by TEXT,
        FOREIGN KEY (stage_id) REFERENCES pipeline_stages(id),
        FOREIGN KEY (customer_id) REFERENCES customers(id),
        FOREIGN KEY (assigned_user_id) REFERENCES users(id)
    )
    """)

    # 12. Kanban Boards, Columns, Cards (Bảng Kanban làm việc)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kanban_boards (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        department_id TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        deleted_at TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kanban_columns (
        id TEXT PRIMARY KEY,
        board_id TEXT NOT NULL,
        name TEXT NOT NULL,
        color TEXT DEFAULT '#64748B',
        order_index INTEGER DEFAULT 0,
        wip_limit INTEGER DEFAULT 0,
        FOREIGN KEY (board_id) REFERENCES kanban_boards(id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kanban_cards (
        id TEXT PRIMARY KEY,
        board_id TEXT NOT NULL,
        column_id TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        priority TEXT DEFAULT 'TRUNG_BINH', -- 'KHAN_CAP', 'CAO', 'TRUNG_BINH', 'THAP'
        due_date TEXT,
        order_index INTEGER DEFAULT 0,
        assigned_user_id TEXT,
        linked_type TEXT,                  -- 'CUSTOMER', 'DEAL', 'ORDER'
        linked_id TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        deleted_at TEXT,
        created_by TEXT,
        FOREIGN KEY (board_id) REFERENCES kanban_boards(id) ON DELETE CASCADE,
        FOREIGN KEY (column_id) REFERENCES kanban_columns(id) ON DELETE CASCADE,
        FOREIGN KEY (assigned_user_id) REFERENCES users(id)
    )
    """)

    # 20. OTP Verifications (Mã xác thực SMS)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS otp_verifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT NOT NULL,
        code_hash TEXT NOT NULL,
        purpose TEXT NOT NULL,
        ip_address TEXT,
        attempts INTEGER DEFAULT 0,
        max_attempts INTEGER DEFAULT 5,
        is_used INTEGER DEFAULT 0,
        expires_at TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_otp_phone ON otp_verifications(phone)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_otp_created ON otp_verifications(created_at)")

    # 21. OTP Locks (Khóa tạm thời do nhập sai quá nhiều lần)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS otp_locks (
        phone TEXT PRIMARY KEY,
        locked_until TEXT NOT NULL,
        reason TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    # 22. CAPTCHA Challenges (Thử thách kéo ghép hình server-side)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS captcha_challenges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        challenge_id TEXT UNIQUE NOT NULL,
        correct_x INTEGER NOT NULL,
        correct_y INTEGER NOT NULL,
        action TEXT NOT NULL,
        ip_address TEXT,
        fallback_answer TEXT,
        expires_at TEXT NOT NULL,
        is_used INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_captcha_chl ON captcha_challenges(challenge_id)")

    # 23. CAPTCHA Single-Use Tokens (Cấp sau khi kéo ghép đúng)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS captcha_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token TEXT UNIQUE NOT NULL,
        action TEXT NOT NULL,
        ip_address TEXT,
        expires_at TEXT NOT NULL,
        is_used INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_captcha_tok ON captcha_tokens(token)")

    # 24. CAPTCHA Attempt / Lock Tracker (Khóa IP khi kéo sai > 5 lần)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS captcha_attempts (
        ip_address TEXT PRIMARY KEY,
        failed_count INTEGER DEFAULT 0,
        locked_until TEXT,
        updated_at TEXT NOT NULL
    )
    """)

    # 25. User Recovery Codes (8 mã khôi phục 1 lần dạng XXXX-XXXX, lưu dạng băm)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_recovery_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        code_hash TEXT NOT NULL,
        is_used INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        used_at TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_recov_user ON user_recovery_codes(user_id)")

    # 26. Password Reset Tokens (Liên kết đặt lại mật khẩu qua email, hạn 30 phút)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS password_reset_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        token_hash TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        is_used INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reset_token ON password_reset_tokens(token_hash)")

    # 27. Analysis Reports (Báo cáo lưu trữ của Không gian phân tích Soconie CRM)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analysis_reports (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        title TEXT NOT NULL,
        summary TEXT,
        dataset_name TEXT,
        report_data TEXT NOT NULL,
        share_token TEXT UNIQUE,
        is_public INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_user ON analysis_reports(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_share ON analysis_reports(share_token)")

    # 28. Contact Inquiries (Khách hàng liên hệ từ trang chủ Landing)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contact_inquiries (
        id TEXT PRIMARY KEY,
        full_name TEXT NOT NULL,
        contact TEXT NOT NULL,
        need TEXT,
        message TEXT,
        ip_address TEXT,
        status TEXT DEFAULT 'new',
        created_at TEXT NOT NULL
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inquiry_created ON contact_inquiries(created_at)")

    # Migrations for users table
    migrations = [
        "ALTER TABLE users ADD COLUMN phone_verified INTEGER DEFAULT 0",
        "ALTER TABLE users ADD COLUMN email_verified INTEGER DEFAULT 0",
        "ALTER TABLE users ADD COLUMN email_verification_token TEXT",
        "ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER DEFAULT 0",
        "ALTER TABLE users ADD COLUMN locked_until TEXT",
        "ALTER TABLE users ADD COLUMN last_device_info TEXT",
    ]
    for m in migrations:
        try:
            cursor.execute(m)
        except sqlite3.OperationalError:
            pass

    conn.commit()



# Auto-initialize on module load
init_db()
