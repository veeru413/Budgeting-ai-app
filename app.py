import sqlite3
import os
import json
import datetime
from flask import Flask, render_template, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import google.generativeai as genai
from dotenv import load_dotenv

# --- CONFIG ---
load_dotenv()
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL = genai.GenerativeModel("gemini-2.5-flash")

# --- DATABASE SETUP ---
def get_db():
    conn = sqlite3.connect('finance.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    # Table 1: User Credentials (User Data)
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )''')
    
    # Table 2: Financial Profile (User Info - Mapped by user_id)
    c.execute('''CREATE TABLE IF NOT EXISTS user_profiles (
        user_id INTEGER PRIMARY KEY,
        income REAL,
        budget_rent REAL,
        budget_food REAL,
        budget_clothing REAL,
        budget_electronics REAL,
        budget_travel REAL,
        budget_medical REAL,
        budget_other REAL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    # Table 3: Transactions
    c.execute('''CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        category TEXT,
        amount REAL,
        description TEXT,
        date TEXT,
        image_path TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    conn.commit()
    conn.close()

init_db()

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    try:
        conn = get_db()
        hashed_pw = generate_password_hash(data['password'])
        conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                     (data['username'], hashed_pw))
        conn.commit()
        return jsonify({"status": "success", "message": "User created"})
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Username exists"}), 400
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (data['username'],)).fetchone()
    conn.close()
    
    if user and check_password_hash(user['password_hash'], data['password']):
        session['user_id'] = user['id']
        # Check if onboarding is needed
        conn = get_db()
        profile = conn.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user['id'],)).fetchone()
        conn.close()
        return jsonify({"status": "success", "needs_onboarding": profile is None})
    
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401

@app.route('/api/onboard', methods=['POST'])
def onboard():
    if 'user_id' not in session: return jsonify({"status": "error"}), 401
    data = request.json
    conn = get_db()
    conn.execute('''INSERT OR REPLACE INTO user_profiles 
                    (user_id, income, budget_rent, budget_food, budget_clothing, 
                    budget_electronics, budget_travel, budget_medical, budget_other)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (session['user_id'], data['income'], data['rent'], data['food'], 
                  data['clothing'], data['electronics'], data['travel'], data['medical'], data['other']))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/api/dashboard_data')
def dashboard_data():
    if 'user_id' not in session: return jsonify({"status": "error"}), 401
    uid = session['user_id']
    conn = get_db()
    
    # Get Profile
    profile = dict(conn.execute("SELECT * FROM user_profiles WHERE user_id=?", (uid,)).fetchone())
    
    # Get Expenses
    expenses = conn.execute("SELECT category, SUM(amount) as total FROM expenses WHERE user_id=? GROUP BY category", (uid,)).fetchall()
    expense_map = {row['category']: row['total'] for row in expenses}
    
    # Calculate Remaining
    categories = ['Rent', 'Food', 'Clothing', 'Electronics', 'Travel', 'Medical', 'Other']
    dashboard = []
    
    for cat in categories:
        budget_key = f"budget_{cat.lower()}"
        budget = profile.get(budget_key, 0)
        spent = expense_map.get(cat, 0)
        dashboard.append({
            "category": cat,
            "budget": budget,
            "spent": spent,
            "remaining": budget - spent
        })
        
    return jsonify({"profile": profile, "stats": dashboard})

@app.route('/api/upload_bill', methods=['POST'])
def upload_bill():
    if 'user_id' not in session: return jsonify({"status": "error"}), 401
    
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['file']
    
    if file:
        filename = secure_filename(f"{datetime.datetime.now().timestamp()}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Call Gemini
        try:
            with open(filepath, "rb") as f:
                img_data = f.read()
                
            prompt = """
            Analyze this receipt. Extract:
            1. Total Amount.
            2. Category (Rent, Food, Clothing, Electronics, Travel, Medical, Other).
            3. Merchant Name.
            Return ONLY raw JSON: {"amount": 0.0, "category": "String", "description": "String"}
            """
            
            response = MODEL.generate_content([
                {'mime_type': file.content_type, 'data': img_data},
                prompt
            ])
            
            # Parse JSON
            text = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(text)
            
            # Save to DB
            conn = get_db()
            conn.execute("INSERT INTO expenses (user_id, category, amount, description, date, image_path) VALUES (?, ?, ?, ?, ?, ?)",
                         (session['user_id'], data['category'], data['amount'], data['description'], datetime.datetime.now(), filepath))
            conn.commit()
            conn.close()
            
            return jsonify({"status": "success", "data": data})
            
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)