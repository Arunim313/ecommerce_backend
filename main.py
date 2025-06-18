# main.py
from fastapi import FastAPI
from auth.routes import router as auth_router
from products.routes import router as products_router
from products.public_routes import router as public_products_router
from cart.routes import router as cart_router
from checkout.routes import router as checkout_router
from orders.routes import router as orders_router
from core.database import init_database
from core.config import settings
from core.logging import get_logger, setup_logging

# Setup logging explicitly after config is loaded
setup_logging()

# Initialize logger
logger = get_logger(__name__)

# Debug logging test
logger.debug(f"Application starting with DEBUG={settings.DEBUG}")
logger.debug(f"Database URL: {settings.DATABASE_URL}")
logger.debug(f"App Name: {settings.APP_NAME}")
logger.debug(f"Host: {settings.HOST}, Port: {settings.PORT}")

app = FastAPI(title=settings.APP_NAME)

# Initialize database
logger.info("Initializing database...")
logger.debug("About to call init_database()")
init_database()
logger.debug("Database initialization completed")
logger.info("Database initialized successfully")

# Include routers with debug logging
logger.debug("Including authentication router...")
app.include_router(auth_router, prefix="/auth", tags=["authentication"])

logger.debug("Including admin products router...")
app.include_router(products_router, prefix="/admin", tags=["admin-products"])

logger.debug("Including public products router...")
app.include_router(public_products_router, prefix="/products", tags=["public-products"])

logger.debug("Including cart router...")
app.include_router(cart_router, prefix="/cart", tags=["cart"])

logger.debug("Including checkout router...")
app.include_router(checkout_router, prefix="/checkout", tags=["checkout"])

logger.debug("Including orders router...")
app.include_router(orders_router, prefix="/orders", tags=["orders"])

logger.info(f"Application '{settings.APP_NAME}' started successfully")
logger.debug("All routers included successfully")

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on {settings.HOST}:{settings.PORT}")
    logger.debug("About to start uvicorn server")
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)