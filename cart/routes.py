# cart/routes.py
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import List, Optional
from auth.utils import get_current_user
from .utils import (
    add_to_cart,
    get_cart_items,
    remove_from_cart,
    update_cart_quantity,
    get_cart_total
)

router = APIRouter()

# Pydantic models
class AddToCartRequest(BaseModel):
    product_id: int
    quantity: int

class UpdateCartRequest(BaseModel):
    quantity: int

class CartItemResponse(BaseModel):
    product_id: int
    product_name: str
    product_price: float
    quantity: int
    subtotal: float
    image_url: Optional[str] = None

class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total_items: int
    total_amount: float

@router.post("", response_model=dict)
async def add_to_cart_api(
    request: AddToCartRequest,
    current_user: dict = Depends(get_current_user)
):
    """Add item to cart (User only)"""
    try:
        if request.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be greater than 0"
            )
        
        success = add_to_cart(
            user_id=current_user["id"],
            product_id=request.product_id,
            quantity=request.quantity
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to add item to cart. Product may not exist or insufficient stock."
            )
        
        return {"message": "Item added to cart successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("", response_model=CartResponse)
async def view_cart_api(
    current_user: dict = Depends(get_current_user)
):
    """View cart items (User only)"""
    try:
        cart_items = get_cart_items(current_user["id"])
        total_amount = get_cart_total(current_user["id"])
        
        # Convert to response format
        items_response = []
        total_items = 0
        
        for item in cart_items:
            items_response.append(CartItemResponse(
                product_id=item[0],
                product_name=item[1],
                product_price=item[2],
                quantity=item[3],
                subtotal=item[4],
                image_url=item[5]
            ))
            total_items += item[3]
        
        return CartResponse(
            items=items_response,
            total_items=total_items,
            total_amount=total_amount
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/{product_id}")
async def remove_from_cart_api(
    product_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Remove item from cart (User only)"""
    try:
        success = remove_from_cart(
            user_id=current_user["id"],
            product_id=product_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found in cart"
            )
        
        return {"message": "Item removed from cart successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/{product_id}")
async def update_cart_quantity_api(
    product_id: int,
    request: UpdateCartRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update item quantity in cart (User only)"""
    try:
        if request.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be greater than 0"
            )
        
        success = update_cart_quantity(
            user_id=current_user["id"],
            product_id=product_id,
            quantity=request.quantity
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found in cart or insufficient stock"
            )
        
        return {"message": "Cart quantity updated successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 