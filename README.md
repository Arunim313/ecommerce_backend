# E-Commerce API

A FastAPI-based e-commerce backend with authentication, product management, cart functionality, checkout, and order history.

---

## 🛠️ Complete Setup Guide

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd NQT-Python/backend
```

### 2. (Recommended) Create a virtual environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
- Copy the example env file and edit as needed:
```bash
cp .env.example .env  # or create .env manually
```
- Edit `.env` with your configuration (see below for important variables)

### 5. Run the application
```bash
python main.py
```

### 6. Access the API documentation
- Swagger UI: http://localhost:8000/docs

---

## 🐳 Docker Usage

You can run this application in a Docker container:

### 1. Build the Docker image
```bash
docker build -t ecommerce-api .
```

### 2. Run the container
```bash
docker run --env-file .env -p 8000:8000 ecommerce-api
```

- The app will be available at http://localhost:8000
- Logs will be written to the `logs/` directory inside the container (mount a volume if you want to persist logs)

---

## 📝 Environment Variables
- All configuration is loaded from the `.env` file in the project root.
- Example variables:
  - `DATABASE_URL=auth.db`
  - `SECRET_KEY=your-super-secret-key`
  - `DEBUG=True` (set to `True` to enable detailed logging)
  - `HOST=0.0.0.0`
  - `PORT=8000`

---


The application automatically validates critical settings on startup and shows warnings for:

- **Default SECRET_KEY**: Warns if using the default JWT secret key
- **Default Email Settings**: Warns if using default email configuration

## 📋 API Endpoints

### Authentication (`/auth`)
- `POST /auth/signup` - User registration
- `POST /auth/signin` - User login
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password

### Products (`/products`) - Public
- `GET /products` - List products with filters
- `GET /products/search` - Search products
- `GET /products/{product_id}` - Get product details

### Admin Products (`/admin`)
- `POST /admin/products` - Create product (Admin only)
- `GET /admin/products` - List products (Admin only)
- `GET /admin/products/{product_id}` - Get product (Admin only)
- `PUT /admin/products/{product_id}` - Update product (Admin only)
- `DELETE /admin/products/{product_id}` - Delete product (Admin only)

### Cart (`/cart`) - User only
- `POST /cart` - Add item to cart
- `GET /cart` - View cart
- `PUT /cart/{product_id}` - Update quantity
- `DELETE /cart/{product_id}` - Remove item

### Checkout (`/checkout`) - User only
- `POST /checkout` - Process checkout with dummy payment

### Orders (`/orders`) - User only
- `GET /orders` - View order history
- `GET /orders/{order_id}` - View order details

## 🔐 Authentication

The API uses JWT tokens for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### User Roles
- **user**: Can access cart, checkout, and order history
- **admin**: Can manage products and access all endpoints

## 💾 Database

The application uses SQLite with the following tables:
- `users` - User accounts
- `reset_tokens` - Password reset tokens
- `products` - Product catalog
- `cart` - Shopping cart items
- `orders` - Order information
- `order_items` - Individual items in orders


### Database Changes

All database initialization is centralized in `core/database.py`. Add new tables there.
