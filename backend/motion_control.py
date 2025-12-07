"""
PIR Motion Sensor Controller with Alert Callback
GPIO 27 (Pin 13) - HC-SR501 PIR Sensor
"""

from gpiozero import MotionSensor
from gpiozero.exc import BadPinFactory
from gpio_control import light_controller
import threading
import time
import asyncio
from datetime import datetime
from typing import Callable, Optional


class MotionSensorController:
    def __init__(self, pir_pin=27, timeout=10, calibration_time=60):
        """Initialize PIR motion sensor on GPIO 27 (Pin 13)"""
        self.pir_pin = pir_pin
        self.timeout = timeout
        self.calibration_time = calibration_time
        self.enabled = True
        self.simulation_mode = False
        self.is_calibrated = False
        self.pir = None
        self.timer = None
        self.motion_active = False
        
        # NEW: Pause alerts when camera is being viewed
        self.alerts_paused = False
        
        # Turn off LED when closing camera (user acknowledged the alert)
        light_controller.turn_off()
        print("🌑 LED turned OFF (camera view closed)")
        
        # Alert callback for WebSocket notifications
        self._alert_callback: Optional[Callable] = None
        self._alert_loop: Optional[asyncio.AbstractEventLoop] = None
        
        try:
            self.pir = MotionSensor(pir_pin)
            print(f"✅ PIR Motion Sensor initialized on GPIO {pir_pin} (Pin 13)")
            
            self.calibration_thread = threading.Thread(target=self._calibrate)
            self.calibration_thread.daemon = True
            self.calibration_thread.start()
            
        except (BadPinFactory, Exception) as e:
            print(f"⚠️ PIR sensor not available, running in simulation mode: {e}")
            self.simulation_mode = True
            self.is_calibrated = True
    
    def set_alert_callback(self, callback: Callable, loop: asyncio.AbstractEventLoop):
        """Set callback function to be called when motion is detected"""
        self._alert_callback = callback
        self._alert_loop = loop
        print("✅ Motion alert callback configured")
    
    def _trigger_alert(self):
        """Trigger the alert callback (thread-safe) - only if not paused"""
        # NEW: Check if alerts are paused (camera being viewed)
        if self.alerts_paused:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] 🔇 Alert suppressed (camera is being viewed)")
            return
        
        if self._alert_callback and self._alert_loop:
            try:
                asyncio.run_coroutine_threadsafe(
                    self._alert_callback(),
                    self._alert_loop
                )
            except Exception as e:
                print(f"⚠️ Alert callback error: {e}")
    
    def _calibrate(self):
        """Calibrate PIR sensor with countdown (runs in background)"""
        print(f"⏳ PIR calibrating for {self.calibration_time} seconds...")
        print("   Please stay still!")
        
        for remaining in range(self.calibration_time, 0, -10):
            print(f"   {remaining} seconds remaining...")
            time.sleep(10)
        
        self.is_calibrated = True
        print("✅ PIR sensor calibrated and ready!")
        
        self.start()
    
    def start(self):
        """Start listening for motion events"""
        if not self.pir:
            print("⚠️ Motion sensor in simulation mode - no hardware events")
            return
        
        if not self.is_calibrated:
            print("⚠️ Cannot start - PIR still calibrating...")
            return
            
        self.pir.when_motion = self._on_motion_detected
        self.pir.when_no_motion = self._on_no_motion
        print("🎯 Motion sensor active and listening...")
    
    def _on_motion_detected(self):
        """Called when motion is detected"""
        if not self.enabled or not self.is_calibrated:
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.motion_active = True
        
        # NEW: If alerts are paused (camera viewing), skip LED and alert
        if self.alerts_paused:
            print(f"[{timestamp}] 👁️ Motion detected (suppressed - camera active)")
            return
        
        print(f"[{timestamp}] 🚨 MOTION DETECTED!")
        print(f"[{timestamp}] 💡 LED turned ON by motion sensor")
        
        # Turn on LED (existing behavior)
        light_controller.turn_on()
        
        # Cancel any existing auto-off timer
        if self.timer and self.timer.is_alive():
            self.timer.cancel()
        
        # Trigger WebSocket alert
        self._trigger_alert()
    
    def _on_no_motion(self):
        """Called when motion stops"""
        if not self.enabled or not self.is_calibrated:
            return
        
        # NEW: If alerts paused, don't start auto-off timer
        if self.alerts_paused:
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] 🛑 No motion detected. Auto-off in {self.timeout}s...")
        
        self.timer = threading.Timer(self.timeout, self._auto_turn_off)
        self.timer.start()
    
    def _auto_turn_off(self):
        """Turn off light after timeout (if still no motion)"""
        # NEW: Don't auto-off if camera is being viewed
        if self.alerts_paused:
            return
        
        if self.pir and not self.pir.motion_detected:
            self.motion_active = False
            light_controller.turn_off()
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] 💤 Auto-off: Light turned OFF")
        else:
            print("Motion re-detected during countdown, keeping light on")
    
    # NEW: Pause/Resume alerts for camera viewing
    def pause_alerts(self):
        """Pause motion alerts (when user is viewing camera)"""
        self.alerts_paused = True
        # Cancel any pending auto-off timer
        if self.timer and self.timer.is_alive():
            self.timer.cancel()
        print("🔇 Motion alerts PAUSED (camera viewing active)")
        return {"alerts_paused": True, "message": "Motion alerts paused"}
    
    def resume_alerts(self):
        """Resume motion alerts (when user closes camera)"""
        self.alerts_paused = False
        
        # Turn off LED when closing camera (user acknowledged the alert)
        light_controller.turn_off()
        print("🌑 LED turned OFF (camera view closed)")
        self.motion_active = False
        print("🔔 Motion alerts RESUMED")
        return {"alerts_paused": False, "message": "Motion alerts resumed, light turned off"}
    
    def get_status(self):
        """Get current motion sensor status"""
        return {
            "enabled": self.enabled,
            "timeout": self.timeout,
            "calibrated": self.is_calibrated,
            "motion_detected": self.pir.motion_detected if (self.pir and self.is_calibrated) else False,
            "motion_active": self.motion_active,
            "simulation_mode": self.simulation_mode,
            "alerts_paused": self.alerts_paused  # NEW: Include pause status
        }
    
    def update_settings(self, enabled=None, timeout=None):
        """Update motion sensor settings"""
        if not self.is_calibrated:
            return {
                "error": "PIR still calibrating",
                "calibrated": False
            }
        
        if enabled is not None:
            self.enabled = enabled
            status = "enabled" if enabled else "disabled"
            print(f"🔧 Motion sensor {status}")
        
        if timeout is not None and timeout > 0:
            self.timeout = timeout
            print(f"🔧 Motion timeout set to {timeout}s")
        
        return self.get_status()
    
    def simulate_motion(self):
        """Simulate a motion detection event (for testing)"""
        if not self.enabled:
            return {"error": "Motion sensor is disabled"}
        
        # NEW: Check if alerts are paused
        if self.alerts_paused:
            return {"error": "Alerts are paused (camera is being viewed)", "alerts_paused": True}
        
        print("🧪 Simulating motion detection...")
        self._on_motion_detected()
        return {"message": "Motion simulated", "alert_sent": True}
    
    def cleanup(self):
        """Clean up resources"""
        if self.timer and self.timer.is_alive():
            self.timer.cancel()
        if self.pir:
            self.pir.close()
        print("🧹 Motion sensor cleaned up")


# Global motion sensor controller instance - GPIO 27 (Pin 13)
motion_controller = MotionSensorController(pir_pin=27, timeout=10, calibration_time=60)
