from io import BytesIO  # 新增
import openpyxl  # 新增
import os
import sys
import csv
import openpyxl  # 處理 Excel 的核心
from io import BytesIO, TextIOWrapper  # <--- 把這兩個寫在一起
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


@app.route('/api/records/import', methods=['POST'])
def import_records():
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 403

    file = request.files.get('file')
    if not file:
        return jsonify({"error": "未選取檔案"}), 400

    filename = file.filename.lower()
    all_new_records = []

    try:
        # --- 處理 Excel (.xlsx) ---
        if filename.endswith('.xlsx'):
            wb = openpyxl.load_workbook(BytesIO(file.read()), data_only=True)
            for sheet in wb.worksheets:
                rows = list(sheet.rows)
                if not rows:
                    continue

                header_row = [str(cell.value).strip()
                              if cell.value else "" for cell in rows[0]]

                idx_id = header_row.index("編號") if "編號" in header_row else -1
                idx_name = -1
                for n in ["姓名", "信眾姓名"]:
                    if n in header_row:
                        idx_name = header_row.index(n)
                        break
                idx_amount = header_row.index(
                    "金額") if "金額" in header_row else -1
                idx_altar = header_row.index(
                    "壇名") if "壇名" in header_row else -1

                if -1 in [idx_id, idx_name, idx_amount, idx_altar]:
                    continue

                current_main = None
                for row_data in rows[1:]:
                    raw_id = str(row_data[idx_id].value).strip(
                    ) if row_data[idx_id].value is not None else ""
                    name = str(row_data[idx_name].value).strip(
                    ) if row_data[idx_name].value is not None else ""
                    altar = str(row_data[idx_altar].value).strip(
                    ) if row_data[idx_altar].value is not None else ""

                    amt_val = str(row_data[idx_amount].value).replace(
                        ',', '') if row_data[idx_amount].value is not None else "0"
                    amount = int(float(amt_val)) if amt_val.replace(
                        '.', '').isdigit() else 0

                    if not raw_id or not name:
                        continue

                    is_sub = "." in raw_id and not raw_id.endswith(".0")

                    if not is_sub:
                        if current_main:
                            all_new_records.append(current_main)
                        current_main = {
                            "names": [name], "amount": amount, "altar": altar}
                    else:
                        if current_main:
                            current_main["names"].append(name)

                if current_main:
                    all_new_records.append(current_main)

        # --- 處理 CSV (.csv) ---
        elif filename.endswith('.csv'):
            file_content = file.read().decode('utf-8-sig')  # 處理 BOM 問題
            reader = csv.reader(file_content.splitlines())

            # 讀取標頭並清理空白
            header = [h.strip() for h in next(reader)]

            idx_id = header.index("編號") if "編號" in header else -1
            idx_name = -1
            for n in ["姓名", "信眾姓名"]:
                if n in header:
                    idx_name = header.index(n)
                    break
            idx_amount = header.index("金額") if "金額" in header else -1
            idx_altar = header.index("壇名") if "壇名" in header else -1

            if -1 not in [idx_id, idx_name, idx_amount, idx_altar]:
                current_main = None
                for row_data in reader:
                    # 如果該行為空或欄位不足，則跳過
                    if len(row_data) < max(idx_id, idx_name, idx_amount, idx_altar) + 1:
                        continue

                    raw_id = str(row_data[idx_id]).strip()
                    name = str(row_data[idx_name]).strip()
                    altar = str(row_data[idx_altar]).strip()

                    amt_val = str(row_data[idx_amount]).replace(',', '')
                    amount = int(float(amt_val)) if amt_val.replace(
                        '.', '').isdigit() else 0

                    if not raw_id or not name:
                        continue

                    # 子編號合併邏輯
                    is_sub = "." in raw_id and not raw_id.endswith(".0")

                    if not is_sub:
                        if current_main:
                            all_new_records.append(current_main)
                        # 如果是匯出的 CSV，姓名可能已經是用空格隔開的多人，這裡直接當作單一名稱存入（後續寫入資料庫會再處理）
                        current_main = {
                            "names": [name], "amount": amount, "altar": altar}
                    else:
                        if current_main:
                            current_main["names"].append(name)

                if current_main:
                    all_new_records.append(current_main)

        # --- 統一寫入資料庫 ---
        if all_new_records:
            LightRecord.query.delete()  # 覆蓋模式
            for r in all_new_records:
                # 把陣列裡的姓名用分號合併，如果原本裡面就有空格也會保留
                final_names = ",".join(r["names"])
                # 這裡再將系統匯出時使用的空格，轉換為內部儲存用的分號，確保跨系統一致性
                final_names = final_names.replace(" ", ";")

                db.session.add(LightRecord(
                    names=final_names,
                    amount=r["amount"],
                    altar_name=r["altar"]
                ))
            db.session.commit()
            return jsonify({"success": True, "count": len(all_new_records)})
        else:
            return jsonify({"error": "找不到符合格式的資料，請檢查標頭名稱是否包含：編號、姓名、金額、壇名"}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"匯入崩潰: {str(e)}"}), 500
