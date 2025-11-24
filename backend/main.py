from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os

# Import from your modules
from database import get_db, User, LightHistory, hash_password, verify_password, init_db
from auth import (
    UserCreate, UserLogin, Token, create_access_token, 
    get_current_user, revoke_token, security
)
from gpio_control import light_controller

# Initialize FastAPI app
app = FastAPI(
    title="Smart Home Light Control API",
    description="IoT light control system with JWT authentication",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    print("🚀 Server started successfully!")

# Cleanup GPIO on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    light_controller.cleanup()
    print("👋 Server shutting down...")

# ==================== FRONTEND ROUTES ====================

@app.get("/")
async def read_root():
    """Serve the frontend HTML"""
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return {"message": "Smart Home Light Control API", "docs": "/docs"}

# ==================== AUTHENTICATION ROUTES ====================

@app.post("/auth/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if username exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_pw = hash_password(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pw
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": new_user.username, "user_id": new_user.id}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login and receive JWT token"""
    # Find user
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/logout")
async def logout(token_revoked: bool = Depends(revoke_token)):
    """Logout and revoke token"""
    if token_revoked:
        return {"message": "Successfully logged out"}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Logout failed"
    )

# ==================== LIGHT CONTROL ROUTES ====================

@app.get("/light/status")
async def get_light_status(current_user: User = Depends(get_current_user)):
    """Get current light status"""
    status = light_controller.get_status()
    return {
        "is_on": status["is_on"],
        "simulation_mode": status["simulation_mode"],
        "user": current_user.username
    }

@app.post("/light/toggle")
async def toggle_light(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle light ON/OFF"""
    new_state = light_controller.toggle()
    action = "ON" if new_state else "OFF"
    
    # Log action to history
    history_entry = LightHistory(
        user_id=current_user.id,
        username=current_user.username,
        action=action
    )
    db.add(history_entry)
    db.commit()
    
    return {
        "is_on": new_state,
        "action": action,
        "user": current_user.username
    }

@app.post("/light/timer")
async def set_timer(
    seconds: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set a timer to turn off the light"""
    if seconds <= 0 or seconds > 86400:  # Max 24 hours
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Timer must be between 1 second and 24 hours"
        )
    
    timer_seconds = light_controller.set_timer(seconds)
    
    # Log action to history
    history_entry = LightHistory(
        user_id=current_user.id,
        username=current_user.username,
        action=f"TIMER_SET_{seconds}s"
    )
    db.add(history_entry)
    db.commit()
    
    return {
        "message": f"Timer set for {seconds} seconds",
        "timer_seconds": timer_seconds,
        "user": current_user.username
    }

@app.get("/light/history")
async def get_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get light control history"""
    history = db.query(LightHistory).order_by(
        LightHistory.timestamp.desc()
    ).limit(limit).all()
    
    return {
        "history": [
            {
                "id": entry.id,
                "username": entry.username,
                "action": entry.action,
                "timestamp": entry.timestamp.isoformat()
            }
            for entry in history
        ],
        "total": len(history)
    }

# ==================== HEALTH CHECK ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "gpio_mode": "simulation" if light_controller.simulation_mode else "hardware"
    }
