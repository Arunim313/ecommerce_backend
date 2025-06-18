import sqlite3
from typing import List, Tuple, Optional
from core.database import get_database_connection

def get_user_orders(user_id: int) -> List[Tuple]:
    """Get all orders for a user"""
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
    return orders

def get_order_by_id(order_id: int) -> Optional[Tuple]:
    """Get order by ID"""
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, user_id, total_amount, shipping_address, payment_method, order_status, created_at
        FROM orders
        WHERE id = ?
    ''', (order_id,))
    order = cursor.fetchone()
    conn.close()
    return order

def get_order_items(order_id: int) -> List[Tuple]:
    """Get all items for a specific order"""
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
    return items
