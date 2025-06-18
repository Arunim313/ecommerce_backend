from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import List, Optional
from auth.utils import get_current_user
from .utils import (
    create_order,
    process_dummy_payment
)
from cart.utils import get_cart_items, get_cart_total, clear_cart

router = APIRouter()

# Pydantic models
class CheckoutRequest(BaseModel):
    shipping_address: str
    payment_method: str = "dummy_payment"

class CheckoutResponse(BaseModel):
    order_id: int
    message: str
    total_amount: float

@router.post("", response_model=CheckoutResponse)
async def checkout_api(
    request: CheckoutRequest,
    current_user: dict = Depends(get_current_user)
):
    """Process checkout with dummy payment (User only)"""
    try:
        # Get cart items
        cart_items = get_cart_items(current_user["id"])
        if not cart_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart is empty"
            )
        
        total_amount = get_cart_total(current_user["id"])
        
        # Process dummy payment
        payment_success = process_dummy_payment(total_amount)
        if not payment_success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment failed"
            )
        
        # Create order
        order_id = create_order(
            user_id=current_user["id"],
            cart_items=cart_items,
            total_amount=total_amount,
            shipping_address=request.shipping_address,
            payment_method=request.payment_method
        )
        
        # Clear cart after successful order
        clear_cart(current_user["id"])
        
        return CheckoutResponse(
            order_id=order_id,
            message="Order placed successfully! Payment processed.",
            total_amount=total_amount
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 