import spidev
import time

class LightSensor:
    def __init__(self, channel=0):
        """ADC0834 for reading photoresistor (LDR)"""
        self.channel = channel
        self.spi = None
        self.simulation_mode = False
        
        try:
            self.spi = spidev.SpiDev()
            self.spi.open(0, 0)  # Bus 0, Device 0
            self.spi.max_speed_hz = 1000000
            print(f"✅ ADC0834 initialized on SPI, channel {channel}")
        except Exception as e:
            print(f"⚠️ ADC0834 not available: {e}")
            print("Running in simulation mode")
            self.simulation_mode = True
    
    def read_light_level(self):
        """
        Read light level from ADC0834
        Returns: 0-255 (0=dark, 255=bright)
        """
        if self.simulation_mode:
            return 128  # Default mid-value for testing
        
        try:
            # ADC0834 protocol: Single-ended channel read
            # Command byte: 0x8C for CH0 single-ended
            adc_value = self.spi.xfer2([0x8C, 0])[1]
            return adc_value
        except Exception as e:
            print(f"ADC read error: {e}")
            return 128
    
    def is_dark(self, threshold=80):
        """
        Check if it's dark enough to turn on lights
        threshold: 0-255 (lower = darker needed to trigger)
        Default 80 = moderate darkness (adjust based on your room)
        """
        level = self.read_light_level()
        return level < threshold
    
    def get_brightness_percentage(self):
        """Get brightness as percentage (0-100%)"""
        level = self.read_light_level()
        return int((level / 255) * 100)
    
    def cleanup(self):
        """Clean up SPI resources"""
        if self.spi:
            self.spi.close()
        print("🧹 Light sensor cleaned up")

# Global instance
light_sensor = LightSensor()
