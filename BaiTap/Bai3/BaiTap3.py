from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = '123456'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:khoa1598753@localhost/sinhvien'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class DanhSach(db.Model):
    __tablename__ = 'danhsach'
    id = db.Column(db.Integer, primary_key=True)
    MSSV = db.Column(db.String(20), unique=True, nullable=False)
    Hoten = db.Column(db.String(100))
    Nganhhoc = db.Column(db.String(100))

def reorder_ids():
    students = DanhSach.query.order_by(DanhSach.id).all()
    for index, student in enumerate(students, start=1):
        student.id = index
    db.session.commit()

@app.route('/')
def index():
    students = DanhSach.query.order_by(DanhSach.id).all()
    return render_template('index.html', students=students)

@app.route('/add', methods=['GET', 'POST'])
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
def delete_student(student_id):
    student = DanhSach.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()

    reorder_ids()  # Sắp xếp lại ID sau khi xóa
    flash('Xóa sinh viên thành công!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
