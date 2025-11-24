**Here's a focused README.md based on exactly what you built:**

```markdown
# 🏠 Smart Home IoT Light Control System

A dual-mode IoT light control system with motion detection and daylight awareness, built on Raspberry Pi 5 using FastAPI + Vanilla JavaScript. Control lights manually through a web interface OR automatically via motion sensor - both modes work together seamlessly.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![Vanilla JS](https://img.shields.io/badge/Vanilla%20JS-ES6+-yellow.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🎮 **Dual Control Mode** | Manual web control AND automatic motion detection work simultaneously |
| 🎯 **Motion Detection** | PIR sensor automatically triggers lights when movement detected |
| 🌅 **Daylight Awareness** | Only activates on motion when it's dark (saves energy) |
| 💡 **Real Light Control** | 5V relay switches actual lights |
| 🔐 **Secure Login** | JWT authentication with password hashing |
| ⏱️ **Timer Function** | Auto-off after configurable timeout |
| 📜 **Action History** | Logs all manual and automatic actions |
| 📱 **Responsive UI** | Works on desktop and mobile |
| 🔒 **HTTPS** | Secure encrypted communication |

## 🔬 How It Works

### Dual Hybrid System:

```
Manual Mode: User clicks toggle → Light changes state (always works)
Auto Mode:   Motion detected + Dark → Light turns ON automatically
             No motion for timeout → Light turns OFF
```

**Smart Logic:**
- Motion sensor checks ambient light before activating (energy efficient)
- Manual control always overrides automatic behavior
- Web interface shows real-time status from both modes
- All actions logged with timestamps

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** + **SQLite** - Database and ORM
- **JWT (python-jose)** - Token authentication
- **Passlib** - Password hashing (bcrypt)
- **GPIO Zero** - Raspberry Pi GPIO control
- **SpiDev** - SPI communication for ADC

### Frontend
- **Vanilla JavaScript (ES6+)** - No frameworks, ~25KB
- **CSS3** - Responsive styling
- **Fetch API** - Backend communication
- **Single Page App** - One HTML file

### Why Vanilla JS?
- ✅ Lightweight - 25KB vs 250MB with frameworks
- ✅ Fast - Instant load, no build step
- ✅ Perfect for IoT devices
- ✅ Modern - ES6+, async/await

## 🔌 Hardware Used

| Component | Model | Purpose |
|-----------|-------|---------|
| Microcontroller | Raspberry Pi 5 | Main controller |
| PIR Motion Sensor | HC-SR501 | Motion detection |
| Photoresistor | GL5528 LDR | Ambient light sensing |
| ADC Converter | ADC0834CCN | Read analog LDR values |
| Relay Module | SRD-05VDC-SL-C | Switch real lights |
| Resistors | 10kΩ, 330Ω | Voltage dividers |
| LED | Standard 5mm | Status indicator |
| Breadboard | 400-point | Circuit prototyping |
| Jumper Wires | M-M, M-F | Connections |

**Hardware Cost:** ~$25-30 (excluding Raspberry Pi)

## 📋 Prerequisites

### Hardware
- Raspberry Pi 5 (or Pi 4)
- microSD card (16GB+)
- Components listed above
- Power supply

### Software
- Raspberry Pi OS (64-bit)
- Python 3.11+
- SSH enabled
- Network connection

## ⚡ Quick Start

### 1. Hardware Wiring

**PIR Motion Sensor:**
```
VCC → Pi Pin 2 (5V)
GND → Pi Pin 6 (GND)
OUT → Pi Pin 13 (GPIO 27)
```

**Status LED:**
```
GPIO 18 (Pin 12) → 330Ω → LED (+)
GND (Pin 6) → LED (-)
```

**Relay Module:**
```
VCC → Pin 2 (5V)
GND → Pin 6 (GND)
IN  → Pin 11 (GPIO 17)
```

**LDR + ADC0834:**
```
3.3V → LDR → ADC CH0 → 10kΩ → GND

ADC Pin 1 (CS)  → GPIO 8  (SPI CE0)
ADC Pin 4 (GND) → GND
ADC Pin 5 (DI)  → GPIO 10 (SPI MOSI)
ADC Pin 6 (DO)  → GPIO 9  (SPI MISO)
ADC Pin 7 (CLK) → GPIO 11 (SPI SCLK)
ADC Pin 8 (VCC) → 3.3V
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

### 3. Enable SPI

```bash
sudo raspi-config
# Interface Options → SPI → Enable
sudo reboot
```

### 4. Configure Environment

```bash
# Generate secret key
python3 -c "import secrets; print(secrets.token_hex(32))"

# Add to backend/.env
nano backend/.env
```

**backend/.env:**
```env
JWT_SECRET_KEY=<your-generated-key>
DATABASE_URL=sqlite:///./smart_light.db
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
```

### 5. Initialize Database

```bash
cd backend
source venv/bin/activate
python database.py
deactivate
cd ..
```

### 6. Generate SSL Certificates

```bash
cd backend
openssl req -x509 -newkey rsa:4096 -nodes -keyout key.pem -out cert.pem -days 365 -subj "/CN=smartlight-an.local"
cd ..
```

### 7. Start Server

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000 \
  --ssl-keyfile=./key.pem \
  --ssl-certfile=./cert.pem
```

**Expected output:**
```
🚀 Server started successfully!
💡 Manual toggle control: ACTIVE
🎯 Motion sensor control: ACTIVE
🌅 Daylight detection: ACTIVE
```

### 8. Access Application

- **Web Interface:** https://smartlight-an.local:8000
- **API Docs:** https://smartlight-an.local:8000/docs

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login and get JWT |
| POST | `/auth/logout` | Revoke token |

### Light Control
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/light/status` | Get light state |
| POST | `/light/toggle` | Manual toggle |
| POST | `/light/timer` | Set auto-off timer |
| GET | `/light/history` | View action log |

### Motion Sensor
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/motion/status` | Get sensor status |
| POST | `/motion/settings` | Configure motion sensor |

### Light Sensor
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/sensor/light` | Get ambient light level |

## 📁 Project Structure

```
smart-home-light/
├── backend/
│   ├── main.py              # FastAPI routes
│   ├── database.py          # Database models
│   ├── auth.py              # JWT authentication
│   ├── gpio_control.py      # LED/relay control
│   ├── motion_control.py    # PIR sensor logic
│   ├── light_sensor.py      # LDR/ADC reading
│   ├── requirements.txt     # Dependencies
│   └── smart_light.db       # SQLite database
├── frontend/
│   └── index.html          # Web interface (~25KB)
├── install.sh              # Setup script
└── README.md
```

## 🐛 Troubleshooting

### Motion Sensor Not Working
```bash
# Add user to GPIO group
sudo usermod -a -G gpio $USER
sudo reboot
```

### LDR Not Reading
```bash
# Check SPI is enabled
lsmod | grep spi
```

### Token Expired
- Login again (tokens expire after 1 hour)
- Clear browser localStorage

## 🔒 Security

- ✅ Bcrypt password hashing
- ✅ JWT tokens (1-hour expiration)
- ✅ HTTPS/TLS encryption
- ✅ SQL injection prevention
- ✅ Environment variable secrets

## 🎓 Project Context

**Built for Embedded Systems Course | November 2024**

Demonstrates:
- IoT hardware integration
- RESTful API design
- Dual-mode control system
- Sensor data processing
- Secure authentication
- Energy-efficient automation

## 📄 License

MIT License

## 📧 Contact

**GitHub:** [github.com/aqn96/smart-home-light](https://github.com/aqn96/smart-home-light)

⭐ **Star if helpful!**
```

---

**This version:**
- ✅ Focuses on your dual manual/automatic system
- ✅ Only mentions hardware you actually have
- ✅ Removes "future features" speculation
- ✅ Keeps it concise and focused
- ✅ Maintains your GitHub style

**Ready to copy and push!** 🚀
