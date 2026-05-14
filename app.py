from flask import Flask, render_template, request, redirect, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3

app = Flask(__name__)
app.secret_key = "secure-secret-key"


# ──────────────────────────────────────────
# DATABASE CONNECTION
# ──────────────────────────────────────────
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# ──────────────────────────────────────────
# INITIALIZE DATABASE
# ──────────────────────────────────────────
def init_db():
    db = get_db()

    # Users table with role column
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    ''')

    # Students table
    db.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            course TEXT NOT NULL
        )
    ''')

    # Add role column if upgrading from Task-3
    try:
        db.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
    except:
        pass  # Column already exists

    # Create default admin account if not exists
    existing_admin = db.execute(
        "SELECT * FROM users WHERE username = 'admin'"
    ).fetchone()
    if not existing_admin:
        from werkzeug.security import generate_password_hash
        db.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ('admin', generate_password_hash('admin123'), 'admin')
        )
        print("✅ Default admin created — Username: admin | Password: admin123")

    db.commit()
    db.close()


# ──────────────────────────────────────────
# DECORATORS
# ──────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user' not in session or session.get('role') != 'admin':
            return redirect('/dashboard')
        return f(*args, **kwargs)
    return wrapper


# ──────────────────────────────────────────
# HOME
# ──────────────────────────────────────────
@app.route('/')
def home():
    return redirect('/login')


# ──────────────────────────────────────────
# REGISTER
# ──────────────────────────────────────────
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        if not username or not password:
            error = "All fields are required."
        else:
            hashed_password = generate_password_hash(password)
            db = get_db()
            try:
                db.execute(
                    "INSERT INTO users (username, password, role) VALUES (?, ?, 'user')",
                    (username, hashed_password)
                )
                db.commit()
                return redirect('/login')
            except sqlite3.IntegrityError:
                error = "Username already exists."
            finally:
                db.close()

    return render_template('register.html', error=error)


# ──────────────────────────────────────────
# LOGIN — stores role in session
# ──────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        db.close()

        if user and check_password_hash(user['password'], password):
            session['user'] = user['username']
            session['role'] = user['role']
            if user['role'] == 'admin':
                return redirect('/admin')
            return redirect('/dashboard')
        else:
            error = "Invalid username or password."

    return render_template('login.html', error=error)


# ──────────────────────────────────────────
# LOGOUT
# ──────────────────────────────────────────
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ──────────────────────────────────────────
# USER DASHBOARD (Normal Users)
# ──────────────────────────────────────────
@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    students = db.execute("SELECT * FROM students").fetchall()
    db.close()
    return render_template('dashboard.html', user=session['user'],
                           role=session['role'], students=students)


# ──────────────────────────────────────────
# ADMIN DASHBOARD
# ──────────────────────────────────────────
@app.route('/admin')
@admin_required
def admin_dashboard():
    db = get_db()
    users = db.execute("SELECT id, username, role FROM users").fetchall()
    students = db.execute("SELECT * FROM students").fetchall()
    db.close()
    return render_template('admin.html', users=users, students=students,
                           user=session['user'])


# ──────────────────────────────────────────
# CRUD — Add Student (logged-in users)
# ──────────────────────────────────────────
@app.route('/add-student', methods=['GET', 'POST'])
@login_required
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        course = request.form['course']

        db = get_db()
        db.execute(
            "INSERT INTO students (name, email, course) VALUES (?, ?, ?)",
            (name, email, course)
        )
        db.commit()
        db.close()
        return redirect('/students')

    return render_template('add_student.html')


# ──────────────────────────────────────────
# CRUD — View All Students (logged-in users)
# ──────────────────────────────────────────
@app.route('/students')
@login_required
def students():
    db = get_db()
    data = db.execute("SELECT * FROM students").fetchall()
    db.close()
    return render_template('students.html', students=data,
                           role=session.get('role'))


# ──────────────────────────────────────────
# CRUD — Edit Student (logged-in users)
# ──────────────────────────────────────────
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    db = get_db()
    student = db.execute(
        "SELECT * FROM students WHERE id = ?", (id,)
    ).fetchone()

    if request.method == 'POST':
        db.execute(
            "UPDATE students SET name=?, email=?, course=? WHERE id=?",
            (request.form['name'], request.form['email'],
             request.form['course'], id)
        )
        db.commit()
        db.close()
        return redirect('/students')

    db.close()
    return render_template('edit_student.html', student=student)


# ──────────────────────────────────────────
# CRUD — Delete Student (ADMIN ONLY)
# ──────────────────────────────────────────
@app.route('/admin/delete/<int:id>')
@admin_required
def admin_delete_student(id):
    db = get_db()
    db.execute("DELETE FROM students WHERE id=?", (id,))
    db.commit()
    db.close()
    return redirect('/admin')


# ──────────────────────────────────────────
# ADMIN — Delete User
# ──────────────────────────────────────────
@app.route('/admin/delete-user/<int:id>')
@admin_required
def admin_delete_user(id):
    db = get_db()
    db.execute("DELETE FROM users WHERE id=?", (id,))
    db.commit()
    db.close()
    return redirect('/admin')


# ──────────────────────────────────────────
# ADMIN — Make User Admin
# ──────────────────────────────────────────
@app.route('/admin/make-admin/<int:id>')
@admin_required
def make_admin(id):
    db = get_db()
    db.execute("UPDATE users SET role='admin' WHERE id=?", (id,))
    db.commit()
    db.close()
    return redirect('/admin')


# ══════════════════════════════════════════
# REST API ENDPOINTS
# ══════════════════════════════════════════

# API — Get All Students
@app.route('/api/students', methods=['GET'])
def api_get_students():
    db = get_db()
    students = db.execute("SELECT * FROM students").fetchall()
    db.close()
    return jsonify([dict(row) for row in students])


# API — Get Single Student
@app.route('/api/students/<int:id>', methods=['GET'])
def api_get_student(id):
    db = get_db()
    student = db.execute(
        "SELECT * FROM students WHERE id = ?", (id,)
    ).fetchone()
    db.close()
    if student:
        return jsonify(dict(student))
    return jsonify({"error": "Student not found"}), 404


# API — Add Student
@app.route('/api/students', methods=['POST'])
def api_add_student():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('email') or not data.get('course'):
        return jsonify({"error": "name, email and course are required"}), 400

    db = get_db()
    db.execute(
        "INSERT INTO students (name, email, course) VALUES (?, ?, ?)",
        (data['name'], data['email'], data['course'])
    )
    db.commit()
    db.close()
    return jsonify({"message": "Student added successfully"}), 201


# API — Update Student
@app.route('/api/students/<int:id>', methods=['PUT'])
def api_update_student(id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    db = get_db()
    db.execute(
        "UPDATE students SET name=?, email=?, course=? WHERE id=?",
        (data['name'], data['email'], data['course'], id)
    )
    db.commit()
    db.close()
    return jsonify({"message": "Student updated successfully"})


# API — Delete Student
@app.route('/api/students/<int:id>', methods=['DELETE'])
def api_delete_student(id):
    db = get_db()
    db.execute("DELETE FROM students WHERE id=?", (id,))
    db.commit()
    db.close()
    return jsonify({"message": "Student deleted successfully"})


# API — Get All Users (admin info)
@app.route('/api/users', methods=['GET'])
def api_get_users():
    db = get_db()
    users = db.execute("SELECT id, username, role FROM users").fetchall()
    db.close()
    return jsonify([dict(row) for row in users])


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
