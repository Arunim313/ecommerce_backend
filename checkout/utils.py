# checkout/utils.py
import sqlite3
import random
import time
from datetime import datetime
from typing import Optional, List, Tuple
from products.utils import get_product_by_id, update_product
from core.database import get_database_connection
from core.config import settings
from core.logging import get_logger

# Initialize logger
logger = get_logger(__name__)

def init_checkout_db():
    """Initialize the checkout database tables"""
    # This function is now handled by core.database.init_database()
    pass

def process_dummy_payment(amount: float) -> bool:
    """Process dummy payment - simulates payment processing"""
    try:
        logger.debug(f"Processing dummy payment for amount: ${amount}")
        # Simulate payment processing time
        time.sleep(0.1)
        
        # Simulate payment success/failure (configurable success rate)
        if random.random() < settings.DUMMY_PAYMENT_SUCCESS_RATE:
            logger.info(f"Payment successful for amount: ${amount}")
            return True
        else:
            logger.warning(f"Payment failed for amount: ${amount}")
            return False
    except Exception as e:
        logger.error(f"Payment processing error: {e}")
        return False

def create_order(
    user_id: int,
    cart_items: List[Tuple],
    total_amount: float,
    shipping_address: str,
    payment_method: str
) -> int:
    """Create a new order from cart items"""
    logger.info(f"Creating order for user {user_id} with {len(cart_items)} items")
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Create order
        cursor.execute('''
            INSERT INTO orders (user_id, total_amount, shipping_address, payment_method, order_status)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, total_amount, shipping_address, payment_method, 'confirmed'))
        
        order_id = cursor.lastrowid
        logger.debug(f"Created order with ID: {order_id}")
        
        # Create order items and update product stock
        for item in cart_items:
            try:
                product_id, product_name, product_price, quantity, subtotal, image_url = item
                
                # Insert order item
                cursor.execute('''
                    INSERT INTO order_items (order_id, product_id, product_name, product_price, quantity, subtotal)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (order_id, product_id, product_name, product_price, quantity, subtotal))
                
                # Update product stock within the same transaction
                cursor.execute('''
                    UPDATE products SET stock = stock - ? WHERE id = ?
                ''', (quantity, product_id))
                
                logger.debug(f"Added item to order: {product_name} (qty: {quantity})")
                
            except Exception as item_error:
                logger.error(f"Error processing cart item: {item_error}")
                raise item_error
        
        conn.commit()
        logger.info(f"Order {order_id} created successfully")
        return order_id
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating order: {e}")
        raise e
    finally:
        conn.close()

def get_order_by_id(order_id: int) -> Optional[Tuple]:
    """Get order by ID"""
    logger.debug(f"Fetching order by ID: {order_id}")
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, user_id, total_amount, shipping_address, payment_method, order_status, created_at
        FROM orders
        WHERE id = ?
    ''', (order_id,))
    
    order = cursor.fetchone()
    conn.close()
    
    if order:
        logger.debug(f"Found order {order_id}")
    else:
        logger.debug(f"Order {order_id} not found")
    
    return order

def get_user_orders(user_id: int) -> List[Tuple]:
    """Get all orders for a user"""
    logger.debug(f"Fetching orders for user: {user_id}")
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, user_id, total_amount, shipping_address, payment_method, order_status, created_at
        FROM orders
        WHERE user_id = ?
        ORDER BY created_at DESC
    ''', (user_id,))
    
    orders = cursor.fetchall()
    conn.close()
    
    logger.debug(f"Found {len(orders)} orders for user {user_id}")
    return orders

def get_order_items(order_id: int) -> List[Tuple]:
    """Get all items for a specific order"""
    logger.debug(f"Fetching items for order: {order_id}")
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, product_id, product_name, product_price, quantity, subtotal
        FROM order_items
        WHERE order_id = ?
        ORDER BY id
    ''', (order_id,))
    
    items = cursor.fetchall()
    conn.close()
    
    logger.debug(f"Found {len(items)} items for order {order_id}")
    return items

def update_order_status(order_id: int, status: str) -> bool:
    """Update order status"""
    logger.info(f"Updating order {order_id} status to: {status}")
    valid_statuses = ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
    if status not in valid_statuses:
        logger.warning(f"Invalid order status: {status}")
        return False
    
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE orders SET order_status = ? WHERE id = ?
    ''', (status, order_id))
    
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    if success:
        logger.info(f"Order {order_id} status updated to {status}")
    else:
        logger.warning(f"Failed to update order {order_id} status")
    
    return success

def get_order_total(order_id: int) -> float:
    """Get total amount for an order"""
    logger.debug(f"Fetching total for order: {order_id}")
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT total_amount FROM orders WHERE id = ?
    ''', (order_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    total = result[0] if result else 0.0
    logger.debug(f"Order {order_id} total: ${total}")
    return total

def get_order_count(user_id: int) -> int:
    """Get total number of orders for a user"""
    logger.debug(f"Fetching order count for user: {user_id}")
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COUNT(*) FROM orders WHERE user_id = ?
    ''', (user_id,))
    
    count = cursor.fetchone()[0]
    conn.close()
    
    logger.debug(f"User {user_id} has {count} orders")
    return count

def cancel_order(order_id: int, user_id: int) -> bool:
    """Cancel an order and restore product stock"""
    logger.info(f"Attempting to cancel order {order_id} for user {user_id}")
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Check if order exists and belongs to user
        cursor.execute('''
            SELECT order_status FROM orders 
            WHERE id = ? AND user_id = ?
        ''', (order_id, user_id))
        
        order = cursor.fetchone()
        if not order:
            logger.warning(f"Order {order_id} not found or doesn't belong to user {user_id}")
            return False
        
        if order[0] in ['shipped', 'delivered']:
            logger.warning(f"Cannot cancel order {order_id} - status is {order[0]}")
            return False
        
        # Get order items to restore stock
        order_items = get_order_items(order_id)
        
        # Restore product stock
        for item in order_items:
            product_id = item[1]
            quantity = item[4]
            
            product = get_product_by_id(product_id)
            if product:
                new_stock = product[4] + quantity
                update_product(product_id=product_id, stock=new_stock)
                logger.debug(f"Restored {quantity} units to product {product_id}")
        
        # Update order status to cancelled
        cursor.execute('''
            UPDATE orders SET order_status = 'cancelled' WHERE id = ?
        ''', (order_id,))
        
        conn.commit()
        logger.info(f"Order {order_id} cancelled successfully")
        return True
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error cancelling order {order_id}: {e}")
        return False
    finally:
        conn.close() 