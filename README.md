# 🏠 Smart Home IoT Light Control System

A dual-mode IoT light control system with motion detection, built on Raspberry Pi 5 using FastAPI + Vanilla JavaScript. Control lights manually through a web interface OR automatically via motion sensor - both modes work together seamlessly.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.121+-green.svg)
![Vanilla JS](https://img.shields.io/badge/Vanilla%20JS-ES6+-yellow.svg)
![Raspberry Pi 5](https://img.shields.io/badge/Raspberry%20Pi-5-red.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🎮 **Dual Control Mode** | Manual web control AND automatic motion detection work simultaneously |
| 🎯 **Motion Detection** | PIR sensor automatically triggers LED when movement detected |
| 💡 **Status LED** | Visual indicator controlled by web interface and motion sensor |
| 🔐 **Secure Login** | JWT authentication with password hashing |
| ⏱️ **Timer Function** | Auto-off after configurable timeout (5s, 10s, 30s, 60s) |
| 📜 **Action History** | Logs all manual and automatic actions with timestamps |
| 📱 **Responsive UI** | Works on desktop and mobile browsers |
| 🔒 **HTTPS** | Secure encrypted communication |

## 🔬 How It Works

### Dual Hybrid System:
```
Manual Mode: User clicks toggle → LED changes state (always works)
Auto Mode:   Motion detected → LED turns ON automatically
             No motion for timeout → LED turns OFF
```

**Smart Logic:**
- Motion sensor activates LED when movement detected
- Manual control always works independently
- Configurable auto-off timeout (5-60 seconds)
- Web interface shows real-time status from both modes
- All actions logged with timestamps in database

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** + **SQLite** - Database and ORM  
- **JWT (python-jose)** - Token authentication
- **Passlib** - Password hashing (bcrypt)
- **gpiozero** - Raspberry Pi GPIO control
- **rpi-lgpio** - Raspberry Pi 5 GPIO support

### Frontend
- **Vanilla JavaScript (ES6+)** - No frameworks, ~25KB
- **CSS3** - Responsive styling with gradient backgrounds
- **Fetch API** - Async backend communication
- **Single Page App** - One HTML file, no build process

### Why Vanilla JS?
- ✅ Lightweight - 25KB vs 250MB with frameworks
- ✅ Fast - Instant load, no build step
- ✅ Perfect for IoT devices with limited resources
- ✅ Modern - ES6+, async/await, template literals

## 🔌 Hardware Components

| Component | Model | GPIO Pin | Purpose |
|-----------|-------|----------|---------|
| Microcontroller | Raspberry Pi 5 | - | Main controller |
| PIR Motion Sensor | HC-SR501 | GPIO 27 (Pin 13) | Motion detection |
| Status LED | 5mm Blue LED | GPIO 18 (Pin 12) | Visual indicator |
| Resistor | 330Ω | - | LED current limiting |
| Breadboard | 400-point | - | Circuit prototyping |
| Jumper Wires | M-M, M-F | - | Connections |

**Hardware Cost:** ~$10-15 (excluding Raspberry Pi)

## 📋 Prerequisites

### Hardware
- Raspberry Pi 5 (or Pi 4)
- microSD card (16GB+) with Raspberry Pi OS (64-bit)
- Components listed above
- USB-C power supply (5V/3A minimum)

### Software
- Raspberry Pi OS (64-bit, Bookworm recommended)
- Python 3.11+
- SSH enabled (for remote access)
- Network connection (Wi-Fi or Ethernet)

## ⚡ Quick Start

### 1. Hardware Wiring

**PIR Motion Sensor (HC-SR501):**
```
VCC (right pin)   → Pi Pin 4 (5V)
Dout (middle pin) → Pi Pin 13 (GPIO 27)
GND (left pin)    → Pi Pin 6 (GND) or ground rail
```

**Status LED Circuit:**
```
Pi Pin 12 (GPIO 18) → 330Ω Resistor → LED Long Leg (+)
LED Short Leg (-)   → Pi Pin 6 (GND) or ground rail
```

**Using Breadboard Ground Rail (Recommended):**
```
Pi Pin 6 (GND) → Ground rail (-)
PIR GND        → Ground rail (-)
LED Short Leg  → Ground rail (-)
```

### 2. Software Installation
```bash
# Clone repository
git clone https://github.com/aqn96/smart-home-light.git
cd smart-home-light

# Run installation script
chmod +x install.sh
./install.sh
```

**Note:** The install script will:
- Create Python virtual environment
- Install system dependencies (including lgpio for Pi 5)
- Install Python packages
- Set up project structure

### 3. Configure Environment
```bash
# Generate secret key
python3 -c "import secrets; print(secrets.token_hex(32))"

# Create environment file
nano backend/.env
```

Add to `backend/.env`:
```env
JWT_SECRET_KEY=<your-generated-key-from-above>
DATABASE_URL=sqlite:///./smart_light.db
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
```

### 4. Initialize Database
```bash
cd backend
source venv/bin/activate
python database.py
deactivate
cd ..
```

### 5. Generate SSL Certificates
```bash
cd backend
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout key.pem -out cert.pem -days 365 \
  -subj "/CN=smartlight-an.local"
cd ..
```

### 6. Start Server
```bash
cd backend
./start_https.sh
```

**Expected output:**
```
🚀 Server started successfully!
✅ LED initialized on GPIO 18 (Pin 12)
✅ PIR Motion Sensor initialized on GPIO 27 (Pin 13)
⏳ PIR calibrating for 60 seconds...
   60 seconds remaining...
   ...
✅ PIR sensor calibrated and ready!
🎯 Motion sensor active and listening...
INFO:     Uvicorn running on https://0.0.0.0:8000
```

### 7. Access Application

- **Web Interface:** `https://smartlight-an.local:8000`
- **API Docs:** `https://smartlight-an.local:8000/docs`
- **Alternative:** `https://<your-pi-ip>:8000`

⚠️ You'll see a security warning (self-signed certificate) - click "Advanced" → "Proceed"

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login and get JWT token |
| POST | `/auth/logout` | Revoke token |

### Light Control
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/light/status` | Get current LED state |
| POST | `/light/toggle` | Manual toggle LED |
| POST | `/light/timer` | Set auto-off timer |
| GET | `/light/history` | View action log |

### Motion Sensor
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/motion/status` | Get sensor status and calibration |
| POST | `/motion/settings` | Update timeout and enable/disable |

## 📁 Project Structure
```
smart-home-light/
├── backend/
│   ├── main.py              # FastAPI routes and endpoints
│   ├── database.py          # SQLAlchemy models
│   ├── auth.py              # JWT authentication
│   ├── gpio_control.py      # LED control (GPIO 18)
│   ├── motion_control.py    # PIR sensor logic (GPIO 27)
│   ├── light_sensor.py      # LDR/ADC (optional, for future)
│   ├── requirements.txt     # Python dependencies
│   ├── start_https.sh       # Server startup script
│   └── .env                 # Environment variables (gitignored)
├── frontend/
│   └── index.html           # Web interface (~25KB)
├── .gitignore               # Git ignore rules
├── .env.example             # Environment template
├── install.sh               # Automated setup script
└── README.md                # This file
```

## 🧪 Testing

### Test 1: LED Blink Test (Hardware)
```bash
python3 << 'EOF'
from gpiozero import LED
import time
led = LED(18)
for i in range(5):
    led.on()
    time.sleep(0.5)
    led.off()
    time.sleep(0.5)
led.close()
print("✅ LED test complete!")
EOF
```

### Test 2: Motion Sensor Test (Hardware)
```bash
python3 << 'EOF'
from gpiozero import MotionSensor
import time
pir = MotionSensor(27)
print("⏳ Calibrating PIR (60 seconds)...")
time.sleep(60)
print("👋 Wave at sensor...")
pir.wait_for_motion()
print("✅ Motion detected!")
pir.close()
EOF
```

### Test 3: Full System Test
1. Start server: `cd backend && ./start_https.sh`
2. Access web interface: `https://smartlight-an.local:8000`
3. Login with your credentials
4. **Manual Test:** Click "Manual Toggle" → LED should light up
5. **Motion Test:** Enable motion control → Wave at PIR → LED should light up automatically

## 🐛 Troubleshooting

### Issue: GPIO not available / simulation mode
```bash
# Install Raspberry Pi 5 GPIO support
sudo apt install -y python3-lgpio liblgpio-dev

# Add user to GPIO group
sudo usermod -a -G gpio $USER
sudo reboot
```

### Issue: Motion sensor not working
```bash
# Check GPIO permissions
groups | grep gpio  # Should show 'gpio'

# Verify PIR calibration (wait 60 seconds after power-on)
# PIR sensor needs time to stabilize
```

### Issue: SSL certificate warning
This is normal for self-signed certificates. Options:
- Click "Advanced" → "Proceed anyway" (recommended for local use)
- Or generate CA-signed certificate for production

### Issue: Can't access web interface
```bash
# Find your Pi's IP address
hostname -I

# Access using IP instead
https://<ip-address>:8000

# Check firewall
sudo ufw status
```

## 🔒 Security Features

- ✅ **Bcrypt password hashing** - Passwords never stored in plain text
- ✅ **JWT tokens** - 1-hour expiration with secure signing
- ✅ **HTTPS/TLS encryption** - All traffic encrypted
- ✅ **SQL injection prevention** - Parameterized queries via SQLAlchemy
- ✅ **Environment variables** - Secrets not committed to Git

## 🎓 Project Context

**Built for:** Embedded Systems Course  
**Date:** November 2024  
**Platform:** Raspberry Pi 5

### Learning Objectives Demonstrated:
- ✅ IoT hardware integration (PIR sensor, LED control)
- ✅ RESTful API design with FastAPI
- ✅ Real-time sensor data processing
- ✅ Secure authentication and authorization
- ✅ Full-stack web development
- ✅ GPIO programming on embedded Linux
- ✅ Dual-mode control system (manual + automatic)

## 🚀 Future Enhancements

Potential additions (not yet implemented):
- [ ] Relay module for controlling real AC/DC lights
- [ ] LDR sensor for daylight-aware automation
- [ ] Multiple PIR sensors for different rooms
- [ ] Mobile app (React Native or Flutter)
- [ ] MQTT integration for IoT platform connectivity
- [ ] Scheduled automation (turn on/off at specific times)

## 📄 License

MIT License - feel free to use for learning and projects!

## 📧 Contact

- **GitHub:** [github.com/aqn96/smart-home-light](https://github.com/aqn96/smart-home-light)
- **Issues:** [Report bugs or request features](https://github.com/aqn96/smart-home-light/issues)

---

⭐ **Star this repo if it helped you learn IoT and embedded systems!**

**Built with 💙 on Raspberry Pi 5**
