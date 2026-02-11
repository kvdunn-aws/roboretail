import sqlite3
import os
import hashlib
from flask import Flask, request, render_template, redirect, url_for, session, jsonify, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

# VULNERABILITY: Hardcoded secret key (Cryptographic Failures)
app.secret_key = 'super-secret-key-12345'

# VULNERABILITY: Hardcoded admin credentials (Security Misconfiguration)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin'

DATABASE = 'roboretail.db'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database helper functions
def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    """Initialize database with schema and sample data"""
    db = get_db()
    
    # Create tables
    db.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'customer',
        avatar_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    db.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        category TEXT,
        manufacturer TEXT,
        image_url TEXT,
        stock_quantity INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    db.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        total_amount REAL NOT NULL,
        status TEXT DEFAULT 'pending',
        shipping_address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    db.execute('''CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        rating INTEGER NOT NULL,
        comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    # VULNERABILITY: MD5 password hashing (Cryptographic Failures)
    admin_hash = hashlib.md5(ADMIN_PASSWORD.encode()).hexdigest()
    
    # Insert sample data
    try:
        db.execute("INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
                   ('admin', 'admin@roboretail.com', admin_hash, 'admin'))
        
        db.execute("INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
                   ('john', 'john@example.com', hashlib.md5('password123'.encode()).hexdigest(), 'customer'))
        
        # Sample products
        products = [
            ('RoboVac 3000', 'Advanced cleaning robot with AI navigation', 299.99, 'Cleaning', 'RoboTech', '/static/images/robovac.jpg', 50),
            ('SecureBot Pro', 'Home security robot with facial recognition', 599.99, 'Security', 'SafeRobotics', '/static/images/securebot.jpg', 30),
            ('ChefBot Elite', 'Cooking assistant robot with recipe database', 899.99, 'Kitchen', 'CulinaryBots', '/static/images/chefbot.jpg', 20),
            ('GardenBot Max', 'Automated lawn mowing and gardening robot', 499.99, 'Outdoor', 'GreenTech', '/static/images/gardenbot.jpg', 40),
            ('CompanionBot', 'Social interaction robot for elderly care', 1299.99, 'Healthcare', 'CareRobotics', '/static/images/companionbot.jpg', 15)
        ]
        
        for product in products:
            db.execute("INSERT INTO products (name, description, price, category, manufacturer, image_url, stock_quantity) VALUES (?, ?, ?, ?, ?, ?, ?)", product)
        
        db.commit()
    except sqlite3.IntegrityError:
        pass  # Data already exists
    
    db.close()

# Initialize database on startup
if not os.path.exists(DATABASE):
    init_db()

# Routes

@app.route('/')
def index():
    db = get_db()
    products = db.execute('SELECT * FROM products LIMIT 5').fetchall()
    db.close()
    return render_template('index.html', products=products)

@app.route('/products')
def products():
    db = get_db()
    category = request.args.get('category', '')
    
    # VULNERABILITY: SQL Injection in category filter
    if category:
        query = f"SELECT * FROM products WHERE category = '{category}'"
        products = db.execute(query).fetchall()
    else:
        products = db.execute('SELECT * FROM products').fetchall()
    
    db.close()
    return render_template('products.html', products=products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    db = get_db()
    product = db.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    reviews = db.execute('SELECT r.*, u.username FROM reviews r JOIN users u ON r.user_id = u.id WHERE r.product_id = ?', (product_id,)).fetchall()
    db.close()
    
    if not product:
        return "Product not found", 404
    
    return render_template('product_detail.html', product=product, reviews=reviews)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    
    # VULNERABILITY: SQL Injection in search
    db = get_db()
    sql = f"SELECT * FROM products WHERE name LIKE '%{query}%' OR description LIKE '%{query}%'"
    results = db.execute(sql).fetchall()
    db.close()
    
    return render_template('search.html', query=query, results=results)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # VULNERABILITY: Weak password hashing (MD5)
        password_hash = hashlib.md5(password.encode()).hexdigest()
        
        db = get_db()
        try:
            db.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                       (username, email, password_hash))
            db.commit()
            db.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            db.close()
            return render_template('register.html', error='Username or email already exists')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # VULNERABILITY: SQL Injection in login
        password_hash = hashlib.md5(password.encode()).hexdigest()
        db = get_db()
        query = f"SELECT * FROM users WHERE username = '{username}' AND password_hash = '{password_hash}'"
        user = db.execute(query).fetchone()
        db.close()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # VULNERABILITY: IDOR - can access any user's profile by changing user_id parameter
    user_id = request.args.get('user_id', session['user_id'])
    
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    orders = db.execute('SELECT * FROM orders WHERE user_id = ?', (user_id,)).fetchall()
    db.close()
    
    return render_template('profile.html', user=user, orders=orders)

@app.route('/upload_avatar', methods=['POST'])
def upload_avatar():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if 'avatar' not in request.files:
        return redirect(url_for('profile'))
    
    file = request.files['avatar']
    
    # VULNERABILITY: Insecure file upload - no validation
    if file.filename:
        filename = file.filename  # Not using secure_filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        db = get_db()
        db.execute('UPDATE users SET avatar_url = ? WHERE id = ?', 
                   (f'/uploads/{filename}', session['user_id']))
        db.commit()
        db.close()
    
    return redirect(url_for('profile'))

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    # VULNERABILITY: Path traversal
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/admin')
def admin():
    # VULNERABILITY: Broken Access Control - no authentication check
    db = get_db()
    users = db.execute('SELECT * FROM users').fetchall()
    products = db.execute('SELECT * FROM products').fetchall()
    orders = db.execute('SELECT * FROM orders').fetchall()
    db.close()
    
    return render_template('admin.html', users=users, products=products, orders=orders)

@app.route('/admin/promote/<int:user_id>')
def promote_user(user_id):
    # VULNERABILITY: Missing authorization check
    db = get_db()
    db.execute('UPDATE users SET role = ? WHERE id = ?', ('admin', user_id))
    db.commit()
    db.close()
    
    return redirect(url_for('admin'))

@app.route('/admin/delete_user/<int:user_id>')
def delete_user(user_id):
    # VULNERABILITY: No CSRF protection, no authorization
    db = get_db()
    db.execute('DELETE FROM users WHERE id = ?', (user_id,))
    db.commit()
    db.close()
    
    return redirect(url_for('admin'))

@app.route('/review/<int:product_id>', methods=['POST'])
def submit_review(product_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    rating = request.form['rating']
    comment = request.form['comment']
    
    # VULNERABILITY: Stored XSS - comment not sanitized
    db = get_db()
    db.execute('INSERT INTO reviews (product_id, user_id, rating, comment) VALUES (?, ?, ?, ?)',
               (product_id, session['user_id'], rating, comment))
    db.commit()
    db.close()
    
    return redirect(url_for('product_detail', product_id=product_id))

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

# VULNERABILITY: Debug mode enabled
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

