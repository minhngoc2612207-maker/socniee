"""
Email Service for Soconie CRM.
Supports SMTP (e.g. Gmail App Password), Resend API, and local Console mode.
"""
import os
import smtplib
import logging
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from crm.site_config import (
    EMAIL_BACKEND,
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASS,
    RESEND_API_KEY,
    EMAIL_SENDER,
    SYSTEM_NAME,
    OWNER_NAME,
    HOTLINE_DISPLAY
)

logger = logging.getLogger("soconie.email")


def send_email(to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
    """Sends email via configured backend (console, smtp, resend)."""
    if not to_email:
        return False

    backend = EMAIL_BACKEND.lower()

    # 1. Console Backend (Default for dev / no credentials)
    if backend == "console" or not (SMTP_USER or RESEND_API_KEY):
        border = "=" * 65
        print(f"\n{border}")
        print(f"📧 [DEV EMAIL MÔ PHỎNG] GỬI EMAIL ĐẾN: {to_email}")
        print(f"   Tiêu đề: {subject}")
        print(f"   Nội dung tóm tắt:\n{text_content or html_content[:300]}...")
        print(f"{border}\n")
        return True

    # 2. Resend API Backend
    if backend == "resend" and RESEND_API_KEY:
        try:
            res = requests.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {RESEND_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "from": EMAIL_SENDER,
                    "to": [to_email],
                    "subject": subject,
                    "html": html_content,
                    "text": text_content or html_content
                },
                timeout=10
            )
            return res.status_code in (200, 201)
        except Exception as e:
            logger.error(f"Resend error: {e}")
            return False

    # 3. SMTP Backend (e.g. Gmail App Password)
    if backend == "smtp" and SMTP_USER and SMTP_PASS:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = EMAIL_SENDER
            msg["To"] = to_email

            if text_content:
                msg.attach(MIMEText(text_content, "plain", "utf-8"))
            msg.attach(MIMEText(html_content, "html", "utf-8"))

            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=12) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(SMTP_USER, [to_email], msg.as_string())
            return True
        except Exception as e:
            logger.error(f"SMTP error: {e}")
            return False

    return False


def send_password_reset_email(to_email: str, reset_url: str) -> bool:
    """Sends password reset link with 30-minute validity."""
    subject = f"[{SYSTEM_NAME}] Yêu cầu đặt lại mật khẩu của bạn"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 580px; margin: 0 auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 16px; background: #ffffff;">
        <h2 style="color: #1B1535; margin-top: 0;">Đặt Lại Mật Khẩu {SYSTEM_NAME}</h2>
        <p style="color: #2E2750; font-size: 15px; line-height: 1.6;">
            Chào bạn, hệ thống nhận được yêu cầu đặt lại mật khẩu cho tài khoản liên kết với email này.
        </p>
        <p style="text-align: center; margin: 30px 0;">
            <a href="{reset_url}" style="background: linear-gradient(135deg, #7C3AED 0%, #EC4899 100%); color: #ffffff; text-decoration: none; padding: 14px 28px; border-radius: 9999px; font-weight: bold; font-size: 14px; display: inline-block;">
                Đặt Lại Mật Khẩu Mới
            </a>
        </p>
        <p style="color: #5B5478; font-size: 13px; line-height: 1.5;">
            Liên kết này chỉ có hiệu lực trong <strong>30 phút</strong> và chỉ sử dụng được 1 lần.<br>
            Nếu không bấm được nút trên, hãy sao chép liên kết sau vào trình duyệt:<br>
            <span style="word-break: break-all; color: #4338CA;">{reset_url}</span>
        </p>
        <hr style="border: none; border-top: 1px solid #f1f5f9; margin: 24px 0;">
        <p style="color: #8A84A3; font-size: 12px; margin-bottom: 0;">
            Nếu bạn không yêu cầu thao tác này, vui lòng bỏ qua email. Tài khoản của bạn vẫn được bảo mật an toàn.<br>
            Hỗ trợ: {OWNER_NAME} · Hotline {HOTLINE_DISPLAY}
        </p>
    </div>
    """
    text = f"Yêu cầu đặt lại mật khẩu {SYSTEM_NAME}. Truy cập liên kết (hạn 30 phút): {reset_url}"
    return send_email(to_email, subject, html, text)


def send_new_device_login_alert(to_email: str, device_info: str, ip_address: str) -> bool:
    """Sends security alert email when login occurs from a new device / IP."""
    subject = f"[{SYSTEM_NAME}] Cảnh báo đăng nhập từ thiết bị mới"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 580px; margin: 0 auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 16px;">
        <h3 style="color: #1B1535; margin-top: 0;">Thông Báo Đăng Nhập Mới</h3>
        <p style="color: #2E2750; font-size: 14px;">
            Tài khoản của bạn vừa đăng nhập thành công vào <strong>{SYSTEM_NAME}</strong>:
        </p>
        <ul style="color: #5B5478; font-size: 13px; line-height: 1.8;">
            <li><strong>Thời gian:</strong> Vừa xong</li>
            <li><strong>Địa chỉ IP:</strong> {ip_address}</li>
            <li><strong>Thiết bị:</strong> {device_info}</li>
        </ul>
        <p style="color: #5B5478; font-size: 13px;">
            Nếu chính bạn vừa đăng nhập, bạn có thể yên tâm bỏ qua email này. Nếu nghi ngờ có người truy cập trái phép, vui lòng đổi mật khẩu ngay lập tức.
        </p>
    </div>
    """
    text = f"Cảnh báo đăng nhập mới tại {SYSTEM_NAME}: IP {ip_address}, Thiết bị: {device_info}."
    return send_email(to_email, subject, html, text)
