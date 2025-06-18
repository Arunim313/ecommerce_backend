import sqlite3
from datetime import datetime
from typing import Optional, List, Tuple
from products.utils import get_product_by_id, update_product
from core.database import get_database_connection

def init_cart_db():
    """Initialize the cart database table"""
    # This function is now handled by core.database.init_database()
    pass

def add_to_cart(user_id: int, product_id: int, quantity: int) -> bool:
    """Add item to cart or update quantity if already exists"""
    try:
        # Check if product exists and has sufficient stock
        product = get_product_by_id(product_id)
        if not product:
            return False
        
        if product[4] < quantity:  # product[4] is stock
            return False
        
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Check if item already exists in cart
        cursor.execute('''
            SELECT quantity FROM cart 
            WHERE user_id = ? AND product_id = ?
        ''', (user_id, product_id))
        
        existing_item = cursor.fetchone()
        
        if existing_item:
            # Update quantity
            new_quantity = existing_item[0] + quantity
            if new_quantity > product[4]:  # Check stock again
                conn.close()
                return False
            
            cursor.execute('''
                UPDATE cart SET quantity = ? 
                WHERE user_id = ? AND product_id = ?
            ''', (new_quantity, user_id, product_id))
        else:
            # Add new item
            cursor.execute('''
                INSERT INTO cart (user_id, product_id, quantity)
                VALUES (?, ?, ?)
            ''', (user_id, product_id, quantity))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        return False

def get_cart_items(user_id: int) -> List[Tuple]:
    """Get all items in user's cart with product details"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            c.product_id,
            p.name,
            p.price,
            c.quantity,
            (p.price * c.quantity) as subtotal,
            p.image_url
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
        ORDER BY c.created_at DESC
    ''', (user_id,))
    
    items = cursor.fetchall()
    conn.close()
    
    return items

def remove_from_cart(user_id: int, product_id: int) -> bool:
    """Remove item from cart"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM cart 
        WHERE user_id = ? AND product_id = ?
    ''', (user_id, product_id))
    
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return success

def update_cart_quantity(user_id: int, product_id: int, quantity: int) -> bool:
    """Update quantity of item in cart"""
    try:
        # Check if product exists and has sufficient stock
        product = get_product_by_id(product_id)
        if not product:
            return False
        
        if product[4] < quantity:  # product[4] is stock
            return False
        
        conn = get_database_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE cart SET quantity = ? 
            WHERE user_id = ? AND product_id = ?
        ''', (quantity, user_id, product_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
        
    except Exception as e:
        return False

def get_cart_total(user_id: int) -> float:
    """Get total amount of items in cart"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT SUM(p.price * c.quantity) as total
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
    ''', (user_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result[0] else 0.0

def clear_cart(user_id: int) -> bool:
    """Clear all items from user's cart"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
    
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return success

def get_cart_item_count(user_id: int) -> int:
    """Get total number of items in cart"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT SUM(quantity) FROM cart WHERE user_id = ?
    ''', (user_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result[0] else 0

def check_cart_item_exists(user_id: int, product_id: int) -> bool:
    """Check if item exists in user's cart"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 1 FROM cart 
        WHERE user_id = ? AND product_id = ?
    ''', (user_id, product_id))
    
    exists = cursor.fetchone() is not None
    conn.close()
    
    return exists
