from gpiozero import MotionSensor
from gpiozero.exc import BadPinFactory
from gpio_control import light_controller
from light_sensor import light_sensor
import threading
import time
from datetime import datetime

class MotionSensorController:
    def __init__(self, pir_pin=27, timeout=10, calibration_time=60):
        """Initialize PIR motion sensor on GPIO 27 (Pin 13)"""
        self.pir_pin = pir_pin
        self.timeout = timeout  # Seconds to keep light on after motion stops
        self.calibration_time = calibration_time  # PIR calibration time
        self.enabled = True  # Motion sensor can be disabled
        self.simulation_mode = False
        self.is_calibrated = False  # NEW: Track calibration status
        self.pir = None
        self.timer = None
        self.motion_active = False
        
        try:
            self.pir = MotionSensor(pir_pin)
            print(f"✅ PIR Motion Sensor initialized on GPIO {pir_pin} (Pin 13)")
            
            # Start calibration in background thread
            self.calibration_thread = threading.Thread(target=self._calibrate)
            self.calibration_thread.daemon = True
            self.calibration_thread.start()
            
        except (BadPinFactory, Exception) as e:
            print(f"⚠️ PIR sensor not available, running in simulation mode: {e}")
            self.simulation_mode = True
            self.is_calibrated = True  # Skip calibration in simulation mode
    
    def _calibrate(self):
        """Calibrate PIR sensor with countdown (runs in background)"""
        print(f"⏳ PIR calibrating for {self.calibration_time} seconds...")
        print("   Please stay still!")
        
        # Countdown every 10 seconds
        for remaining in range(self.calibration_time, 0, -10):
            print(f"   {remaining} seconds remaining...")
            time.sleep(10)
        
        self.is_calibrated = True
        print("✅ PIR sensor calibrated and ready!")
        
        # Now start listening for motion
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
        
        # It's dark AND motion detected - turn on light
        self.motion_active = True
        print(f"[{timestamp}] 🎯 Motion + Darkness → Turning light ON")
        
        # Turn on light using existing controller
        light_controller.turn_on()
        
        # Cancel any existing auto-off timer
        if self.timer and self.timer.is_alive():
            self.timer.cancel()
    
    def _on_no_motion(self):
        """Called when motion stops"""
        if not self.enabled or not self.is_calibrated:
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
            "calibrated": self.is_calibrated,  # NEW: Include calibration status
            "motion_detected": self.pir.motion_detected if (self.pir and self.is_calibrated) else False,
            "motion_active": self.motion_active,
            "simulation_mode": self.simulation_mode
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
    
    def cleanup(self):
        """Clean up resources"""
        if self.timer and self.timer.is_alive():
            self.timer.cancel()
        if self.pir:
            self.pir.close()
        print("🧹 Motion sensor cleaned up")

# Global motion sensor controller instance - GPIO 27 (Pin 13)
motion_controller = MotionSensorController(pir_pin=27, timeout=10, calibration_time=60)
