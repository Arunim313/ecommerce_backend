from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel
from typing import Optional, List
from .utils import (
    get_products_filtered,
    search_products,
    get_product_by_id,
    get_total_products_count_filtered
)

router = APIRouter()

# Pydantic models
class PublicProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    stock: int
    category: str
    image_url: Optional[str]

class PublicProductListResponse(BaseModel):
    products: List[PublicProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

@router.get("", response_model=PublicProductListResponse)
async def get_products_public(
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    sort_by: Optional[str] = Query("created_at", description="Sort by: name, price, created_at"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page")
):
    """Get list of products with filters and pagination (Public access)"""
    try:
        # Validate price range
        if min_price is not None and max_price is not None and min_price > max_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="min_price cannot be greater than max_price"
            )
        
        # Validate sort_by parameter
        valid_sort_fields = ["name", "price", "created_at"]
        if sort_by not in valid_sort_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sort_by field. Must be one of: {', '.join(valid_sort_fields)}"
            )
        
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get filtered products
        products = get_products_filtered(
            category=category,
            min_price=min_price,
            max_price=max_price,
            sort_by=sort_by,
            limit=page_size,
            offset=offset
        )
        
        # Get total count with same filters
        total_count = get_total_products_count_filtered(
            category=category,
            min_price=min_price,
            max_price=max_price
        )
        
        total_pages = (total_count + page_size - 1) // page_size
        
        product_responses = []
        for product in products:
            product_responses.append(PublicProductResponse(
                id=product[0],
                name=product[1],
                description=product[2],
                price=product[3],
                stock=product[4],
                category=product[5],
                image_url=product[6]
            ))
        
        return PublicProductListResponse(
            products=product_responses,
            total=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/search", response_model=PublicProductListResponse)
async def search_products_public(
    keyword: str = Query(..., min_length=1, description="Search keyword"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page")
):
    """Search products by keyword (Public access)"""
    try:
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Search products
        products = search_products(
            keyword=keyword,
            limit=page_size,
            offset=offset
        )
        
        # Get total count for search
        total_count = get_total_products_count_filtered(search_keyword=keyword)
        total_pages = (total_count + page_size - 1) // page_size
        
        product_responses = []
        for product in products:
            product_responses.append(PublicProductResponse(
                id=product[0],
                name=product[1],
                description=product[2],
                price=product[3],
                stock=product[4],
                category=product[5],
                image_url=product[6]
            ))
        
        return PublicProductListResponse(
            products=product_responses,
            total=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{product_id}", response_model=PublicProductResponse)
async def get_product_public(product_id: int):
    """Get product details by ID (Public access)"""
    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return PublicProductResponse(
        id=product[0],
        name=product[1],
        description=product[2],
        price=product[3],
        stock=product[4],
        category=product[5],
        image_url=product[6]
    )