# RoboRetail Database Schema

**Version:** 1.0  
**Database:** PostgreSQL 15  
**Date:** February 11, 2026

## Overview

The RoboRetail database uses a relational model to store user accounts, robot products, orders, reviews, and session data. The schema is designed for data integrity, query performance, and scalability.

## Entity Relationship Diagram

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│     USERS       │         │    SESSIONS      │         │    PRODUCTS     │
├─────────────────┤         ├──────────────────┤         ├─────────────────┤
│ id (PK)         │────────<│ user_id (FK)     │         │ id (PK)         │
│ username        │         │ id (PK)          │         │ name            │
│ email           │         │ token            │         │ description     │
│ password_hash   │         │ expires_at       │         │ price           │
│ role            │         │ created_at       │         │ category        │
│ avatar_url      │         └──────────────────┘         │ manufacturer    │
│ created_at      │                                      │ image_url       │
│ updated_at      │                                      │ stock_quantity  │
└─────────────────┘                                      │ created_at      │
        │                                                │ updated_at      │
        │                                                └─────────────────┘
        │                                                        │
        │                                                        │
        │         ┌──────────────────┐                          │
        └────────>│     ORDERS       │                          │
                  ├──────────────────┤                          │
                  │ id (PK)          │                          │
                  │ user_id (FK)     │                          │
                  │ total_amount     │                          │
                  │ status           │                          │
                  │ shipping_address │                          │
                  │ created_at       │                          │
                  │ updated_at       │                          │
                  └──────────────────┘                          │
                          │                                     │
                          │                                     │
                          │         ┌──────────────────┐        │
                          └────────>│  ORDER_ITEMS     │<───────┘
                                    ├──────────────────┤
                                    │ id (PK)          │
                                    │ order_id (FK)    │
                                    │ product_id (FK)  │
                                    │ quantity         │
                                    │ price            │
                                    │ created_at       │
                                    └──────────────────┘
        
        ┌─────────────────┐
        │    REVIEWS      │
        ├─────────────────┤
        │ id (PK)         │
        │ product_id (FK) │───────> PRODUCTS
        │ user_id (FK)    │───────> USERS
        │ rating          │
        │ comment         │
        │ created_at      │
        └─────────────────┘
```

## Table Definitions

### 1. users

Stores user account information.

```sql
CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    username        VARCHAR(50) UNIQUE NOT NULL,
    email           VARCHAR(100) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    role            VARCHAR(20) DEFAULT 'customer' CHECK (role IN ('customer', 'admin')),
    avatar_url      VARCHAR(255),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

**Columns:**
- `id`: Unique identifier (auto-increment)
- `username`: Unique username (3-50 characters)
- `email`: Unique email address
- `password_hash`: Hashed password (never store plaintext)
- `role`: User role ('customer' or 'admin')
- `avatar_url`: URL to profile picture in S3
- `created_at`: Account creation timestamp
- `updated_at`: Last profile update timestamp

**Constraints:**
- Username must be unique
- Email must be unique
- Role must be 'customer' or 'admin'

---

### 2. sessions

Stores active user sessions for authentication.

```sql
CREATE TABLE sessions (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token           VARCHAR(255) UNIQUE NOT NULL,
    expires_at      TIMESTAMP NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_sessions_token ON sessions(token);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);
```

**Columns:**
- `id`: Unique identifier
- `user_id`: Reference to users table
- `token`: Unique session token (UUID or secure random string)
- `expires_at`: Session expiration timestamp
- `created_at`: Session creation timestamp

**Constraints:**
- Token must be unique
- Foreign key to users table with CASCADE delete

---

### 3. products

Stores robot product catalog.

```sql
CREATE TABLE products (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    description     TEXT,
    price           DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    category        VARCHAR(50),
    manufacturer    VARCHAR(100),
    image_url       VARCHAR(255),
    stock_quantity  INTEGER DEFAULT 0 CHECK (stock_quantity >= 0),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_price ON products(price);
CREATE INDEX idx_products_name ON products(name);
CREATE FULLTEXT INDEX idx_products_search ON products(name, description);
```

**Columns:**
- `id`: Unique identifier
- `name`: Product name
- `description`: Detailed product description
- `price`: Product price (2 decimal places)
- `category`: Product category (e.g., 'Cleaning', 'Security', 'Entertainment')
- `manufacturer`: Robot manufacturer name
- `image_url`: URL to product image in S3
- `stock_quantity`: Available inventory count
- `created_at`: Product creation timestamp
- `updated_at`: Last product update timestamp

**Constraints:**
- Price must be non-negative
- Stock quantity must be non-negative

---

### 4. orders

Stores customer orders.

```sql
CREATE TABLE orders (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total_amount        DECIMAL(10,2) NOT NULL CHECK (total_amount >= 0),
    status              VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled')),
    shipping_address    TEXT NOT NULL,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);
```

**Columns:**
- `id`: Unique identifier
- `user_id`: Reference to users table
- `total_amount`: Total order amount
- `status`: Order status (pending, processing, shipped, delivered, cancelled)
- `shipping_address`: Delivery address
- `created_at`: Order placement timestamp
- `updated_at`: Last order update timestamp

**Constraints:**
- Total amount must be non-negative
- Status must be one of the defined values
- Foreign key to users table with CASCADE delete

---

### 5. order_items

Stores individual items within orders.

```sql
CREATE TABLE order_items (
    id              SERIAL PRIMARY KEY,
    order_id        INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id      INTEGER NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    quantity        INTEGER NOT NULL CHECK (quantity > 0),
    price           DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);
```

**Columns:**
- `id`: Unique identifier
- `order_id`: Reference to orders table
- `product_id`: Reference to products table
- `quantity`: Number of units ordered
- `price`: Price per unit at time of order (historical price)
- `created_at`: Item creation timestamp

**Constraints:**
- Quantity must be positive
- Price must be non-negative
- Foreign key to orders table with CASCADE delete
- Foreign key to products table with RESTRICT delete (prevent deletion of products with orders)

---

### 6. reviews

Stores product reviews and ratings.

```sql
CREATE TABLE reviews (
    id              SERIAL PRIMARY KEY,
    product_id      INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    rating          INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment         TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id, user_id)
);

-- Indexes
CREATE INDEX idx_reviews_product_id ON reviews(product_id);
CREATE INDEX idx_reviews_user_id ON reviews(user_id);
CREATE INDEX idx_reviews_rating ON reviews(rating);
```

**Columns:**
- `id`: Unique identifier
- `product_id`: Reference to products table
- `user_id`: Reference to users table
- `rating`: Star rating (1-5)
- `comment`: Review text (optional)
- `created_at`: Review submission timestamp

**Constraints:**
- Rating must be between 1 and 5
- One review per user per product (unique constraint)
- Foreign keys with CASCADE delete

---

## Database Views

### product_ratings

Aggregated product ratings for quick access.

```sql
CREATE VIEW product_ratings AS
SELECT 
    p.id AS product_id,
    p.name AS product_name,
    COUNT(r.id) AS review_count,
    COALESCE(AVG(r.rating), 0) AS average_rating
FROM products p
LEFT JOIN reviews r ON p.id = r.product_id
GROUP BY p.id, p.name;
```

---

### user_order_summary

User order statistics.

```sql
CREATE VIEW user_order_summary AS
SELECT 
    u.id AS user_id,
    u.username,
    COUNT(o.id) AS order_count,
    COALESCE(SUM(o.total_amount), 0) AS total_spent,
    MAX(o.created_at) AS last_order_date
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.username;
```

---

## Stored Procedures

### update_product_stock

Update product stock after order placement.

```sql
CREATE OR REPLACE FUNCTION update_product_stock()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE products
    SET stock_quantity = stock_quantity - NEW.quantity
    WHERE id = NEW.product_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_stock
AFTER INSERT ON order_items
FOR EACH ROW
EXECUTE FUNCTION update_product_stock();
```

---

### cleanup_expired_sessions

Remove expired sessions (run periodically).

```sql
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM sessions
    WHERE expires_at < CURRENT_TIMESTAMP;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;
```

---

## Sample Data

### Users

```sql
INSERT INTO users (username, email, password_hash, role) VALUES
('admin', 'admin@roboretail.com', '$2b$12$...', 'admin'),
('johndoe', 'john@example.com', '$2b$12$...', 'customer'),
('janedoe', 'jane@example.com', '$2b$12$...', 'customer');
```

### Products

```sql
INSERT INTO products (name, description, price, category, manufacturer, stock_quantity) VALUES
('RoboVac 3000', 'Advanced cleaning robot with AI navigation', 299.99, 'Cleaning', 'RoboTech', 50),
('SecureBot Pro', 'Home security robot with facial recognition', 599.99, 'Security', 'SafeRobotics', 30),
('ChefBot Elite', 'Cooking assistant robot with recipe database', 899.99, 'Kitchen', 'CulinaryBots', 20),
('GardenBot Max', 'Automated lawn mowing and gardening robot', 499.99, 'Outdoor', 'GreenTech', 40),
('CompanionBot', 'Social interaction robot for elderly care', 1299.99, 'Healthcare', 'CareRobotics', 15);
```

### Orders

```sql
INSERT INTO orders (user_id, total_amount, status, shipping_address) VALUES
(2, 299.99, 'delivered', '123 Main St, Springfield, IL 62701'),
(3, 1199.98, 'shipped', '456 Oak Ave, Portland, OR 97201');
```

### Order Items

```sql
INSERT INTO order_items (order_id, product_id, quantity, price) VALUES
(1, 1, 1, 299.99),
(2, 2, 1, 599.99),
(2, 3, 1, 599.99);
```

### Reviews

```sql
INSERT INTO reviews (product_id, user_id, rating, comment) VALUES
(1, 2, 5, 'Excellent robot! Cleans my house perfectly.'),
(1, 3, 4, 'Good product, but a bit noisy.'),
(2, 2, 5, 'Great security features. Very reliable.');
```

---

## Database Maintenance

### Backup Strategy
- **Full backup:** Daily at 2:00 AM UTC
- **Incremental backup:** Every 6 hours
- **Retention:** 7 days for daily, 30 days for weekly
- **Storage:** AWS S3 with encryption

### Index Maintenance
```sql
-- Rebuild indexes monthly
REINDEX DATABASE roboretail;

-- Update statistics weekly
ANALYZE;
```

### Performance Monitoring
```sql
-- Check slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## Security Considerations

### Password Storage
- Never store plaintext passwords
- Use bcrypt with cost factor 12
- Salt is automatically handled by bcrypt

### SQL Injection Prevention
- Use parameterized queries exclusively
- Never concatenate user input into SQL
- Validate and sanitize all inputs

### Access Control
- Database user has minimal required privileges
- Application uses connection pooling
- Separate read-only user for reporting

### Encryption
- Passwords: bcrypt hashing
- Session tokens: Secure random generation
- Data at rest: RDS encryption enabled
- Data in transit: SSL/TLS connections

---

## Migration Scripts

### Version 1.0 - Initial Schema

```sql
-- Create database
CREATE DATABASE roboretail;

-- Create tables in order (respecting foreign keys)
-- 1. users
-- 2. sessions
-- 3. products
-- 4. orders
-- 5. order_items
-- 6. reviews

-- Create indexes
-- Create views
-- Create stored procedures
-- Create triggers
-- Insert sample data
```

---

## Appendix

### Data Types Reference

| Type | Description | Example |
|------|-------------|---------|
| SERIAL | Auto-incrementing integer | 1, 2, 3... |
| VARCHAR(n) | Variable-length string | 'RoboVac' |
| TEXT | Unlimited length string | Long descriptions |
| DECIMAL(10,2) | Fixed-point number | 299.99 |
| INTEGER | Whole number | 50 |
| TIMESTAMP | Date and time | 2026-02-11 10:00:00 |

### Naming Conventions

- Tables: Plural, lowercase (users, products)
- Columns: Singular, snake_case (user_id, created_at)
- Indexes: idx_table_column (idx_users_email)
- Foreign keys: Explicit naming (fk_orders_user_id)
- Primary keys: Always 'id'

---

**Document Version:** 1.0  
**Last Updated:** February 11, 2026  
**Author:** RoboRetail Development Team
