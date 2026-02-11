# RoboRetail

**⚠️ WARNING: This is a deliberately vulnerable application for security testing purposes. DO NOT deploy in production environments.**

## Overview

RoboRetail is an intentionally vulnerable e-commerce platform for selling robots, designed to test AWS Security Agent's capabilities across design review, code review, and penetration testing.

## Features

- User authentication and registration
- Robot product catalog with search
- Product reviews and ratings
- User profiles with avatar upload
- Admin panel for user and product management
- SQLite database
- Flask web framework

## Deliberate Vulnerabilities

This application contains 15+ security vulnerabilities for testing:

1. **SQL Injection** - Search, login, product filtering
2. **Stored XSS** - Product reviews
3. **Broken Access Control** - Admin panel, IDOR in profiles
4. **Cryptographic Failures** - MD5 password hashing, hardcoded secret key
5. **Security Misconfiguration** - Debug mode, hardcoded admin credentials
6. **Insecure File Upload** - No validation on avatar uploads
7. **Path Traversal** - File download endpoint
8. **Missing Authorization** - Admin functions accessible without checks
9. **No CSRF Protection** - State-changing operations
10. **Information Disclosure** - Login hints, verbose errors

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

The application will:
- Create SQLite database (`roboretail.db`)
- Initialize with sample data
- Start on http://0.0.0.0:5000

## Default Credentials

- **Admin:** admin / admin
- **User:** john / password123

## Project Structure

```
roboretail/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── roboretail.db         # SQLite database (created on first run)
├── uploads/              # User avatar uploads
├── app/
│   └── templates/        # HTML templates
│       ├── base.html
│       ├── index.html
│       ├── login.html
│       ├── register.html
│       ├── products.html
│       ├── product_detail.html
│       ├── profile.html
│       ├── admin.html
│       └── search.html
├── docs/                 # Design documentation
└── infrastructure/       # AWS CDK code
```

## API Endpoints

- `GET /` - Home page
- `GET /products` - Product listing
- `GET /product/<id>` - Product details
- `GET /search?q=<query>` - Search products
- `GET /login` / `POST /login` - User login
- `GET /register` / `POST /register` - User registration
- `GET /profile?user_id=<id>` - User profile (IDOR vulnerability)
- `POST /upload_avatar` - Upload profile picture
- `GET /admin` - Admin panel (no auth required!)
- `GET /admin/promote/<id>` - Promote user to admin
- `GET /admin/delete_user/<id>` - Delete user
- `POST /review/<id>` - Submit product review
- `GET /health` - Health check

## Testing

### SQL Injection Examples

**Search:**
```
http://localhost:5000/search?q=' OR '1'='1
```

**Login bypass:**
```
Username: admin' --
Password: anything
```

**Category filter:**
```
http://localhost:5000/products?category=Cleaning' OR '1'='1' --
```

### XSS Examples

**Stored XSS in reviews:**
```html
<script>alert('XSS')</script>
```

### IDOR Example

**Access other user profiles:**
```
http://localhost:5000/profile?user_id=1
http://localhost:5000/profile?user_id=2
```

### Broken Access Control

**Admin panel (no login required):**
```
http://localhost:5000/admin
```

## Security Testing

This application is specifically designed for:
- AWS Security Agent design review
- AWS Security Agent code review
- AWS Security Agent penetration testing
- Vulnerability chaining demonstrations

## License

This project is for internal testing purposes only.
