import sqlite3
from datetime import datetime
from typing import Optional, List, Tuple
from core.database import get_database_connection

def init_products_db():
    """Initialize the products database table"""
    # This function is now handled by core.database.init_database()
    pass

def create_product(
    name: str,
    description: str,
    price: float,
    stock: int,
    category: str,
    image_url: Optional[str] = None
) -> int:
    """Create a new product in the database"""
    if price < 0:
        raise ValueError("Price cannot be negative")
    if stock < 0:
        raise ValueError("Stock cannot be negative")
    
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO products (name, description, price, stock, category, image_url)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, description, price, stock, category, image_url))
    
    product_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return product_id

def get_products(limit: int = 10, offset: int = 0) -> List[Tuple]:
    """Get products with pagination"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, description, price, stock, category, image_url, created_at, updated_at
        FROM products
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    ''', (limit, offset))
    
    products = cursor.fetchall()
    conn.close()
    
    return products

def get_products_filtered(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: str = "created_at",
    limit: int = 10,
    offset: int = 0
) -> List[Tuple]:
    """Get products with filters and sorting"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Build WHERE clause
    where_conditions = []
    params = []
    
    if category:
        where_conditions.append("category = ?")
        params.append(category)
    
    if min_price is not None:
        where_conditions.append("price >= ?")
        params.append(min_price)
    
    if max_price is not None:
        where_conditions.append("price <= ?")
        params.append(max_price)
    
    where_clause = ""
    if where_conditions:
        where_clause = "WHERE " + " AND ".join(where_conditions)
    
    # Validate sort_by parameter
    valid_sort_fields = ["name", "price", "created_at"]
    if sort_by not in valid_sort_fields:
        sort_by = "created_at"
    
    # Build ORDER BY clause
    order_clause = f"ORDER BY {sort_by}"
    if sort_by == "created_at":
        order_clause += " DESC"
    
    query = f'''
        SELECT id, name, description, price, stock, category, image_url, created_at, updated_at
        FROM products
        {where_clause}
        {order_clause}
        LIMIT ? OFFSET ?
    '''
    
    params.extend([limit, offset])
    cursor.execute(query, params)
    
    products = cursor.fetchall()
    conn.close()
    
    return products

def search_products(
    keyword: str,
    limit: int = 10,
    offset: int = 0
) -> List[Tuple]:
    """Search products by keyword in name and description"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    search_pattern = f"%{keyword}%"
    
    cursor.execute('''
        SELECT id, name, description, price, stock, category, image_url, created_at, updated_at
        FROM products
        WHERE name LIKE ? OR description LIKE ?
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    ''', (search_pattern, search_pattern, limit, offset))
    
    products = cursor.fetchall()
    conn.close()
    
    return products

def get_product_by_id(product_id: int) -> Optional[Tuple]:
    """Get product by ID"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, description, price, stock, category, image_url, created_at, updated_at
        FROM products
        WHERE id = ?
    ''', (product_id,))
    
    product = cursor.fetchone()
    conn.close()
    
    return product

def update_product(
    product_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    price: Optional[float] = None,
    stock: Optional[int] = None,
    category: Optional[str] = None,
    image_url: Optional[str] = None
) -> bool:
    """Update product by ID"""
    # Build update query dynamically
    update_fields = []
    params = []
    
    if name is not None:
        update_fields.append("name = ?")
        params.append(name)
    
    if description is not None:
        update_fields.append("description = ?")
        params.append(description)
    
    if price is not None:
        if price < 0:
            raise ValueError("Price cannot be negative")
        update_fields.append("price = ?")
        params.append(price)
    
    if stock is not None:
        if stock < 0:
            raise ValueError("Stock cannot be negative")
        update_fields.append("stock = ?")
        params.append(stock)
    
    if category is not None:
        update_fields.append("category = ?")
        params.append(category)
    
    if image_url is not None:
        update_fields.append("image_url = ?")
        params.append(image_url)
    
    if not update_fields:
        return True  # No fields to update
    
    params.append(product_id)
    
    conn = get_database_connection()
    cursor = conn.cursor()
    
    query = f"UPDATE products SET {', '.join(update_fields)} WHERE id = ?"
    cursor.execute(query, params)
    
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return success

def delete_product(product_id: int) -> bool:
    """Delete product by ID"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return success

def get_total_products_count() -> int:
    """Get total count of products"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]
    conn.close()
    
    return count

def get_total_products_count_filtered(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search_keyword: Optional[str] = None
) -> int:
    """Get total count of products with filters"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Build WHERE clause
    where_conditions = []
    params = []
    
    if category:
        where_conditions.append("category = ?")
        params.append(category)
    
    if min_price is not None:
        where_conditions.append("price >= ?")
        params.append(min_price)
    
    if max_price is not None:
        where_conditions.append("price <= ?")
        params.append(max_price)
    
    if search_keyword:
        search_pattern = f"%{search_keyword}%"
        where_conditions.append("(name LIKE ? OR description LIKE ?)")
        params.extend([search_pattern, search_pattern])
    
    where_clause = ""
    if where_conditions:
        where_clause = "WHERE " + " AND ".join(where_conditions)
    
    query = f"SELECT COUNT(*) FROM products {where_clause}"
    cursor.execute(query, params)
    
    count = cursor.fetchone()[0]
    conn.close()
    
    return count