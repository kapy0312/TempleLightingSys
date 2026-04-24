import os
import sys
from flask import Flask, jsonify, request, session, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
    db_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_dir = base_dir

app = Flask(
    __name__,
    template_folder=os.path.join(base_dir, 'templates'),
    static_folder=os.path.join(base_dir, 'static')
)

app.secret_key = 'temple_secret_key_v1'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(db_dir, 'temple_data.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)


class LightRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    names = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    altar_name = db.Column(db.Text, nullable=False)


def init_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            hashed_pw = generate_password_hash('admin123')
            admin_user = User(username='admin', password_hash=hashed_pw)
            db.session.add(admin_user)
            db.session.commit()


init_db()


def is_admin():
    return session.get('logged_in', False)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    return jsonify({"logged_in": is_admin()})


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()
    if user and check_password_hash(user.password_hash, data.get('password')):
        session['logged_in'] = True
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "帳號或密碼錯誤"}), 401


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)
    return jsonify({"success": True})


# [NEW] 合併後的正確邏輯：支援「空搜尋」、「特定搜尋」與「強制全部」
@app.route('/api/records', methods=['GET'])
def get_records():
    search = request.args.get('q', '')
    show_all = request.args.get('all', 'false') == 'true'

    if show_all:
        # 強制顯示全部
        records = LightRecord.query.all()
    elif search:
        # 模糊搜尋
        records = LightRecord.query.filter(
            (LightRecord.names.contains(search)) |
            (LightRecord.altar_name.contains(search))
        ).all()
    else:
        # 初始狀態或空搜尋，回傳空清單（符合 User 需求）
        records = []

    result = [{
        "id": r.id, "names": r.names,
        "amount": r.amount, "altar_name": r.altar_name
    } for r in records]
    return jsonify(result)

# [INSERT] 新增更新 API at line 95
@app.route('/api/records', methods=['POST'])
def add_record():
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    new_record = LightRecord(
        names=data.get('names'),
        amount=data.get('amount'),
        altar_name=data.get('altar_name')
    )
    db.session.add(new_record)
    db.session.commit()
    return jsonify({"success": True, "id": new_record.id})

@app.route('/api/records/<int:record_id>', methods=['PUT'])
def update_record(record_id):
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    record = LightRecord.query.get_or_404(record_id)
    record.names = data.get('names', record.names)
    record.amount = data.get('amount', record.amount)
    record.altar_name = data.get('altar_name', record.altar_name)
    db.session.commit()
    return jsonify({"success": True})


@app.route('/api/records/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 403
    record = LightRecord.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()
    return jsonify({"success": True})
