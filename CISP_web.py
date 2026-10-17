# -*- coding: utf-8 -*-
"""CISP Web Server — Final Version"""
import json, secrets, os
from pathlib import Path
from datetime import datetime
from flask import Flask, request, session, redirect, send_file, abort, Response
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

LOGO_BK = BASE / "logo_bach_khoa.png"
LOGO_CISP = BASE / "logo_cisp.png"
ICON = BASE / "app_icon.ico"
HEADER_BG = BASE / "header_bg.jpg"

# --- BẢO MẬT & ĐĂNG NHẬP ---
@app.before_request
def _require_login():
    if request.path in ("/favicon.ico", "/logo/bk", "/logo/cisp", "/header_bg", "/login"):
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
                return redirect("/me")
            else:
                return "Sai tên đăng nhập hoặc mật khẩu! <a href='/login'>Thử lại</a>"
        except Exception as e:
            return f"Lỗi kết nối Server: {e} <a href='/login'>Thử lại</a>"
    
    return '''
    <body style="background:#F1F5F9;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;font-family:sans-serif;">
    <div style="background:#fff;padding:40px;border-radius:16px;box-shadow:0 10px 30px rgba(0,0,0,0.1);width:350px;text-align:center;">
        <h2 style="color:#0033A0;margin-bottom:30px;">CỔNG THÔNG TIN SINH VIÊN</h2>
        <form method="POST">
            <input type="text" name="username" placeholder="Mã sinh viên (MSSV)" required style="width:100%;padding:14px;margin-bottom:20px;border:1px solid #CBD5E1;border-radius:8px;box-sizing:border-box;"><br>
            <input type="password" name="password" placeholder="Mật khẩu" required style="width:100%;padding:14px;margin-bottom:25px;border:1px solid #CBD5E1;border-radius:8px;box-sizing:border-box;"><br>
            <button type="submit" style="width:100%;padding:14px;background:#0033A0;color:white;border:none;border-radius:8px;font-weight:bold;cursor:pointer;font-size:16px;">ĐĂNG NHẬP</button>
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
    return redirect("/me")

@app.route("/me")
def me():
    sname = session.get("student_name")
    if not sname: return redirect("/login")
    try:
        res = supabase.table("students").select("*").eq("name", sname).execute()
        if not res.data: 
            return f"<h3 style='text-align:center;margin-top:50px;color:red;font-family:sans-serif;'>Chưa có dữ liệu điểm cho sinh viên: {sname}.<br>Vui lòng liên hệ Giáo viên.</h3><div style='text-align:center;margin-top:20px;'><a href='/logout'>Đăng xuất</a></div>"
        stu = res.data[0]
    except Exception as e:
        return f"<h3 style='text-align:center;margin-top:50px;color:red;'>Lỗi đọc dữ liệu: {e}</h3>"
    
    sc = stu.get("scores", {})
    g = 0
    for v in sc.values():
        if v.get("tb"): g += float(v["tb"])
    gpa = g / len(sc) if sc else 0
    
    rows = ""
    for mon, v in sc.items():
        rows += f"<tr><td style='padding:10px;border:1px solid #E2E8F0;'>{mon}</td><td style='padding:10px;border:1px solid #E2E8F0;'>{v.get('tb10','—')}</td><td style='padding:10px;border:1px solid #E2E8F0;'>{v.get('tb','—')}</td></tr>"

    html = f"""
    <body style="background:#F1F5F9;font-family:sans-serif;margin:0;padding:20px;">
        <div style="max-width:800px;margin:0 auto;background:#fff;border-radius:16px;padding:30px;box-shadow:0 4px 20px rgba(0,0,0,0.05);">
            <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #0033A0;padding-bottom:20px;margin-bottom:20px;">
                <h2 style="color:#0033A0;margin:0;">Xin chào, {sname}</h2>
                <a href="/logout" style="color:red;text-decoration:none;font-weight:bold;">Đăng xuất</a>
            </div>
            <div style="background:#EFF6FF;padding:20px;border-radius:12px;margin-bottom:20px;text-align:center;">
                <h3 style="margin:0;color:#1E40AF;">GPA Tích lũy: {gpa:.2f} / 4.0</h3>
            </div>
            <table style="width:100%;border-collapse:collapse;text-align:center;">
                <tr style="background:#0033A0;color:white;">
                    <th style="padding:12px;border:1px solid #E2E8F0;">Học phần</th>
                    <th style="padding:12px;border:1px solid #E2E8F0;">Điểm TB (Hệ 10)</th>
                    <th style="padding:12px;border:1px solid #E2E8F0;">Điểm TB (Hệ 4)</th>
                </tr>
                {rows}
            </table>
        </div>
        <script>setTimeout(function(){{ location.reload(); }}, 5000);</script>
    </body>
    """
    return html
