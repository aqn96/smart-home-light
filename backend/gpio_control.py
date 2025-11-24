from gpiozero import LED
from gpiozero.exc import BadPinFactory
import threading
import time

class LightController:
    def __init__(self, led_pin=18):
        """Initialize LED on GPIO 18 (Pin 12)"""
        self.led_pin = led_pin
        self.is_on = False
        self.timer = None
        self.simulation_mode = False
        
        try:
            self.led = LED(led_pin)
            print(f"✅ LED initialized on GPIO {led_pin} (Pin 12)")
        except (BadPinFactory, Exception) as e:
            print(f"⚠️ GPIO not available, running in simulation mode: {e}")
            self.led = None
            self.simulation_mode = True
    
    def turn_on(self):
        """Turn the LED ON"""
        if self.led:
            self.led.on()
        self.is_on = True
        print("💡 LED turned ON")
        return self.is_on
    
    def turn_off(self):
        """Turn the LED OFF"""
        if self.led:
            self.led.off()
        self.is_on = False
        print("🌑 LED turned OFF")
        return self.is_on
    
    def toggle(self):
        """Toggle LED state"""
        if self.is_on:
            return self.turn_off()
        else:
            return self.turn_on()
    
    def get_status(self):
        """Get current LED status"""
        return {
            "is_on": self.is_on,
            "simulation_mode": self.simulation_mode
        }
    
    def set_timer(self, seconds: int):
        """Set a timer to turn off the LED"""
        if self.timer and self.timer.is_alive():
            self.timer.cancel()
        
        if not self.is_on:
            self.turn_on()
        
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

# Global light controller instance - GPIO 18 (Pin 12)
light_controller = LightController(led_pin=18)
