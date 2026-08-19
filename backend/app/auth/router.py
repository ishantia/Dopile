from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.core.security import verify_password, create_access_token, create_refresh_token, generate_csrf_token, decode_token
from app.core.rate_limit import check_rate_limit, limiter
from app.core.config import settings
from app.audit.service import log_audit_event
from app.auth.schemas import LoginRequest, TokenResponse, UserResponse
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    client_ip = request.client.host if request.client else "127.0.0.1"
    rate_key = f"login:{client_ip}:{payload.username}"

    # Check brute force rate limit
    is_limited, retry_after = limiter.is_rate_limited(rate_key, max_requests=5, window_seconds=300)
    if is_limited:
        log_audit_event(db, "LOGIN_BLOCKED", "USER", source_ip=client_ip, metadata={"username": payload.username})
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed login attempts. Try again in {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)}
        )

    # Generic security message (never reveal whether username exists)
    invalid_credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password"
    )

    user = db.query(User).filter(User.username == payload.username).first()
    if not user:
        limiter.record_failed_login(rate_key)
        log_audit_event(db, "LOGIN_FAILURE", "USER", source_ip=client_ip, metadata={"username": payload.username})
        raise invalid_credentials_exc

    if not user.is_active:
        limiter.record_failed_login(rate_key)
        log_audit_event(db, "LOGIN_FAILURE_DEACTIVATED", "USER", actor_user_id=user.id, source_ip=client_ip)
        raise invalid_credentials_exc

    if not verify_password(payload.password, user.password_hash):
        limiter.record_failed_login(rate_key)
        log_audit_event(db, "LOGIN_FAILURE", "USER", actor_user_id=user.id, source_ip=client_ip)
        raise invalid_credentials_exc

    # Successful login: reset rate limit attempts
    limiter.reset_failures(rate_key)
    
    # Update last login timestamp
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    # Create tokens
    access_token = create_access_token({"sub": user.id, "role": user.role})
    refresh_token = create_refresh_token({"sub": user.id})
    csrf_token = generate_csrf_token(user.id)

    # Set HttpOnly cookies
    is_secure = not settings.is_dev()
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=is_secure,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=is_secure,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
    )
    response.headers["X-CSRF-Token"] = csrf_token

    log_audit_event(db, "LOGIN_SUCCESS", "USER", actor_user_id=user.id, source_ip=client_ip)

    return TokenResponse(
        access_token=access_token,
        csrf_token=csrf_token,
        token_type="bearer",
        expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    client_ip = request.client.host if request.client else "127.0.0.1"
    
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    log_audit_event(db, "LOGOUT", "USER", actor_user_id=current_user.id, source_ip=client_ip)
    return {"message": "Logged out successfully"}


@router.post("/refresh", response_model=TokenResponse)
def refresh_token_endpoint(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        # Check header fallback
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            refresh_token = auth_header.split(" ", 1)[1].strip()

    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")

    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User unavailable")

    new_access_token = create_access_token({"sub": user.id, "role": user.role})
    csrf_token = generate_csrf_token(user.id)

    is_secure = not settings.is_dev()
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        samesite="lax",
        secure=is_secure,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    response.headers["X-CSRF-Token"] = csrf_token

    return TokenResponse(
        access_token=new_access_token,
        csrf_token=csrf_token,
        token_type="bearer",
        expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
