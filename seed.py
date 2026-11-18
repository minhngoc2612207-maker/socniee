"""
Seed data script for Minh Ngọc Enterprise CRM.
Populates standard departments, roles, permissions, users, customers, pipeline, and kanban.
"""
from datetime import datetime
from crm.database import execute_db, query_db
from crm.auth import hash_password


def seed_crm_data():
    """Seeds initial master data if tables are empty."""
    # Check if already seeded
    existing_user = query_db("SELECT id FROM users LIMIT 1", one=True)
    if existing_user:
        return

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Departments
    depts = [
        ("dept-1", "BGD", "Ban Giám Đốc", "Điều hành & Ra quyết định chiến lược"),
        ("dept-2", "KD", "Phòng Kinh Doanh", "Tìm kiếm khách hàng, tư vấn & chốt doanh số"),
        ("dept-3", "MKT", "Phòng Marketing", "Quảng bá thương hiệu & thu hút lead"),
        ("dept-4", "CSKH", "Phòng Chăm Sóc Khách Hàng", "Hỗ trợ kỹ thuật, xử lý ticket & bảo hành"),
        ("dept-5", "KT", "Phòng Kế Toán - Tài Chính", "Quản lý dòng tiền, công nợ & xuất hóa đơn")
    ]
    for d_id, code, name, desc in depts:
        execute_db("""
            INSERT OR IGNORE INTO departments (id, code, name, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (d_id, code, name, desc, now, now))

    # 2. Roles
    roles = [
        ("role-admin", "ADMIN", "Quản trị viên Cấp cao", "Toàn quyền quản trị hệ thống", 1),
        ("role-manager", "MANAGER", "Trưởng phòng Kinh doanh", "Quản lý phòng ban, phân bổ lead & duyệt đơn", 1),
        ("role-staff", "SALES", "Chuyên viên Bán hàng", "Chăm sóc lead, quản lý khách hàng & cơ hội", 1),
        ("role-accountant", "ACCOUNTANT", "Kế toán viên", "Theo dõi công nợ, hóa đơn & thu chi", 1),
        ("role-support", "SUPPORT", "Chuyên viên Hỗ trợ (CSKH)", "Xử lý ticket khiếu nại & khảo sát hài lòng", 1)
    ]
    for r_id, code, name, desc, is_sys in roles:
        execute_db("""
            INSERT OR IGNORE INTO roles (id, code, name, description, is_system, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (r_id, code, name, desc, is_sys, now, now))

    # 3. Permissions Modules
    modules = ["customers", "leads", "deals", "quotes", "orders", "kanban", "reports", "users", "settings"]
    actions = [("view", "Xem"), ("create", "Tạo mới"), ("edit", "Chỉnh sửa"), ("delete", "Xóa"), ("export", "Xuất Excel")]
    for mod in modules:
        for act, act_name in actions:
            p_code = f"{mod}_{act}"
            execute_db("""
                INSERT OR IGNORE INTO permissions (id, code, module, action, name, description)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (f"perm-{p_code}", p_code, mod, act, f"{act_name} {mod}", f"Quyền {act_name.lower()} trong module {mod}"))

    # Grant permissions to ADMIN (all), MANAGER (all dept), SALES (own)
    all_perms = query_db("SELECT code FROM permissions")
    for p in all_perms:
        # Admin gets everything with 'all' scope
        execute_db("INSERT INTO role_permissions (role_id, permission_code, scope) VALUES (?, ?, ?)", ("role-admin", p["code"], "all"))
        # Manager gets sales & kanban with 'department'
        if any(p["code"].startswith(m) for m in ["customers", "leads", "deals", "quotes", "orders", "kanban", "reports"]):
            execute_db("INSERT INTO role_permissions (role_id, permission_code, scope) VALUES (?, ?, ?)", ("role-manager", p["code"], "department"))
        # Staff gets sales & kanban with 'own'
        if any(p["code"].startswith(m) for m in ["customers", "leads", "deals", "quotes", "orders", "kanban"]) and not p["code"].endswith("_delete"):
            execute_db("INSERT INTO role_permissions (role_id, permission_code, scope) VALUES (?, ?, ?)", ("role-staff", p["code"], "own"))

    # 4. Users (Lê Minh Ngọc is Superadmin)
    users = [
        ("u-admin", "admin", hash_password("admin123"), "Lê Minh Ngọc", "minhngoc2612207@gmail.com", "+84363651407", "role-admin", "dept-1", 1),
        ("u-nam", "sales_lead", hash_password("123456"), "Hoàng Văn Nam", "nam.hoang@enterprise.vn", "+84912345678", "role-manager", "dept-2", 0),
        ("u-ha", "sales_staff", hash_password("123456"), "Trần Thu Hà", "ha.tran@enterprise.vn", "+84988234567", "role-staff", "dept-2", 0),
        ("u-oanh", "accountant", hash_password("123456"), "Đặng Kim Oanh", "oanh.dang@enterprise.vn", "+84934567890", "role-accountant", "dept-5", 0),
        ("u-minh", "support", hash_password("123456"), "Lê Hoàng Minh", "minh.le@enterprise.vn", "+84977889900", "role-support", "dept-4", 0)
    ]
    for u_id, uname, phash, fname, mail, phone, rid, did, is_admin in users:
        execute_db("""
            INSERT OR REPLACE INTO users (id, username, password_hash, full_name, email, phone, phone_verified, role_id, department_id, status, is_superadmin, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, 'active', ?, ?, ?)
        """, (u_id, uname, phash, fname, mail, phone, rid, did, is_admin, now, now))

    # 5. Company Settings (Unified Contact Info)
    settings = [
        ("company_name", "Soconie CRM - Lê Minh Ngọc", "company", "Tên doanh nghiệp hiển thị"),
        ("tax_id", "0109988776", "company", "Mã số thuế doanh nghiệp"),
        ("company_phone", "0363651407", "company", "Hotline tổng đài"),
        ("company_email", "minhngoc2612207@gmail.com", "company", "Email đại diện"),
        ("company_address", "Đang cập nhật", "company", "Địa chỉ trụ sở chính"),
        ("brand_color", "#4F46E5", "theme", "Mã màu chủ đạo"),
        ("date_format", "DD/MM/YYYY", "general", "Định dạng ngày hiển thị")
    ]
    for k, v, cat, desc in settings:
        execute_db("""
            INSERT OR IGNORE INTO settings (key, value, category, description, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (k, v, cat, desc, now))

    # 6. Pipeline Stages (Giai đoạn cơ hội bán hàng)
    stages = [
        ("stage-1", "1. Tiếp cận / Mới", "#6366F1", 1, 15.0, 0, 0),
        ("stage-2", "2. Đang tư vấn & Khảo sát", "#3B82F6", 2, 35.0, 0, 0),
        ("stage-3", "3. Gửi báo giá & Đề xuất", "#F59E0B", 3, 60.0, 0, 0),
        ("stage-4", "4. Đàm phán hợp đồng", "#EC4899", 4, 80.0, 0, 0),
        ("stage-5", "5. Chốt thành công 🎉", "#10B981", 5, 100.0, 1, 0),
        ("stage-6", "6. Thất bại", "#EF4444", 6, 0.0, 0, 1)
    ]
    for s_id, s_name, s_color, s_order, s_prob, s_won, s_lost in stages:
        execute_db("""
            INSERT OR IGNORE INTO pipeline_stages (id, name, color, order_index, probability, is_won, is_lost)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (s_id, s_name, s_color, s_order, s_prob, s_won, s_lost))

    # 7. Sample Customers (Khách hàng mẫu)
    customers = [
        ("cust-1", "KH-2024-001", "Công ty TNHH Ánh Dương Tech", "0102345678", "0903123456", "contact@anhduong.vn", "Tầng 5, Keangnam Landmark 72, Hà Nội", "VIP", "u-ha", "Công nghệ thông tin"),
        ("cust-2", "KH-2024-002", "Đại lý Thiết bị Gia dụng Hoàng Kim", "0301987654", "0988234567", "kinhdoanh@hoangkim.com", "88 Nguyễn Huệ, Quận 1, TP. Hồ Chí Minh", "VIP", "u-ha", "Bán lẻ & Gia dụng"),
        ("cust-3", "KH-2024-003", "Doanh nghiệp Tư nhân Sao Mai Logistics", "0103456789", "0912345678", "info@saomai.vn", "Cảng Hải Phòng, TP. Hải Phòng", "THUONG", "u-nam", "Vận tải Logistics"),
        ("cust-4", "KH-2024-004", "Công ty CP Xây dựng & Kiến trúc Vạn Phát", "0401122334", "0945667788", "vanphat@build.vn", "25 Nguyễn Văn Linh, Đà Nẵng", "TIEM_NANG", "u-ha", "Xây dựng"),
        ("cust-5", "KH-2024-005", "Chuỗi Cafe & Trà Sữa Phúc An House", "0305566778", "0933112233", "phucan@fnb.vn", "154 Cầu Giấy, Hà Nội", "VIP", "u-nam", "F&B")
    ]
    for c_id, code, c_name, tax, phone, email, addr, gtype, uid, ind in customers:
        execute_db("""
            INSERT OR IGNORE INTO customers (id, code, name, tax_id, phone, email, address, group_type, status, assigned_user_id, industry, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'HOAT_DONG', ?, ?, ?, ?)
        """, (c_id, code, c_name, tax, phone, email, addr, gtype, uid, ind, now, now))

    # 8. Sample Leads
    leads = [
        ("lead-1", "Nguyễn Tiến Đạt", "0918 223 344", "tiendat@vinafood.vn", "VinaFood Corp", "Facebook", 85.0, "DANG_CHAM", "u-ha"),
        ("lead-2", "Vũ Mai Phương", "0976 554 433", "phuong.vu@beauty.vn", "Thẩm mỹ viện Ngọc Mai", "Website", 92.0, "MOI", "u-ha"),
        ("lead-3", "Bùi Quốc Cường", "0942 998 877", "cuong.bui@fasttrans.com", "FastTrans Express", "Zalo", 65.0, "DANG_CHAM", "u-nam")
    ]
    for l_id, lname, lphone, lemail, lcomp, lsrc, lscore, lstatus, luid in leads:
        execute_db("""
            INSERT OR IGNORE INTO leads (id, full_name, phone, email, company, source, lead_score, status, assigned_user_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (l_id, lname, lphone, lemail, lcomp, lsrc, lscore, lstatus, luid, now, now))

    # 9. Sample Deals (Cơ hội kinh doanh)
    deals = [
        ("deal-1", "Hợp đồng Cung cấp Thiết bị Smart Office Ánh Dương", 185000000, "stage-3", "cust-1", "u-ha", "2026-12-15"),
        ("deal-2", "Đơn hàng Đại lý Gia dụng Lô hàng Quý 4 - Hoàng Kim", 320000000, "stage-4", "cust-2", "u-ha", "2026-11-30"),
        ("deal-3", "Gói Nâng cấp Hệ thống Kho bãi Sao Mai", 95000000, "stage-2", "cust-3", "u-nam", "2026-12-25"),
        ("deal-4", "Dự án Vật tư Chuỗi Cửa hàng Phúc An", 240000000, "stage-5", "cust-5", "u-nam", "2026-11-20")
    ]
    for d_id, title, rev, stg, cid, uid, cdate in deals:
        execute_db("""
            INSERT OR IGNORE INTO deals (id, title, expected_revenue, stage_id, customer_id, assigned_user_id, expected_close_date, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (d_id, title, rev, stg, cid, uid, cdate, now, now))

    # 10. Sample Kanban Boards & Tasks
    execute_db("""
        INSERT OR IGNORE INTO kanban_boards (id, name, description, department_id, created_at, updated_at)
        VALUES ('kb-1', 'Bảng Điều Phối Dự Án & Bán Hàng Q4/2026', 'Theo dõi toàn bộ công việc trọng điểm của đội ngũ', 'dept-2', ?, ?)
    """, (now, now))

    cols = [
        ("col-1", "kb-1", "Cần làm (Backlog)", "#94A3B8", 1, 10),
        ("col-2", "kb-1", "Đang thực hiện", "#3B82F6", 2, 5),
        ("col-3", "kb-1", "Chờ phê duyệt", "#F59E0B", 3, 3),
        ("col-4", "kb-1", "Hoàn thành 🎉", "#10B981", 4, 0)
    ]
    for c_id, bid, cname, col_color, o_idx, w_lim in cols:
        execute_db("""
            INSERT OR IGNORE INTO kanban_columns (id, board_id, name, color, order_index, wip_limit)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (c_id, bid, cname, col_color, o_idx, w_lim))

    cards = [
        ("card-1", "kb-1", "col-2", "Gặp khách hàng Ánh Dương demo tính năng", "Chuẩn bị slide giới thiệu và bảng báo giá chi tiết", "KHAN_CAP", "2026-11-20", 1, "u-ha", "CUSTOMER", "cust-1"),
        ("card-2", "kb-1", "col-3", "Duyệt hợp đồng phân phối Đại lý Hoàng Kim", "Trình Giám đốc Minh Ngọc ký duyệt phụ lục chiết khấu", "CAO", "2026-11-19", 1, "u-nam", "DEAL", "deal-2"),
        ("card-3", "kb-1", "col-1", "Gửi email chúc mừng sinh nhật khách hàng VIP", "Thiết lập kịch bản gửi voucher tự động qua Zalo OA", "TRUNG_BINH", "2026-11-28", 1, "u-ha", None, None),
        ("card-4", "kb-1", "col-4", "Đối soát công nợ kỳ 1 tháng 11", "Đã thu đủ 100% công nợ theo hóa đơn đợt trước", "TRUNG_BINH", "2026-11-15", 1, "u-oanh", "CUSTOMER", "cust-2")
    ]
    for card_id, bid, col_id, title, desc, pri, ddate, o_idx, uid, ltype, lid in cards:
        execute_db("""
            INSERT OR IGNORE INTO kanban_cards (id, board_id, column_id, title, description, priority, due_date, order_index, assigned_user_id, linked_type, linked_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (card_id, bid, col_id, title, desc, pri, ddate, o_idx, uid, ltype, lid, now, now))

    # 11. Initial Notifications
    notifs = [
        ("notif-1", "u-admin", "Chào mừng Giám đốc Minh Ngọc!", "Hệ thống CRM Doanh Nghiệp đã sẵn sàng hoạt động với 100% dữ liệu mẫu chuẩn.", "system", "/tong-quan"),
        ("notif-2", "u-admin", "Cơ hội bán hàng mới được tạo", "Nhân viên Trần Thu Hà vừa mở cơ hội trị giá 185,000,000 đ cho Ánh Dương Tech.", "deal", "/co-hoi"),
        ("notif-3", "u-ha", "Nhắc hạn công việc khẩn", "Công việc 'Gặp khách hàng Ánh Dương demo' đến hạn vào ngày mai.", "task", "/kanban")
    ]
    for nid, uid, title, cnt, cat, link in notifs:
        execute_db("""
            INSERT OR IGNORE INTO notifications (id, user_id, title, content, category, link, is_read, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 0, ?)
        """, (nid, uid, title, cnt, cat, link, now))
