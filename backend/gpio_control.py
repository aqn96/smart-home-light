from gpiozero import LED
from gpiozero.exc import BadPinFactory
import threading
import time

class LightController:
    def __init__(self, pin=17):
        """Initialize LED on specified GPIO pin"""
        self.pin = pin
        self.is_on = False
        self.timer = None
        self.simulation_mode = False
        
        try:
            self.led = LED(pin)
            print(f"✅ GPIO initialized on pin {pin}")
        except (BadPinFactory, Exception) as e:
            print(f"⚠️ GPIO not available, running in simulation mode: {e}")
            self.led = None
            self.simulation_mode = True
    
    def turn_on(self):
        """Turn the light ON"""
        if self.led:
            self.led.on()
        self.is_on = True
        print("💡 Light turned ON")
        return self.is_on
    
    def turn_off(self):
        """Turn the light OFF"""
        if self.led:
            self.led.off()
        self.is_on = False
        print("🌑 Light turned OFF")
        return self.is_on
    
    def toggle(self):
        """Toggle light state"""
        if self.is_on:
            return self.turn_off()
        else:
            return self.turn_on()
    
    def get_status(self):
        """Get current light status"""
        return {
            "is_on": self.is_on,
            "simulation_mode": self.simulation_mode
        }
    
    def set_timer(self, seconds: int):
        """Set a timer to turn off the light"""
        # Cancel existing timer if any
        if self.timer and self.timer.is_alive():
            self.timer.cancel()
        
        # Turn on the light if it's off
        if not self.is_on:
            self.turn_on()
        
        # Create new timer
        self.timer = threading.Timer(seconds, self.turn_off)
        self.timer.start()
        print(f"⏰ Timer set for {seconds} seconds")
        return seconds
    
    def cleanup(self):
        """Clean up GPIO resources"""
        if self.timer:
            self.timer.cancel()
        if self.led:
            self.led.close()
        print("🧹 GPIO cleaned up")

# Global light controller instance
light_controller = LightController()
