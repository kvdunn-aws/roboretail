# RoboRetail API Specification

**Version:** 1.0  
**Base URL:** `https://api.roboretail.com`  
**Date:** February 11, 2026

## Overview

The RoboRetail API provides RESTful endpoints for managing robot e-commerce operations including user authentication, product catalog, shopping cart, orders, and administrative functions.

## Authentication

### Session-Based Authentication
All authenticated endpoints require a valid session token passed via cookie or Authorization header.

**Header Format:**
```
Authorization: Bearer <session_token>
```

**Cookie Format:**
```
session_token=<token>; HttpOnly; Secure
```

## API Endpoints

### 1. Authentication & User Management

#### 1.1 Register User
Create a new user account.

**Endpoint:** `POST /api/register`

**Request Body:**
```json
{
  "username": "string (3-50 chars, required)",
  "email": "string (valid email, required)",
  "password": "string (8+ chars, required)",
  "confirm_password": "string (must match password, required)"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "role": "customer"
  }
}
```

**Error Responses:**
- `400 Bad Request` - Invalid input data
- `409 Conflict` - Username or email already exists

---

#### 1.2 Login
Authenticate user and create session.

**Endpoint:** `POST /api/login`

**Request Body:**
```json
{
  "username": "string (required)",
  "password": "string (required)"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Login successful",
  "session_token": "abc123...",
  "user": {
    "id": 1,
    "username": "johndoe",
    "role": "customer"
  }
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid credentials
- `400 Bad Request` - Missing fields

---

#### 1.3 Logout
End user session.

**Endpoint:** `POST /api/logout`

**Authentication:** Required

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

#### 1.4 Get User Profile
Retrieve current user's profile information.

**Endpoint:** `GET /api/profile`

**Authentication:** Required

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "role": "customer",
  "avatar_url": "https://s3.amazonaws.com/avatars/user1.jpg",
  "created_at": "2026-02-11T10:00:00Z"
}
```

---

#### 1.5 Update User Profile
Update current user's profile.

**Endpoint:** `PUT /api/profile`

**Authentication:** Required

**Request Body:**
```json
{
  "email": "string (optional)",
  "current_password": "string (required if changing password)",
  "new_password": "string (optional)"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "newemail@example.com"
  }
}
```

---

#### 1.6 Upload Avatar
Upload user profile picture.

**Endpoint:** `POST /api/profile/avatar`

**Authentication:** Required

**Request:** Multipart form data
```
avatar: file (image/jpeg, image/png, max 5MB)
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Avatar uploaded successfully",
  "avatar_url": "https://s3.amazonaws.com/avatars/user1.jpg"
}
```

---

### 2. Product Catalog

#### 2.1 List Products
Get all robot products with optional filtering.

**Endpoint:** `GET /api/products`

**Query Parameters:**
- `category` (optional) - Filter by category
- `min_price` (optional) - Minimum price
- `max_price` (optional) - Maximum price
- `limit` (optional, default: 20) - Results per page
- `offset` (optional, default: 0) - Pagination offset

**Response (200 OK):**
```json
{
  "products": [
    {
      "id": 1,
      "name": "RoboVac 3000",
      "description": "Advanced cleaning robot",
      "price": 299.99,
      "category": "Cleaning",
      "manufacturer": "RoboTech",
      "image_url": "https://s3.amazonaws.com/products/robovac3000.jpg",
      "stock_quantity": 50,
      "average_rating": 4.5
    }
  ],
  "total": 100,
  "limit": 20,
  "offset": 0
}
```

---

#### 2.2 Get Product Details
Get detailed information about a specific robot.

**Endpoint:** `GET /api/products/{id}`

**Path Parameters:**
- `id` (integer, required) - Product ID

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "RoboVac 3000",
  "description": "Advanced cleaning robot with AI navigation",
  "price": 299.99,
  "category": "Cleaning",
  "manufacturer": "RoboTech",
  "image_url": "https://s3.amazonaws.com/products/robovac3000.jpg",
  "stock_quantity": 50,
  "specifications": {
    "battery_life": "120 minutes",
    "weight": "3.5 kg",
    "dimensions": "35cm x 35cm x 10cm"
  },
  "average_rating": 4.5,
  "review_count": 42
}
```

**Error Responses:**
- `404 Not Found` - Product does not exist

---

#### 2.3 Search Products
Search robots by keyword.

**Endpoint:** `GET /api/products/search`

**Query Parameters:**
- `q` (required) - Search query
- `limit` (optional, default: 20)
- `offset` (optional, default: 0)

**Response (200 OK):**
```json
{
  "results": [
    {
      "id": 1,
      "name": "RoboVac 3000",
      "description": "Advanced cleaning robot",
      "price": 299.99,
      "image_url": "https://s3.amazonaws.com/products/robovac3000.jpg"
    }
  ],
  "query": "vacuum",
  "total": 5
}
```

---

#### 2.4 Create Product (Admin)
Add a new robot to the catalog.

**Endpoint:** `POST /api/products`

**Authentication:** Required (Admin role)

**Request Body:**
```json
{
  "name": "string (required)",
  "description": "string (required)",
  "price": "number (required)",
  "category": "string (required)",
  "manufacturer": "string (required)",
  "image_url": "string (optional)",
  "stock_quantity": "integer (required)"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Product created successfully",
  "product": {
    "id": 101,
    "name": "RoboMow Pro",
    "price": 599.99
  }
}
```

---

#### 2.5 Update Product (Admin)
Update existing robot information.

**Endpoint:** `PUT /api/products/{id}`

**Authentication:** Required (Admin role)

**Request Body:** Same as Create Product (all fields optional)

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Product updated successfully"
}
```

---

#### 2.6 Delete Product (Admin)
Remove a robot from the catalog.

**Endpoint:** `DELETE /api/products/{id}`

**Authentication:** Required (Admin role)

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Product deleted successfully"
}
```

---

### 3. Shopping Cart

#### 3.1 Get Cart
Retrieve current user's shopping cart.

**Endpoint:** `GET /api/cart`

**Authentication:** Required

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "product_id": 5,
      "product_name": "RoboVac 3000",
      "price": 299.99,
      "quantity": 2,
      "subtotal": 599.98
    }
  ],
  "total": 599.98,
  "item_count": 2
}
```

---

#### 3.2 Add to Cart
Add a robot to shopping cart.

**Endpoint:** `POST /api/cart`

**Authentication:** Required

**Request Body:**
```json
{
  "product_id": "integer (required)",
  "quantity": "integer (required, min: 1)"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Item added to cart",
  "cart_item_count": 3
}
```

---

#### 3.3 Remove from Cart
Remove an item from cart.

**Endpoint:** `DELETE /api/cart/{item_id}`

**Authentication:** Required

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Item removed from cart"
}
```

---

### 4. Orders

#### 4.1 Checkout
Place an order from cart items.

**Endpoint:** `POST /api/checkout`

**Authentication:** Required

**Request Body:**
```json
{
  "shipping_address": "string (required)"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Order placed successfully",
  "order": {
    "id": 1001,
    "total_amount": 599.98,
    "status": "pending",
    "created_at": "2026-02-11T15:30:00Z"
  }
}
```

---

#### 4.2 Get User Orders
Retrieve current user's order history.

**Endpoint:** `GET /api/orders`

**Authentication:** Required

**Response (200 OK):**
```json
{
  "orders": [
    {
      "id": 1001,
      "total_amount": 599.98,
      "status": "shipped",
      "created_at": "2026-02-11T15:30:00Z",
      "item_count": 2
    }
  ]
}
```

---

#### 4.3 Get Order Details
Get detailed information about a specific order.

**Endpoint:** `GET /api/orders/{id}`

**Authentication:** Required

**Response (200 OK):**
```json
{
  "id": 1001,
  "user_id": 1,
  "total_amount": 599.98,
  "status": "shipped",
  "shipping_address": "123 Main St, City, State 12345",
  "items": [
    {
      "product_id": 5,
      "product_name": "RoboVac 3000",
      "quantity": 2,
      "price": 299.99
    }
  ],
  "created_at": "2026-02-11T15:30:00Z",
  "updated_at": "2026-02-12T10:00:00Z"
}
```

---

### 5. Reviews

#### 5.1 Get Product Reviews
Get all reviews for a specific robot.

**Endpoint:** `GET /api/products/{id}/reviews`

**Response (200 OK):**
```json
{
  "reviews": [
    {
      "id": 1,
      "user_id": 5,
      "username": "janedoe",
      "rating": 5,
      "comment": "Excellent robot! Works perfectly.",
      "created_at": "2026-02-10T14:20:00Z"
    }
  ],
  "average_rating": 4.5,
  "total_reviews": 42
}
```

---

#### 5.2 Submit Review
Add a review for a robot.

**Endpoint:** `POST /api/products/{id}/reviews`

**Authentication:** Required

**Request Body:**
```json
{
  "rating": "integer (1-5, required)",
  "comment": "string (optional, max 1000 chars)"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Review submitted successfully",
  "review": {
    "id": 43,
    "rating": 5,
    "created_at": "2026-02-11T16:00:00Z"
  }
}
```

---

### 6. Admin Operations

#### 6.1 List All Users
Get all registered users.

**Endpoint:** `GET /api/admin/users`

**Authentication:** Required (Admin role)

**Response (200 OK):**
```json
{
  "users": [
    {
      "id": 1,
      "username": "johndoe",
      "email": "john@example.com",
      "role": "customer",
      "created_at": "2026-01-15T10:00:00Z"
    }
  ],
  "total": 150
}
```

---

#### 6.2 Get User Details
Get detailed information about a specific user.

**Endpoint:** `GET /api/admin/users/{id}`

**Authentication:** Required (Admin role)

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "role": "customer",
  "order_count": 5,
  "total_spent": 1499.95,
  "created_at": "2026-01-15T10:00:00Z"
}
```

---

#### 6.3 Update User
Modify user information or promote to admin.

**Endpoint:** `PUT /api/admin/users/{id}`

**Authentication:** Required (Admin role)

**Request Body:**
```json
{
  "role": "string (optional, 'customer' or 'admin')",
  "email": "string (optional)"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "User updated successfully"
}
```

---

#### 6.4 Delete User
Remove a user account.

**Endpoint:** `DELETE /api/admin/users/{id}`

**Authentication:** Required (Admin role)

**Response (200 OK):**
```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

---

#### 6.5 List All Orders
Get all orders in the system.

**Endpoint:** `GET /api/admin/orders`

**Authentication:** Required (Admin role)

**Query Parameters:**
- `status` (optional) - Filter by order status
- `limit` (optional, default: 50)
- `offset` (optional, default: 0)

**Response (200 OK):**
```json
{
  "orders": [
    {
      "id": 1001,
      "user_id": 1,
      "username": "johndoe",
      "total_amount": 599.98,
      "status": "pending",
      "created_at": "2026-02-11T15:30:00Z"
    }
  ],
  "total": 500
}
```

---

#### 6.6 Update Order Status
Change order status.

**Endpoint:** `PUT /api/admin/orders/{id}`

**Authentication:** Required (Admin role)

**Request Body:**
```json
{
  "status": "string (required: 'pending', 'processing', 'shipped', 'delivered', 'cancelled')"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Order status updated successfully"
}
```

---

#### 6.7 Generate Reports
Generate system reports.

**Endpoint:** `GET /api/admin/reports`

**Authentication:** Required (Admin role)

**Query Parameters:**
- `type` (required) - Report type: 'sales', 'inventory', 'users'
- `start_date` (optional) - Start date (YYYY-MM-DD)
- `end_date` (optional) - End date (YYYY-MM-DD)
- `format` (optional, default: 'json') - Output format: 'json', 'csv'

**Response (200 OK):**
```json
{
  "report_type": "sales",
  "period": {
    "start": "2026-02-01",
    "end": "2026-02-11"
  },
  "data": {
    "total_sales": 15999.50,
    "order_count": 45,
    "average_order_value": 355.54
  }
}
```

---

#### 6.8 Export Data
Export data in various formats.

**Endpoint:** `POST /api/admin/export`

**Authentication:** Required (Admin role)

**Request Body:**
```json
{
  "type": "string (required: 'products', 'orders', 'users')",
  "format": "string (required: 'csv', 'pdf', 'xlsx')",
  "filters": "object (optional)"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "download_url": "https://s3.amazonaws.com/exports/products_20260211.csv",
  "expires_at": "2026-02-12T16:00:00Z"
}
```

---

## Error Response Format

All error responses follow this structure:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": "Additional error information (optional)"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| INVALID_INPUT | 400 | Request validation failed |
| UNAUTHORIZED | 401 | Authentication required |
| FORBIDDEN | 403 | Insufficient permissions |
| NOT_FOUND | 404 | Resource not found |
| CONFLICT | 409 | Resource already exists |
| SERVER_ERROR | 500 | Internal server error |

---

## Rate Limiting

- **Authenticated requests:** 1000 requests per hour
- **Unauthenticated requests:** 100 requests per hour
- **Admin operations:** 500 requests per hour

Rate limit headers included in all responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1707667200
```

---

## Versioning

API version is included in the base URL. Current version: v1

Future versions will be available at:
- `https://api.roboretail.com/v2/...`

---

## CORS Policy

Allowed origins:
- `https://roboretail.com`
- `https://www.roboretail.com`

Allowed methods: GET, POST, PUT, DELETE, OPTIONS

Allowed headers: Content-Type, Authorization

---

## Changelog

### Version 1.0 (2026-02-11)
- Initial API specification
- Authentication endpoints
- Product catalog management
- Shopping cart and orders
- Review system
- Admin operations
