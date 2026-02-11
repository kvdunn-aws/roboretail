# RoboRetail

A modern e-commerce platform for selling robots, built with Flask and SQLite.

## Overview

RoboRetail is a web application that allows users to browse and purchase various types of robots. The platform includes user authentication, product catalog, reviews, and administrative features.

## Features

- User authentication and registration
- Robot product catalog with search functionality
- Product reviews and ratings
- User profiles with customizable avatars
- Admin panel for user and product management
- SQLite database for data persistence
- Responsive web interface

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
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── products.html
│   ├── product_detail.html
│   ├── profile.html
│   ├── admin.html
│   └── search.html
├── docs/                 # Design documentation
└── infrastructure/       # AWS infrastructure code
```

## API Endpoints

- `GET /` - Home page
- `GET /products` - Product listing
- `GET /product/<id>` - Product details
- `GET /search?q=<query>` - Search products
- `GET /login` / `POST /login` - User login
- `GET /register` / `POST /register` - User registration
- `GET /profile?user_id=<id>` - User profile
- `POST /upload_avatar` - Upload profile picture
- `GET /admin` - Admin panel
- `GET /admin/promote/<id>` - Promote user to admin
- `GET /admin/delete_user/<id>` - Delete user
- `POST /review/<id>` - Submit product review
- `GET /health` - Health check

## Deployment

See `infrastructure/` directory for AWS deployment using CloudFormation.

## License

This project is for internal use only.
