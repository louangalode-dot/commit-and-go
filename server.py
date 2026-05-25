from flask import Flask, request, jsonify, session, redirect, render_template
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'commitandgo_secret_2026')

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS content (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

def get_content():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT key, value FROM content')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {row['key']: row['value'] for row in rows}

def save_content(data):
    conn = get_db()
    cur = conn.cursor()
    for key, value in data.items():
        cur.execute('''
            INSERT INTO content (key, value) VALUES (%s, %s)
            ON CONFLICT (key) DO UPDATE SET value = %s
        ''', (key, value, value))
    conn.commit()
    cur.close()
    conn.close()

@app.route('/')
def index():
    content = get_content()
    return render_template('index.html', content=content)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == 'admin123':
            session['logged_in'] = True
            return redirect('/')
        return render_template('login.html', error='Mot de passe incorrect')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/login')

@app.route('/api/is-admin')
def is_admin():
    return jsonify({'admin': session.get('logged_in', False)})

@app.route('/api/content', methods=['GET'])
def get_content_api():
    return jsonify(get_content())

@app.route('/api/content', methods=['POST'])
def update_content():
    if not session.get('logged_in'):
        return jsonify({'error': 'Non autorisé'}), 401
    data = request.json
    save_content(data)
    return jsonify({'success': True})

init_db()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
