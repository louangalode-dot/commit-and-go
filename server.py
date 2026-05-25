from flask import Flask, request, jsonify, session, redirect, render_template
from dotenv import load_dotenv
import json, os

load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')
app.secret_key = os.getenv('SECRET_KEY', 'commitandgo2026')

ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
DATA_FILE = 'content.json'

def load_content():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {}

def save_content(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect('/login')
    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.json.get('password') == ADMIN_PASSWORD:
            session['logged_in'] = True
            return jsonify({'success': True, 'redirect': '/'})
        return jsonify({'success': False})
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/login')


@app.route('/api/is-admin')
def is_admin():
    return jsonify({'admin': session.get('logged_in', False)})

@app.route('/api/content', methods=['GET'])
def get_content():
    return jsonify(load_content())

@app.route('/api/content', methods=['POST'])
def update_content():
    if not session.get('logged_in'):
        return jsonify({'error': 'Non autorise'}), 401
    data = request.json
    save_content(data)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
