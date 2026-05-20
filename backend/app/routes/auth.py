from fastapi import APIRouter, HTTPException
from app.database.db import SessionLocal
from app.models.user_model import User

from app.services.auth_service import (
    hash_password,
    verify_password
)

from app.services.jwt_service import (
    create_access_token
)

router = APIRouter()

@router.post("/signup")
async def signup(data: dict):

    db = SessionLocal()

    existing_user = db.query(User).filter(
        User.email == data["email"]
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    hashed_pw = hash_password(data["password"])

    new_user = User(
        email=data["email"],
        hashed_password=hashed_pw
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    db.close()

    return {
        "message": "User created successfully"
    }

@router.post("/login")
async def login(data: dict):

    db = SessionLocal()

    user = db.query(User).filter(
        User.email == data["email"]
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    valid_password = verify_password(
        data["password"],
        user.hashed_password
    )

    if not valid_password:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_access_token({
        "sub": user.email
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }