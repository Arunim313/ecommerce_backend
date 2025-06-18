from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List
from auth.utils import get_current_user
from .utils import get_user_orders, get_order_by_id, get_order_items

router = APIRouter()

class OrderItemResponse(BaseModel):
    product_id: int
    product_name: str
    product_price: float
    quantity: int
    subtotal: float

class OrderResponse(BaseModel):
    order_id: int
    user_id: int
    total_amount: float
    shipping_address: str
    payment_method: str
    order_status: str
    created_at: str
    items: List[OrderItemResponse]

class OrderHistoryResponse(BaseModel):
    order_id: int
    created_at: str
    total_amount: float
    order_status: str

@router.get("", response_model=List[OrderHistoryResponse])
async def get_orders(current_user: dict = Depends(get_current_user)):
    """Get order history for the current user"""
    orders = get_user_orders(current_user["id"])
    return [
        OrderHistoryResponse(
            order_id=o[0],
            created_at=o[6],
            total_amount=o[2],
            order_status=o[5]
        ) for o in orders
    ]

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_detail(order_id: int, current_user: dict = Depends(get_current_user)):
    """Get order details for the current user"""
    order = get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order[1] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your order")
    items = get_order_items(order_id)
    return OrderResponse(
        order_id=order[0],
        user_id=order[1],
        total_amount=order[2],
        shipping_address=order[3],
        payment_method=order[4],
        order_status=order[5],
        created_at=order[6],
        items=[
            OrderItemResponse(
                product_id=i[1],
                product_name=i[2],
                product_price=i[3],
                quantity=i[4],
                subtotal=i[5]
            ) for i in items
        ]
    )
