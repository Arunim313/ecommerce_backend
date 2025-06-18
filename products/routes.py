from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi.security import HTTPBearer
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from decimal import Decimal
from .utils import (
    create_product,
    get_products,
    get_product_by_id,
    update_product,
    delete_product,
    get_total_products_count
)
from auth.utils import get_current_user

router = APIRouter()

# Pydantic models
class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    stock: int
    category: str
    image_url: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category: Optional[str] = None
    image_url: Optional[str] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    stock: int
    category: str
    image_url: Optional[str]
    created_at: str
    updated_at: str

class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

# Dependency to verify admin role
async def verify_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user

@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product_endpoint(
    product: ProductCreate,
    admin_user: dict = Depends(verify_admin)
):
    """Create a new product (Admin only)"""
    try:
        product_id = create_product(
            name=product.name,
            description=product.description,
            price=product.price,
            stock=product.stock,
            category=product.category,
            image_url=product.image_url
        )
        
        # Get the created product
        created_product = get_product_by_id(product_id)
        return ProductResponse(
            id=created_product[0],
            name=created_product[1],
            description=created_product[2],
            price=created_product[3],
            stock=created_product[4],
            category=created_product[5],
            image_url=created_product[6],
            created_at=created_product[7],
            updated_at=created_product[8]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/products", response_model=ProductListResponse)
async def get_products_endpoint(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    admin_user: dict = Depends(verify_admin)
):
    """Get list of products with pagination (Admin only)"""
    try:
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Get products
        products = get_products(limit=per_page, offset=offset)
        total_count = get_total_products_count()
        total_pages = (total_count + per_page - 1) // per_page
        
        product_responses = []
        for product in products:
            product_responses.append(ProductResponse(
                id=product[0],
                name=product[1],
                description=product[2],
                price=product[3],
                stock=product[4],
                category=product[5],
                image_url=product[6],
                created_at=product[7],
                updated_at=product[8]
            ))
        
        return ProductListResponse(
            products=product_responses,
            total=total_count,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product_endpoint(
    product_id: int,
    admin_user: dict = Depends(verify_admin)
):
    """Get product details by ID (Admin only)"""
    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return ProductResponse(
        id=product[0],
        name=product[1],
        description=product[2],
        price=product[3],
        stock=product[4],
        category=product[5],
        image_url=product[6],
        created_at=product[7],
        updated_at=product[8]
    )

@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product_endpoint(
    product_id: int,
    product_update: ProductUpdate,
    admin_user: dict = Depends(verify_admin)
):
    """Update product by ID (Admin only)"""
    # Check if product exists
    existing_product = get_product_by_id(product_id)
    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    try:
        # Update product
        success = update_product(
            product_id=product_id,
            name=product_update.name,
            description=product_update.description,
            price=product_update.price,
            stock=product_update.stock,
            category=product_update.category,
            image_url=product_update.image_url
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update product"
            )
        
        # Get the updated product
        updated_product = get_product_by_id(product_id)
        return ProductResponse(
            id=updated_product[0],
            name=updated_product[1],
            description=updated_product[2],
            price=updated_product[3],
            stock=updated_product[4],
            category=updated_product[5],
            image_url=updated_product[6],
            created_at=updated_product[7],
            updated_at=updated_product[8]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_endpoint(
    product_id: int,
    admin_user: dict = Depends(verify_admin)
):
    """Delete product by ID (Admin only)"""
    # Check if product exists
    existing_product = get_product_by_id(product_id)
    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    try:
        success = delete_product(product_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete product"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
