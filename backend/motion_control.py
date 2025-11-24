from gpiozero import MotionSensor
from gpiozero.exc import BadPinFactory
from gpio_control import light_controller
from light_sensor import light_sensor
import threading
from datetime import datetime

class MotionSensorController:
    def __init__(self, pir_pin=27, timeout=10):
        """Initialize PIR motion sensor on specified GPIO pin"""
        self.pir_pin = pir_pin
        self.timeout = timeout  # Seconds to keep light on after motion stops
        self.enabled = True  # Motion sensor can be disabled
        self.simulation_mode = False
        self.pir = None
        self.timer = None
        self.motion_active = False
        
        try:
            self.pir = MotionSensor(pir_pin)
            print(f"✅ PIR Motion Sensor initialized on pin {pir_pin}")
        except (BadPinFactory, Exception) as e:
            print(f"⚠️ PIR sensor not available, running in simulation mode: {e}")
            self.simulation_mode = True
    
    def start(self):
        """Start listening for motion events"""
        if not self.pir:
            print("⚠️ Motion sensor in simulation mode - no hardware events")
            return
            
        self.pir.when_motion = self._on_motion_detected
        self.pir.when_no_motion = self._on_no_motion
        print("🎯 Motion sensor active and listening...")
    
    def _on_motion_detected(self):
        """Called when motion is detected"""
        if not self.enabled:
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # NEW: Check if it's dark before turning on light
        if not light_sensor.is_dark():
            print(f"[{timestamp}] ☀️ Daylight detected - motion ignored (energy saved!)")
            return
        
        # It's dark AND motion detected - turn on light
        self.motion_active = True
        print(f"[{timestamp}] 🚶 Motion + Darkness → Turning light ON")
        
        # Turn on light using existing controller
        light_controller.turn_on()
        
        # Cancel any existing auto-off timer
        if self.timer and self.timer.is_alive():
            self.timer.cancel()
    
    def _on_no_motion(self):
        """Called when motion stops"""
        if not self.enabled:
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] 🛑 No motion detected. Auto-off in {self.timeout}s...")
        
        # Start countdown timer for auto-off
        self.timer = threading.Timer(self.timeout, self._auto_turn_off)
        self.timer.start()
    
    def _auto_turn_off(self):
        """Turn off light after timeout (if still no motion)"""
        # Double-check: only turn off if motion is still not detected
        if self.pir and not self.pir.motion_detected:
            self.motion_active = False
            light_controller.turn_off()
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] 💤 Auto-off: Light turned OFF")
        else:
            print("Motion re-detected during countdown, keeping light on")
    
    def get_status(self):
        """Get current motion sensor status"""
        return {
            "enabled": self.enabled,
            "timeout": self.timeout,
            "motion_detected": self.pir.motion_detected if self.pir else False,
            "motion_active": self.motion_active,
            "simulation_mode": self.simulation_mode
        }
    
    def update_settings(self, enabled=None, timeout=None):
        """Update motion sensor settings"""
        if enabled is not None:
            self.enabled = enabled
            status = "enabled" if enabled else "disabled"
            print(f"🔧 Motion sensor {status}")
        
        if timeout is not None and timeout > 0:
            self.timeout = timeout
            print(f"🔧 Motion timeout set to {timeout}s")
        
        return self.get_status()
    
    def cleanup(self):
        """Clean up resources"""
        if self.timer and self.timer.is_alive():
            self.timer.cancel()
        if self.pir:
            self.pir.close()
        print("🧹 Motion sensor cleaned up")

# Global motion sensor controller instance
motion_controller = MotionSensorController()
