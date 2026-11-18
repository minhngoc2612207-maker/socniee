"""
Central site configuration for Soconie CRM.
Single source of truth for branding, contact information, and system parameters.
"""
import os

# =====================================================================
# THÔNG TIN THƯƠNG HIỆU & LIÊN HỆ CHÍNH THỨC
# =====================================================================
SYSTEM_NAME = "Soconie CRM"
OWNER_NAME = "Lê Minh Ngọc"
OWNER_SUBTITLE = "Quản trị bán hàng & CRM"

# Hotline & Điện thoại
HOTLINE_RAW = "0363651407"
HOTLINE_DISPLAY = "0363 651 407"
HOTLINE_LINK = "tel:0363651407"
OWNER_PHONE = HOTLINE_RAW

# Email liên hệ
EMAIL = "minhngoc2612207@gmail.com"
EMAIL_LINK = "mailto:minhngoc2612207@gmail.com"

# Địa chỉ & Giờ làm việc
ADDRESS = "Đang cập nhật"
WORKING_HOURS = "Thứ 2 - Thứ 6, 08:30 - 17:30"

# Bản quyền & Avatar
COPYRIGHT = "© 2026 Soconie CRM · Lê Minh Ngọc. Bảo lưu mọi quyền."
AVATAR_PLACEHOLDER = "N"

# Cờ cấu hình hiển thị phân hệ CRM cũ (Sidebar, Dashboard KPI...)
# Mặc định tắt (False) để tuân thủ luồng 3 màn chuẩn:
# Màn 1: Chào mừng (/) -> Màn 2: Landing (/trang-chu) -> Màn 3: Không gian phân tích (/phan-tich/buoc-1..4)
ENABLE_LEGACY_CRM = os.environ.get("ENABLE_LEGACY_CRM", "0") == "1"

# =====================================================================
# CẤU HÌNH HỆ THỐNG & ĐƯỜNG DẪN
# =====================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# Hỗ trợ môi trường Serverless (Vercel, AWS Lambda) - chỉ /tmp có quyền ghi
if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    DATA_DIR = "/tmp"
    DB_PATH = "/tmp/crm.db"
else:
    DATA_DIR = os.path.join(BASE_DIR, "data")
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
    except Exception:
        pass
    DB_PATH = os.path.join(DATA_DIR, "crm.db")

SECRET_KEY = os.environ.get("CRM_SECRET_KEY", "soconie-crm-secret-key-2026-production-secure-salt")

# Brand Visual Tokens
BRAND_COLOR = "#4F46E5"
BRAND_ACCENT = "#7C5CFF"

# =====================================================================
# CẤU HÌNH XÁC THỰC: BỎ OTP SMS, DÙNG CAPTCHA KÉO GHÉP HÌNH
# =====================================================================
AUTH_OTP_ENABLED = os.environ.get("AUTH_OTP_ENABLED", "false").lower() in ("true", "1", "yes")

# CAPTCHA Configuration
CAPTCHA_PROVIDER = os.environ.get("CAPTCHA_PROVIDER", "slider").lower()  # slider, turnstile, hcaptcha
CAPTCHA_ASSETS_DIR = os.path.join(BASE_DIR, "captcha_assets")
CAPTCHA_TOLERANCE_PX = int(os.environ.get("CAPTCHA_TOLERANCE_PX", 4))  # 3-5px tolerance
CAPTCHA_TTL_SECONDS = int(os.environ.get("CAPTCHA_TTL_SECONDS", 120))  # 2 minutes
CAPTCHA_MAX_FAILS = int(os.environ.get("CAPTCHA_MAX_FAILS", 5))
CAPTCHA_LOCK_MINUTES = int(os.environ.get("CAPTCHA_LOCK_MINUTES", 10))

# Email Service Configuration (Console, SMTP, Resend)
EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND", "console").lower()
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
EMAIL_SENDER = os.environ.get("EMAIL_SENDER", "Soconie CRM <no-reply@soconie.com>")

# OTP & SMS Security Configurations (TẮT MẶC ĐỊNH, GIỮ ADAPTER ĐỂ BẬT LẠI KHI CẦN)
OTP_LENGTH = int(os.environ.get("OTP_LENGTH", 6))
OTP_TTL_SECONDS = int(os.environ.get("OTP_TTL_SECONDS", 300))  # 5 minutes
OTP_RESEND_COOLDOWN_SECONDS = int(os.environ.get("OTP_RESEND_COOLDOWN_SECONDS", 60))  # 60s
OTP_MAX_ATTEMPTS = int(os.environ.get("OTP_MAX_ATTEMPTS", 5))
OTP_LOCK_MINUTES = int(os.environ.get("OTP_LOCK_MINUTES", 15))
OTP_DAILY_LIMIT_PER_PHONE = int(os.environ.get("OTP_DAILY_LIMIT_PER_PHONE", 5))
OTP_DAILY_LIMIT_PER_IP = int(os.environ.get("OTP_DAILY_LIMIT_PER_IP", 20))
OTP_PEPPER = os.environ.get("OTP_PEPPER", "soconie-crm-secure-pepper-salt-2026-hmac-sha256")
OTP_DEV_ECHO = os.environ.get("OTP_DEV_ECHO", "false").lower() in ("true", "1", "yes")

# SMS Provider Configuration
SMS_PROVIDER = os.environ.get("SMS_PROVIDER", "esms").lower()
SMS_API_KEY = os.environ.get("SMS_API_KEY", "")
SMS_SECRET_KEY = os.environ.get("SMS_SECRET_KEY", "")
SMS_BRANDNAME = os.environ.get("SMS_BRANDNAME", "Soconie")

# =====================================================================
# BẢNG GIÁ DỊCH VỤ SOCONIE CRM (Chính thức, không bịa số liệu thật)
# =====================================================================
PRICING_PACKAGES = [
    {
        "id": "starter",
        "name": "Cơ bản",
        "badge": "Khởi đầu",
        "price_display": "Liên hệ báo giá",
        "period": "/tháng",
        "description": "Phù hợp cho cá nhân kinh doanh hoặc đội ngũ bán hàng từ 1 - 3 người.",
        "features": [
            "Quản lý tối đa 500 khách hàng",
            "Pipeline cơ hội bán hàng cơ bản",
            "Biểu mẫu thu thập Lead website",
            "Bảo mật CAPTCHA kéo ghép hình",
            "Hỗ trợ qua Email & Ticket"
        ],
        "highlight": False,
        "cta_text": "Chọn gói Cơ bản"
    },
    {
        "id": "professional",
        "name": "Chuyên nghiệp",
        "badge": "Phổ biến nhất",
        "price_display": "Liên hệ báo giá",
        "period": "/tháng",
        "description": "Dành cho doanh nghiệp vừa và nhỏ cần tự động hóa quy trình chốt đơn.",
        "features": [
            "Không giới hạn khách hàng & Lead",
            "Pipeline kéo thả đa kênh nâng cao",
            "Không gian phân tích dữ liệu AI",
            "Tự động xuất báo giá & đơn hàng",
            "Báo cáo KPI & Phân tích 80/20 Pareto",
            "Hỗ trợ Hotline ưu tiên 24/7"
        ],
        "highlight": True,
        "cta_text": "Chọn gói Chuyên nghiệp"
    },
    {
        "id": "enterprise",
        "name": "Doanh nghiệp",
        "badge": "Tùy biến cao cấp",
        "price_display": "Liên hệ báo giá",
        "period": "/thỏa thuận",
        "description": "Giải pháp tùy biến toàn diện theo mô hình kinh doanh đặc thù.",
        "features": [
            "Toàn bộ tính năng Chuyên nghiệp",
            "Không gian phân tích AI riêng biệt",
            "Tích hợp API & Webhook tùy biến",
            "Kết nối Google Sheets & ERP",
            "Phân quyền đa chi nhánh & phòng ban",
            "Kỹ sư cố vấn triển khai tận nơi"
        ],
        "highlight": False,
        "cta_text": "Liên hệ Doanh nghiệp"
    }
]

# =====================================================================
# CẤU HÌNH KHÔNG GIAN PHÂN TÍCH & TRỢ LÝ AI (Máy chủ bảo mật)
# =====================================================================
AI_PROVIDER = os.environ.get("CRM_AI_PROVIDER", "internal").lower()  # 'internal' or 'gemini'
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
AI_MAX_TOKENS = int(os.environ.get("CRM_AI_MAX_TOKENS", 2048))
ANALYSIS_MAX_FILE_SIZE_MB = int(os.environ.get("ANALYSIS_MAX_FILE_SIZE_MB", 20))
ANALYSIS_SAMPLE_DATASET_NAME = "CRM_Kinh_Doanh_2026.csv"
