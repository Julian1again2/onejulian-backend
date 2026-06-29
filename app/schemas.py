from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class DeliveryBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "pending"


class DeliveryCreate(DeliveryBase):
    pass


class DeliveryUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class DeliveryOut(DeliveryBase):
    id: int
    owner_id: int
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(UserBase):
    id: int
    created_at: Optional[datetime] = None
    deliveries: List[DeliveryOut] = []

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: Optional[str] = None


class PaymentBase(BaseModel):
    order_id: int
    amount_usd: float
    status: str = "created"


class PaymentCreate(PaymentBase):
    pass


class PaymentOut(PaymentBase):
    id: int
    owner_id: int
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class RefundBase(BaseModel):
    payment_id: int
    amount_usd: float
    status: str = "created"


class RefundCreate(RefundBase):
    pass


class RefundOut(RefundBase):
    id: int
    owner_id: int
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True
