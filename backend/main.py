from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os

from database import get_db, User, LightHistory, hash_password, verify_password, init_db
from auth import (
    UserCreate, UserLogin, Token, create_access_token, 
    get_current_user, revoke_token, security
)
from gpio_control import light_controller
from motion_control import motion_controller
from light_sensor import light_sensor

app = FastAPI(
    title="Smart Home Light Control API",
    description="IoT light control system with JWT authentication, motion sensor, and daylight detection",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    init_db()
    motion_controller.start()
    print("🚀 Server started successfully!")
    print("💡 Manual toggle control: ACTIVE")
    print("🎯 Motion sensor control: ACTIVE")
    print("🌅 Daylight detection: ACTIVE")

@app.on_event("shutdown")
async def shutdown_event():
    motion_controller.cleanup()
    light_controller.cleanup()
    light_sensor.cleanup()
    print("👋 Server shutting down...")

@app.get("/")
async def read_root():
    """Serve the frontend HTML"""
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return {"message": "Smart Home Light Control API", "docs": "/docs"}

@app.post("/auth/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_pw = hash_password(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pw
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = create_access_token(
        data={"sub": new_user.username, "user_id": new_user.id}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login and receive JWT token"""
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
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
    """Toggle light ON/OFF (manual control)"""
    new_state = light_controller.toggle()
    action = "ON" if new_state else "OFF"
    
    history_entry = LightHistory(
        user_id=current_user.id,
        username=current_user.username,
        action=f"MANUAL_{action}"
    )
    db.add(history_entry)
    db.commit()
    
    return {
        "is_on": new_state,
        "action": action,
        "user": current_user.username,
        "source": "manual"
    }

@app.post("/light/timer")
async def set_timer(
    seconds: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set a timer to turn off the light"""
    if seconds <= 0 or seconds > 86400:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Timer must be between 1 second and 24 hours"
        )
    
    timer_seconds = light_controller.set_timer(seconds)
    
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

@app.get("/motion/status")
async def get_motion_status(current_user: User = Depends(get_current_user)):
    """Get current motion sensor status"""
    status = motion_controller.get_status()
    return {
        "enabled": status["enabled"],
        "timeout": status["timeout"],
        "motion_detected": status["motion_detected"],
        "motion_active": status["motion_active"],
        "simulation_mode": status["simulation_mode"],
        "user": current_user.username
    }

@app.post("/motion/settings")
async def update_motion_settings(
    enabled: bool = None,
    timeout: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update motion sensor settings"""
    if timeout is not None and (timeout <= 0 or timeout > 300):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Timeout must be between 1 and 300 seconds"
        )
    
    status = motion_controller.update_settings(enabled=enabled, timeout=timeout)
    
    changes = []
    if enabled is not None:
        changes.append(f"enabled={enabled}")
    if timeout is not None:
        changes.append(f"timeout={timeout}s")
    
    history_entry = LightHistory(
        user_id=current_user.id,
        username=current_user.username,
        action=f"MOTION_SETTINGS: {', '.join(changes)}"
    )
    db.add(history_entry)
    db.commit()
    
    return {
        "message": "Motion sensor settings updated",
        "settings": status,
        "user": current_user.username
    }

@app.get("/sensor/light")
async def get_light_level(current_user: User = Depends(get_current_user)):
    """Get current ambient light level"""
    level = light_sensor.read_light_level()
    brightness_pct = light_sensor.get_brightness_percentage()
    is_dark = light_sensor.is_dark()
    
    return {
        "light_level": level,
        "brightness_percentage": brightness_pct,
        "is_dark": is_dark,
        "threshold": 80,
        "simulation_mode": light_sensor.simulation_mode,
        "user": current_user.username
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "light_gpio_mode": "simulation" if light_controller.simulation_mode else "hardware",
        "motion_sensor_mode": "simulation" if motion_controller.simulation_mode else "hardware",
        "light_sensor_mode": "simulation" if light_sensor.simulation_mode else "hardware",
        "motion_enabled": motion_controller.enabled
    }
