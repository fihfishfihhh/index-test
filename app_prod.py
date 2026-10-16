# Production-ready Flask app with nonce/challenge and server-side verification
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os, json, time, secrets
from datetime import datetime, timedelta
from pathlib import Path

# Use SQLAlchemy so we can switch between SQLite and Postgres via DATABASE_URL
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

BASE_DIR = Path(__file__).parent

def now_str():
    return datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S')

# Config from env
API_ORIGINS = os.environ.get('API_ORIGINS', 'https://fihfishfihhh.github.io')
DATABASE_URL = os.environ.get('DATABASE_URL') or f'sqlite:///{str(BASE_DIR / "data" / "library.db")}'
DEV_KEY = os.environ.get('DEV_KEY','dev-secret-2026')
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', str(BASE_DIR / 'uploads'))
EXPORT_FOLDER = os.environ.get('EXPORT_FOLDER', str(BASE_DIR / 'exports'))
FACE_CONF_THRESHOLD = float(os.environ.get('FACE_CONF_THRESHOLD', '10'))
FACE_SIZE_THRESHOLD = float(os.environ.get('FACE_SIZE_THRESHOLD','10'))
LOAN_DAYS = int(os.environ.get('LOAN_DAYS','5'))
MAX_BOOKS = int(os.environ.get('MAX_BOOKS','3'))

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXPORT_FOLDER, exist_ok=True)

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app, origins=[orig.strip() for orig in API_ORIGINS.split(',')])

engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False} if DATABASE_URL.startswith('sqlite') else {})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# DB models
class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    class_name = Column(String)
    # store descriptors as JSON list of lists
    descriptors = Column(Text, default='[]')
    created_at = Column(String, default=now_str)

class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    available = Column(Integer, default=0)
    created_at = Column(String, default=now_str)

class Loan(Base):
    __tablename__ = 'loans'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer)
    book_id = Column(Integer)
    borrowed_at = Column(String)
    due_at = Column(String)
    returned_at = Column(String, nullable=True)
    created_at = Column(String, default=now_str)

class Log(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    action = Column(String)
    actor = Column(String)
    book = Column(String)
    details = Column(Text)
    created_at = Column(String, default=now_str)

class Nonce(Base):
    __tablename__ = 'nonces'
    id = Column(Integer, primary_key=True)
    nonce = Column(String, unique=True)
    action = Column(String)
    created_at = Column(String, default=now_str)
    used = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

# Utility
def db_session():
    return SessionLocal()

def require_dev_key(req):
    key = req.headers.get('X-Dev-Key') or req.args.get('dev_key') or (req.json or {}).get('dev_key')
    return key == DEV_KEY

@app.route('/')
def index():
    return send_file('docs/index.html')

@app.route('/api/health')
def health():
    return jsonify({'ok':True,'ts':now_str()})

@app.route('/api/nonce', methods=['POST'])
def api_nonce():
    # create a one-time nonce for a challenge; dev/client can request
    data = request.get_json() or {}
    action = data.get('action','scan')
    n = secrets.token_urlsafe(16)
    db = db_session()
    rec = Nonce(nonce=n, action=action, created_at=now_str(), used=False)
    db.add(rec); db.commit(); db.close()
    return jsonify({'ok':True,'nonce':n})

@app.route('/api/register-student', methods=['POST'])
def api_register_student():
    if not require_dev_key(request): return jsonify({'ok':False,'msg':'no dev key'}),401
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    class_name = (data.get('class_name') or '').strip()
    descriptors = data.get('descriptors') or []
    if not name: return jsonify({'ok':False,'msg':'name required'}),400
    db = db_session()
    s = Student(name=name, class_name=class_name, descriptors=json.dumps(descriptors, ensure_ascii=False), created_at=now_str())
    try:
        db.add(s); db.commit(); db.close();
        log('student_register','dev',name,{'count':len(descriptors)})
        return jsonify({'ok':True})
    except IntegrityError:
        db.rollback(); db.close(); return jsonify({'ok':False,'msg':'exists'}),409

@app.route('/api/add-book', methods=['POST'])
def api_add_book():
    if not require_dev_key(request): return jsonify({'ok':False,'msg':'no dev key'}),401
    data = request.get_json() or {}
    code = (data.get('code') or '').strip()
    title = (data.get('title') or '').strip()
    qty = int(data.get('quantity') or 0)
    if not code or not title or qty<=0: return jsonify({'ok':False,'msg':'bad params'}),400
    db = db_session()
    b = db.query(Book).filter(Book.code==code).first()
    if b:
        b.available = b.available + qty; db.commit(); db.close(); log('book_update','dev',title,{'code':code,'add':qty}); return jsonify({'ok':True,'msg':'updated'})
    nb = Book(code=code,title=title,available=qty,created_at=now_str())
    db.add(nb); db.commit(); db.close(); log('book_add','dev',title,{'code':code,'qty':qty}); return jsonify({'ok':True})

@app.route('/api/books')
def api_books():
    q = (request.args.get('q') or '').strip().lower()
    db = db_session()
    if q:
        rows = db.query(Book).filter((Book.title.ilike(f'%{q}%')) | (Book.code.ilike(f'%{q}%'))).limit(50).all()
    else:
        rows = db.query(Book).limit(50).all()
    db.close()
    return jsonify({'items':[{'code':r.code,'title':r.title,'available':r.available} for r in rows]})

@app.route('/api/student-search')
def api_student_search():
    q = (request.args.get('name') or '').strip()
    db = db_session()
    rows = db.query(Student).filter(Student.name.ilike(f'%{q}%')).limit(20).all() if q else []
    out = [{'name':r.name,'class':r.class_name} for r in rows]
    db.close(); return jsonify({'items':out})

@app.route('/api/student-detail')
def api_student_detail():
    name = (request.args.get('name') or '').strip()
    db = db_session()
    s = db.query(Student).filter(Student.name==name).first()
    if not s: db.close(); return jsonify({'student':None,'borrowed':[],'overdue':[]})
    loans = db.query(Loan).filter(Loan.student_id==s.id, Loan.returned_at==None).all()
    borrowed = []
    overdue = []
    for l in loans:
        book = db.query(Book).filter(Book.id==l.book_id).first()
        item = {'book': book.title if book else '', 'due': l.due_at}
        borrowed.append(item)
        if l.due_at and datetime.fromisoformat(l.due_at) < datetime.now(): overdue.append(item)
    db.close(); return jsonify({'student':{'name':s.name,'class':s.class_name}, 'borrowed':borrowed, 'overdue':overdue})

@app.route('/api/nonce/verify', methods=['POST'])
def api_verify_nonce():
    data = request.get_json() or {}
    nonce = data.get('nonce')
    db = db_session(); rec = db.query(Nonce).filter(Nonce.nonce==nonce, Nonce.used==False).first()
    if not rec: db.close(); return jsonify({'ok':False,'msg':'invalid nonce'}),400
    rec.used = True; db.commit(); db.close(); return jsonify({'ok':True})

# scanning endpoint: expects student_name, book_code, descriptor (list), nonce
@app.route('/api/scan', methods=['POST'])
def api_scan():
    data = request.get_json() or {}
    student_name = (data.get('student_name') or '').strip()
    book_code = (data.get('book_code') or '').strip()
    descriptor = data.get('descriptor')
    client_conf = float(data.get('face_confidence') or 0)
    nonce = data.get('nonce')
    # basic validation
    if not student_name or not book_code or not descriptor or not nonce:
        return jsonify({'ok':False,'status':'invalid','message':'Thiếu thông tin'}),400
    # verify nonce
    db = db_session(); nrec = db.query(Nonce).filter(Nonce.nonce==nonce, Nonce.used==False).first()
    if not nrec: db.close(); return jsonify({'ok':False,'status':'invalid','message':'Nonce không hợp lệ'}),400
    # mark used
    nrec.used=True; db.commit()
    # find student
    s = db.query(Student).filter(Student.name==student_name).first()
    if not s: db.close(); return jsonify({'ok':False,'status':'invalid','message':'Học sinh chưa đăng ký'}),400
    # match descriptor server-side: iterate stored descriptors and compute euclidean distance
    try:
        stored = json.loads(s.descriptors or '[]')
    except Exception:
        stored = []
    def euclid(a,b):
        ssum=0.0
        for i in range(min(len(a),len(b))): ssum += (a[i]-b[i])**2
        return ssum**0.5
    best = None; bestd = 1e9
    for d in stored:
        dval = euclid(d, descriptor)
        if dval < bestd: bestd = dval; best = d
    # threshold: accept if bestd < 0.6 (tuneable)
    if best is None or bestd>0.6:
        db.close(); log('scan_fail', student_name, book_code, {'reason':'descriptor_mismatch','d':bestd}); return jsonify({'ok':False,'status':'invalid','message':'KHÔNG HỢP LỆ: không khớp khuôn mặt'}),400
    # check book
    book = db.query(Book).filter(Book.code.ilike(book_code)).first()
    if not book: db.close(); log('scan_fail', student_name, book_code, {'reason':'no_book'}); return jsonify({'ok':False,'status':'invalid','message':'KHÔNG HỢP LỆ: sách không tồn tại'}),400
    # check overdue
    loans = db.query(Loan).filter(Loan.student_id==s.id, Loan.returned_at==None).all()
    overdue = [l for l in loans if l.due_at and datetime.fromisoformat(l.due_at) < datetime.now()]
    if overdue: db.close(); log('blocked_overdue', student_name, book.code, {}); return jsonify({'ok':False,'status':'invalid','message':'KHÔNG HỢP LỆ: có sách quá hạn'}),400
    if data.get('action')=='borrow' or data.get('action')=='mượn' or data.get('action')=='muon':
        if len(loans) >= MAX_BOOKS: db.close(); log('blocked_limit', student_name, book.code, {}); return jsonify({'ok':False,'status':'invalid','message':'KHÔNG HỢP LỆ: đã đạt tối đa số cuốn'}),400
        if book.available <= 0: db.close(); log('no_qty', student_name, book.code, {}); return jsonify({'ok':False,'status':'invalid','message':'KHÔNG HỢP LỆ: sách đã hết'}),400
        due = (datetime.now() + timedelta(days=LOAN_DAYS)).isoformat()
        ln = Loan(student_id=s.id, book_id=book.id, borrowed_at=datetime.now().isoformat(), due_at=due, created_at=now_str())
        db.add(ln); book.available = book.available - 1; db.commit(); log('borrow', student_name, book.title, {'nonce':nonce}); db.close(); return jsonify({'ok':True,'status':'valid','message':'HỢP LỆ: mượn sách thành công'})
    else:
        # return
        loan = db.query(Loan).filter(Loan.student_id==s.id, Loan.book_id==book.id, Loan.returned_at==None).order_by(Loan.id.desc()).first()
        if not loan: db.close(); log('no_loan', student_name, book.code, {}); return jsonify({'ok':False,'status':'invalid','message':'KHÔNG HỢP LỆ: không có khoản mượn'})
        loan.returned_at = datetime.now().isoformat(); book.available = book.available + 1; db.commit(); log('return', student_name, book.title, {'nonce':nonce}); db.close(); return jsonify({'ok':True,'status':'valid','message':'HỢP LỆ: trả sách thành công'})

@app.route('/api/logs')
def api_logs():
    if not require_dev_key(request): return jsonify({'ok':False}),401
    db = db_session(); rows = db.query(Log).order_by(Log.id.desc()).limit(200).all(); out=[{'action':r.action,'actor':r.actor,'book':r.book,'details':json.loads(r.details or '{}') if r.details else {},'ts':r.created_at} for r in rows]; db.close(); return jsonify({'items':out})

@app.route('/api/export-logs')
def api_export_logs():
    if not require_dev_key(request): return jsonify({'ok':False}),401
    db = db_session(); rows = db.query(Log).order_by(Log.id.desc()).all(); payload=[{'action':r.action,'actor':r.actor,'book':r.book,'details':json.loads(r.details or '{}') if r.details else {},'ts':r.created_at} for r in rows]; db.close(); path = os.path.join(EXPORT_FOLDER,'library-log.json'); with open(path,'w',encoding='utf-8') as f: json.dump(payload,f,ensure_ascii=False,indent=2); return send_file(path, as_attachment=True)

@app.route('/api/backup-db')
def api_backup_db():
    if not require_dev_key(request): return jsonify({'ok':False}),401
    # if sqlite, copy file; for postgres, instruct admin to use pg_dump (we return not implemented)
    if DATABASE_URL.startswith('sqlite'):
        src = str(BASE_DIR / 'data' / 'library.db')
        dst = os.path.join(EXPORT_FOLDER, 'backup.sqlite')
        from shutil import copy2
        copy2(src,dst)
        return jsonify({'ok':True,'path':dst})
    return jsonify({'ok':False,'msg':'backup not implemented for non-sqlite DB'}),501

# small logging helper
def log(action, actor, book, details):
    db = db_session(); rec = Log(action=action, actor=actor, book=book, details=json.dumps(details, ensure_ascii=False), created_at=now_str()); db.add(rec); db.commit(); db.close()

if __name__=='__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',5000)), debug=False)
