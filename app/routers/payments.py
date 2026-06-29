from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import auth, models, schemas
from app.database import get_db
from app.eventing import record_event, trigger_event

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])


@router.post("/", response_model=schemas.PaymentOut, status_code=status.HTTP_201_CREATED)
def create_payment(payment: schemas.PaymentCreate, db: Session = Depends(get_db), current_user=Depends(auth.get_current_user)):
    db_payment = models.Payment(order_id=payment.order_id, amount_usd=payment.amount_usd, status=payment.status or "created", owner_id=current_user.id)
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    payload = {"payment_id": db_payment.id, "order_id": db_payment.order_id, "amount_usd": db_payment.amount_usd, "status": db_payment.status, "owner_id": db_payment.owner_id}
    record_event("payment.created", payload)
    trigger_event("payment.created", payload)
    return db_payment


@router.get("/", response_model=list[schemas.PaymentOut])
def list_payments(db: Session = Depends(get_db), current_user=Depends(auth.get_current_user)):
    return db.query(models.Payment).filter(models.Payment.owner_id == current_user.id).all()


@router.get("/{payment_id}", response_model=schemas.PaymentOut)
def get_payment(payment_id: int, db: Session = Depends(get_db), current_user=Depends(auth.get_current_user)):
    payment = db.query(models.Payment).filter(models.Payment.id == payment_id, models.Payment.owner_id == current_user.id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.post("/{payment_id}/capture", response_model=schemas.PaymentOut)
def capture_payment(payment_id: int, db: Session = Depends(get_db), current_user=Depends(auth.get_current_user)):
    payment = db.query(models.Payment).filter(models.Payment.id == payment_id, models.Payment.owner_id == current_user.id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    payment.status = "captured"
    db.commit()
    db.refresh(payment)
    payload = {"payment_id": payment.id, "order_id": payment.order_id, "amount_usd": payment.amount_usd, "status": payment.status, "owner_id": payment.owner_id}
    record_event("payment.captured", payload)
    trigger_event("payment.captured", payload)
    return payment


@router.post("/{payment_id}/refund", response_model=schemas.RefundOut, status_code=status.HTTP_201_CREATED)
def create_refund(payment_id: int, refund: schemas.RefundCreate, db: Session = Depends(get_db), current_user=Depends(auth.get_current_user)):
    payment = db.query(models.Payment).filter(models.Payment.id == payment_id, models.Payment.owner_id == current_user.id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    db_refund = models.Refund(payment_id=payment.id, amount_usd=refund.amount_usd, status=refund.status or "created", owner_id=current_user.id)
    db.add(db_refund)
    payment.status = "refunded"
    db.commit()
    db.refresh(db_refund)
    payload = {"refund_id": db_refund.id, "payment_id": db_refund.payment_id, "amount_usd": db_refund.amount_usd, "status": db_refund.status, "owner_id": db_refund.owner_id}
    record_event("refund.created", payload)
    trigger_event("refund.created", payload)
    return db_refund


@router.get("/refunds/", response_model=list[schemas.RefundOut])
def list_refunds(db: Session = Depends(get_db), current_user=Depends(auth.get_current_user)):
    return db.query(models.Refund).filter(models.Refund.owner_id == current_user.id).all()
