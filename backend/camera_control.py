"""
USB Camera Controller for live streaming and snapshots
Uses OpenCV to capture from USB camera (typically /dev/video0)
"""

import cv2
import threading
import time
from datetime import datetime


class CameraController:
    """Controls USB camera for MJPEG streaming and snapshots"""
    
    def __init__(self, camera_index=0):
        """
        Initialize camera controller
        
        Args:
            camera_index: Camera device index (0 = /dev/video0)
        """
        self.camera_index = camera_index
        self.camera = None
        self.is_available = False
        self.simulation_mode = False
        self._lock = threading.Lock()
        self._frame_cache = None
        self._last_frame_time = 0
        
        # Try to initialize camera
        self._init_camera()
    
    def _init_camera(self):
        """Initialize the USB camera"""
        try:
            self.camera = cv2.VideoCapture(self.camera_index)
            
            if self.camera.isOpened():
                # Set camera properties for better performance
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.camera.set(cv2.CAP_PROP_FPS, 15)
                self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                
                # Test read
                ret, frame = self.camera.read()
                if ret and frame is not None:
                    self.is_available = True
                    print(f"✅ USB Camera initialized on /dev/video{self.camera_index}")
                    print(f"   Resolution: {int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
                else:
                    raise Exception("Camera opened but cannot read frames")
            else:
                raise Exception("Cannot open camera device")
                
        except Exception as e:
            print(f"⚠️ USB Camera not available: {e}")
            print("   Running in simulation mode (no video)")
            self.simulation_mode = True
            self.is_available = False
            if self.camera:
                self.camera.release()
                self.camera = None
    
    def get_frame(self):
        """
        Capture a single frame from the camera
        
        Returns:
            JPEG bytes or None if unavailable
        """
        if self.simulation_mode or not self.camera:
            return self._generate_placeholder_frame()
        
        with self._lock:
            try:
                ret, frame = self.camera.read()
                if ret and frame is not None:
                    # Add timestamp overlay
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cv2.putText(frame, timestamp, (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, "Smart Home Security", (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    
                    # Encode to JPEG
                    _, jpeg = cv2.imencode('.jpg', frame, 
                                          [cv2.IMWRITE_JPEG_QUALITY, 70])
                    return jpeg.tobytes()
            except Exception as e:
                print(f"⚠️ Camera frame capture error: {e}")
        
        return self._generate_placeholder_frame()
    
    def _generate_placeholder_frame(self):
        """Generate a placeholder frame when camera is unavailable"""
        import numpy as np
        
        # Create a dark gray placeholder image
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[:] = (40, 40, 40)  # Dark gray
        
        # Add text
        cv2.putText(frame, "Camera Unavailable", (180, 220),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100), 2)
        cv2.putText(frame, "Check USB connection", (195, 260),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (80, 80, 80), 1)
        
        # Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 2)
        
        _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        return jpeg.tobytes()
    
    def generate_mjpeg_stream(self):
        """
        Generator for MJPEG streaming
        
        Yields:
            MJPEG frame bytes for streaming response
        """
        print("📹 Starting MJPEG stream...")
        frame_interval = 1.0 / 15  # 15 FPS target
        
        while True:
            start_time = time.time()
            
            frame = self.get_frame()
            if frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
            # Control frame rate
            elapsed = time.time() - start_time
            if elapsed < frame_interval:
                time.sleep(frame_interval - elapsed)
    
    def get_snapshot(self):
        """
        Get a single snapshot image
        
        Returns:
            JPEG bytes
        """
        return self.get_frame()
    
    def get_status(self):
        """Get camera status"""
        return {
            "available": self.is_available,
            "simulation_mode": self.simulation_mode,
            "camera_index": self.camera_index,
            "device": f"/dev/video{self.camera_index}"
        }
    
    def restart(self):
        """Restart the camera (useful if connection lost)"""
        print("🔄 Restarting camera...")
        self.cleanup()
        time.sleep(1)
        self._init_camera()
        return self.get_status()
    
    def cleanup(self):
        """Release camera resources"""
        if self.camera:
            self.camera.release()
            self.camera = None
        self.is_available = False
        print("🧹 Camera resources released")


# Global camera controller instance
camera_controller = CameraController(camera_index=0)
