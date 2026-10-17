# -*- coding: utf-8 -*-
"""CISP Web Server — Flask."""
import json, secrets
from pathlib import Path
from datetime import datetime
from flask import Flask, request, session, redirect, send_file, abort

from supabase import create_client
SUPABASE_URL = "https://zebcclcgozhhdalunoch.supabase.co"
SUPABASE_KEY = "sb_publishable_i3crMi5NBh69XDkz6GFlpw_XUWdI7xa"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

import sys as _sys
if getattr(_sys, "frozen", False):
    BASE = Path(_sys.executable).parent.resolve()
else:
    BASE = Path(__file__).parent.resolve()
MAIL_FILE = BASE / "mail_inbox.json"
ATTACH_DIR = BASE / "mail_attachments"
ATTACH_DIR.mkdir(exist_ok=True)

# ═══════════════ RESOURCE PATH (chay duoc khi frozen) ═══════════════
def _resource_path(name):
    """Tim file anh: uu tien _MEIPASS (folder tam exe), roi den folder exe, roi folder code."""
    import sys as _s
    cands = []
    if getattr(_s, "frozen", False):
        mp = getattr(_s, "_MEIPASS", None)
        if mp:
            cands.append(Path(mp) / name)
        cands.append(Path(_s.executable).parent / name)
    cands.append(BASE / name)
    for c in cands:
        if c.exists():
            return c
    return BASE / name

LOGO_BK = _resource_path("logo_bach_khoa.png")
LOGO_CISP = _resource_path("logo_cisp.png")
ICON = _resource_path("app_icon.ico")
HEADER_BG = _resource_path("header_bg.jpg")

KEY_FILE = BASE / "web_session.key"
app_secret = KEY_FILE.read_text() if KEY_FILE.exists() else secrets.token_hex(32)
if not KEY_FILE.exists(): KEY_FILE.write_text(app_secret)

app = Flask(__name__)
app.secret_key = app_secret


# =============== BASIC AUTH ===============
# =============== SESSION AUTH ===============
@app.before_request
def _require_login():
    if request.path in ("/favicon.ico", "/logo/bk", "/logo/cisp", "/header_bg", "/login"):
        return
    if request.path.startswith("/announce_file/"):
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
            else:
                return "Sai tên đăng nhập hoặc mật khẩu! <a href='/login'>Thử lại</a>"
        except Exception as e:
            import traceback
            error_msg = traceback.format_exc()
            print("=== LOI DANG NHAP ===")
            print(error_msg)
            return f"Lỗi kết nối Server! Chi tiết lỗi: <br><br> <b style='color:red'>{e}</b> <br><br><a href='/login'>Thử lại</a>"
    
    return '''
    <div style="max-width:400px;margin:100px auto;padding:30px;background:#fff;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.1);text-align:center;font-family:sans-serif;">
        <h2 style="color:#0033A0;margin-bottom:20px;">CỔNG THÔNG TIN SINH VIÊN</h2>
        <form method="POST">
            <input type="text" name="username" placeholder="Mã sinh viên (MSSV)" required style="width:100%;padding:12px;margin-bottom:15px;border:1px solid #ccc;border-radius:8px;box-sizing:border-box;"><br>
            <input type="password" name="password" placeholder="Mật khẩu" required style="width:100%;padding:12px;margin-bottom:20px;border:1px solid #ccc;border-radius:8px;box-sizing:border-box;"><br>
            <button type="submit" style="width:100%;padding:12px;background:#0033A0;color:white;border:none;border-radius:8px;font-weight:bold;cursor:pointer;">ĐĂNG NHẬP</button>
        </form>
    </div>
    '''

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
# =============== END SESSION AUTH ===============
TEACHER_NAME = "Nguyễn Thanh Hải"

# ── Thống kê CTĐT ──
# 9 học kỳ = 67 học phần (đã trừ "Tự chọn")
# Học phần tự chọn = 12
# Tổng = 79
TOTAL_SUBJECTS = 79
TOTAL_CREDITS = 156
TEACHER_EMAIL = "hai.nt@dut.udn.vn"


# ─── DỮ LIỆU CHƯƠNG TRÌNH ĐÀO TẠO ───
CHUONG_TRINH_DAO_TAO = {
    "Học kỳ 1": [("Giải tích", 4), ("Vật lý Cơ và Nhiệt", 3),
        ("Thí nghiệm Vật lý (cơ và nhiệt)", 1), ("Nhập môn ngành", 2),
        ("Triết học Mác - Lênin", 3), ("Hình họa - Vẽ kỹ thuật", 3),
        ("Nhập môn công nghệ số và ứng dụng trí tuệ nhân tạo", 2)],
    "Học kỳ 2": [("Chủ nghĩa xã hội khoa học", 2), ("Giải tích nâng cao", 4),
        ("Đại số tuyến tính", 3), ("Anh văn A2.2", 4),
        ("Ngôn ngữ lập trình trong xây dựng", 2), ("Hóa đại cương", 2),
        ("Cơ lý thuyết", 2)],
    "Học kỳ 3": [("Lịch sử Đảng Cộng sản Việt Nam", 2),
        ("Cấu trúc và cơ sở dữ liệu trong xây dựng", 2), ("Anh văn B1.1", 3),
        ("Phương pháp tính", 2), ("Sức bền vật liệu", 3),
        ("Thí nghiệm Sức bền vật liệu", 0.5), ("Trắc địa", 2),
        ("Thực tập trắc địa", 1), ("Thủy lực", 2), ("Thí nghiệm thủy lực", 0.5)],
    "Học kỳ 4": [("Phân tích và thiết kế thuật toán trong xây dựng", 2),
        ("Kinh tế chính trị Mác - Lênin", 2),
        ("Ứng dụng xác suất và thống kê trong xây dựng", 2),
        ("Môi trường và phát triển bền vững", 2), ("Cơ học kết cấu 1", 2),
        ("Cơ học đất", 2), ("Thí nghiệm cơ học đất", 0.5),
        ("Vật liệu xây dựng", 2), ("Thí nghiệm Vật liệu xây dựng", 0.5),
        ("Thủy lực công trình", 2)],
    "Học kỳ 5": [("Tư tưởng Hồ Chí Minh", 2),
        ("Thực hành lập trình trên môi trường Windows", 1),
        ("Phương pháp Phần tử hữu hạn", 2),
        ("Phương pháp nghiên cứu khoa học", 2), ("Cơ học kết cấu 2", 2),
        ("Nền và móng", 2), ("Đồ án Nền và móng", 1),
        ("Kết cấu bê tông cốt thép - phần cơ bản", 3),
        ("Đồ án Kết cấu bê tông cốt thép", 1), ("Thủy văn", 2)],
    "Học kỳ 6": [("Pháp luật đại cương", 2),
        ("Tư duy khởi nghiệp và đổi mới sáng tạo", 2),
        ("Kết cấu nhà bê tông cốt thép", 2), ("Công trình thủy", 3),
        ("Đồ án: Thiết kế công trình thủy", 1),
        ("Cơ sở thiết kế kết cấu thép", 2), ("Phần mềm trong xây dựng", 2),
        ("Ứng dụng GIS trong xây dựng", 2), ("Thực tập nhận thức", 1)],
    "Học kỳ 7": [("Phát triển phần mềm mã nguồn mở", 2), ("Kỹ thuật thi công", 3),
        ("Kinh tế xây dựng", 2), ("Công nghệ BIM trong xây dựng", 3),
        ("Công trình giao thông", 3), ("PBL Thiết kế công trình giao thông", 2)],
    "Học kỳ 8": [("Thiết kế công trình đường", 2), ("Thiết kế công trình cầu", 2),
        ("Tổ chức thi công", 2), ("PBL Công nghệ BIM trong thi công", 2),
        ("Kết cấu nhà cao tầng", 2),
        ("PBL Công nghệ BIM trong thiết kế kết cấu dân dụng", 2),
        ("Tự chọn (chọn 2 học phần)", 4)],
    "Học kỳ 9": [("Thực tập tốt nghiệp", 8), ("Đồ án tốt nghiệp", 10)],
}

HOC_PHAN_TU_CHON = [("Thủy văn công trình", 2),
    ("Mô hình toán thủy văn thủy lực", 2), ("Cấp nước đô thị", 2),
    ("Thoát nước đô thị", 2), ("Mô hình toán ngập lụt đô thị", 2),
    ("Công trình ven bờ", 2), ("Bê tông cốt thép dự ứng lực", 2),
    ("Thiết kế nhà thép", 2), ("Quản lý dự án công trình xây dựng", 2),
    ("Quản trị doanh nghiệp xây dựng", 2), ("Bản sao kỹ thuật số xây dựng", 2),
    ("Trí tuệ nhân tạo trong xây dựng", 2)]

# ─── DỮ LIỆU GIỚI THIỆU NGÀNH ───
INTRO_INFO = {
    "rows_a": [
        ("1. Tên chương trình", ["Kỹ thuật xây dựng - chuyên ngành Tin học xây dựng"]),
        ("2. Trình độ đào tạo", ["Chuyên sâu đặc thù trình độ đại học"]),
        ("3. Tên ngành đào tạo", ["Kỹ thuật xây dựng – chuyên ngành Tin học xây dựng"]),
        ("4. Mã ngành đào tạo", ["7580201A"]),
        ("5. Đối tượng tuyển sinh", ["Học sinh tốt nghiệp THPT hoặc trình độ tương đương có kết quả đánh giá kiến thức/năng khiếu đáp ứng yêu cầu đầu vào theo quy định Trường."]),
        ("6. Thời gian đào tạo", ["4,5 năm"]),
        ("7. Hình thức đào tạo", ["Chính quy"]),
        ("8. Số tín chỉ yêu cầu", ["156 tín chỉ"]),
        ("9. Thang điểm", ["Thang điểm 4"]),
        ("10. Điều kiện tốt nghiệp", [
            "1. Tích lũy đủ số học phần và khối lượng của chương trình đào tạo;",
            "2. Điểm trung bình chung tích lũy toàn khóa học đạt từ 2,00 trở lên;",
            "3. Có chứng chỉ Giáo dục quốc phòng - an ninh, hoàn thành các học phần Giáo dục thể chất;",
            "4. Có chứng chỉ ứng dụng công nghệ thông tin cơ bản;",
            "5. Đạt chuẩn đầu ra của chương trình đào tạo;",
            "6. Không bị truy cứu trách nhiệm hình sự, không đang trong thời gian bị kỷ luật ở mức đình chỉ học tập.",
        ]),
        ("11. Văn bằng tốt nghiệp", ["Kỹ sư (bậc 6)"]),
        ("12. Vị trí việc làm", [
            "Cán bộ tư vấn, thiết kế, thi công các công trình xây dựng trong nước và quốc tế.",
            "Cán bộ kỹ thuật tại các Ban quản lý dự án, các Sở Ban ngành.",
            "Cán bộ kỹ thuật tại các công ty phát triển, ứng dụng CNTT trong xây dựng.",
            "Tham gia giảng dạy, nghiên cứu tại các cơ sở giáo dục.",
        ]),
        ("13. Khả năng nâng cao trình độ", ["SV tốt nghiệp có thể dự tuyển chương trình thạc sĩ, tiến sĩ cùng ngành và ngành gần."]),
        ("14. CTĐT đối sánh", [
            "• CTĐT Tin học xây dựng - Trường ĐH Xây dựng Hà Nội",
            "• CTĐT Kỹ thuật xây dựng - Trường The Auburn University",
        ]),
    ],
    "mt_general": "Mục tiêu chương trình đào tạo (CTĐT) trình độ kỹ sư của ngành Kỹ thuật xây dựng - chuyên ngành Tin học xây dựng (THXD) là đào tạo nguồn nhân lực trong lĩnh vực kỹ thuật xây dựng có phẩm chất chính trị, đạo đức xã hội, sức khỏe đáp ứng yêu cầu phát triển kinh tế - xã hội, bảo đảm quốc phòng và an ninh; có kiến thức, kỹ năng thực hành nghề nghiệp; có năng lực số, năng lực nghiên cứu và phát triển ứng dụng khoa học và công nghệ; có khả năng sáng tạo và học tập suốt đời; có trách nhiệm nghề nghiệp, ý thức phục vụ cộng đồng, thích nghi với môi trường làm việc trong bối cảnh công nghiệp 4.0 và hội nhập quốc tế.",
    "mt_items": [
        ("MT1", "Đào tạo nguồn nhân lực trong lĩnh vực kỹ thuật xây dựng - chuyên ngành THXD có phẩm chất chính trị, đạo đức xã hội, sức khỏe đáp ứng yêu cầu phát triển kinh tế - xã hội, bảo đảm quốc phòng và an ninh."),
        ("MT2", "Trang bị cho người học nền tảng kiến thức cốt lõi, kiến thức chuyên sâu và khoa học kỹ thuật trong lĩnh vực xây dựng các công trình thủy, dân dụng, giao thông và hạ tầng kỹ thuật."),
        ("MT3", "Đào tạo người học có kỹ năng giao tiếp, khả năng sử dụng ngoại ngữ trong hoạt động nghề nghiệp; khả năng làm việc độc lập, làm việc nhóm."),
        ("MT4", "Đào tạo người học khả năng phát hiện, phân tích và giải quyết những vấn đề kỹ thuật xây dựng phức tạp trong thực tiễn nghề nghiệp."),
    ],
    "plo_items": [
        ("P1", "Vận dụng kiến thức toán, khoa học tự nhiên, công nghệ thông tin, kiến thức cốt lõi, chuyên sâu và liên ngành trong lĩnh vực kỹ thuật xây dựng để phân tích, thiết kế, thi công, quản lý, vận hành và giải quyết các vấn đề thực tiễn phức tạp."),
        ("P2", "Áp dụng tư duy hệ thống, tư duy chuyển đổi xanh, tư duy khởi nghiệp để đề xuất, phát triển các giải pháp kỹ thuật, công nghệ mới."),
        ("P3", "Làm việc độc lập, làm việc nhóm hiệu quả; có đạo đức, trách nhiệm nghề nghiệp."),
        ("P4", "Truyền đạt tri thức, giao tiếp hiệu quả; sử dụng ngoại ngữ trong hoạt động chuyên môn."),
        ("P5", "Tiến hành thí nghiệm, phân tích số liệu và đưa ra các kết luận trong lĩnh vực chuyên môn."),
        ("P6", "Ứng dụng công nghệ thông tin, trí tuệ nhân tạo để phát triển các công cụ tính toán, phân tích dữ liệu và tự động hóa nhằm tối ưu thiết kế, thi công, vận hành công trình."),
        ("P7", "Hình thành ý tưởng, xây dựng quy trình thiết kế hệ thống, triển khai thiết kế, vận hành và quản trị, quản lý hoạt động hệ thống phù hợp với bối cảnh công nghiệp 4.0."),
    ],
}

# ── Bảng tín chỉ môn học (copy từ CISP.py) ──
SUBJECT_CREDITS = {
    "Giải tích": 4, "Vật lý Cơ và Nhiệt": 3,
    "Thí nghiệm Vật lý (cơ và nhiệt)": 1, "Nhập môn ngành": 2,
    "Triết học Mác - Lênin": 3, "Hình họa - Vẽ kỹ thuật": 3,
    "Nhập môn công nghệ số và ứng dụng trí tuệ nhân tạo": 2,
    "Chủ nghĩa xã hội khoa học": 2, "Giải tích nâng cao": 4,
    "Đại số tuyến tính": 3, "Anh văn A2.2": 4,
    "Ngôn ngữ lập trình trong xây dựng": 2, "Hóa đại cương": 2,
    "Cơ lý thuyết": 2,
    "Lịch sử Đảng Cộng sản Việt Nam": 2,
    "Cấu trúc và cơ sở dữ liệu trong xây dựng": 2, "Anh văn B1.1": 3,
    "Phương pháp tính": 2, "Sức bền vật liệu": 3,
    "Thí nghiệm Sức bền vật liệu": 0.5, "Trắc địa": 2,
    "Thực tập trắc địa": 1, "Thủy lực": 2, "Thí nghiệm thủy lực": 0.5,
    "Phân tích và thiết kế thuật toán trong xây dựng": 2,
    "Kinh tế chính trị Mác - Lênin": 2,
    "Ứng dụng xác suất và thống kê trong xây dựng": 2,
    "Môi trường và phát triển bền vững": 2, "Cơ học kết cấu 1": 2,
    "Cơ học đất": 2, "Thí nghiệm cơ học đất": 0.5,
    "Vật liệu xây dựng": 2, "Thí nghiệm Vật liệu xây dựng": 0.5,
    "Thủy lực công trình": 2,
    "Tư tưởng Hồ Chí Minh": 2,
    "Thực hành lập trình trên môi trường Windows": 1,
    "Phương pháp Phần tử hữu hạn": 2,
    "Phương pháp nghiên cứu khoa học": 2, "Cơ học kết cấu 2": 2,
    "Nền và móng": 2, "Đồ án Nền và móng": 1,
    "Kết cấu bê tông cốt thép - phần cơ bản": 3,
    "Đồ án Kết cấu bê tông cốt thép": 1, "Thủy văn": 2,
    "Pháp luật đại cương": 2,
    "Tư duy khởi nghiệp và đổi mới sáng tạo": 2,
    "Kết cấu nhà bê tông cốt thép": 2, "Công trình thủy": 3,
    "Đồ án: Thiết kế công trình thủy": 1,
    "Cơ sở thiết kế kết cấu thép": 2, "Phần mềm trong xây dựng": 2,
    "Ứng dụng GIS trong xây dựng": 2, "Thực tập nhận thức": 1,
    "Phát triển phần mềm mã nguồn mở": 2, "Kỹ thuật thi công": 3,
    "Kinh tế xây dựng": 2, "Công nghệ BIM trong xây dựng": 3,
    "Công trình giao thông": 3, "PBL Thiết kế công trình giao thông": 2,
    "Thiết kế công trình đường": 2, "Thiết kế công trình cầu": 2,
    "Tổ chức thi công": 2, "PBL Công nghệ BIM trong thi công": 2,
    "Kết cấu nhà cao tầng": 2,
    "PBL Công nghệ BIM trong thiết kế kết cấu dân dụng": 2,
    "Thực tập tốt nghiệp": 8, "Đồ án tốt nghiệp": 10,
    "Thủy văn công trình": 2,
    "Mô hình toán thủy văn thủy lực": 2, "Cấp nước đô thị": 2,
    "Thoát nước đô thị": 2, "Mô hình toán ngập lụt đô thị": 2,
    "Công trình ven bờ": 2, "Bê tông cốt thép dự ứng lực": 2,
    "Thiết kế nhà thép": 2, "Quản lý dự án công trình xây dựng": 2,
    "Quản trị doanh nghiệp xây dựng": 2, "Bản sao kỹ thuật số xây dựng": 2,
    "Trí tuệ nhân tạo trong xây dựng": 2,
}


def _load(p, d=None):
    try:
        if Path(p).exists(): return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception: pass
    return d if d is not None else {}


def _find_students_file():
    try:
        cands = [f for f in BASE.glob("students_*.json") if f.name != "students_guest.json"]
        if cands:
            def cnt(f):
                try: return len(_load(f, {}).get("students", []))
                except: return -1
            cands.sort(key=cnt, reverse=True)
            if cnt(cands[0]) > 0: return cands[0]
    except Exception: pass
    return BASE / "students_guest.json"


def load_students(): return _load(_find_students_file(), {}).get("students", []) or []


def find_student(name):
    for s in load_students():
        if (s.get("name", "") or "").lower() == name.lower(): return s
    return None


def _sort_key(name):
    import unicodedata
    parts = (name or "").strip().split()
    if not parts: return ""
    n = unicodedata.normalize("NFD", parts[-1].lower())
    return "".join(c for c in n if unicodedata.category(c) != "Mn")


def _gpa(sc):
    """GPA hệ 4 tính theo TC thực của từng môn."""
    tt, tp = 0.0, 0.0
    for mon, v in (sc or {}).items():
        tb = v.get("tb", "")
        if tb == "": continue
        try:
            tc = SUBJECT_CREDITS.get(mon, 2)
            tt += tc
            tp += float(tb) * tc
        except: pass
    return (tp / tt) if tt else 0.0


def _rank(g):
    if g >= 3.6: return "Xuất sắc", "#16A34A"
    if g >= 3.2: return "Giỏi", "#16A34A"
    if g >= 2.5: return "Khá", "#F59E0B"
    if g >= 2.0: return "Trung bình", "#EA580C"
    if g >= 1.0: return "Yếu", "#DC2626"
    if g > 0:    return "Kém", "#7F1D1D"
    return "—", "#64748B"


def _avatar_color(name):
    palette = ["#0284C7","#16A34A","#D4A000","#7C3AED","#DC2626","#0891B2","#EA580C","#DB2777"]
    h = 0
    for c in (name or ""): h = (h * 31 + ord(c)) & 0xFFFFFFFF
    return palette[h % len(palette)]


def _initial(name):
    parts = (name or "?").strip().split()
    return parts[-1][0].upper() if parts else "?"


CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Inter','Segoe UI',sans-serif;background:#F1F5F9;color:#0F172A;line-height:1.55;min-height:100vh;display:flex;flex-direction:column}
.topbar{background:rgba(255,255,255,.85);backdrop-filter:blur(12px);border-bottom:1px solid #E2E8F0;position:sticky;top:0;z-index:100}
.tb-in{max-width:1320px;margin:0 auto;display:flex;align-items:center;gap:14px;padding:12px 28px}
.tb-brand{display:flex;align-items:center;gap:11px;font-weight:800;font-size:15px;color:#0033A0}
.tb-brand img{width:38px;height:38px;border-radius:10px;object-fit:contain;background:#fff;padding:3px;box-shadow:0 2px 6px rgba(0,0,0,.08)}
.tb-nav{margin-left:auto;display:flex;gap:6px}
.tb-link{padding:10px 17px;border-radius:10px;text-decoration:none;color:#475569;font-weight:600;font-size:15px;display:flex;align-items:center;gap:7px;transition:.2s}
.tb-link:hover{background:#EFF6FF;color:#0033A0}
.tb-link.active{background:#0033A0;color:#fff;box-shadow:0 4px 12px rgba(0,51,160,.28)}
.hero{background:linear-gradient(135deg,rgba(14,130,232,.78),rgba(13,71,161,.85) 55%,rgba(12,74,110,.88)),url('/header_bg') center/cover no-repeat;color:#fff;padding:36px 28px 32px;position:relative;overflow:hidden}
.hero::after{content:"";position:absolute;left:0;right:0;bottom:0;height:3px;background:linear-gradient(90deg,transparent,#FFCC00,transparent)}
.hero-in{max-width:1320px;margin:0 auto;display:flex;align-items:center;gap:24px;position:relative;z-index:1}
.hero-logo{width:100px;height:100px;background:#fff;border-radius:20px;padding:10px;display:flex;align-items:center;justify-content:center;box-shadow:0 10px 30px rgba(0,0,0,.2);flex-shrink:0}
.hero-logo img{max-width:100%;max-height:100%;object-fit:contain}
.hero-t1{font-size:27px;font-weight:800;line-height:1.2}
.hero-t2{font-size:23px;font-weight:800;color:#FFCC00;margin-top:3px}
.hero-t3{font-size:14px;color:#D6E4F7;margin-top:8px;font-weight:600}
.hero-chip{display:inline-block;background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.25);padding:4px 10px;border-radius:999px;font-size:11px;font-weight:700;margin-right:6px;margin-top:6px}
main{flex:1}
.wrap{max-width:1320px;margin:0 auto;padding:28px}
.card{background:#fff;border:1px solid #E2E8F0;border-radius:16px;padding:26px;margin-bottom:18px;box-shadow:0 1px 3px rgba(15,23,42,.06)}
.card-h{display:flex;align-items:center;gap:10px;margin-bottom:18px}
.card-h h2{font-size:17px;color:#0033A0;font-weight:800}
.srch{margin-bottom:18px}
.srch input{width:100%;padding:14px 20px;border:2px solid #E2E8F0;border-radius:14px;font-size:14px;outline:none;background:#fff;transition:.2s}
.srch input:focus{border-color:#3B82F6;box-shadow:0 0 0 4px rgba(59,130,246,.12)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}
.stu{display:flex;align-items:center;gap:12px;padding:14px 16px;border:1.5px solid #E2E8F0;border-radius:12px;text-decoration:none;color:inherit;background:#fff;transition:.2s}
.stu:hover{border-color:#0033A0;background:#EFF6FF;transform:translateY(-2px);box-shadow:0 8px 20px rgba(0,51,160,.12)}
.stu-av{width:44px;height:44px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:800;font-size:17px;flex-shrink:0;box-shadow:0 3px 10px rgba(0,0,0,.12)}
.stu-info{min-width:0;flex:1}
.stu-nm{font-size:14.5px;font-weight:700;color:#0F172A;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.stu-rl{font-size:11.5px;color:#64748B;margin-top:2px}
.greet{background:linear-gradient(135deg,#0284C7,#0C4A6E);color:#fff;border:none;padding:28px 30px;display:flex;align-items:center;gap:22px;position:relative;overflow:hidden}
.greet::before{content:"";position:absolute;top:-50%;right:-10%;width:280px;height:280px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.12),transparent 70%)}
.greet-av{width:74px;height:74px;border-radius:50%;background:rgba(255,255,255,.18);border:3px solid #fff;display:flex;align-items:center;justify-content:center;font-size:30px;font-weight:800;flex-shrink:0;position:relative;z-index:1}
.greet-txt{flex:1;min-width:0;position:relative;z-index:1}
.greet-hi{font-size:23px;font-weight:800}
.greet-rl{font-size:13px;opacity:.9;margin-top:6px;font-weight:600}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin-bottom:18px}
.stat{background:#fff;border:1px solid #E2E8F0;border-radius:14px;padding:20px;text-align:center;position:relative;overflow:hidden;transition:.2s}
.stat:hover{transform:translateY(-3px);box-shadow:0 10px 28px rgba(15,23,42,.1)}
.stat::before{content:"";position:absolute;top:0;left:0;right:0;height:3px;background:var(--a,#3B82F6)}
.stat-ic{font-size:24px;margin-bottom:6px}
.stat-v{font-size:30px;font-weight:800;margin:2px 0 4px;line-height:1}
.stat-l{font-size:10.5px;color:#64748B;text-transform:uppercase;font-weight:800;letter-spacing:.5px}
.pbar{height:10px;background:#E2E8F0;border-radius:5px;overflow:hidden;margin:10px 0}
.pfil{height:100%;background:linear-gradient(90deg,#2563EB,#60A5FA);border-radius:5px;position:relative;overflow:hidden}
.pfil::after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,transparent,rgba(255,255,255,.4),transparent);animation:sh 2.4s infinite}
@keyframes sh{0%{transform:translateX(-100%)}100%{transform:translateX(100%)}}
.pinfo{font-size:12.5px;color:#64748B;font-weight:600;display:flex;justify-content:space-between;margin-top:4px}
.pinfo b{color:#0033A0}
.sct{width:100%;border-collapse:separate;border-spacing:0;font-size:13px;margin-top:8px;border-radius:12px;overflow:hidden;border:1px solid #E2E8F0}
.sct thead th{background:linear-gradient(135deg,#0033A0,#0D47A1);color:#fff;padding:13px 14px;text-align:left;font-weight:700;font-size:12px;text-transform:uppercase;letter-spacing:.4px}
.sct tbody td{padding:12px 14px;border-bottom:1px solid #E2E8F0;color:#475569}
.sct tbody tr:nth-child(even) td{background:#FAFBFC}
.sct tbody tr:hover td{background:#EFF6FF;color:#0F172A}
.sct tbody td b{color:#0033A0}
.sct tbody td:nth-child(5) b,.sct tbody tr td:nth-child(6) b{color:#16A34A}
.ro{background:linear-gradient(135deg,#FEF3C7,#FDE68A);color:#92400E;padding:14px 18px;border-radius:12px;font-weight:700;font-size:13px;text-align:center;margin-top:14px;border:1px solid #FCD34D}
.alert{padding:14px 18px;border-radius:12px;margin-bottom:18px;font-weight:600;font-size:13.5px}
.alert.ok{background:#DCFCE7;color:#15803D;border-left:4px solid #16A34A}
.alert.err{background:#FEE2E2;color:#DC2626;border-left:4px solid #DC2626}
.fg{margin-bottom:18px}
.fg label{display:block;font-weight:800;font-size:11.5px;color:#334155;text-transform:uppercase;margin-bottom:8px;letter-spacing:.4px}
.fg input,.fg select,.fg textarea{width:100%;padding:13px 16px;border:2px solid #E2E8F0;border-radius:12px;font-size:14.5px;font-family:inherit;background:#fff;outline:none;transition:.18s;color:#0F172A}
.fg input:focus,.fg select:focus,.fg textarea:focus{border-color:#3B82F6;box-shadow:0 0 0 4px rgba(59,130,246,.12)}
.fg textarea{min-height:170px;resize:vertical}
.btn{padding:14px 30px;background:linear-gradient(135deg,#16A34A,#15803D);color:#fff;border:none;border-radius:12px;font-weight:800;font-size:15px;cursor:pointer;transition:.18s;display:inline-flex;align-items:center;justify-content:center;gap:8px}
.btn:hover{transform:translateY(-2px);box-shadow:0 10px 24px rgba(22,163,74,.3)}
.btn svg{width:18px;height:18px;flex-shrink:0}
.tbox{background:#EFF6FF;border:1px solid #BFDBFE;border-radius:12px;padding:14px 18px;color:#1E40AF;margin-bottom:20px;font-weight:600;font-size:14px;display:flex;align-items:center;gap:10px}
.empty{text-align:center;padding:60px 20px;color:#94A3B8}
.empty-ic{font-size:60px;margin-bottom:14px;opacity:.5}
.ftr{background:linear-gradient(135deg,#0C4A6E 0%,#0D47A1 55%,#05070F 100%);color:#fff;margin-top:50px;position:relative;overflow:hidden}
.ftr-wave{position:absolute;top:-1px;left:0;right:0;height:36px;pointer-events:none;line-height:0}
.ftr-wave svg{display:block;width:100%;height:100%}
.ftr-in{max-width:1320px;margin:0 auto;padding:46px 28px 24px;display:grid;grid-template-columns:1.3fr 1.4fr 1.2fr;gap:32px;position:relative;z-index:1}
.ftr-brand{display:flex;align-items:center;gap:12px;margin-bottom:12px}
.ftr-logo{width:52px;height:52px;border-radius:12px;background:#fff;display:flex;align-items:center;justify-content:center;flex-shrink:0;box-shadow:0 4px 14px rgba(2,132,199,.4);padding:5px;overflow:hidden}.ftr-logo img{max-width:100%;max-height:100%;object-fit:contain;display:block}
.ftr-t1{font-size:13.5px;font-weight:800;letter-spacing:.3px;color:#fff}
.ftr-t2{font-size:11px;color:#7DD3FC;font-weight:600;margin-top:3px}
.ftr-sub{font-size:11.5px;color:#94A3B8;margin-top:10px;line-height:1.65}
.ftr-sub b{color:#7DD3FC}
.ftr-ttl{font-size:11.5px;font-weight:800;letter-spacing:.6px;text-transform:uppercase;color:#7DD3FC;margin-bottom:14px}
.ftr-names{display:flex;flex-wrap:wrap;gap:8px 16px}
.ftr-name{font-size:12px;font-weight:700;color:#E2E8F0;display:flex;align-items:center;gap:7px}
.ftr-name::before{content:"";width:6px;height:6px;border-radius:50%;background:#38BDF8;box-shadow:0 0 8px rgba(56,189,248,.7);flex-shrink:0}
.ftr-gvhd{font-size:13px;color:#E2E8F0;font-weight:600;line-height:1.7}
.ftr-gvhd b{color:#FBBF24;font-weight:800}
.ftr-meta{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}
.ftr-chip{background:rgba(56,189,248,.14);border:1px solid rgba(56,189,248,.3);color:#7DD3FC;font-size:10.5px;font-weight:800;padding:5px 11px;border-radius:999px;letter-spacing:.3px}
.ftr-chip.gold{background:rgba(251,191,36,.14);border-color:rgba(251,191,36,.35);color:#FBBF24}
.ftr-links{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}
.ftr-link{display:inline-flex;align-items:center;gap:6px;padding:7px 13px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);border-radius:9px;color:#CBD5E0;text-decoration:none;font-size:11.5px;font-weight:600;transition:.2s}
.ftr-link:hover{background:rgba(56,189,248,.15);border-color:rgba(56,189,248,.4);color:#fff;transform:translateY(-1px)}
.ftr-bot{max-width:1320px;margin:0 auto;padding:16px 28px 22px;border-top:1px solid rgba(255,255,255,.08);display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;font-size:11.5px;color:#94A3B8;position:relative;z-index:1}
.ftr-bot b{color:#7DD3FC}
.ftr-soc{display:flex;gap:8px}
.ftr-soc a{width:34px;height:34px;border-radius:9px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);display:flex;align-items:center;justify-content:center;color:#CBD5E0;text-decoration:none;font-size:15px;transition:.2s}
.ftr-soc a:hover{background:#0EA5E9;border-color:#0EA5E9;color:#fff;transform:translateY(-2px);box-shadow:0 6px 16px rgba(14,165,233,.4)}
.btt{position:fixed;right:434px;bottom:22px;width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,#0EA5E9,#0C4A6E);color:#fff;border:none;display:flex;align-items:center;justify-content:center;font-size:22px;cursor:pointer;box-shadow:0 8px 22px rgba(2,132,199,.45);opacity:0;visibility:hidden;transition:.25s;z-index:99;font-weight:800}
.btt.show{opacity:1;visibility:visible}
.btt:hover{transform:translateY(-3px) scale(1.05);box-shadow:0 12px 28px rgba(2,132,199,.6)}
/* ─── TĂNG FONT + FIX LAYOUT ─── */
.card{font-size:15px}
.card-h h2{font-size:19px!important}
.sct{font-size:15px!important}
.sct thead th{font-size:13.5px!important;padding:14px 16px!important}
.sct tbody td{font-size:15px!important;padding:14px 16px!important;vertical-align:top;line-height:1.65}
.tbox{font-size:15px!important}
.alert{font-size:15px!important}
.fg label{font-size:13px!important}
.fg input,.fg select,.fg textarea{font-size:15.5px!important}
.btn{font-size:16px!important}
.stu-nm{font-size:15.5px!important}
.stu-rl{font-size:12.5px!important}
.pinfo{font-size:13.5px!important}
.greet-hi{font-size:24px!important}
.greet-rl{font-size:14px!important}
.stat-v{font-size:32px!important}
.stat-l{font-size:11.5px!important}
.empty{font-size:15px!important}
.empty-ic{font-size:64px!important}
/* CTĐT grid */
.ct-card{background:#fff;border:1px solid #E2E8F0;border-radius:14px;overflow:hidden;box-shadow:0 1px 3px rgba(15,23,42,.05)}
.ct-hd{background:linear-gradient(135deg,#0033A0,#0D47A1);color:#fff;padding:16px 20px;font-weight:800;font-size:17px;display:flex;align-items:center;gap:10px}
.ct-row{display:flex;gap:12px;padding:10px 18px;border-bottom:1px solid #F1F5F9;align-items:flex-start}
.ct-row:last-child{border-bottom:none}
.ct-stt{width:28px;flex-shrink:0;color:#94A3B8;font-size:14px;text-align:right;padding-top:2px}
.ct-nm{flex:1;color:#334155;font-size:15px;line-height:1.6;word-break:break-word}
.ct-tc{flex-shrink:0;color:#0033A0;font-weight:800;font-size:15px;white-space:nowrap;padding-top:1px}
.ct-ft{padding:14px 18px;background:#F8FAFC;border-top:1px solid #E2E8F0;text-align:right;font-weight:800;color:#0033A0;font-size:15px}
/* Info rows */
.info-row{display:grid;grid-template-columns:minmax(240px,300px) 1fr;gap:20px;padding:16px 0;border-bottom:1px solid #E2E8F0;align-items:start}
.info-row .lb{color:#0033A0;font-weight:800;font-size:15px;line-height:1.55;word-break:break-word}
.info-row .vl{color:#334155;font-size:15px;line-height:1.75;word-break:break-word;overflow-wrap:anywhere}
.info-row .vl > div{margin-bottom:6px}
@media(max-width:700px){.info-row{grid-template-columns:1fr!important;gap:6px!important}}

/* ─── BĂNG ROLL ─── */
.roll-bar{background:linear-gradient(90deg,#001A4D,#0033A0 30%,#0D47A1 50%,#0033A0 70%,#001A4D);color:#FFCC00;padding:12px 0;overflow:hidden;white-space:nowrap;border-top:2px solid #FFCC00;border-bottom:2px solid #FFCC00;position:relative;box-shadow:0 3px 12px rgba(0,51,160,.25)}
.roll-bar::before,.roll-bar::after{content:"";position:absolute;top:0;bottom:0;width:80px;z-index:2;pointer-events:none}
.roll-bar::before{left:0;background:linear-gradient(90deg,#001A4D,transparent)}
.roll-bar::after{right:0;background:linear-gradient(-90deg,#001A4D,transparent)}
.roll-track{display:inline-block;white-space:nowrap;animation:marquee 45s linear infinite;padding-left:100%}
.roll-track span{display:inline-block;padding:0 80px;font-weight:800;font-size:15px;letter-spacing:0.8px;font-family:'Segoe UI',sans-serif}
.roll-track span .fire{font-size:17px;margin:0 4px}
@keyframes marquee{0%{transform:translateX(0)}100%{transform:translateX(-100%)}}

/* ─── KHUNG THÔNG BÁO TRÁI ─── */
/* ─── KHUNG THÔNG BÁO CỐ ĐỊNH BÊN PHẢI ─── */
.layout-2col{display:grid;grid-template-columns:1fr 400px;gap:20px;align-items:start}
@media(max-width:1250px){.layout-2col{grid-template-columns:1fr}}
.notif-box{background:#fff;border:2px solid #0033A0;border-radius:16px;overflow:hidden;position:sticky;top:88px;box-shadow:0 4px 20px rgba(0,51,160,.12)}
.notif-hd{background:linear-gradient(135deg,#0033A0,#0D47A1);color:#fff;padding:14px 16px;display:flex;align-items:center;gap:10px}
.notif-hd .ic{font-size:22px}
.notif-hd .tt{font-weight:800;font-size:15px;flex:1;letter-spacing:.3px}
.notif-hd .bg-badge{background:#DC2626;color:#fff;font-size:12px;font-weight:800;padding:3px 10px;border-radius:999px}
.notif-body{padding:12px;overflow-y:auto;background:#F8FAFC;max-height:calc(100vh - 220px)}
.notif-body::-webkit-scrollbar{width:8px}
.notif-body::-webkit-scrollbar-thumb{background:#CBD5E1;border-radius:4px}
.notif-body::-webkit-scrollbar-thumb:hover{background:#94A3B8}
.notif-item{background:#fff;border:1.5px solid #E2E8F0;border-radius:10px;padding:10px 12px;margin-bottom:8px;transition:.2s}
.notif-item:hover{border-color:#0033A0;background:#EFF6FF;transform:translateX(3px)}
.notif-item.pinned{border-color:#F59E0B;background:#FFFBEB;border-width:2px}
.notif-item .t{font-weight:800;font-size:12.5px;color:#0033A0;margin-bottom:4px}
.notif-item .c{font-size:11.5px;color:#475569;line-height:1.55;overflow:hidden;text-overflow:ellipsis;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical}
.notif-item .m{font-size:10px;color:#94A3B8;margin-top:6px;display:flex;gap:8px;flex-wrap:wrap}
.notif-empty{text-align:center;padding:30px 10px;color:#94A3B8;font-size:12px}
.notif-empty .ic{font-size:34px;margin-bottom:6px;opacity:.5}

.notif-attach{margin-top:8px;display:flex;flex-wrap:wrap;gap:6px}
.notif-attach a{display:inline-flex;align-items:center;gap:5px;padding:5px 10px;border-radius:8px;text-decoration:none;font-size:11px;font-weight:700;border:1px solid transparent}
.notif-attach a:hover{transform:translateY(-1px)}
.notif-attach a.file{background:#DCFCE7;color:#15803D;border-color:#86EFAC}
.notif-attach a.video{background:#FEF3C7;color:#B45309;border-color:#FCD34D}
.notif-attach a.link{background:#DBEAFE;color:#1E40AF;border-color:#93C5FD}
.notif-img{margin-top:8px;border-radius:8px;overflow:hidden;border:1px solid #E2E8F0}
.notif-img img{display:block;width:100%;height:auto;max-height:180px;object-fit:cover}
.notif-item .t{font-size:13.5px!important}
.notif-item .c{font-size:12.5px!important;line-height:1.6}

@media(max-width:880px){
  .hero{padding:24px 18px}
  .hero-in{flex-direction:column;text-align:center;gap:16px}
  .hero-logo{width:80px;height:80px;padding:8px}
  .hero-t1{font-size:17px}.hero-t2{font-size:15px}.hero-t3{font-size:12px}
  .wrap{padding:18px 16px}
  .topbar .tb-in{padding:10px 16px}
  .ftr-in{grid-template-columns:1fr;gap:24px;padding:38px 20px 20px}
  .ftr-bot{padding:14px 20px 20px;flex-direction:column;text-align:center}
}
"""


def _header():
    # Topbar dùng logo app CISP
    logo = '<img src="/logo/cisp" alt="CISP">' if LOGO_CISP.exists() else '<span style="font-size:28px">🎓</span>'
    # Hero dùng logo trường Bách Khoa
    hero_logo = '<img src="/logo/bk" alt="BK">' if LOGO_BK.exists() else logo
    return f'''
    <div class="topbar"><div class="tb-in">
      <div class="tb-brand">{logo}<span>CISP Portal</span></div>
      <div class="tb-nav">
        <a class="tb-link" href="/">🏠 Trang chủ</a>
        <a class="tb-link" href="/chuong-trinh">📚 Chương trình đào tạo</a>
        <a class="tb-link" href="/gioi-thieu">🏢 Tin học Xây dựng</a>
        <a class="tb-link" href="/quy-che">📚 Quy chế</a>
                <a class="tb-link" href="/community">🌐 Cộng đồng</a>
        <a class="tb-link" href="/mail">✉️ Gửi mail</a>
      </div>
    </div></div>
    <div class="hero"><div class="hero-in">
      <div class="hero-logo">{hero_logo}</div>
      <div>
        <div class="hero-t1">TRƯỜNG ĐẠI HỌC BÁCH KHOA ĐÀ NẴNG</div>
        <div class="hero-t2">KHOA XÂY DỰNG</div>
        <div class="hero-t3">
          <span class="hero-chip">🎓 Lớp 26THXD1</span>
          <span class="hero-chip">💻 Tin học Xây dựng</span>
        </div>
      </div>
    </div></div>
    <div class="roll-bar">
      <div class="roll-track">
        <span>🔥 TIN HỌC XÂY DỰNG MÃI ĐỈNH 🔥</span>
        <span>📚 HỌC TẬP • SÁNG TẠO • ĐỔI MỚI</span>
        <span>🏆 CHINH PHỤC TRI THỨC • KIẾN TẠO TƯƠNG LAI</span>
        <span>🚀 CISP PORTAL — CỔNG THÔNG TIN SINH VIÊN</span>
        <span>🔥 TIN HỌC XÂY DỰNG MÃI ĐỈNH 🔥</span>
        <span>📚 HỌC TẬP • SÁNG TẠO • ĐỔI MỚI</span>
        <span>🏆 CHINH PHỤC TRI THỨC • KIẾN TẠO TƯƠNG LAI</span>
        <span>🚀 CISP PORTAL — CỔNG THÔNG TIN SINH VIÊN</span>
      </div>
    </div>
    '''


def _footer():
    return '''
    <footer class="ftr">
      <div class="ftr-wave">
        <svg viewBox="0 0 1440 40" preserveAspectRatio="none">
          <path fill="#F1F5F9" d="M0,40 C240,10 480,30 720,20 C960,10 1200,30 1440,15 L1440,0 L0,0 Z"/>
        </svg>
      </div>
      <div class="ftr-in">
        <div>
          <div class="ftr-brand">
            <div class="ftr-logo"><img src="/logo/bk" alt="BK" onerror="this.style.display='none';this.parentNode.textContent='🎓'"></div>
            <div>
              <div class="ftr-t1">TRƯỜNG ĐH BÁCH KHOA ĐÀ NẴNG</div>
              <div class="ftr-t2">KHOA XÂY DỰNG • LỚP 26THXD1</div>
            </div>
          </div>
          <div class="ftr-sub">
            Cổng thông tin sinh viên <b>CISP Portal</b> — Tra cứu điểm, theo dõi tiến độ học tập, gửi mail cho GVHD.
          </div>
          <div class="ftr-links">
            <a class="ftr-link" href="https://dut.udn.vn" target="_blank" rel="noopener">🌐 dut.udn.vn</a>
            <a class="ftr-link" href="tel:02363842309">📞 (0236) 3842 309</a>
            <a class="ftr-link" href="mailto:hai.nt@dut.udn.vn">✉️ hai.nt@dut.udn.vn</a>
          </div>
        </div>
        <div>
          <div class="ftr-ttl">👥 NHÓM THỰC HIỆN</div>
          <div class="ftr-names">
            <span class="ftr-name">Đỗ Thanh Phong</span>
            <span class="ftr-name">Trần Trung Đỉnh</span>
            <span class="ftr-name">Nguyễn Phước Đạt</span>
            <span class="ftr-name">Trần Minh Trí</span>
          </div>
          <div class="ftr-meta">
            <span class="ftr-chip">👑 Trưởng nhóm: Đỗ Thanh Phong</span>
            <span class="ftr-chip gold">🎓 Kỹ sư 156 TC</span>
          </div>
        </div>
        <div>
          <div class="ftr-ttl">👨‍🏫 GIẢNG VIÊN HƯỚNG DẪN</div>
          <div class="ftr-gvhd">Thầy <b>Nguyễn Thanh Hải</b><br><span style="font-size:11.5px;color:#94A3B8">Khoa Xây dựng — ĐH Bách khoa Đà Nẵng</span></div>
          <div class="ftr-meta">
            <span class="ftr-chip">CISP v1.0</span>
            <span class="ftr-chip gold">05/10/2026</span>
          </div>
        </div>
      </div>
      <div class="ftr-bot">
        <div>© 2026 <b>CISP Portal</b> • Made with 💙 in Đà Nẵng</div>
        <div class="ftr-soc">
          <a href="https://dut.udn.vn" target="_blank" rel="noopener" title="Website">🌐</a>
          <a href="mailto:hai.nt@dut.udn.vn" title="Email">✉️</a>
          <a href="#" onclick="return false" title="Facebook">📘</a>
          <a href="#" onclick="return false" title="GitHub">🐙</a>
        </div>
      </div>
    </footer>
'''


def _announcements_data():
    """Đọc danh sách thông báo từ announcements.json."""
    d = _load(BASE / "announcements.json", {"announcements": []})
    lst = d.get("announcements", []) or []
    try:
        lst = sorted(lst, key=lambda a: (
            0 if a.get("pinned", False) else 1,
            -(float(a.get("ts", 0)) or 0)))
    except Exception:
        pass
    return lst


def _notif_panel_html():
    from pathlib import Path as _P
    anns = _announcements_data()
    if not anns:
        items = '<div class="notif-empty"><div class="ic">📭</div><div>Chưa có thông báo</div></div>'
        badge = ""
    else:
        unread = sum(1 for a in anns if not a.get("read", False))
        badge = f'<span class="bg-badge">{unread}</span>' if unread else ""
        rows = []
        for a in anns[:20]:
            pinned = a.get("pinned", False)
            cls = "notif-item pinned" if pinned else "notif-item"
            title = (a.get("title") or "(Không tiêu đề)")
            content = (a.get("content") or "").strip()
            if len(content) > 150: content = content[:150] + "..."
            author = a.get("author", "")
            created = a.get("created_at", "")

            img_html = ""
            img_p = a.get("image_path", "")
            if img_p:
                fname = _P(img_p).name
                img_file = BASE / "announce_images" / fname
                if img_file.exists():
                    img_html = f'<div class="notif-img"><a href="/announce_file/{fname}" target="_blank"><img src="/announce_file/{fname}" alt="{fname}"></a></div>'

            atts = []
            fp = a.get("file_path", "")
            if fp:
                fname = _P(fp).name
                fdisp = a.get("file_name") or fname
                atts.append(f'<a class="file" href="/announce_file/{fname}" download>📎 {fdisp}</a>')
            vp = a.get("video_path", "")
            if vp:
                fname = _P(vp).name
                vdisp = a.get("video_name") or fname
                atts.append(f'<a class="video" href="/announce_file/{fname}" target="_blank">🎬 {vdisp}</a>')
            url = a.get("url", "")
            if url:
                atts.append(f'<a class="link" href="{url}" target="_blank" rel="noopener">🔗 Mở link</a>')
            att_html = f'<div class="notif-attach">{"".join(atts)}</div>' if atts else ""

            pin_ic = "📌 " if pinned else ""
            rows.append(f'''<div class="{cls}">
              <div class="t">{pin_ic}{title}</div>
              <div class="c">{content or "(không có nội dung)"}</div>
              {img_html}
              {att_html}
              <div class="m"><span>👤 {author}</span><span>🕐 {created}</span></div>
            </div>''')
        items = "".join(rows)
    return f'''
    <div class="notif-box" id="nf">
      <div class="notif-hd">
        <span class="ic">📢</span>
        <span class="tt">THÔNG BÁO</span>
        {badge}
      </div>
      <div class="notif-body">{items}</div>
    </div>'''


def page(title, body, active=""):
    return f'''<!DOCTYPE html><html lang="vi"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#0033A0"><title>{title} — CISP Portal</title><link rel="icon" href="/favicon.ico" type="image/x-icon"><link rel="apple-touch-icon" href="/logo/cisp"><style>{CSS}</style></head><body>{_header()}<main><div class="wrap">{body}</div></main>{_footer()}
<button class="btt" id="btt" type="button" aria-label="Lên đầu trang">↑</button>
<script>
(function(){{
  var b = document.getElementById('btt');
  if(!b) return;
  function _upd() {{
    if (window.scrollY > 300) b.classList.add('show');
    else b.classList.remove('show');
  }}
  window.addEventListener('scroll', _upd, {{passive:true}});
  b.addEventListener('click', function(e){{
    e.preventDefault();
    try {{ window.scrollTo({{top:0, behavior:'smooth'}}); }}
    catch(err) {{ window.scrollTo(0, 0); }}
  }});
  _upd();
  // Active nav
  document.querySelectorAll('.tb-link').forEach(function(a){{
    if (a.getAttribute('href') === location.pathname) a.classList.add('active');
  }});
}})();
</script></body></html>'''


@app.route("/logo/bk")
def logo_bk():
    if LOGO_BK.exists(): return send_file(LOGO_BK, mimetype="image/png")
    abort(404)


@app.route("/logo/cisp")
def logo_cisp():
    if LOGO_CISP.exists(): return send_file(LOGO_CISP, mimetype="image/png")
    abort(404)


@app.route("/header_bg")
def header_bg():
    for name in ("header_bg.jpg", "header_bg.jpeg", "header_bg.png", "header_bg.webp"):
        p = _resource_path(name)
        if p.exists():
            sfx = p.suffix.lower()
            mt = "image/jpeg" if sfx in (".jpg", ".jpeg") else ("image/png" if sfx == ".png" else "image/webp")
            return send_file(p, mimetype=mt)
    abort(404)


@app.route("/favicon.ico")
def favicon():
    if ICON.exists(): return send_file(ICON, mimetype="image/x-icon")
    if LOGO_CISP.exists(): return send_file(LOGO_CISP, mimetype="image/png")
    abort(404)


@app.route("/")
def home():
    return redirect("/me")

@app.route("/list")
def student_list():
    students = load_students()
    students.sort(key=lambda s: _sort_key(s.get("name", "")))
    kw = (request.args.get("q") or "").strip().lower()
    if kw:
        students = [s for s in students if kw in (s.get("name", "") or "").lower()]

    all_stu = load_students()
    total = len(all_stu)
    n_dat = 0; n_rot = 0
    for s in all_stu:
        g = _gpa(s.get("scores", {}))
        if g == 0: continue
        if g >= 2.0: n_dat += 1
        else: n_rot += 1
    rate = f"{n_dat}/{total}" if total else "—"
    rc = "#16A34A" if n_rot == 0 and n_dat > 0 else ("#F59E0B" if n_rot <= max(1, total // 5) else "#DC2626")

    stats = f'''
    <div class="stats">
      <div class="stat" style="--a:#2563EB"><div class="stat-ic">👨‍🎓</div><div class="stat-v" style="color:#2563EB">{total}</div><div class="stat-l">Tổng sinh viên</div></div>
      <div class="stat" style="--a:#16A34A"><div class="stat-ic">📚</div><div class="stat-v" style="color:#16A34A">{TOTAL_SUBJECTS}</div><div class="stat-l">Học phần</div></div>
      <div class="stat" style="--a:#D4A000"><div class="stat-ic">🎯</div><div class="stat-v" style="color:#D4A000">{TOTAL_CREDITS}</div><div class="stat-l">Tín chỉ</div></div>
      <div class="stat" style="--a:{rc}"><div class="stat-ic">🏆</div><div class="stat-v" style="color:{rc}">{rate}</div><div class="stat-l">Tỷ lệ đạt</div></div>
    </div>'''

    leaders = [s for s in all_stu if s.get("role") == "lt"]
    vices = [s for s in all_stu if s.get("role") == "lp"]
    roles_html = ""
    if leaders or vices:
        parts = []
        if leaders: parts.append(f'👑 Lớp trưởng: <b>{", ".join(s["name"] for s in leaders)}</b>')
        if vices: parts.append(f'⭐ Lớp phó: <b>{", ".join(s["name"] for s in vices)}</b>')
        roles_html = f'<div style="background:#EFF6FF;border-radius:10px;padding:12px 18px;margin-bottom:16px;font-size:13px;font-weight:700;color:#0033A0">{" &nbsp;•&nbsp; ".join(parts)}</div>'

    if not students:
        msg = "Không tìm thấy sinh viên" if kw else "Chưa có sinh viên"
        items = f'<div class="empty"><div class="empty-ic">📭</div><div>{msg}</div></div>'
    else:
        rows = []
        role_map = {"lt": "Lớp trưởng", "lp": "Lớp phó", "tv": "Thành viên"}
        for s in students:
            nm = s.get("name", "?")
            col = _avatar_color(nm)
            ini = _initial(nm)
            role = s.get("role", "tv")
            rl = role_map.get(role, "Thành viên")
            badge = " 👑" if role == "lt" else (" ⭐" if role == "lp" else "")
            safe_nm = nm.replace("&", "&amp;").replace('"', "&quot;")
            rows.append(f'<a class="stu" href="/me?name={safe_nm}"><div class="stu-av" style="background:{col}">{ini}</div><div class="stu-info"><div class="stu-nm">{nm}{badge}</div><div class="stu-rl">{rl}</div></div></a>')
        items = f'<div class="grid" id="sg">{"".join(rows)}</div>'
        items += '<div class="empty" id="em" style="display:none"><div class="empty-ic">🔍</div><div>Không tìm thấy</div></div>'

    notif_html = _notif_panel_html()
    body = stats + f'''
    <div class="layout-2col">
      <div class="card" style="margin-bottom:0">
        <div class="card-h"><h2>📋 Danh sách sinh viên ({len(students)})</h2></div>
        {roles_html}
        <div class="srch"><input id="q" placeholder="🔍 Nhập tên sinh viên..." oninput="filt(this.value)" autofocus></div>
        {items}
      </div>
      <div>
        {notif_html}
      </div>
    </div>
    <script>
    function filt(v){{
      v=v.toLowerCase().trim();
      var n=0;
      document.querySelectorAll('#sg .stu').forEach(function(el){{
        var m=!v||el.textContent.toLowerCase().includes(v);
        el.style.display=m?'':'none';
        if(m)n++;
      }});
      document.getElementById('em').style.display=n===0?'block':'none';
    }}
    </script>'''
    return page("Trang chủ", body, "home")


@app.route("/me")
def me():
    sid = session.get("student_id")
    if not sid: return redirect("/login")
    try:
        res = supabase.table("students").select("*").eq("user_id", sid).execute()
        if not res.data: return "Chưa có dữ liệu điểm."
        stu = res.data[0]
    except:
        return "Lỗi đọc dữ liệu."
    name = stu.get("name", "Sinh Viên")

    sc = stu.get("scores", {}) or {}
    g = _gpa(sc)
    rk, col = _rank(g)
    training = float(stu.get("training_total", 0) or 0)
    n_sub = sum(1 for v in sc.values() if v.get("tb", "") != "")
    done_cr = 0
    for mon, v in sc.items():
        try:
            if float(v.get("tb", 0) or 0) >= 1.0:
                done_cr += SUBJECT_CREDITS.get(mon, 2)
        except: pass
    pct = min(100.0, done_cr / 156 * 100) if done_cr else 0.0

    role_map = {"lt": "Lớp trưởng", "lp": "Lớp phó", "tv": "Thành viên"}
    rl = role_map.get(stu.get("role", "tv"), "Thành viên")
    ini = _initial(name)
    av_col = _avatar_color(name)

    greet = f'''
    <div class="card greet">
      <div class="greet-av" style="background:{av_col}">{ini}</div>
      <div class="greet-txt">
        <div class="greet-hi">👋 Xin chào, {name}!</div>
        <div class="greet-rl">{rl} • Lớp 26THXD1</div>
      </div>
      <a href="/change" style="position:relative;z-index:1;padding:11px 22px;background:linear-gradient(135deg,#F59E0B,#EA580C);color:#fff;text-decoration:none;border-radius:12px;font-weight:800;font-size:13.5px;box-shadow:0 4px 16px rgba(245,158,11,.4);white-space:nowrap">🔄 Đổi SV</a>
    </div>'''

    stats = f'''
    <div class="stats">
      <div class="stat" style="--a:{col}"><div class="stat-ic">📊</div><div class="stat-v" style="color:{col}">{g:.2f}</div><div class="stat-l">GPA</div></div>
      <div class="stat" style="--a:{col}"><div class="stat-ic">🏆</div><div class="stat-v" style="color:{col}">{rk}</div><div class="stat-l">Học lực</div></div>
      <div class="stat" style="--a:#DC2626"><div class="stat-ic">⭐</div><div class="stat-v" style="color:#DC2626">{training:.0f}<span style="font-size:16px;opacity:.6">/100</span></div><div class="stat-l">Điểm rèn luyện</div></div>
      <div class="stat" style="--a:#2563EB"><div class="stat-ic">📚</div><div class="stat-v" style="color:#2563EB">{n_sub}</div><div class="stat-l">Số môn đã học</div></div>
    </div>'''

    prog = f'''
    <div class="card">
      <div class="card-h"><h2>🎓 Tiến độ toàn khóa</h2></div>
      <div class="pbar"><div class="pfil" style="width:{pct:.1f}%"></div></div>
      <div class="pinfo"><span>Đã tích lũy <b>{done_cr}</b> / 156 tín chỉ</span><span><b>{pct:.1f}%</b></span></div>
    </div>'''

    if sc:
        rows = []
        for mon in sorted(sc.keys()):
            v = sc[mon]
            rows.append(f'<tr><td>{mon}</td><td>{v.get("qt","—")}</td><td>{v.get("gk","—")}</td><td>{v.get("ck","—")}</td><td><b>{v.get("tb10","—")}</b></td><td><b>{v.get("tb","—")}</b></td></tr>')
        scores = f'''<div class="card"><div class="card-h"><h2>📊 Bảng điểm chi tiết ({n_sub} môn)</h2></div><div style="overflow-x:auto"><table class="sct"><thead><tr><th>Học phần</th><th>QT</th><th>GK</th><th>CK</th><th>TB10</th><th>TB4</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div></div>'''
    else:
        scores = '<div class="card"><div class="card-h"><h2>📊 Bảng điểm</h2></div><div class="empty"><div class="empty-ic">📭</div><div>Chưa có điểm</div></div></div>'

    body = greet + stats + prog + scores + '<div class="ro">🔒 Chế độ CHỈ XEM — Liên hệ GVHD nếu cần chỉnh sửa</div>'
    return page(name, body)


@app.route("/change")
def change():
    session.pop("student_name", None)
    return redirect("/")


@app.route("/mail", methods=["GET", "POST"])
def mail():
    msg = None
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        sender = (request.form.get("sender") or "").strip()
        mssv = (request.form.get("mssv") or "").strip()
        content = (request.form.get("content") or "").strip()
        email = (request.form.get("email") or "").strip()
        errs = []
        if not title: errs.append("Thiếu tiêu đề")
        if not sender: errs.append("Chưa chọn SV")
        if not mssv.isdigit(): errs.append("MSSV chỉ chứa số")
        if not content: errs.append("Thiếu nội dung")
        if "@" not in email: errs.append("Email không hợp lệ")
        if errs:
            msg = ("err", " • ".join(errs))
        else:
            saved = []
            for f in request.files.getlist("files"):
                if not f or not f.filename: continue
                try:
                    safe = "".join(c for c in f.filename if c.isalnum() or c in "._- ")[:80]
                    if not safe: continue
                    uid = secrets.token_hex(6)
                    fname = f"{uid}_{safe}"
                    fpath = ATTACH_DIR / fname
                    f.save(str(fpath))
                    saved.append({"name": safe, "path": fname, "size": fpath.stat().st_size})
                except: pass
            mails = _load(MAIL_FILE, {}).get("mails", []) or []
            mails.append({"id": secrets.token_hex(8), "title": title, "sender_name": sender, "mssv": mssv, "content": content, "contact_email": email, "sent_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "read": False, "attachments": saved})
            MAIL_FILE.write_text(json.dumps({"mails": mails}, ensure_ascii=False, indent=2), encoding="utf-8")
            msg = ("ok", "✅ Đã gửi mail thành công!")

    students = load_students()
    names = sorted({s.get("name", "") for s in students if s.get("name")}, key=_sort_key)
    opts = "".join(f'<option value="{n}">{n}</option>' for n in names)
    alert = ""
    if msg:
        alert = f'<div class="alert {"ok" if msg[0]=="ok" else "err"}">{msg[1]}</div>'

    body = f'''
    <div class="card">
      <div class="card-h"><h2>✉️ Gửi mail cho Giảng viên hướng dẫn</h2></div>
      <div class="tbox">👨‍🏫 <span>GVHD: <b>{TEACHER_NAME}</b> • {TEACHER_EMAIL}</span></div>
      {alert}
      <form method="post" enctype="multipart/form-data">
        <div class="fg"><label>Tiêu đề mail *</label><input type="text" name="title" required placeholder="VD: Xin phép nghỉ học..."></div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px" class="two">
          <div class="fg"><label>Email của bạn *</label><input type="email" name="email" required placeholder="Nhập mail để nhận phản hồi..."></div>
          <div class="fg"><label>MSSV *</label><input type="text" name="mssv" required pattern="[0-9]+" placeholder="26123456"></div>
        </div>
        <div class="fg"><label>Tên sinh viên *</label><select name="sender" required><option value="">-- Chọn tên --</option>{opts}</select></div>
        <div class="fg"><label>Nội dung *</label><textarea name="content" required placeholder="Nhập nội dung mail..."></textarea></div>
        <div class="fg"><label>Đính kèm (tùy chọn)</label><input type="file" name="files" multiple></div>
        <button type="submit" class="btn">📨 Gửi mail</button>
      </form>
    </div>
    <style>@media(max-width:600px){{.two{{grid-template-columns:1fr!important}}}}</style>'''
    return page("Gửi mail", body, "mail")


@app.route("/announce_file/<path:fname>")
def announce_file(fname):
    from pathlib import Path as _P
    fname = _P(fname).name
    for sub in ("announce_files", "announce_images"):
        p = BASE / sub / fname
        if p.exists():
            ext = p.suffix.lower()
            inline = ext in (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".svg")
            return send_file(p, as_attachment=not inline)
    abort(404)


@app.route("/quy-che")
def quy_che():
    rows_scale = [
        ("9.5 đến 10,0", "A+", "4,0"), ("8.5 đến 9,5", "A", "4,0"),
        ("8.0 đến 8,5", "B+", "3,5"), ("7.0 đến 8,0", "B", "3,0"),
        ("6.5 đến 7,0", "C+", "2,5"), ("5.5 đến 6,5", "C", "2,0"),
        ("5.0 đến 5,5", "D+", "1,5"), ("4.0 đến 5,0", "D", "1,0"),
        ("Dưới 4,0", "F", "0"),
    ]
    rows_gpa = [
        ("Loại xuất sắc", "từ 3,60 đến 4,00"),
        ("Loại giỏi", "từ 3,20 đến 3,59"),
        ("Loại khá", "từ 2,50 đến 3,19"),
        ("Loại trung bình", "từ 2,00 đến 2,49"),
    ]
    rows_warn_year = [
        ("Năm nhất", "< 1,20"), ("Năm 2", "< 1,40"),
        ("Năm 3", "< 1,60"), ("Năm 4 trở lên", "< 1,80"),
        ("Sinh viên liên thông", "< 1,80"),
    ]
    rows_warn_hk = [
        ("Học kỳ thứ nhất", "< 0,80"),
        ("Học kỳ thứ 2 trở đi", "< 1,20"),
        ("Sinh viên liên thông", "< 1,20"),
    ]

    def t(data):
        return "".join(
            f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" if len(x) == 3
            else f"<tr><td>{a}</td><td>{b}</td></tr>"
            for x in data
            for a, b, *rest in [x + (None,) if len(x) == 2 else x]
            for c in [rest[0] if rest else ""]
        )

    def t2(data):
        return "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in data)

    def t3(data):
        return "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in data)

    body = f"""
    <div class="card" style="background:linear-gradient(135deg,#0033A0,#0D47A1);color:#fff;border:none">
      <div style="display:flex;align-items:center;gap:14px">
        <div style="font-size:42px">📚</div>
        <div>
          <div style="font-size:22px;font-weight:800">QUY CHẾ HỌC TẬP</div>
          <div style="font-size:13px;color:#D6E4F7;margin-top:4px;font-weight:600">
            Trường ĐH Bách khoa Đà Nẵng — Khoa Xây dựng
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-h"><h2>📐 Bảng quy đổi điểm</h2></div>
      <table class="sct">
        <thead><tr><th>Điểm hệ 10</th><th>Thang chữ</th><th>Thang hệ 4</th></tr></thead>
        <tbody>{t3(rows_scale)}</tbody>
      </table>
      <div class="tbox" style="margin-top:14px">
        <span>💡 <b>Loại đạt:</b> D trở lên (≥ 1.0 hệ 4)</span>
      </div>
      <div class="tbox" style="background:#FEE2E2;border-color:#FECACA;color:#DC2626">
        <span>⛔ <b>Loại không đạt:</b> F (0.0 hệ 4) — phải học lại</span>
      </div>
    </div>

    <div class="card">
      <div class="card-h"><h2>🏆 Xếp loại GPA</h2></div>
      <table class="sct">
        <thead><tr><th>Phân loại</th><th>GPA</th></tr></thead>
        <tbody>{t2(rows_gpa)}</tbody>
      </table>
    </div>

    <div class="card">
      <div class="card-h"><h2>🧮 Công thức tính GPA</h2></div>
      <div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:12px;padding:20px;text-align:center;font-size:22px;font-weight:700;color:#0033A0;font-family:serif;margin:10px 0">
        GPA = Σ ( Điểm<sub>i</sub> × TC<sub>i</sub> ) / Σ TC<sub>i</sub>
      </div>
      <div style="font-size:13px;color:#64748B;line-height:1.8">
        Điểm<sub>i</sub>: điểm tích lũy của học phần i &nbsp;•&nbsp;
        TC<sub>i</sub>: số tín chỉ của học phần i<br>
        N: số học phần tích lũy từ đầu khóa học
      </div>
    </div>

    <div class="card" style="border-color:#FCD34D">
      <div class="card-h"><h2 style="color:#B45309">⚠️ CẢNH BÁO KẾT QUẢ HỌC TẬP</h2></div>
      <p style="margin-bottom:14px;color:#7C2D12;font-weight:600;font-size:14px">
        Cuối mỗi học kỳ, sinh viên bị cảnh báo học tập nếu rơi vào một trong các trường hợp:
      </p>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px" class="two-col">
        <div>
          <div style="font-weight:800;color:#B45309;font-size:13px;margin-bottom:8px">
            📉 Theo điểm TB tích lũy toàn khóa (theo năm)
          </div>
          <table class="sct">
            <thead><tr><th>Năm</th><th>GPA</th></tr></thead>
            <tbody>{t2(rows_warn_year)}</tbody>
          </table>
        </div>
        <div>
          <div style="font-weight:800;color:#B45309;font-size:13px;margin-bottom:8px">
            📊 Theo điểm TB chung học kỳ
          </div>
          <table class="sct">
            <thead><tr><th>Học kỳ</th><th>GPA</th></tr></thead>
            <tbody>{t2(rows_warn_hk)}</tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="card" style="border-color:#F87171">
      <div class="card-h"><h2 style="color:#DC2626">🛑 BUỘC THÔI HỌC</h2></div>
      <p style="margin-bottom:14px;color:#991B1B;font-weight:600;font-size:14px">
        Sinh viên bị buộc thôi học nếu rơi vào một trong các trường hợp sau:
      </p>
      <div style="line-height:1.9;color:#334155;font-size:14px">
        <div style="padding:10px 14px;background:#FEF2F2;border-left:4px solid #DC2626;border-radius:8px;margin-bottom:10px">
          <b>❗ Tự ý bỏ học:</b> Có khối lượng học tập từ 0 tín chỉ
          <i>(không kể sinh viên được Trường cho quyết định cho ngừng học)</i>
        </div>
        <div style="padding:10px 14px;background:#FEF2F2;border-left:4px solid #DC2626;border-radius:8px;margin-bottom:10px">
          <b>❗ Điểm F toàn bộ:</b> Điểm của tất cả các học phần trong học kỳ đều là 0 theo thang điểm 10
        </div>
        <div style="padding:10px 14px;background:#FEF2F2;border-left:4px solid #DC2626;border-radius:8px;margin-bottom:10px">
          <b>❗ Hết thời gian:</b> Hết thời gian học tối đa theo quy định (6.0 năm)
        </div>
        <div style="padding:10px 14px;background:#FEF2F2;border-left:4px solid #DC2626;border-radius:8px">
          <b>❗ CB KQHT 2 lần:</b> Tính đến cuối học kỳ trước, sinh viên đã bị cảnh báo kết quả
          học tập 2 lần và có kết quả học tập thấp dưới mức quy định
        </div>
      </div>
    </div>

    <div class="card" style="border-color:#93C5FD">
      <div class="card-h"><h2>🔄 HỌC LẠI — HỌC CẢI THIỆN</h2></div>
      <div style="line-height:1.9;color:#334155;font-size:14px">
        <div style="padding:12px 16px;background:#EFF6FF;border-left:4px solid #2563EB;border-radius:8px;margin-bottom:12px">
          <b style="color:#0033A0">📘 Học lại</b>
          <div style="margin-top:6px">
            • Đối với <b>học phần bắt buộc</b>: phải đăng ký học lại học phần đó
              hoặc học một học phần thay thế nếu học phần đó không còn được giảng dạy<br>
            • Đối với <b>học phần tự chọn</b>: có thể đăng ký học lại học phần đã có điểm
              không đạt hoặc đăng ký học phần tự chọn khác
          </div>
        </div>
        <div style="padding:12px 16px;background:#F0FDF4;border-left:4px solid #16A34A;border-radius:8px;margin-bottom:12px">
          <b style="color:#15803D">📘 Học cải thiện</b>
          <div style="margin-top:6px">
            Điểm cao nhất trong các lần học được công nhận là điểm chính thức của học phần.
          </div>
        </div>
        <div style="padding:12px 16px;background:#FEF2F2;border-left:4px solid #DC2626;border-radius:8px">
          <b style="color:#DC2626">⚠️ Lưu ý</b>
          <div style="margin-top:6px">
            Học lại, học cải thiện <b>quá 5% tổng số tín chỉ</b> sẽ bị hạ một bậc bằng,
            từ Khá trở xuống thì không hạ.
          </div>
        </div>
      </div>
    </div>
    <style>@media(max-width:700px){{.two-col{{grid-template-columns:1fr!important}}}}</style>
    """
    return page("Quy chế", body, "quy-che")


@app.route("/chuong-trinh")
def chuong_trinh():
    # Từng học kỳ
    sem_cards = []
    for hk, subs in CHUONG_TRINH_DAO_TAO.items():
        rows = ""
        total_tc = 0
        for i, (name, tc) in enumerate(subs, 1):
            rows += f'<div class="ct-row"><div class="ct-stt">{i}.</div><div class="ct-nm">{name}</div><div class="ct-tc">{tc:g} TC</div></div>'
            total_tc += tc
        num = hk.replace("Học kỳ ", "")
        sem_cards.append(f"""
        <div class="ct-card">
          <div class="ct-hd">📖 Học kỳ {num}</div>
          {rows}
          <div class="ct-ft">Tổng: {total_tc:g} TC</div>
        </div>""")

    # Tự chọn
    elec_rows = ""
    for i, (name, tc) in enumerate(HOC_PHAN_TU_CHON, 1):
        elec_rows += f'<div class="ct-row"><div class="ct-stt">{i}.</div><div class="ct-nm">{name}</div><div class="ct-tc" style="color:#B45309">{tc:g} TC</div></div>'

    body = f"""
    <div class="card" style="background:linear-gradient(135deg,#0033A0,#0D47A1);color:#fff;border:none">
      <div style="display:flex;align-items:center;gap:14px">
        <div style="font-size:42px">📚</div>
        <div>
          <div style="font-size:22px;font-weight:800">CHƯƠNG TRÌNH ĐÀO TẠO</div>
          <div style="font-size:13px;color:#D6E4F7;margin-top:4px;font-weight:600">
            Trường ĐH Bách khoa Đà Nẵng • 156 TC • 4.5 năm (hệ Kỹ sư)
          </div>
        </div>
      </div>
    </div>

    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(400px,1fr));gap:14px;margin-bottom:18px">
      {"".join(sem_cards)}
    </div>

    <div class="card" style="border-color:#FCD34D">
      <div class="card-h">
        <h2 style="color:#B45309">⭐ HỌC PHẦN TỰ CHỌN — Sinh viên chọn 2/12 học phần (4 TC)</h2>
      </div>
      {elec_rows}
    </div>
    <style>@media(max-width:600px){{main .wrap > div[style*="grid-template-columns:repeat(auto-fill,minmax(400px"]{{grid-template-columns:1fr!important}}}}</style>
    """
    return page("Chương trình đào tạo", body, "chuong-trinh")


@app.route("/gioi-thieu")
def gioi_thieu():
    rows_a = ""
    for label, items in INTRO_INFO["rows_a"]:
        items_html = "".join(f"<div style='margin-bottom:4px'>{t}</div>" for t in items)
        rows_a += f'<div class="info-row"><div class="lb">{label}</div><div class="vl">{items_html}</div></div>'

    mt_items_html = ""
    for badge, txt in INTRO_INFO["mt_items"]:
        mt_items_html += f"""
        <div style="display:flex;gap:14px;padding:12px 0;border-bottom:1px dashed #E2E8F0">
          <div style="background:#16A34A;color:#fff;font-weight:800;font-size:11px;padding:6px 12px;border-radius:8px;flex-shrink:0;height:fit-content">{badge}</div>
          <div style="color:#334155;font-size:15px;line-height:1.75">{txt}</div>
        </div>"""

    plo_items_html = ""
    for badge, txt in INTRO_INFO["plo_items"]:
        plo_items_html += f"""
        <div style="display:flex;gap:14px;padding:12px 0;border-bottom:1px dashed #E2E8F0">
          <div style="background:#D4A000;color:#fff;font-weight:800;font-size:11px;padding:6px 12px;border-radius:8px;flex-shrink:0;height:fit-content">{badge}</div>
          <div style="color:#334155;font-size:15px;line-height:1.75">{txt}</div>
        </div>"""

    body = f"""
    <div class="card" style="background:linear-gradient(135deg,#0033A0,#0D47A1);color:#fff;border:none">
      <div style="display:flex;align-items:center;gap:14px">
        <div style="font-size:42px">🏢</div>
        <div>
          <div style="font-size:22px;font-weight:800">TIN HỌC XÂY DỰNG</div>
          <div style="font-size:13px;color:#D6E4F7;margin-top:4px;font-weight:600">
            Ngành Kỹ thuật Xây dựng • Chuyên ngành Tin học Xây dựng
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-h"><h2>📋 A. THÔNG TIN TỔNG QUÁT</h2></div>
      {rows_a}
    </div>

    <div class="card">
      <div class="card-h"><h2 style="color:#15803D">🎯 B. MỤC TIÊU ĐÀO TẠO</h2></div>
      <div style="font-weight:800;color:#0033A0;font-size:16px;margin-bottom:10px">I. Mục tiêu chung</div>
      <div style="color:#334155;font-size:15.5px;line-height:1.85;padding:18px;background:#F0FDF4;border-radius:10px;border-left:4px solid #16A34A;margin-bottom:18px">
        {INTRO_INFO["mt_general"]}
      </div>
      <div style="font-weight:800;color:#0033A0;font-size:16px;margin-bottom:10px">II. Mục tiêu cụ thể (POs)</div>
      {mt_items_html}
    </div>

    <div class="card">
      <div class="card-h"><h2 style="color:#B45309">✅ C. CHUẨN ĐẦU RA (PLOs)</h2></div>
      <div style="color:#64748B;font-style:italic;font-size:14.5px;margin-bottom:14px">Người học tốt nghiệp CTĐT có khả năng:</div>
      {plo_items_html}
    </div>

    <div class="card">
      <div class="card-h"><h2 style="color:#DC2626">💼 D. CƠ HỘI NGHỀ NGHIỆP</h2></div>
      <div style="color:#334155;font-size:15.5px;line-height:1.9;padding-left:8px">
        <div style="padding:10px 0"><b style="color:#0033A0">🏗 Tư vấn - Thiết kế - Thi công:</b> Cán bộ tư vấn, thiết kế, thi công các công trình xây dựng trong nước và quốc tế.</div>
        <div style="padding:10px 0"><b style="color:#0033A0">📋 Quản lý dự án - Nhà nước:</b> Cán bộ kỹ thuật tại các Ban quản lý dự án, Sở Ban ngành.</div>
        <div style="padding:10px 0"><b style="color:#0033A0">💻 Công nghệ thông tin trong Xây dựng:</b> Cán bộ kỹ thuật tại các công ty phát triển và ứng dụng CNTT trong xây dựng.</div>
        <div style="padding:10px 0"><b style="color:#0033A0">🎓 Giảng dạy - Nghiên cứu:</b> Tham gia giảng dạy, nghiên cứu tại các cơ sở giáo dục, viện nghiên cứu.</div>
        <div style="padding:10px 0"><b style="color:#0033A0">📚 Học lên Thạc sĩ - Tiến sĩ:</b> Có thể dự tuyển chương trình đào tạo thạc sĩ và tiến sĩ cùng ngành.</div>
      </div>
    </div>

    <style>@media(max-width:700px){{
      main .wrap > div[style*="grid-template-columns:280px 1fr"]{{grid-template-columns:1fr!important}}
    }}</style>
    """
    return page("Tin học Xây dựng", body, "gioi-thieu")


@app.route("/community")
def community():
    links = [
        {"title": "Cổng Thông Tin Sinh Viên (CISP)", "desc": "Truy cập Web Portal qua DuckDNS để tra cứu điểm.", "icon": "🌐", "url": "http://thxd-xd-dut.duckdns.org:5000", "color": "#0033A0"},
        {"title": "Nhóm Zalo Lớp 26THXD1", "desc": "Nơi thông báo lịch thi, lịch học và nộp bài tập.", "icon": "💬", "url": "https://zalo.me/g/abcxyz", "color": "#0068FF"},
        {"title": "Group Facebook Tin học Xây dựng", "desc": "Chia sẻ tài liệu, hỏi đáp bài tập, trao đổi kinh nghiệm.", "icon": "📘", "url": "https://facebook.com/groups/abcxyz", "color": "#1877F2"},
        {"title": "Kho Code & Đồ án (Github)", "desc": "Lưu trữ source code các môn học, đồ án mẫu của lớp.", "icon": "🐙", "url": "https://github.com/abcxyz", "color": "#24292F"},
        {"title": "Kênh Bài giảng (Youtube)", "desc": "Video bài giảng, hướng dẫn đồ án từ Giảng viên và sinh viên.", "icon": "▶️", "url": "https://youtube.com/@abcxyz", "color": "#FF0000"},
    ]
    
    cards_html = ""
    for link in links:
        cards_html += f'''
        <div class="card" style="border-left:6px solid {link['color']}; display:flex; align-items:center; gap:20px; transition:transform 0.2s;" onmouseover="this.style.transform='translateY(-3px)'" onmouseout="this.style.transform='translateY(0)'">
            <div style="font-size:42px">{link['icon']}</div>
            <div style="flex:1">
                <div style="font-weight:800; font-size:18px; color:#0F172A; margin-bottom:6px">{link['title']}</div>
                <div style="font-size:14px; color:#64748B; line-height:1.6">{link['desc']}</div>
            </div>
            <a href="{link['url']}" target="_blank" style="background:{link['color']}; color:#fff; padding:12px 24px; border-radius:10px; text-decoration:none; font-weight:800; font-size:14px; white-space:nowrap; box-shadow:0 4px 12px {link['color']}40">Tham gia ngay</a>
        </div>'''

    body = f'''
    <div class="card" style="background:linear-gradient(135deg,#0033A0,#0D47A1);color:#fff;border:none;margin-bottom:24px">
      <div style="display:flex;align-items:center;gap:14px">
        <div style="font-size:42px">🌐</div>
        <div>
          <div style="font-size:24px;font-weight:800">CỘNG ĐỒNG SINH VIÊN</div>
          <div style="font-size:14px;color:#D6E4F7;margin-top:4px;font-weight:600">
            Kết nối - Chia sẻ - Cùng nhau phát triển
          </div>
        </div>
      </div>
    </div>
    
    <div style="display:grid; gap:16px;">
        {cards_html}
    </div>
    
    <div class="tbox" style="margin-top:24px">
        <span>💡 <b>Lưu ý:</b> Hãy sử dụng email trường cấp để tham gia các nhóm kín, đảm bảo quy định bảo mật của Khoa và Nhà trường.</span>
    </div>
    '''
    return page("Cộng đồng", body, "community")

if __name__ == "__main__":
    print()
    print("=" * 52)
    print("  CISP PORTAL — Web server")
    print("=" * 52)
    print(f"  URL    : http://localhost:5000")
    print(f"  File SV: {_find_students_file().name}")
    print(f"  Số SV  : {len(load_students())}")
    print("=" * 52)
    print()
    app.run(host="0.0.0.0", port=5000, debug=False)
