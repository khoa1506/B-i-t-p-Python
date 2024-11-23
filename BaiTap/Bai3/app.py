from flask import Flask, render_template, request, redirect, url_for, flash, make_response, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import pandas as pd
from io import BytesIO

app = Flask(__name__)
app.secret_key = '123456'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:khoa1598753@localhost/sinhvien'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Cấu hình Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Model cho bảng sinh viên
class DanhSach(db.Model):
    __tablename__ = 'danhsach'
    id = db.Column(db.Integer, primary_key=True)
    MSSV = db.Column(db.String(20), unique=True, nullable=False)
    Hoten = db.Column(db.String(100))
    Nganhhoc = db.Column(db.String(100))

# Model cho bảng người dùng
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Tạo database
with app.app_context():
    db.create_all()

# User loader cho Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def reorder_ids():
    students = DanhSach.query.order_by(DanhSach.id).all()
    for index, student in enumerate(students, start=1):
        student.id = index
    db.session.commit()

# Routes
@app.route('/')
@login_required
def index():
    students = DanhSach.query.order_by(DanhSach.id).all()
    return render_template('index.html', students=students)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Kiểm tra người dùng đã tồn tại
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Tên đăng nhập hoặc email đã tồn tại!', 'error')
            return redirect(url_for('register'))

        # Tạo người dùng mới
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        # Thông báo và chuyển hướng đến trang đăng nhập
        flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng!', 'error')
    return render_template('login.html')




@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Đăng xuất thành công!', 'success')
    return redirect(url_for('login'))


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_student():
    if request.method == 'POST':
        mssv = request.form['mssv']
        hoten = request.form['hoten']
        nganhhoc = request.form['nganhhoc']
        
        existing_student = DanhSach.query.filter_by(MSSV=mssv).first()
        if existing_student:
            flash('MSSV đã tồn tại. Vui lòng nhập MSSV khác.', 'error')
            return redirect(url_for('add_student'))

        new_student = DanhSach(MSSV=mssv, Hoten=hoten, Nganhhoc=nganhhoc)
        db.session.add(new_student)
        db.session.commit()

        reorder_ids()  # Sắp xếp lại ID sau khi thêm
        flash('Thêm sinh viên thành công!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add.html')

@app.route('/edit/<int:student_id>', methods=['GET', 'POST'])
@login_required
def edit_student(student_id):
    student = DanhSach.query.get_or_404(student_id)
    if request.method == 'POST':
        student.MSSV = request.form['mssv']
        student.Hoten = request.form['hoten']
        student.Nganhhoc = request.form['nganhhoc']
        db.session.commit()
        flash('Cập nhật thông tin sinh viên thành công!', 'success')
        return redirect(url_for('index'))
    
    return render_template('edit.html', student=student)

@app.route('/delete/<int:student_id>')
@login_required
def delete_student(student_id):
    student = DanhSach.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()

    reorder_ids()  # Sắp xếp lại ID sau khi xóa
    flash('Xóa sinh viên thành công!', 'success')
    return redirect(url_for('index'))

@app.route('/export/pdf')
@login_required
def export_pdf():
    students = DanhSach.query.all()
    pdf_file = "danh_sach.pdf"
    document = SimpleDocTemplate(pdf_file, pagesize=letter)

    data = [['MSSV', 'Họ Tên', 'Ngành Học']]
    for student in students:
        data.append([student.MSSV, student.Hoten, student.Nganhhoc])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements = [table]
    document.build(elements)

    return send_file(pdf_file, as_attachment=True)


@app.route('/export/excel')
@login_required
def export_excel():
    # Lấy danh sách sinh viên từ cơ sở dữ liệu
    students = DanhSach.query.all()

    # Chuyển đổi dữ liệu thành DataFrame của pandas
    data = {
        'MSSV': [student.MSSV for student in students],
        'Họ Tên': [student.Hoten for student in students],
        'Ngành Học': [student.Nganhhoc for student in students],
    }
    df = pd.DataFrame(data)

    # Tạo file Excel trong bộ nhớ bằng BytesIO
    excel_file = BytesIO()
    df.to_excel(excel_file, index=False, sheet_name='Danh Sách Sinh Viên')

    # Đặt con trỏ trở lại đầu file để gửi tới client
    excel_file.seek(0)

    # Gửi file Excel cho người dùng tải về
    return send_file(
        excel_file,
        as_attachment=True,
        download_name="danh_sach.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if __name__ == '__main__':
    app.run(debug=True)
