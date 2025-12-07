"""
Smart Home Light Control API
FastAPI backend with JWT auth, motion sensor, camera, and WebSocket alerts
"""

from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from jose import JWTError, jwt
import os
import asyncio

from database import get_db, User, LightHistory, hash_password, verify_password, init_db
from auth import (
    UserCreate, UserLogin, Token, create_access_token, 
    get_current_user, revoke_token, security, SECRET_KEY, ALGORITHM
)
from gpio_control import light_controller
from motion_control import motion_controller
from camera_control import camera_controller
from websocket_manager import ws_manager

app = FastAPI(
    title="Smart Home Light Control API",
    description="IoT light control with JWT auth, motion sensor, camera streaming, and real-time alerts",
    version="2.3.0"  # Updated version
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
    """Initialize all components on startup"""
    init_db()
    
    # Get the event loop and set up motion alert callback
    loop = asyncio.get_event_loop()
    motion_controller.set_alert_callback(ws_manager.send_motion_alert, loop)
    
    # Start motion sensor (will calibrate first)
    motion_controller.start()
    
    print("🚀 Server started successfully!")
    print("💡 Manual toggle control: ACTIVE")
    print("🎯 Motion sensor control: ACTIVE")
    print("📹 Camera streaming: ACTIVE" if camera_controller.is_available else "📹 Camera: SIMULATION MODE")
    print("🔔 WebSocket alerts: ACTIVE")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    motion_controller.cleanup()
    light_controller.cleanup()
    camera_controller.cleanup()
    print("👋 Server shutting down...")


# ============== Frontend ==============

@app.get("/")
async def read_root():
    """Serve the frontend HTML"""
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return {"message": "Smart Home Light Control API", "docs": "/docs"}


# ============== Authentication ==============

@app.post("/auth/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    hashed_pw = hash_password(user_data.password)
    new_user = User(username=user_data.username, email=user_data.email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = create_access_token(data={"sub": new_user.username, "user_id": new_user.id})
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
    
    access_token = create_access_token(data={"sub": user.username, "user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/auth/logout")
async def logout(token_revoked: bool = Depends(revoke_token)):
    """Logout and revoke token"""
    if token_revoked:
        return {"message": "Successfully logged out"}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Logout failed")


# ============== Light Control ==============

@app.get("/light/status")
async def get_light_status(current_user: User = Depends(get_current_user)):
    """Get current light status"""
    status = light_controller.get_status()
    return {"is_on": status["is_on"], "simulation_mode": status["simulation_mode"], "user": current_user.username}


@app.post("/light/toggle")
async def toggle_light(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Toggle light ON/OFF (manual control)"""
    new_state = light_controller.toggle()
    action = "ON" if new_state else "OFF"
    
    history_entry = LightHistory(user_id=current_user.id, username=current_user.username, action=f"MANUAL_{action}")
    db.add(history_entry)
    db.commit()
    
    return {"is_on": new_state, "action": action, "user": current_user.username, "source": "manual"}


@app.post("/light/timer")
async def set_timer(seconds: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Set a timer to turn off the light"""
    if seconds <= 0 or seconds > 86400:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Timer must be between 1 second and 24 hours")
    
    timer_seconds = light_controller.set_timer(seconds)
    
    history_entry = LightHistory(user_id=current_user.id, username=current_user.username, action=f"TIMER_SET_{seconds}s")
    db.add(history_entry)
    db.commit()
    
    return {"message": f"Timer set for {seconds} seconds", "timer_seconds": timer_seconds, "user": current_user.username}


@app.get("/light/history")
async def get_history(limit: int = 20, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get light control history"""
    history = db.query(LightHistory).order_by(LightHistory.timestamp.desc()).limit(limit).all()
    
    return {
        "history": [
            {"id": e.id, "username": e.username, "action": e.action, "timestamp": e.timestamp.isoformat()}
            for e in history
        ],
        "total": len(history)
    }


# ============== Motion Sensor ==============

@app.get("/motion/status")
async def get_motion_status(current_user: User = Depends(get_current_user)):
    """Get current motion sensor status"""
    status = motion_controller.get_status()
    return {**status, "user": current_user.username}


@app.post("/motion/settings")
async def update_motion_settings(
    enabled: bool = None,
    timeout: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update motion sensor settings"""
    if timeout is not None and (timeout <= 0 or timeout > 300):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Timeout must be between 1 and 300 seconds")
    
    status = motion_controller.update_settings(enabled=enabled, timeout=timeout)
    
    changes = []
    if enabled is not None:
        changes.append(f"enabled={enabled}")
    if timeout is not None:
        changes.append(f"timeout={timeout}s")
    
    history_entry = LightHistory(user_id=current_user.id, username=current_user.username, action=f"MOTION_SETTINGS: {', '.join(changes)}")
    db.add(history_entry)
    db.commit()
    
    return {"message": "Motion sensor settings updated", "settings": status, "user": current_user.username}


@app.post("/motion/simulate")
async def simulate_motion(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Simulate motion detection (for testing without hardware)"""
    result = motion_controller.simulate_motion()
    
    # Only log if simulation was successful (not paused)
    if "error" not in result:
        history_entry = LightHistory(user_id=current_user.id, username=current_user.username, action="MOTION_SIMULATED")
        db.add(history_entry)
        db.commit()
    
    return {**result, "user": current_user.username}


# ============== NEW: Motion Alert Pause/Resume ==============

@app.post("/motion/pause")
async def pause_motion_alerts(current_user: User = Depends(get_current_user)):
    """
    Pause motion alerts (call when user opens camera view)
    This prevents repeated alert popups while user is already watching the camera
    """
    result = motion_controller.pause_alerts()
    return {**result, "user": current_user.username}


@app.post("/motion/resume")
async def resume_motion_alerts(current_user: User = Depends(get_current_user)):
    """
    Resume motion alerts (call when user closes camera view)
    """
    result = motion_controller.resume_alerts()
    return {**result, "user": current_user.username}


# ============== Camera ==============

@app.get("/camera/status")
async def get_camera_status(current_user: User = Depends(get_current_user)):
    """Get camera status"""
    status = camera_controller.get_status()
    return {**status, "user": current_user.username}


@app.get("/camera/stream")
async def camera_stream(token: str = Query(..., description="JWT token for authentication")):
    """
    MJPEG video stream endpoint
    
    Note: Uses query param for auth because <img> tags can't send headers
    Access: /camera/stream?token=YOUR_JWT_TOKEN
    """
    # Validate token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return StreamingResponse(
        camera_controller.generate_mjpeg_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.get("/camera/snapshot")
async def camera_snapshot(current_user: User = Depends(get_current_user)):
    """Get a single camera snapshot"""
    frame = camera_controller.get_snapshot()
    if frame:
        return StreamingResponse(iter([frame]), media_type="image/jpeg")
    raise HTTPException(status_code=503, detail="Camera unavailable")


@app.post("/camera/restart")
async def restart_camera(current_user: User = Depends(get_current_user)):
    """Restart the camera (if connection lost)"""
    status = camera_controller.restart()
    return {"message": "Camera restart attempted", "status": status, "user": current_user.username}


# ============== WebSocket ==============

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    """
    WebSocket endpoint for real-time alerts
    
    Connect with: ws://host:port/ws?token=YOUR_JWT_TOKEN
    """
    # Validate token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        username = payload.get("sub")
        if not user_id or not username:
            await websocket.close(code=4001, reason="Invalid token")
            return
    except JWTError:
        await websocket.close(code=4001, reason="Invalid token")
        return
    
    # Accept connection
    await ws_manager.connect(websocket, user_id)
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": f"Welcome {username}! You'll receive motion alerts here.",
            "user": username
        })
        
        # Keep connection alive and listen for messages
        while True:
            try:
                # Wait for any client messages (ping/pong, etc.)
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                
                # Echo back or handle commands
                if data == "ping":
                    await websocket.send_json({"type": "pong"})
                    
            except asyncio.TimeoutError:
                # Send keepalive ping
                try:
                    await websocket.send_json({"type": "ping"})
                except:
                    break
                    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"⚠️ WebSocket error: {e}")
    finally:
        await ws_manager.disconnect(websocket, user_id)


# ============== Health Check ==============

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.3.0",
        "light_gpio_mode": "simulation" if light_controller.simulation_mode else "hardware",
        "motion_sensor_mode": "simulation" if motion_controller.simulation_mode else "hardware",
        "camera_mode": "simulation" if camera_controller.simulation_mode else "hardware",
        "camera_available": camera_controller.is_available,
        "motion_enabled": motion_controller.enabled,
        "motion_calibrated": motion_controller.is_calibrated,
        "motion_alerts_paused": motion_controller.alerts_paused,  # NEW
        "websocket_connections": ws_manager.get_connection_count()
    }
