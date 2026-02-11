# RoboRetail System Architecture

**Version:** 1.0  
**Date:** February 11, 2026  
**Status:** Design Phase

## Executive Summary

RoboRetail is a modern e-commerce platform specializing in robot sales. The system provides a comprehensive online shopping experience with user management, product catalog, shopping cart, order processing, and administrative capabilities.

## System Overview

### Purpose
RoboRetail enables customers to browse, search, and purchase robots online. The platform supports multiple user roles (customers and administrators) with distinct capabilities and access levels.

### Key Features
- User registration and authentication
- Robot product catalog with advanced search
- Shopping cart and checkout process
- Order management and tracking
- User profile management with avatar uploads
- Administrative dashboard for product and user management
- Report generation and export capabilities
- Product reviews and ratings

## Architecture Style

**Pattern:** Three-Tier Architecture

### Tier 1: Presentation Layer (Frontend)
- **Technology:** HTML5, CSS3, JavaScript (Vanilla JS)
- **Responsibilities:**
  - User interface rendering
  - Client-side form validation
  - AJAX requests to backend API
  - Session management
  - Dynamic content updates

### Tier 2: Application Layer (Backend API)
- **Technology:** Python 3.11, Flask 3.0
- **Responsibilities:**
  - Business logic processing
  - API endpoint management
  - Authentication and authorization
  - Data validation
  - File upload handling
  - Report generation
  - Integration with database

### Tier 3: Data Layer (Database)
- **Technology:** PostgreSQL 15
- **Responsibilities:**
  - Persistent data storage
  - Data integrity enforcement
  - Transaction management
  - Query optimization

## Component Architecture

### Frontend Components

#### 1. Public Pages
- **Home Page** - Featured robots, promotions
- **Product Listing** - Browse all robots with filtering
- **Product Detail** - Individual robot information, reviews
- **Search Results** - Search functionality across products
- **Shopping Cart** - Cart management
- **Checkout** - Order placement

#### 2. User Pages
- **Login/Register** - Authentication forms
- **User Profile** - Account information, order history
- **Order Tracking** - View order status

#### 3. Admin Pages
- **Admin Dashboard** - System overview, metrics
- **Product Management** - CRUD operations for robots
- **User Management** - View and manage users
- **Order Management** - Process and track orders
- **Reports** - Generate sales and inventory reports

### Backend API Endpoints

#### Authentication & User Management
```
POST   /api/register          - Create new user account
POST   /api/login             - Authenticate user
POST   /api/logout            - End user session
GET    /api/profile           - Get user profile
PUT    /api/profile           - Update user profile
POST   /api/profile/avatar    - Upload profile picture
```

#### Product Catalog
```
GET    /api/products          - List all robots
GET    /api/products/{id}     - Get robot details
GET    /api/products/search   - Search robots
POST   /api/products          - Create robot (admin)
PUT    /api/products/{id}     - Update robot (admin)
DELETE /api/products/{id}     - Delete robot (admin)
```

#### Shopping & Orders
```
GET    /api/cart              - Get shopping cart
POST   /api/cart              - Add item to cart
DELETE /api/cart/{id}         - Remove item from cart
POST   /api/checkout          - Place order
GET    /api/orders            - Get user orders
GET    /api/orders/{id}       - Get order details
```

#### Reviews
```
GET    /api/products/{id}/reviews  - Get product reviews
POST   /api/products/{id}/reviews  - Submit review
```

#### Admin Operations
```
GET    /api/admin/users       - List all users
GET    /api/admin/users/{id}  - Get user details
PUT    /api/admin/users/{id}  - Update user (promote to admin)
DELETE /api/admin/users/{id}  - Delete user
GET    /api/admin/orders      - List all orders
PUT    /api/admin/orders/{id} - Update order status
GET    /api/admin/reports     - Generate reports
POST   /api/admin/export      - Export data
```

### Database Schema

#### Users Table
```sql
users (
    id              SERIAL PRIMARY KEY,
    username        VARCHAR(50) UNIQUE NOT NULL,
    email           VARCHAR(100) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    role            VARCHAR(20) DEFAULT 'customer',
    avatar_url      VARCHAR(255),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### Products Table
```sql
products (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    description     TEXT,
    price           DECIMAL(10,2) NOT NULL,
    category        VARCHAR(50),
    manufacturer    VARCHAR(100),
    image_url       VARCHAR(255),
    stock_quantity  INTEGER DEFAULT 0,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### Orders Table
```sql
orders (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER REFERENCES users(id),
    total_amount    DECIMAL(10,2) NOT NULL,
    status          VARCHAR(20) DEFAULT 'pending',
    shipping_address TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### Order Items Table
```sql
order_items (
    id              SERIAL PRIMARY KEY,
    order_id        INTEGER REFERENCES orders(id),
    product_id      INTEGER REFERENCES products(id),
    quantity        INTEGER NOT NULL,
    price           DECIMAL(10,2) NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### Reviews Table
```sql
reviews (
    id              SERIAL PRIMARY KEY,
    product_id      INTEGER REFERENCES products(id),
    user_id         INTEGER REFERENCES users(id),
    rating          INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment         TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### Sessions Table
```sql
sessions (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER REFERENCES users(id),
    token           VARCHAR(255) UNIQUE NOT NULL,
    expires_at      TIMESTAMP NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## Data Flow

### User Registration Flow
1. User submits registration form (frontend)
2. Frontend sends POST to /api/register
3. Backend validates input data
4. Backend hashes password
5. Backend creates user record in database
6. Backend returns success response
7. Frontend redirects to login page

### Product Search Flow
1. User enters search query (frontend)
2. Frontend sends GET to /api/products/search?q={query}
3. Backend queries database with search terms
4. Backend returns matching products
5. Frontend displays search results

### Checkout Flow
1. User reviews cart and clicks checkout
2. Frontend sends POST to /api/checkout with cart data
3. Backend validates cart items and stock
4. Backend creates order record
5. Backend creates order_items records
6. Backend updates product stock quantities
7. Backend returns order confirmation
8. Frontend displays order success page

### Admin User Management Flow
1. Admin navigates to user management page
2. Frontend sends GET to /api/admin/users
3. Backend verifies admin role
4. Backend queries all users from database
5. Backend returns user list
6. Frontend displays users in table
7. Admin can promote/delete users via PUT/DELETE requests

## Security Architecture

### Authentication
- Session-based authentication using secure tokens
- Password hashing using industry-standard algorithms
- Session tokens stored in database with expiration
- Automatic session cleanup for expired tokens

### Authorization
- Role-based access control (RBAC)
- Two roles: customer, admin
- Middleware checks user role before processing requests
- Admin endpoints protected by role verification

### Data Protection
- HTTPS encryption for data in transit
- Password hashing for data at rest
- Input validation on all user inputs
- SQL parameterization to prevent injection
- File upload validation for avatars

### Session Management
- Secure session token generation
- Token expiration after 24 hours
- Session invalidation on logout
- Token stored in HTTP-only cookies

## Deployment Architecture

### AWS Infrastructure

#### Network Layer
- **VPC:** Isolated virtual network (10.0.0.0/16)
- **Public Subnets:** 2 subnets across 2 AZs for ALB
- **Private Subnets:** 2 subnets across 2 AZs for application and database
- **Internet Gateway:** Public internet access
- **NAT Gateway:** Outbound internet for private subnets

#### Compute Layer
- **Application Load Balancer (ALB):** 
  - Public-facing
  - HTTPS termination
  - Health checks
  - Traffic distribution
  
- **EC2 Instances (Application Servers):**
  - t3.medium instances
  - Auto Scaling Group (min: 2, max: 4)
  - Private subnets
  - Flask application deployment

#### Data Layer
- **RDS PostgreSQL:**
  - db.t3.medium instance
  - Multi-AZ deployment
  - Automated backups
  - Private subnets
  - Encryption at rest

#### Storage Layer
- **S3 Bucket:**
  - User avatar storage
  - Report file storage
  - Versioning enabled
  - Server-side encryption

#### Security Layer
- **Security Groups:**
  - ALB: Allow 443 from 0.0.0.0/0
  - App: Allow 5000 from ALB
  - RDS: Allow 5432 from App
  
- **IAM Roles:**
  - EC2 instance role for S3 access
  - RDS access credentials in Secrets Manager

#### Monitoring Layer
- **CloudWatch:**
  - Application logs
  - Performance metrics
  - Alarms for errors and latency

## Technology Stack Summary

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | HTML/CSS/JavaScript | ES6+ |
| Backend | Python Flask | 3.0 |
| Database | PostgreSQL | 15 |
| Web Server | Gunicorn | 21.0 |
| Load Balancer | AWS ALB | - |
| Compute | AWS EC2 | t3.medium |
| Storage | AWS S3 | - |
| Database | AWS RDS | PostgreSQL 15 |
| IaC | AWS CDK | Python |

## Scalability Considerations

### Horizontal Scaling
- Auto Scaling Group adjusts EC2 instances based on CPU utilization
- Target: 70% CPU utilization
- Scale up: Add instance when above threshold for 5 minutes
- Scale down: Remove instance when below threshold for 15 minutes

### Database Scaling
- Read replicas for read-heavy operations
- Connection pooling to optimize database connections
- Query optimization and indexing

### Caching Strategy
- Application-level caching for product catalog
- Session data cached in memory
- Static assets served via CloudFront (future enhancement)

## Disaster Recovery

### Backup Strategy
- **Database:** Automated daily backups, 7-day retention
- **Application:** Infrastructure as Code allows rapid rebuild
- **User Data:** S3 versioning for uploaded files

### Recovery Objectives
- **RTO (Recovery Time Objective):** 4 hours
- **RPO (Recovery Point Objective):** 24 hours

## Performance Requirements

### Response Time Targets
- Page load: < 2 seconds
- API response: < 500ms
- Search results: < 1 second
- Checkout process: < 3 seconds

### Throughput Targets
- Concurrent users: 100
- Requests per second: 50
- Database connections: 20

## Future Enhancements

1. **Payment Integration:** Stripe/PayPal integration
2. **Email Notifications:** Order confirmations, shipping updates
3. **Advanced Search:** Elasticsearch integration
4. **Recommendation Engine:** ML-based product recommendations
5. **Mobile App:** Native iOS/Android applications
6. **CDN Integration:** CloudFront for static assets
7. **Microservices:** Break monolith into services
8. **Container Orchestration:** ECS/EKS deployment

## Appendix

### Glossary
- **ALB:** Application Load Balancer
- **AZ:** Availability Zone
- **CRUD:** Create, Read, Update, Delete
- **IAM:** Identity and Access Management
- **RDS:** Relational Database Service
- **VPC:** Virtual Private Cloud

### References
- Flask Documentation: https://flask.palletsprojects.com/
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- AWS Well-Architected Framework: https://aws.amazon.com/architecture/well-architected/
