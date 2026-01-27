from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.schemas.auth import LoginRequest, LoginResponse, UserResponse
from app.models.user import User

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login endpoint - returns JWT tokens
    """
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()

    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.from_orm(user)
    )


@router.post("/logout")
async def logout():
    """
    Logout endpoint - client should discard tokens
    """
    return {"message": "Successfully logged out"}
