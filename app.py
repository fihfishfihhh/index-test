from flask import Flask, jsonify, request, render_template, send_file
from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequest
import os, sqlite3, json, hashlib, time
from datetime import datetime, timedelta
from pathlib import Path

from config import APP_CONFIG
from database import init_db, get_db_connection, ensure_user_schema

app = Flask(__name__)
app.config.update(
    SECRET_KEY=APP_CONFIG["SECRET_KEY"],
    MAX_CONTENT_LENGTH=APP_CONFIG["MAX_UPLOAD_SIZE"],
)

UPLOAD_FOLDER = APP_CONFIG["UPLOAD_FOLDER"]
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def current_vn_time():
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")


def require_dev_key():
    key = request.headers.get("X-Dev-Key") or request.args.get("dev_key") or request.form.get("dev_key")
    if key != APP_CONFIG["DEV_KEY"]:
        return False
    return True


def json_response(data, status=200):
    return jsonify(data), status


def save_log(action, student_name, book_name, details):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO logs (action, student_name, book_name, details, created_at) VALUES (?, ?, ?, ?, ?)",
        (action, student_name, book_name, json.dumps(details, ensure_ascii=False), current_vn_time()),
    )
    conn.commit()
    conn.close()


def get_student_by_name(name):
    conn = get_db_connection()
    row = conn.execute(
        "SELECT * FROM students WHERE LOWER(name) = LOWER(?) LIMIT 1",
        (name,),
    ).fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)


def get_book_by_code(code):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM books WHERE UPPER(code) = UPPER(?) LIMIT 1", (code,)).fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)


def normalize_student_name(value):
    value = (value or "").strip()
    if not value:
        return ""
    return " ".join(value.split())


def validate_image_upload(file):
    if file is None:
        return None, "Thiếu file ảnh."
    filename = secure_filename(file.filename or "")
    if not filename:
        return None, "Tên file không hợp lệ."
    ext = os.path.splitext(filename)[1].lower()
    if ext not in APP_CONFIG["ALLOWED_EXTENSIONS"]:
        return None, "Chỉ chấp nhận ảnh JPEG/PNG/WebP."
    if file.content_length and file.content_length > APP_CONFIG["MAX_UPLOAD_SIZE"]:
        return None, "File quá lớn."
    if file.stream and file.stream.seekable():
        file.stream.seek(0, os.SEEK_END)
        size = file.stream.tell()
        file.stream.seek(0)
        if size > APP_CONFIG["MAX_UPLOAD_SIZE"]:
            return None, "Dung lượng file vượt giới hạn."
    return filename, None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health")
def health():
    return json_response({"ok": True, "ts": current_vn_time()})


@app.route("/api/config")
def config_api():
    return json_response({
        "loan_days": APP_CONFIG["LOAN_DAYS"],
        "max_books_per_student": APP_CONFIG["MAX_BOOKS_PER_STUDENT"],
        "face_confidence_threshold": APP_CONFIG["FACE_CONFIDENCE_THRESHOLD"],
        "face_size_threshold": APP_CONFIG["FACE_SIZE_THRESHOLD"],
        "liveness_actions": APP_CONFIG["LIVENESS_ACTIONS"],
        "time_zone": APP_CONFIG["TIME_ZONE"],
    })


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    key = str(data.get("key") or "")
    ok = key == APP_CONFIG["DEV_KEY"]
    if not ok:
        return json_response({"ok": False, "message": "Khóa dev không đúng."}, 401)
    return json_response({"ok": True, "message": "Đăng nhập thành công."})


@app.route("/api/student-search")
def api_student_search():
    name = normalize_student_name(request.args.get("name", ""))
    if not name:
        return json_response({"items": []})
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT * FROM students WHERE LOWER(name) LIKE LOWER(?) ORDER BY created_at DESC LIMIT 20",
        (f"%{name}%",),
    ).fetchall()
    conn.close()
    items = []
    for row in rows:
        student = dict(row)
        student["borrowed_books"] = []
        items.append(student)
    return json_response({"items": items})


@app.route("/api/student-detail")
def api_student_detail():
    name = normalize_student_name(request.args.get("name", ""))
    if not name:
        return json_response({"student": None, "borrowed": [], "overdue": []})
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM students WHERE LOWER(name) = LOWER(?) LIMIT 1", (name,)).fetchone()
    if not row:
        conn.close(); return json_response({"student": None, "borrowed": [], "overdue": []})
    student = dict(row)
    loans = conn.execute(
        "SELECT l.*, b.title AS book_title, b.code AS book_code FROM loans l JOIN books b ON b.id = l.book_id WHERE l.student_id = ? AND l.returned_at IS NULL ORDER BY l.borrowed_at DESC",
        (student["id"],),
    ).fetchall()
    conn.close()
    overdue = []
    borrowed = []
    for loan in loans:
        loan_dict = dict(loan)
        loan_dict["is_overdue"] = bool(loan_dict["due_at"] and loan_dict["due_at"] < current_vn_time())
        if loan_dict["is_overdue"]:
            overdue.append(loan_dict)
        borrowed.append(loan_dict)
    return json_response({"student": student, "borrowed": borrowed, "overdue": overdue})


@app.route("/api/books")
def api_books():
    query = request.args.get("q", "").strip()
    conn = get_db_connection()
    if query:
        rows = conn.execute(
            "SELECT * FROM books WHERE LOWER(title) LIKE LOWER(?) OR UPPER(code) LIKE UPPER(?) ORDER BY title LIMIT 50",
            (f"%{query}%", f"%{query}%"),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM books ORDER BY title LIMIT 50").fetchall()
    books = []
    for row in rows:
        item = dict(row)
        item["available_qty"] = item["available_qty"] if item["available_qty"] is not None else 0
        books.append(item)
    conn.close()
    return json_response({"items": books})


@app.route("/api/books", methods=["POST"])
def api_add_book():
    if not require_dev_key():
        return json_response({"ok": False, "message": "Không có quyền dev."}, 401)
    data = request.get_json(silent=True) or {}
    code = (data.get("code") or "").strip()
    title = (data.get("title") or "").strip()
    quantity = int(data.get("quantity") or 0)
    if not code or not title or quantity <= 0:
        return json_response({"ok": False, "message": "Thiếu mã sách, tên sách hoặc số lượng hợp lệ."}, 400)

    conn = get_db_connection()
    existing = conn.execute("SELECT * FROM books WHERE UPPER(code)=UPPER(?) LIMIT 1", (code,)).fetchone()
    if existing:
        conn.execute(
            "UPDATE books SET title=?, available_qty=available_qty+?, updated_at=? WHERE id=?",
            (title, quantity, current_vn_time(), existing["id"]),
        )
        conn.commit(); conn.close(); save_log("book_update", "dev", title, {"code": code, "quantity_added": quantity})
        return json_response({"ok": True, "message": "Đã cập nhật số lượng."})

    conn.execute(
        "INSERT INTO books (code, title, available_qty, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        (code, title, quantity, current_vn_time(), current_vn_time()),
    )
    conn.commit(); conn.close(); save_log("book_add", "dev", title, {"code": code, "quantity": quantity})
    return json_response({"ok": True, "message": "Đã thêm sách."})


@app.route("/api/students/register", methods=["POST"])
def api_register_student():
    if not require_dev_key():
        return json_response({"ok": False, "message": "Không có quyền dev."}, 401)
    data = request.get_json(silent=True) or {}
    name = normalize_student_name(data.get("name"))
    class_name = (data.get("class_name") or "").strip()
    face_descriptors = data.get("face_descriptors") or []
    if not name:
        return json_response({"ok": False, "message": "Tên học sinh bắt buộc."}, 400)
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM students WHERE LOWER(name)=LOWER(?) LIMIT 1", (name,)).fetchone()
    if row:
        student_id = row["id"]
        if face_descriptors:
            existing = row["face_descriptors"] or "[]"
            try:
                arr = json.loads(existing)
            except Exception:
                arr = []
            arr.extend(face_descriptors)
            conn.execute(
                "UPDATE students SET class_name=?, face_descriptors=?, updated_at=? WHERE id=?",
                (class_name, json.dumps(arr, ensure_ascii=False), current_vn_time(), student_id),
            )
    else:
        cursor = conn.execute(
            "INSERT INTO students (name, class_name, face_descriptors, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (name, class_name, json.dumps(face_descriptors, ensure_ascii=False), current_vn_time(), current_vn_time()),
        )
        student_id = cursor.lastrowid
    conn.commit(); conn.close(); save_log("student_register", name, "", {"class_name": class_name, "face_count": len(face_descriptors)})
    return json_response({"ok": True, "message": "Đã lưu khuôn mặt."})


@app.route("/api/upload-image", methods=["POST"])
def api_upload_image():
    if not require_dev_key():
        return json_response({"ok": False, "message": "Không có quyền dev."}, 401)
    if "file" not in request.files:
        return json_response({"ok": False, "message": "Thiếu file ảnh."}, 400)
    file = request.files["file"]
    filename, err = validate_image_upload(file)
    if err:
        return json_response({"ok": False, "message": err}, 400)
    safe_name = secure_filename(filename)
    unique = f"{int(time.time()*1000)}_{safe_name}"
    path = os.path.join(app.config["UPLOAD_FOLDER"], unique)
    file.save(path)
    return json_response({"ok": True, "filename": unique, "url": f"/uploads/{unique}"})


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_file(os.path.join(APP_CONFIG["UPLOAD_FOLDER"], filename), conditional=True)


@app.route("/api/scan", methods=["POST"])
def api_scan():
    data = request.get_json(silent=True) or {}
    student_name = normalize_student_name(data.get("student_name"))
    book_code = (data.get("book_code") or "").strip()
    action_type = (data.get("action_type") or "borrow").strip()
    face_confidence = float(data.get("face_confidence") or 0)
    face_size = float(data.get("face_size") or 0)
    nearby_face_count = int(data.get("nearby_face_count") or 0)
    liveness_ok = bool(data.get("liveness_ok"))
    challenge_nonce = str(data.get("challenge_nonce") or "")
    session_key = str(data.get("session_key") or "")
    device_fps = int(data.get("device_fps") or 0)

    if not student_name:
        return json_response({"ok": False, "status": "invalid", "message": "KHÔNG HỢP LỆ: thiếu tên học sinh."}, 400)
    if not book_code:
        return json_response({"ok": False, "status": "invalid", "message": "KHÔNG HỢP LỆ: thiếu mã sách."}, 400)

    student = get_student_by_name(student_name)
    if not student:
        return json_response({"ok": False, "status": "invalid", "message": "KHÔNG HỢP LỆ: học sinh chưa được lưu khuôn mặt."}, 400)

    if face_confidence < APP_CONFIG["FACE_CONFIDENCE_THRESHOLD"]:
        return json_response({"ok": False, "status": "invalid", "message": "KHÔNG HỢP LỆ: độ tin cậy khuôn mặt thấp; đến gần hơn."})
    if face_size < APP_CONFIG["FACE_SIZE_THRESHOLD"]:
        return json_response({"ok": False, "status": "invalid", "message": "KHÔNG HỢP LỆ: khuôn mặt quá nhỏ; đến gần hơn."})
    if nearby_face_count > 1:
        return json_response({"ok": False, "status": "invalid", "message": "KHÔNG HỢP LỆ: phát hiện nhiều khuôn mặt, chỉ xét người gần nhất."})
    if not liveness_ok:
        return json_response({"ok": False, "status": "invalid", "message": "KHÔNG HỢP LỆ: chưa qua kiểm tra chống mạo danh."})
    if not challenge_nonce:
        return json_response({"ok": False, "status": "invalid", "message": "KHÔNG HỢP LỆ: thiếu nonce an toàn."})

    book = get_book_by_code(book_code)
    if not book:
        return json_response({"ok": False, "status": "invalid", "message": "KHÔNG HỢP LỆ: mã sách không tồn tại trong kho."})

    conn = get_db_connection()
    current_loans = conn.execute(
        "SELECT COUNT(*) FROM loans WHERE student_id=? AND returned_at IS NULL",
        (student["id"],),
    ).fetchone()[0]
    overdue = conn.execute(
        "SELECT COUNT(*) FROM loans WHERE student_id=? AND returned_at IS NULL AND due_at < ?",
        (student["id"], current_vn_time()),
    ).fetchone()[0]
    conn.close()

    if overdue > 0:
        return json_response({"ok": False, "status": "invalid", "message": "KHÔNG HỢP LỆ: học sinh có sách quá hạn."})
    if action_type == "borrow" and current_loans >= APP_CONFIG["MAX_BOOKS_PER_STUDENT"]:
        return json_response({"ok": False, "status": "invalid", "message": "KHÔNG HỢP LỆ: đã đạt tối đa số cuốn được mượn."})

    if action_type == "borrow":
        if int(book["available_qty"]) <= 0:
            return json_response({"ok": False, "status": "invalid", "message": "KHÔNG HỢP LỆ: sách đã hết trong kho."})
        due_at = (datetime.now() + timedelta(days=APP_CONFIG["LOAN_DAYS"])).strftime("%Y-%m-%d %H:%M:%S")
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO loans (student_id, book_id, borrowed_at, due_at, returned_at, created_at) VALUES (?, ?, ?, ?, NULL, ?)",
            (student["id"], book["id"], current_vn_time(), due_at, current_vn_time()),
        )
        conn.execute("UPDATE books SET available_qty = available_qty - 1, updated_at = ? WHERE id = ?", (current_vn_time(), book["id"]))
        conn.commit(); conn.close()
        save_log("borrow", student_name, book["title"], {"book_code": book_code, "device_fps": device_fps, "nonce": challenge_nonce})
        return json_response({"ok": True, "status": "valid", "message": "HỢP LỆ: mượn sách thành công."})

    if action_type == "return":
        conn = get_db_connection()
        loan = conn.execute(
            "SELECT * FROM loans WHERE student_id=? AND book_id=? AND returned_at IS NULL ORDER BY borrowed_at DESC LIMIT 1",
            (student["id"], book["id"]),
        ).fetchone()
        if not loan:
            conn.close(); return json_response({"ok": False, "status": "invalid", "message": "KHÔNG HỢP LỆ: không có khoản mượn tương ứng."})
        conn.execute(
            "UPDATE loans SET returned_at=?, updated_at=? WHERE id=?",
            (current_vn_time(), current_vn_time(), loan["id"]),
        )
        conn.execute("UPDATE books SET available_qty = available_qty + 1, updated_at = ? WHERE id = ?", (current_vn_time(), book["id"]))
        conn.commit(); conn.close()
        save_log("return", student_name, book["title"], {"book_code": book_code, "device_fps": device_fps, "nonce": challenge_nonce})
        return json_response({"ok": True, "status": "valid", "message": "HỢP LỆ: trả sách thành công."})

    return json_response({"ok": False, "status": "invalid", "message": "KHÔNG HỢP LỆ: thao tác không hợp lệ."})


@app.route("/api/logs")
def api_logs():
    if not require_dev_key():
        return json_response({"ok": False, "message": "Không có quyền dev."}, 401)
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM logs ORDER BY created_at DESC LIMIT 100").fetchall()
    conn.close()
    return json_response({"items": [dict(r) for r in rows]})


@app.route("/api/export-log")
def api_export_log():
    if not require_dev_key():
        return json_response({"ok": False, "message": "Không có quyền dev."}, 401)
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM logs ORDER BY created_at DESC").fetchall()
    conn.close()
    payload = [{"id": r["id"], "action": r["action"], "student_name": r["student_name"], "book_name": r["book_name"], "details": json.loads(r["details"] or "{}"), "created_at": r["created_at"]} for r in rows]
    export_path = os.path.join(APP_CONFIG["EXPORT_FOLDER"], "library-log.json")
    os.makedirs(APP_CONFIG["EXPORT_FOLDER"], exist_ok=True)
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return send_file(export_path, as_attachment=True, download_name="library-log.json")


@app.route("/api/backup")
def api_backup():
    if not require_dev_key():
        return json_response({"ok": False, "message": "Không có quyền dev."}, 401)
    export_path = os.path.join(APP_CONFIG["EXPORT_FOLDER"], "backup.sqlite")
    os.makedirs(APP_CONFIG["EXPORT_FOLDER"], exist_ok=True)
    db_path = APP_CONFIG["DB_PATH"]
    import shutil
    shutil.copy2(db_path, export_path)
    return json_response({"ok": True, "path": export_path, "message": "Đã sao lưu cơ sở dữ liệu."})


@app.route("/api/restore", methods=["POST"])
def api_restore():
    if not require_dev_key():
        return json_response({"ok": False, "message": "Không có quyền dev."}, 401)
    if "file" not in request.files:
        return json_response({"ok": False, "message": "Thiếu file sao lưu."}, 400)
    file = request.files["file"]
    file_name = secure_filename(file.filename or "")
    if not file_name.endswith(".sqlite"):
        return json_response({"ok": False, "message": "File sao lưu phải .sqlite."}, 400)
    dest = APP_CONFIG["DB_PATH"]
    file.save(dest)
    init_db()
    return json_response({"ok": True, "message": "Đã phục hồi dữ liệu từ file sao lưu."})


@app.errorhandler(404)
def not_found(_):
    return render_template("index.html"), 404


if __name__ == "__main__":
    init_db()
    ensure_user_schema()
    app.run(host="0.0.0.0", port=5000, debug=True)

































































































































































































































