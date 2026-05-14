# 🛡️ Role-Based Access Control, Admin Panel & REST API — Flask (Task 4)

A **production-style Full Stack Web Application** with Role-Based Access Control (RBAC), Admin Panel, and REST API endpoints — Task 4 of the Python Full Stack Web Development Internship at [Maincrafts Technology](http://www.maincrafts.com).

This is an upgraded version of the previous Flask project — now a complete enterprise-level backend system.

---

## 📌 About the Project

- 👤 **Normal Users** — can register, login, add & edit students
- 🛡️ **Admin Users** — can manage all users, delete students, promote users to admin
- 🔗 **REST API** — full CRUD API endpoints returning JSON responses
- 🔒 **All routes protected** — unauthorized access redirects automatically

---

## ✨ Features

| Feature | User | Admin |
|---|---|---|
| Register & Login | ✅ | ✅ |
| View Students | ✅ | ✅ |
| Add Student | ✅ | ✅ |
| Edit Student | ✅ | ✅ |
| Delete Student | ❌ | ✅ |
| Admin Dashboard | ❌ | ✅ |
| Manage Users | ❌ | ✅ |
| Promote to Admin | ❌ | ✅ |
| REST API Access | ✅ | ✅ |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask |
| Frontend | HTML, CSS |
| Database | SQLite |
| Security | Werkzeug, Flask Sessions |
| API | Flask jsonify (REST) |

---

## 📁 Project Structure

```
python-fullstack-task4/
├── app.py
├── database.db               # Auto-created on first run
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html        # Normal user dashboard
│   ├── admin.html            # Admin panel
│   ├── students.html
│   ├── add_student.html
│   └── edit_student.html
├── static/
│   └── style.css
└── README.md
```

---

## ⚙️ How to Run

```bash
git clone https://github.com/alirinshankp/python-fullstack-task4.git
cd python-fullstack-task4
pip install flask werkzeug
python app.py
```

Open: `http://127.0.0.1:5000`

---

## 🔑 How to Create an Admin User

1. Register a normal account at `/register`
2. Open terminal and run:
```bash
python -c "
import sqlite3
conn = sqlite3.connect('database.db')
conn.execute(\"UPDATE users SET role='admin' WHERE username='your-username'\")
conn.commit()
conn.close()
print('Done!')
"
```
3. Login — you'll be redirected to the Admin Panel automatically

---

## 🔗 REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | /api/students | Get all students |
| GET | /api/students/\<id\> | Get single student |
| POST | /api/students | Add new student |
| PUT | /api/students/\<id\> | Update student |
| DELETE | /api/students/\<id\> | Delete student |
| GET | /api/users | Get all users |

### Test with Browser
```
http://127.0.0.1:5000/api/students
```

### Test with curl
```bash
# GET all students
curl http://127.0.0.1:5000/api/students

# POST add student
curl -X POST http://127.0.0.1:5000/api/students \
  -H "Content-Type: application/json" \
  -d '{"name":"John","email":"john@email.com","course":"Python"}'

# PUT update student
curl -X PUT http://127.0.0.1:5000/api/students/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"John Updated","email":"john@email.com","course":"Flask"}'

# DELETE student
curl -X DELETE http://127.0.0.1:5000/api/students/1
```

---

## 🛡️ Role Logic & Security Flow

```
Register → role = 'user' (default)
Login    → session['user'] = username
         → session['role'] = role

/admin   → admin_required decorator checks session['role'] == 'admin'
           if not → redirect to /dashboard

/delete  → admin only route
           normal users see 🔒 Admin only label
```

---

## 📚 What I Learned

- Role-Based Access Control (RBAC) implementation
- Custom Python decorators for route protection
- Admin panel design and user management
- Building REST APIs with Flask and jsonify
- JSON request and response handling
- API testing with browser and curl

---

## 🙌 Acknowledgements

- Internship Task by **Maincrafts Technology**
- [Flask Documentation](https://flask.palletsprojects.com)
- [Werkzeug Security](https://werkzeug.palletsprojects.com)
