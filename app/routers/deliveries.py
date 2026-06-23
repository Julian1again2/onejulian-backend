from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app import auth, models, schemas
from app.database import get_db


router = APIRouter(prefix="/api/v1/deliveries", tags=["deliveries"])


@router.get("/", response_model=list[schemas.DeliveryOut])
def list_deliveries(
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user),
):
    return db.query(models.Delivery).filter(models.Delivery.owner_id == current_user.id).all()


@router.post("/", response_model=schemas.DeliveryOut, status_code=status.HTTP_201_CREATED)
def create_delivery(
    delivery: schemas.DeliveryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user),
):
    db_delivery = models.Delivery(
        title=delivery.title,
        description=delivery.description,
        status=delivery.status or "pending",
        owner_id=current_user.id,
    )
    db.add(db_delivery)
    db.commit()
    db.refresh(db_delivery)
    return db_delivery


@router.get("/{delivery_id}", response_model=schemas.DeliveryOut)
def get_delivery(
    delivery_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user),
):
    delivery = (
        db.query(models.Delivery)
        .filter(models.Delivery.id == delivery_id, models.Delivery.owner_id == current_user.id)
        .first()
    )
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return delivery


@router.patch("/{delivery_id}", response_model=schemas.DeliveryOut)
def update_delivery(
    delivery_id: int,
    delivery_update: schemas.DeliveryUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user),
):
    delivery = (
        db.query(models.Delivery)
        .filter(models.Delivery.id == delivery_id, models.Delivery.owner_id == current_user.id)
        .first()
    )
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")

    update_data = delivery_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(delivery, field, value)

    db.commit()
    db.refresh(delivery)
    return delivery


@router.delete("/{delivery_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_delivery(
    delivery_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user),
):
    delivery = (
        db.query(models.Delivery)
        .filter(models.Delivery.id == delivery_id, models.Delivery.owner_id == current_user.id)
        .first()
    )
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")

    db.delete(delivery)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
