# E-Commerce API

A FastAPI-based e-commerce backend with authentication, product management, cart functionality, checkout, and order history.

## 🏗️ Project Structure

```
backend/
├── core/                    # Core configuration and database
│   ├── __init__.py
│   ├── config.py           # Centralized configuration
│   ├── database.py         # Database initialization and connection
│   └── logging.py          # Logging configuration
├── auth/                   # Authentication module
│   ├── __init__.py
│   ├── routes.py           # Auth endpoints
│   └── utils.py            # Auth utilities
├── products/               # Product management
│   ├── __init__.py
│   ├── routes.py           # Admin product endpoints
│   ├── public_routes.py    # Public product endpoints
│   └── utils.py            # Product utilities
├── cart/                   # Shopping cart
│   ├── __init__.py
│   ├── routes.py           # Cart endpoints
│   └── utils.py            # Cart utilities
├── checkout/               # Checkout and orders
│   ├── __init__.py
│   ├── routes.py           # Checkout endpoints
│   └── utils.py            # Checkout utilities
├── orders/                 # Order history
│   ├── __init__.py
│   ├── routes.py           # Order endpoints
│   └── utils.py            # Order utilities
├── logs/                   # Application logs (auto-generated)
│   └── app_YYYYMMDD_HHMMSS.log
├── main.py                 # FastAPI application
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## ⚙️ Configuration

The application uses centralized configuration through environment variables. Copy `.env.example` to `.env` and customize the settings:

```bash
cp .env.example .env
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | SQLite database file path | `auth.db` |
| `SECRET_KEY` | JWT secret key | `your-secret-key-change-in-production` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT access token expiry | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | JWT refresh token expiry | `7` |
| `RESET_TOKEN_EXPIRE_MINUTES` | Password reset token expiry | `15` |
| `SMTP_SERVER` | SMTP server for emails | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port | `587` |
| `SMTP_USERNAME` | Email username | `your-email@gmail.com` |
| `SMTP_PASSWORD` | Email password/app password | `your-app-password` |
| `APP_NAME` | Application name | `E-Commerce API` |
| `DEBUG` | Debug mode and logging level | `False` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `DUMMY_PAYMENT_SUCCESS_RATE` | Payment success rate | `0.9` |

### Configuration Validation

The application automatically validates critical settings on startup and shows warnings for:

- **Default SECRET_KEY**: Warns if using the default JWT secret key
- **Default Email Settings**: Warns if using default email configuration

**For Production:**
- Set a strong, unique `SECRET_KEY`
- Configure proper email settings for password reset functionality
- Set `DEBUG=False`

**Example .env for Production:**
```env
SECRET_KEY=your-super-secure-secret-key-here
SMTP_USERNAME=your-actual-email@gmail.com
SMTP_PASSWORD=your-actual-app-password
DEBUG=False
```

## 📝 Logging

The application includes comprehensive logging that can be controlled via the `DEBUG` environment variable:

### Logging Levels
- **DEBUG=False** (default): Shows INFO level logs to console only
- **DEBUG=True**: Shows DEBUG level logs to both console and timestamped log files in `logs/` folder

### Log Files
When `DEBUG=True`, log files are automatically created in the `logs/` folder with timestamps:
```
logs/
├── app_20250618_202132.log
├── app_20250618_203045.log
└── ...
```

### Log Format
```
2025-06-18 20:21:32 - module_name - LEVEL - Message
```

### Using Loggers in Your Code
```python
from core.logging import get_logger

logger = get_logger(__name__)

# Log levels
logger.debug("Debug information")
logger.info("General information")
logger.warning("Warning messages")
logger.error("Error messages")
```

## 🚀 Getting Started

1. **Install dependencies:**
   ```bash
   pip install fastapi uvicorn bcrypt pyjwt python-multipart pydantic[email]
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

4. **Access the API documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

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

## 🔧 Development

### Adding New Configuration

1. Add the variable to `core/config.py`:
   ```python
   NEW_SETTING: str = os.getenv("NEW_SETTING", "default_value")
   ```

2. Add it to `.env.example`:
   ```
   NEW_SETTING=your-value
   ```

### Database Changes

All database initialization is centralized in `core/database.py`. Add new tables there.

### Adding Logging

1. Import the logger in your module:
   ```python
   from core.logging import get_logger
   logger = get_logger(__name__)
   ```

2. Use appropriate log levels:
   - `logger.debug()` - Detailed information for debugging
   - `logger.info()` - General information about program execution
   - `logger.warning()` - Warning messages for potentially problematic situations
   - `logger.error()` - Error messages for serious problems

## 📝 Features

- ✅ User authentication with JWT
- ✅ Password reset via email
- ✅ Product management (CRUD)
- ✅ Public product browsing with filters
- ✅ Shopping cart functionality
- ✅ Dummy payment processing
- ✅ Order management
- ✅ Order history
- ✅ Centralized configuration
- ✅ Environment-based settings
- ✅ Database connection pooling
- ✅ Input validation with Pydantic
- ✅ Comprehensive error handling
- ✅ Structured logging system
- ✅ Debug mode with file logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
