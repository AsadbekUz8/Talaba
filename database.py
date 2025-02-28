import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('teachers.db')
    c = conn.cursor()
    # Eski jadvalni tekshirish va agar kerak bo‘lsa yangilash
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        contact TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS teachers_pending (
        user_id INTEGER,
        name TEXT,
        subject TEXT,
        experience TEXT,
        price TEXT,
        location TEXT,
        photo TEXT,
        bio TEXT,
        contact TEXT,
        gender TEXT
    )''')
    # Teachers jadvalini tekshirish va avg_rating qo‘shish
    c.execute('''CREATE TABLE IF NOT EXISTS teachers (
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        subject TEXT,
        experience TEXT,
        price TEXT,
        location TEXT,
        photo TEXT,
        bio TEXT,
        contact TEXT,
        gender TEXT,
        avg_rating REAL DEFAULT 0.0
    )''')
    # Agar teachers jadvali allaqachon mavjud bo‘lsa, avg_rating qo‘shish
    try:
        c.execute("ALTER TABLE teachers ADD COLUMN avg_rating REAL DEFAULT 0.0")
    except sqlite3.OperationalError:
        pass  # Agar ustun allaqachon mavjud bo‘lsa, hech narsa qilmaymiz
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        sender_id INTEGER,
        receiver_id INTEGER,
        message TEXT,
        timestamp TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS ratings (
        student_id INTEGER,
        teacher_id INTEGER,
        rating INTEGER,
        PRIMARY KEY (student_id, teacher_id)
    )''')
    conn.commit()
    conn.close()

def add_user(user_id, contact):
    conn = sqlite3.connect('teachers.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users (user_id, contact) VALUES (?, ?)", 
              (user_id, contact))
    conn.commit()
    conn.close()

def add_teacher_pending(teacher_data):
    conn = sqlite3.connect('teachers.db')
    c = conn.cursor()
    c.execute("INSERT INTO teachers_pending (user_id, name, subject, experience, price, location, photo, bio, contact, gender) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (teacher_data['user_id'], teacher_data['name'], teacher_data['subject'], teacher_data['experience'], 
               teacher_data['price'], teacher_data['location'], teacher_data['photo'], teacher_data['bio'], 
               teacher_data['contact'], teacher_data['gender']))
    conn.commit()
    conn.close()

def approve_last_teacher():
    conn = sqlite3.connect('teachers.db')
    c = conn.cursor()
    c.execute("SELECT * FROM teachers_pending ORDER BY ROWID DESC LIMIT 1")
    teacher = c.fetchone()
    if teacher:
        c.execute("INSERT OR REPLACE INTO teachers (user_id, name, subject, experience, price, location, photo, bio, contact, gender) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (teacher[0], teacher[1], teacher[2], teacher[3], teacher[4], teacher[5], teacher[6], teacher[7], teacher[8], teacher[9]))
        c.execute("DELETE FROM teachers_pending WHERE user_id = ?", (teacher[0],))
        conn.commit()
        conn.close()
        return {'user_id': teacher[0], 'name': teacher[1], 'subject': teacher[2], 'experience': teacher[3], 
                'price': teacher[4], 'location': teacher[5], 'photo': teacher[6], 'bio': teacher[7], 
                'contact': teacher[8], 'gender': teacher[9]}
    conn.close()
    return None

def reject_last_teacher():
    conn = sqlite3.connect('teachers.db')
    c = conn.cursor()
    c.execute("SELECT * FROM teachers_pending ORDER BY ROWID DESC LIMIT 1")
    teacher = c.fetchone()
    if teacher:
        c.execute("DELETE FROM teachers_pending WHERE user_id = ?", (teacher[0],))
        conn.commit()
        conn.close()
        return {'user_id': teacher[0], 'name': teacher[1], 'subject': teacher[2], 'experience': teacher[3], 
                'price': teacher[4], 'location': teacher[5], 'photo': teacher[6], 'bio': teacher[7], 
                'contact': teacher[8], 'gender': teacher[9]}
    conn.close()
    return None

def get_teachers():
    conn = sqlite3.connect('teachers.db')
    c = conn.cursor()
    c.execute("SELECT * FROM teachers")
    teachers = c.fetchall()
    conn.close()
    return [{'user_id': t[0], 'name': t[1], 'subject': t[2], 'experience': t[3], 'price': t[4], 'location': t[5], 
             'photo': t[6], 'bio': t[7], 'contact': t[8], 'gender': t[9], 'avg_rating': t[10]} for t in teachers]

def get_teachers_by_subject(subject):
    conn = sqlite3.connect('teachers.db')
    c = conn.cursor()
    c.execute("SELECT * FROM teachers WHERE subject LIKE ?", (f"%{subject}%",))
    teachers = c.fetchall()
    conn.close()
    return [{'user_id': t[0], 'name': t[1], 'subject': t[2], 'experience': t[3], 'price': t[4], 'location': t[5], 
             'photo': t[6], 'bio': t[7], 'contact': t[8], 'gender': t[9], 'avg_rating': t[10]} for t in teachers]

def get_top_teachers():
    conn = sqlite3.connect('teachers.db')
    c = conn.cursor()
    c.execute("SELECT * FROM teachers ORDER BY avg_rating DESC, experience DESC LIMIT 5")
    teachers = c.fetchall()
    conn.close()
    return [{'user_id': t[0], 'name': t[1], 'subject': t[2], 'experience': t[3], 'price': t[4], 'location': t[5], 
             'photo': t[6], 'bio': t[7], 'contact': t[8], 'gender': t[9], 'avg_rating': t[10]} for t in teachers]

def has_added_teacher(user_id):
    conn = sqlite3.connect('teachers.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM teachers WHERE user_id = ?", (user_id,))
    count = c.fetchone()[0]
    conn.close()
    return count > 0

def mark_teacher_added(user_id):
    conn = sqlite3.connect('teachers.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO teachers (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def add_message(sender_id, receiver_id, message):
    conn = sqlite3.connect('teachers.db')
    c = conn.cursor()
    c.execute("INSERT INTO messages (sender_id, receiver_id, message, timestamp) VALUES (?, ?, ?, ?)", 
              (sender_id, receiver_id, message, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect('teachers.db')
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    users = c.fetchall()
    conn.close()
    return [user[0] for user in users]

def add_rating(student_id, teacher_id, rating):
    conn = sqlite3.connect('teachers.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO ratings (student_id, teacher_id, rating) VALUES (?, ?, ?)",
              (student_id, teacher_id, rating))
    c.execute("UPDATE teachers SET avg_rating = (SELECT AVG(rating) FROM ratings WHERE teacher_id = ?) WHERE user_id = ?",
              (teacher_id, teacher_id))
    conn.commit()
    conn.close()