from fastapi import APIRouter, Depends

from app import auth, schemas


router = APIRouter(prefix="/api/v1/clients", tags=["clients"])


@router.get("/me", response_model=schemas.UserOut)
def read_me(current_user=Depends(auth.get_current_user)):
    return current_user
