# -*- coding: utf-8 -*-
import json, secrets, os
from pathlib import Path
from datetime import datetime
from flask import Flask, request, session, redirect, send_file, abort
from supabase import create_client

BASE = Path(__file__).parent.resolve()
KEY_FILE = BASE / "web_session.key"
app_secret = KEY_FILE.read_text() if KEY_FILE.exists() else secrets.token_hex(32)
if not KEY_FILE.exists(): KEY_FILE.write_text(app_secret)

app = Flask(__name__)
app.secret_key = app_secret

SUPABASE_URL = "https://zebcclcgozhhdalunoch.supabase.co"
SUPABASE_KEY = "sb_publishable_i3crMi5NBh69XDkz6GFlpw_XUWdI7xa"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- BẢO MẬT & ĐĂNG NHẬP ---
@app.before_request
def _require_login():
    if request.path in ("/favicon.ico", "/login"):
        return
    if not session.get("student_id"):
        return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        import hashlib
        pw_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        try:
            res = supabase.table("users").select("*").eq("username", username).eq("password", pw_hash).execute()
            if res.data and res.data[0]["role"] == "student":
                user = res.data[0]
                session["student_id"] = user["id"]
                session["student_name"] = user["full_name"]
                return redirect("/")
            return "Sai tài khoản! <a href='/login'>Thử lại</a>"
        except Exception as e:
            return f"Lỗi Server: {e}"
    
    return '''
    <body style="background:#F1F5F9;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;font-family:sans-serif;">
    <div style="background:#fff;padding:40px;border-radius:16px;box-shadow:0 10px 30px rgba(0,0,0,0.1);width:350px;text-align:center;">
        <h2 style="color:#0033A0;margin-bottom:30px;">CỔNG THÔNG TIN SINH VIÊN</h2>
        <form method="POST">
            <input type="text" name="username" placeholder="Tên đăng nhập" required style="width:100%;padding:14px;margin-bottom:20px;border:1px solid #CBD5E1;border-radius:8px;box-sizing:border-box;"><br>
            <input type="password" name="password" placeholder="Mật khẩu" required style="width:100%;padding:14px;margin-bottom:25px;border:1px solid #CBD5E1;border-radius:8px;box-sizing:border-box;"><br>
            <button type="submit" style="width:100%;padding:14px;background:#0033A0;color:white;border:none;border-radius:8px;font-weight:bold;cursor:pointer;">ĐĂNG NHẬP</button>
        </form>
    </div>
    </body>
    '''

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/")
def home():
    sname = session.get("student_name", "Sinh Viên")
    
    # Lấy dữ liệu từ Database
    stu_data = None
    try:
        res = supabase.table("students").select("*").ilike("name", sname.strip()).execute()
        if res.data: stu_data = res.data[0]
    except: pass

    # Tính GPA
    gpa = 0.0
    rows = "<tr><td colspan='3' style='padding:20px;text-align:center;color:#64748B;'>Chưa có dữ liệu điểm. Vui lòng chờ Giáo viên nhập điểm.</td></tr>"
    
    if stu_data and stu_data.get("scores"):
        sc = stu_data["scores"]
        total_tb4 = sum(float(v.get("tb", 0)) for v in sc.values())
        gpa = total_tb4 / len(sc) if sc else 0
        rows = ""
        for mon, v in sc.items():
            rows += f"<tr><td style='padding:12px;border-bottom:1px solid #E2E8F0;'>{mon}</td><td style='padding:12px;border-bottom:1px solid #E2E8F0;font-weight:bold;color:#0033A0;'>{v.get('tb10','—')}</td><td style='padding:12px;border-bottom:1px solid #E2E8F0;font-weight:bold;color:#16A34A;'>{v.get('tb','—')}</td></tr>"

    html = f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8"><title>CISP Portal - {sname}</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #F1F5F9; margin: 0; }}
        .header {{ background: #0033A0; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }}
        .header h1 {{ margin: 0; font-size: 20px; }}
        .header a {{ color: #FFCC00; text-decoration: none; font-weight: bold; }}
        .container {{ max-width: 900px; margin: 30px auto; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); overflow: hidden; }}
        .greeting {{ padding: 30px; background: #EFF6FF; border-bottom: 1px solid #DBEAFE; }}
        .greeting h2 {{ margin: 0; color: #1E40AF; }}
        .greeting p {{ margin: 5px 0 0 0; color: #64748B; }}
        .stats {{ display: flex; padding: 20px 30px; border-bottom: 1px solid #E2E8F0; gap: 30px; }}
        .stat-box {{ background: #F8FAFC; padding: 15px 25px; border-radius: 8px; border: 1px solid #E2E8F0; flex: 1; text-align: center; }}
        .stat-box .val {{ font-size: 24px; font-weight: bold; color: #0033A0; }}
        .stat-box .lbl {{ font-size: 12px; color: #64748B; text-transform: uppercase; font-weight: bold; margin-top: 5px; }}
        .content {{ padding: 30px; }}
        table {{ width: 100%; border-collapse: collapse; text-align: left; }}
        th {{ background: #F8FAFC; padding: 12px; color: #475569; font-size: 13px; text-transform: uppercase; border-bottom: 2px solid #E2E8F0; }}
    </style>
    </head><body>
        <div class="header">
            <h1>🎓 CISP - Cổng Thông Tin Sinh Viên</h1>
            <a href="/logout">Đăng xuất</a>
        </div>
        <div class="container">
            <div class="greeting">
                <h2>Xin chào, {sname}!</h2>
                <p>Chào mừng bạn đến với hệ thống tra cứu điểm của Khoa Xây dựng - ĐH Bách Khoa Đà Nẵng.</p>
            </div>
            <div class="stats">
                <div class="stat-box">
                    <div class="val">{gpa:.2f} / 4.0</div>
                    <div class="lbl">GPA Tích Lũy</div>
                </div>
                <div class="stat-box">
                    <div class="val">{len(stu_data.get('scores', {})) if stu_data else 0}</div>
                    <div class="lbl">Học phần đã học</div>
                </div>
            </div>
            <div class="content">
                <h3 style="color:#0033A0; margin-top:0;">📊 Bảng Điểm Chi Tiết</h3>
                <table>
                    <tr><th>Học phần</th><th>Điểm TB (Hệ 10)</th><th>Điểm TB (Hệ 4)</th></tr>
                    {rows}
                </table>
            </div>
        </div>
        <script>
            // Tự động cập nhật sau 5 giây
            setTimeout(function(){{ location.reload(); }}, 5000);
        </script>
    </body></html>
    """
    return html
