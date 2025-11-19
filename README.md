# Smart Home IoT Light Control System

A web-based IoT light control system with JWT authentication, built on Raspberry Pi 5.

## 🎯 Project Overview

Remote light control via web interface meeting these requirements:
1. ✅ Toggle lights ON/OFF from anywhere
2. ✅ Real-time status display
3. ✅ JWT authentication
4. ✅ Timer functionality
5. ✅ User-friendly interface

**Tech Stack:** Python 3.13, Flask, SQLite, GPIO, JWT, HTML/CSS/JS

---

## 🔧 Hardware

- Raspberry Pi 5 with 32GB microSD
- LED + 330Ω resistor + breadboard + jumper wires
- **Circuit:** GPIO 17 → 330Ω → LED(+) → LED(-) → GND

---

## 💻 Software

### System Packages (via apt)
```bash
python3-flask python3-flask-cors python3-bcrypt python3-werkzeug 
python3-jwt python3-dotenv python3-gpiozero python3-rpi.gpio
```

**Note:** Using system packages instead of venv due to Python 3.13 compatibility and SSL issues during setup.

---

## 📥 Quick Installation

```bash
# Clone repository
git clone https://github.com/yourusername/smart-home-light.git
cd smart-home-light

# Run install script
chmod +x install.sh
./install.sh

# Configure environment
cp .env.example .env
python3 -c "import secrets; print(secrets.token_hex(32))"  # Generate secret
nano .env  # Add your generated secret

# Initialize database
python3 database.py

# Start server
python3 app.py

# Access at http://YOUR_PI_IP:5000
```

---

## 🚧 Setup Challenges & Solutions

### 1. Headless Setup (No Monitor)
**Challenge:** No micro-HDMI adapter for Pi 5  
**Solution:** SSH-only setup via `ssh username@smartlight-an.local`  
**Benefit:** Professional IoT approach, no monitor needed permanently

### 2. SSL Certificate Failures
**Problem:** `[SSL: CERTIFICATE_VERIFY_FAILED]` on all downloads  
**Root Causes:**
- Hardware RTC stuck at 1970 → time showed 2025
- Home network (Sophie-BR1-5G) intercepting HTTPS

**Solutions:**
```bash
# Fixed time
sudo timedatectl set-ntp true
sudo date -s "2024-11-19 HH:MM:SS"

# Switched to mobile hotspot for downloads
sudo nmcli connection up "An's network"
```

### 3. Package Installation Issues
**Problems:**
- pip SSL errors on home network
- Python 3.13 wheel incompatibilities
- Hash mismatches (filesize: 0) on apt downloads

**Solution:** System packages via apt on mobile hotspot
```bash
sudo apt install python3-flask python3-bcrypt python3-jwt ...
```

**Why system packages:**
- Pre-compiled for Raspberry Pi OS
- No virtual environment complexity
- Reliable for single-purpose IoT device

### 4. Multi-Network Support
**Need:** Work at home AND school  
**Solution:** Configured both networks
```bash
# Home WiFi (preconfigured in imager)
# Mobile hotspot (added via nmcli)
sudo nmcli dev wifi connect "An's network" password "..."
```

**Result:** Pi auto-switches between networks

---

## 📁 Project Structure

```
smart-home-light/
├── install.sh           # Installation script
├── .env.example         # Config template (commit this)
├── .env                 # Real secrets (DON'T commit!)
├── database.py          # DB schema & user management
├── app.py              # Flask server + JWT + GPIO
├── index.html          # Web UI
├── .gitignore          # Protects .env, *.db, venv/
└── README.md           # This file
```

---

## ⚙️ Configuration

### .env Setup
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
nano .env
```

```env
JWT_SECRET_KEY=your-64-char-hex-string-here
JWT_ACCESS_TOKEN_EXPIRES=3600
```

### Multi-Network
```bash
nmcli connection show  # List configured networks
sudo nmcli connection up "network-name"  # Switch network
```

---

## 🌐 API Endpoints

**All endpoints except auth require:** `Authorization: Bearer {token}`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/register | Create account |
| POST | /auth/login | Get JWT token |
| POST | /auth/logout | Revoke token |
| GET | /light/status | Get light state |
| POST | /light/toggle | Toggle light |
| POST | /light/timer | Set auto-off timer |
| GET | /light/history | View action log |

---

## 🔒 Security

- **Passwords:** bcrypt hashed with salt
- **Tokens:** JWT signed with HS256
- **Expiration:** 1 hour default
- **Revocation:** Logout blocklists tokens
- **Secrets:** Stored in `.env` (never committed)

---

## 🔧 Troubleshooting

### SSH Issues
```bash
ping smartlight-an.local -c 4  # Check if Pi is online
ssh username@IP_ADDRESS        # Try IP instead of hostname
```

### Package Install Fails
**SSL errors?** Switch to mobile hotspot:
```bash
sudo nmcli connection up "An's network"
sudo apt update && sudo apt install [packages]
```

### GPIO Not Working
```bash
sudo usermod -a -G gpio $USER
sudo reboot
```

### Time/SSL Issues
```bash
sudo date -s "2024-11-19 HH:MM:SS"
sudo timedatectl set-ntp true
```

### Can't Access Web Interface
- Verify server running: `python3 app.py`
- Check firewall: `sudo ufw status`
- Confirm same network: `hostname -I`

---

## 📚 Key Learnings

**Technical Decisions:**
- Headless > Desktop: Better for IoT, mirrors production
- System packages > venv: More reliable with Python 3.13 on embedded systems
- Custom JWT > flask-jwt-extended: Simpler dependencies
- Web app > Native app: Cross-platform, easier to maintain

**Network Lessons:**
- Managed networks (university/corporate) can block SSL downloads
- Mobile hotspot bypasses restrictions
- Multi-network config essential for portable demos
- Hardware RTC issues affect SSL certificate validation

**IoT Best Practices:**
- Edge computing (local processing)
- Headless operation
- Multi-network resilience
- Graceful GPIO fallback (simulation mode)

---

## 🚀 Usage Scenarios

**At Home:**
- Pi on home WiFi (10.200.27.134)
- Access from any device on home network

**At School/Demo:**
1. Turn on phone hotspot
2. Pi auto-connects
3. Connect laptop to hotspot
4. Access via new IP

**Remote Development:**
- SSH from Mac: `ssh username@smartlight-an.local`
- Edit code with nano
- Run server, test in browser

---

## 📖 Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [GPIO Zero Docs](https://gpiozero.readthedocs.io/)
- [Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/)
- [JWT Introduction](https://jwt.io/introduction)

---

## 📝 Files to Commit

✅ Commit to GitHub:
- README.md, .gitignore, .env.example
- install.sh, database.py, app.py, index.html

❌ Never commit:
- .env (has secrets!)
- *.db (user data)
- venv/ (if it existed)

---

**Built for Embedded Systems Course | November 2024**# Smart Home IoT Light Control System

A comprehensive IoT project implementing remote light control via web interface with JWT authentication, built on Raspberry Pi 5.

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Hardware Requirements](#hardware-requirements)
- [Software Requirements](#software-requirements)
- [Installation Guide](#installation-guide)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Networking](#networking)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Learning Outcomes](#learning-outcomes)
- [Future Enhancements](#future-enhancements)
- [License](#license)

---

## 🎯 Project Overview

This project implements a **Smart Home IoT Light Control System** that allows users to remotely control lights through a web or mobile interface. The system runs on a Raspberry Pi and demonstrates key IoT and embedded systems concepts including:

- RESTful API design
- JWT authentication
- GPIO hardware control
- Real-time status monitoring
- Database management
- Network communication

### Project Requirements

1. ✅ Users can toggle lights ON/OFF from anywhere
2. ✅ Real-time light state display
3. ✅ Authenticated user access only
4. ✅ Timer functionality for scheduled control
5. ✅ Intuitive and user-friendly interface

---

## ✨ Features

### Core Functionality
- **Remote Control**: Toggle lights ON/OFF from any device on the network
- **Real-Time Status**: Live updates of light state
- **User Authentication**: Secure JWT-based login system
- **Timer Function**: Schedule lights to turn off automatically
- **Action History**: Track all light control actions with timestamps
- **Responsive UI**: Works on desktop, tablet, and mobile browsers

### Technical Features
- RESTful API architecture
- SQLite database for user management
- Password hashing with bcrypt
- CORS support for cross-origin requests
- GPIO control for physical hardware
- Virtual environment for dependency isolation

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Web Browser (HTML/CSS/JavaScript)               │  │
│  │  - Login/Register UI                             │  │
│  │  - Light Control Interface                       │  │
│  │  - Real-time Status Updates                      │  │
│  └────────────────┬─────────────────────────────────┘  │
└───────────────────┼─────────────────────────────────────┘
                    │ HTTP/JSON (WiFi)
                    ↓
┌─────────────────────────────────────────────────────────┐
│              RASPBERRY PI (SERVER SIDE)                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Flask Web Server (Python)                       │  │
│  │  - RESTful API Endpoints                         │  │
│  │  - JWT Token Verification                        │  │
│  │  - Request/Response Handling                     │  │
│  └────────┬─────────────────────┬───────────────────┘  │
│           ↓                     ↓                       │
│  ┌────────────────┐    ┌───────────────────┐          │
│  │ SQLite Database│    │  GPIO Controller   │          │
│  │ - Users        │    │  - Pin Control     │          │
│  │ - Logs         │    │  - Hardware I/O    │          │
│  └────────────────┘    └─────────┬─────────┘          │
│                                   ↓                     │
│                            [Physical LED]               │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User Login:**
   - Frontend sends username/password → Backend validates → Returns JWT token
   
2. **Light Control:**
   - Frontend sends toggle request with JWT → Backend verifies token → GPIO controls LED → Database logs action → Returns status

3. **Real-Time Updates:**
   - Frontend polls status every 2 seconds → Backend returns current state

---

## 🔧 Hardware Requirements

### Essential Components
- **Raspberry Pi** (Recommended: Pi 4 or Pi 5)
- **MicroSD Card** (16GB minimum, 32GB+ recommended, Class 10)
- **Power Supply** (USB-C for Pi 4/5, 5V/3A minimum)
- **MicroSD Card Reader** (for initial setup)

### For Development
- **Monitor + HDMI Cable** (optional with headless setup)
- **USB Keyboard & Mouse** (optional with headless setup)
- **Ethernet Cable** (optional, WiFi works)

### Circuit Components
- **Breadboard** (half or full size)
- **LED** (any color, 3mm or 5mm)
- **330Ω Resistor** (orange-orange-brown color bands)
- **Jumper Wires** (2x male-to-female)

### Circuit Diagram

```
Raspberry Pi                    Breadboard
┌──────────┐
│          │
│  GPIO 17 ├────────┐
│          │        │
│      GND ├────┐   │
│          │    │   │
└──────────┘    │   │
                │   │
                │   └─── [330Ω Resistor] ─── [LED +]
                │                                │
                └────────────────────────────────┘ [LED -]

Connection Details:
- GPIO 17 (Physical Pin 11) → 330Ω Resistor → LED Long Leg (+)
- GND (Physical Pin 6, 9, 14, 20, 25, 30, 34, or 39) → LED Short Leg (-)
```

---

## 💻 Software Requirements

### Operating System
- **Raspberry Pi OS (64-bit)** - Latest version recommended
- Installed via Raspberry Pi Imager (not NOOBS - deprecated)

### Programming Languages & Frameworks
- **Python 3.11+**
- **Flask 3.0+** (Web framework)
- **SQLite3** (Database - included with Python)

### Python Libraries
```
flask                 # Web framework
flask-cors            # Cross-Origin Resource Sharing
flask-jwt-extended    # JWT authentication
python-dotenv         # Environment variables
bcrypt                # Password hashing
werkzeug              # WSGI utilities
gpiozero              # GPIO control (Raspberry Pi)
RPi.GPIO              # Low-level GPIO (Raspberry Pi)
```

### Development Tools
- **SSH** (Remote access)
- **nano** or **vim** (Text editors)
- **Git** (Version control - optional)

---

## 📥 Installation Guide

### Step 1: Prepare Raspberry Pi

#### Option A: With Monitor (Traditional)
1. Download Raspberry Pi Imager from https://www.raspberrypi.com/software/
2. Insert microSD card into computer
3. Open Raspberry Pi Imager
4. Select device, OS (Raspberry Pi OS 64-bit), and storage
5. Configure settings (hostname, WiFi, SSH)
6. Write to SD card
7. Insert SD card into Pi and power on

#### Option B: Headless Setup (No Monitor)
1. Follow steps 1-6 above
2. **Important:** Enable SSH in settings before writing
3. Insert SD card into Pi and power on
4. Wait 3-4 minutes for first boot
5. SSH from computer: `ssh username@hostname.local`

**Detailed Configuration in Imager:**
- **Hostname:** `smartlight-an` (or your choice)
- **Username:** Your username
- **Password:** Your password
- **WiFi SSID:** Your network name
- **WiFi Password:** Your network password
- **Locale:** US, America/Los_Angeles (or your timezone)
- **SSH:** Enable with password authentication ✅

### Step 2: Initial System Setup

```bash
# SSH into your Raspberry Pi
ssh username@smartlight-an.local

# Update system packages
sudo apt update
sudo apt upgrade -y

# Reboot
sudo reboot

# Reconnect after reboot
ssh username@smartlight-an.local
```

### Step 3: Install System Dependencies

```bash
# Install system packages
sudo apt install python3-pip python3-full python3-gpiozero python3-rpi.gpio -y

# Verify Python version
python3 --version  # Should be 3.11+
```

### Step 4: Create Project Structure

```bash
# Create project directory
mkdir ~/smart-home-light
cd ~/smart-home-light

# Create subdirectories
mkdir backend frontend static templates

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

**Note:** Your prompt should now show `(venv)` prefix.

### Step 5: Install Python Dependencies

```bash
# Make sure venv is activated
source venv/bin/activate

# Install packages
pip3 install flask flask-cors flask-jwt-extended python-dotenv bcrypt werkzeug

# Verify installation
pip3 list
```

### Step 6: Find Your Pi's IP Address

```bash
hostname -I
```

**Write this down!** You'll need it to access the web interface.
Example: `10.200.27.134`

---

## 📁 Project Structure

```
smart-home-light/
├── venv/                      # Virtual environment (don't commit)
├── backend/                   # Backend resources (optional organization)
├── frontend/                  # Frontend resources (optional organization)
├── static/                    # Static files (CSS, JS)
├── templates/                 # HTML templates (if using Flask templates)
├── database.py               # Database schema and operations
├── app_secure.py             # Main Flask application
├── .env                      # Environment variables (don't commit)
├── index_secure.html         # Frontend interface
├── smarthome.db              # SQLite database (created automatically)
├── README.md                 # This file
└── .gitignore               # Git ignore file
```

### File Descriptions

- **database.py**: Database initialization, user management, action logging
- **app_secure.py**: Flask server, API endpoints, GPIO control, JWT authentication
- **.env**: Configuration (JWT secret, token expiration)
- **index_secure.html**: Web interface (HTML/CSS/JavaScript)
- **smarthome.db**: SQLite database (auto-generated)

---

## ⚙️ Configuration

### Environment Variables (.env)

Create a `.env` file in the project root:

```env
JWT_SECRET_KEY=your-super-secret-key-change-this
JWT_ACCESS_TOKEN_EXPIRES=3600
```

**Security Note:** 
- Generate a strong random key for production
- Never commit `.env` to version control
- Use different keys for development and production

**Generate a secure key:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Database Configuration

The database is automatically initialized on first run. Default schema:

**Users Table:**
- `id`: Primary key
- `username`: Unique username
- `password_hash`: bcrypt hashed password
- `email`: User email
- `created_at`: Account creation timestamp
- `last_login`: Last login timestamp

**Light Logs Table:**
- `id`: Primary key
- `user_id`: Foreign key to users
- `action`: Action performed (e.g., "light_on", "light_off")
- `timestamp`: Action timestamp

---

## 🚀 Usage

### Starting the Server

```bash
# Navigate to project directory
cd ~/smart-home-light

# Activate virtual environment
source venv/bin/activate

# Run the application
python3 app_secure.py
```

**Expected output:**
```
==================================================
Smart Home Light Control Server - SECURE VERSION
==================================================
Authentication: JWT Required
Server running on: http://0.0.0.0:5000
==================================================
```

### Accessing the Web Interface

**From any device on the same network:**

Open a web browser and navigate to:
```
http://YOUR_PI_IP_ADDRESS:5000
```

Example: `http://10.200.27.134:5000`

**Alternative (hostname):**
```
http://smartlight-an.local:5000
```

### First Time Setup

1. **Register an Account:**
   - Click "Register here"
   - Enter username, email, and password (min 6 characters)
   - Click "Register"

2. **Login:**
   - Enter your credentials
   - Click "Login"
   - You'll be redirected to the control panel

3. **Control the Light:**
   - Click "Toggle Light" to turn LED on/off
   - Set a timer (in seconds) to auto-off
   - View action history

### Stopping the Server

Press `Ctrl + C` in the terminal running the server.

---

## 📡 API Documentation

### Base URL
```
http://YOUR_PI_IP:5000
```

### Authentication Endpoints

#### POST /auth/register
Register a new user.

**Request Body:**
```json
{
  "username": "john",
  "email": "john@example.com",
  "password": "securepass123"
}
```

**Response (201):**
```json
{
  "message": "User registered successfully",
  "user_id": 1
}
```

#### POST /auth/login
Login and receive JWT token.

**Request Body:**
```json
{
  "username": "john",
  "password": "securepass123"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "username": "john",
    "email": "john@example.com"
  }
}
```

#### POST /auth/logout
Logout and revoke token.

**Headers:**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Response (200):**
```json
{
  "message": "Logged out successfully"
}
```

### Light Control Endpoints

**Note:** All light control endpoints require JWT authentication.

#### GET /light/status
Get current light status.

**Headers:**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Response (200):**
```json
{
  "state": "on",
  "timestamp": "2024-11-19T10:30:00",
  "timer_active": false
}
```

#### POST /light/toggle
Toggle light on/off.

**Headers:**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Response (200):**
```json
{
  "state": "off",
  "message": "Light toggled successfully",
  "user_id": 1
}
```

#### POST /light/on
Turn light on.

**Headers:**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Response (200):**
```json
{
  "state": "on",
  "message": "Light turned on"
}
```

#### POST /light/off
Turn light off.

**Headers:**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Response (200):**
```json
{
  "state": "off",
  "message": "Light turned off"
}
```

#### POST /light/timer
Set timer to turn light off.

**Headers:**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Request Body:**
```json
{
  "seconds": 300
}
```

**Response (200):**
```json
{
  "message": "Timer set for 300 seconds",
  "timer_active": true,
  "timer_end_time": "2024-11-19T10:35:00"
}
```

#### GET /light/history
Get user's action history.

**Headers:**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Response (200):**
```json
{
  "history": [
    {
      "action": "light_on",
      "timestamp": "2024-11-19T10:30:00"
    },
    {
      "action": "light_off",
      "timestamp": "2024-11-19T10:28:00"
    }
  ],
  "count": 2
}
```

---

## 🌐 Networking

### Network Architecture

```
[Internet/ISP]
      ↓
[WiFi Router] (Gateway: 10.200.27.1)
      ↓
      ├─ [Laptop/Mac] (10.200.27.XXX)
      ├─ [Raspberry Pi] (10.200.27.134:5000)
      └─ [Phone] (10.200.27.YYY)
```

### Network Configuration

**Home WiFi Setup:**
- Configured during Raspberry Pi Imager setup
- Automatically connects on boot
- Static or DHCP IP assignment

**Mobile Hotspot Setup (Optional):**

For demonstrations away from home:

```bash
# Add mobile hotspot network
sudo nmcli dev wifi connect "Your-Hotspot-Name" password "your-hotspot-password"

# Pi will remember both networks
# Automatically connects to available network
```

**Network Priority:**
1. Wired Ethernet (if connected)
2. Home WiFi (stronger signal/configured first)
3. Mobile Hotspot (backup)

### Port Configuration

- **Port 5000**: Flask web server (HTTP)
- **Port 22**: SSH (for remote access)

**Firewall (Optional):**
```bash
sudo apt install ufw
sudo ufw default deny incoming
sudo ufw allow ssh
sudo ufw allow 5000
sudo ufw enable
```

### Accessing from Different Networks

**Same WiFi Network:**
```
http://10.200.27.134:5000
```

**Using Hostname (same network):**
```
http://smartlight-an.local:5000
```

**From Internet (Advanced - Not Recommended for Beginners):**
- Requires port forwarding on router
- Security risks - use VPN instead
- Dynamic DNS for changing IP

---

## 🔒 Security

### Authentication Flow

1. **Password Storage:**
   - Never stored in plain text
   - Hashed using bcrypt with salt
   - Computationally expensive to crack

2. **JWT Tokens:**
   - Signed with secret key
   - Contains user ID and expiration
   - Verified on each request
   - Expires after 1 hour (configurable)

3. **Token Revocation:**
   - Logout adds token to blocklist
   - Prevents reuse of logged-out tokens

### Security Best Practices Implemented

✅ **Password Hashing**: bcrypt with salt
✅ **JWT Authentication**: Stateless, secure tokens
✅ **CORS Protection**: Configured allowed origins
✅ **Input Validation**: Username, password requirements
✅ **SQL Injection Prevention**: Parameterized queries
✅ **Token Expiration**: 1-hour timeout

### Security Recommendations

**For Production Use:**

1. **HTTPS:**
   ```bash
   pip3 install pyopenssl
   # Use SSL certificates
   ```

2. **Rate Limiting:**
   ```bash
   pip3 install flask-limiter
   # Prevent brute force attacks
   ```

3. **Strong Passwords:**
   - Enforce minimum 12 characters
   - Require special characters
   - Check against common passwords

4. **Environment Variables:**
   - Never commit `.env` file
   - Use strong secret keys
   - Rotate keys periodically

5. **Network Security:**
   - Use VPN for remote access
   - Enable firewall (ufw)
   - Disable unused services

### Current Security Level

**Good for:** 
- ✅ Class projects
- ✅ Home network use
- ✅ Learning purposes
- ✅ Controlled demonstrations

**Not suitable for:**
- ❌ Public internet exposure
- ❌ Production deployment without hardening
- ❌ Critical applications

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Issue: Can't Connect via SSH

**Symptoms:**
```
ssh: connect to host smartlight-an.local port 22: Connection refused
```

**Solutions:**
1. Check Pi is powered on (red LED should be lit)
2. Verify WiFi connection:
   ```bash
   ping smartlight-an.local -c 4
   ```
3. Try IP address instead of hostname:
   ```bash
   ssh username@10.200.27.134
   ```
4. Check SSH is enabled:
   - Re-image SD card with SSH enabled in settings
5. Try different network:
   - Connect both Mac and Pi to phone hotspot

#### Issue: microSD Card Not Recognized

**Solutions:**
1. Remove and reinsert card firmly
2. Check card orientation (metal contacts face board)
3. Try different card reader
4. Format card and re-image:
   ```bash
   # On Mac
   diskutil list
   diskutil eraseDisk FAT32 SDCARD /dev/diskX
   ```

#### Issue: Virtual Environment Errors

**Symptoms:**
```
error: externally-managed-environment
```

**Solution:**
Create and use virtual environment:
```bash
cd ~/smart-home-light
python3 -m venv venv
source venv/bin/activate
pip3 install [packages]
```

#### Issue: GPIO Permission Denied

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied: '/dev/gpiomem'
```

**Solution:**
Add user to gpio group:
```bash
sudo usermod -a -G gpio $USER
sudo reboot
```

#### Issue: Can't Access Web Interface

**Symptoms:**
- Browser shows "Can't reach this page"
- Connection timeout

**Solutions:**
1. Verify server is running:
   ```bash
   python3 app_secure.py
   ```
2. Check you're on same network as Pi
3. Verify IP address:
   ```bash
   hostname -I
   ```
4. Try different browser
5. Check firewall:
   ```bash
   sudo ufw status
   sudo ufw allow 5000
   ```

#### Issue: LED Not Working

**Solutions:**
1. Check wiring:
   - GPIO 17 → Resistor → LED (+) long leg
   - GND → LED (-) short leg
2. Verify GPIO pin number in code (17)
3. Test LED with multimeter
4. Try different LED (might be burned out)
5. Check resistor value (330Ω)

#### Issue: JWT Token Errors

**Symptoms:**
```
401 Unauthorized
Invalid token
```

**Solutions:**
1. Login again to get fresh token
2. Check token hasn't expired (1 hour default)
3. Clear browser localStorage
4. Verify JWT_SECRET_KEY in `.env`

#### Issue: Database Errors

**Symptoms:**
```
sqlite3.OperationalError: database is locked
```

**Solutions:**
1. Close all connections to database
2. Restart Flask server
3. If persistent, delete and recreate:
   ```bash
   rm smarthome.db
   python3 database.py
   ```

#### Issue: Module Not Found

**Symptoms:**
```
ModuleNotFoundError: No module named 'flask'
```

**Solution:**
Activate virtual environment:
```bash
cd ~/smart-home-light
source venv/bin/activate
pip3 install flask [other packages]
```

#### Issue: Hotspot Won't Connect

**Solutions:**
1. Verify hotspot SSID and password
2. Check hotspot is 2.4 GHz (not 5 GHz only)
3. Disable "Auto Hotspot" on phone
4. Disable "One-time password"
5. Reconnect both devices to hotspot

### Debug Mode

Enable detailed error messages:

```python
# In app_secure.py
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Set debug=True
# Smart Home IoT Light Control System

A web-based IoT light control system with JWT authentication, built on Raspberry Pi 5.

## 🎯 Project Overview

Remote light control via web interface meeting these requirements:
1. ✅ Toggle lights ON/OFF from anywhere
2. ✅ Real-time status display
3. ✅ JWT authentication
4. ✅ Timer functionality
5. ✅ User-friendly interface

**Tech Stack:** Python 3.13, Flask, SQLite, GPIO, JWT, HTML/CSS/JS

---

## 🔧 Hardware

- Raspberry Pi 5 with 32GB microSD
- LED + 330Ω resistor + breadboard + jumper wires
- **Circuit:** GPIO 17 → 330Ω → LED(+) → LED(-) → GND

---

## 💻 Software

### System Packages (via apt)
```bash
python3-flask python3-flask-cors python3-bcrypt python3-werkzeug 
python3-jwt python3-dotenv python3-gpiozero python3-rpi.gpio
```

**Note:** Using system packages instead of venv due to Python 3.13 compatibility and SSL issues during setup.

---

## 📥 Quick Installation

```bash
# Clone repository
git clone https://github.com/yourusername/smart-home-light.git
cd smart-home-light

# Run install script
chmod +x install.sh
./install.sh

# Configure environment
cp .env.example .env
python3 -c "import secrets; print(secrets.token_hex(32))"  # Generate secret
nano .env  # Add your generated secret

# Initialize database
python3 database.py

# Start server
python3 app.py

# Access at http://YOUR_PI_IP:5000
```

---

## 🚧 Setup Challenges & Solutions

### 1. Headless Setup (No Monitor)
**Challenge:** No micro-HDMI adapter for Pi 5  
**Solution:** SSH-only setup via `ssh username@smartlight-an.local`  
**Benefit:** Professional IoT approach, no monitor needed permanently

### 2. SSL Certificate Failures
**Problem:** `[SSL: CERTIFICATE_VERIFY_FAILED]` on all downloads  
**Root Causes:**
- Hardware RTC stuck at 1970 → time showed 2025
- Home network (Sophie-BR1-5G) intercepting HTTPS

**Solutions:**
```bash
# Fixed time
sudo timedatectl set-ntp true
sudo date -s "2024-11-19 HH:MM:SS"

# Switched to mobile hotspot for downloads
sudo nmcli connection up "An's network"
```

### 3. Package Installation Issues
**Problems:**
- pip SSL errors on home network
- Python 3.13 wheel incompatibilities
- Hash mismatches (filesize: 0) on apt downloads

**Solution:** System packages via apt on mobile hotspot
```bash
sudo apt install python3-flask python3-bcrypt python3-jwt ...
```

**Why system packages:**
- Pre-compiled for Raspberry Pi OS
- No virtual environment complexity
- Reliable for single-purpose IoT device

### 4. Multi-Network Support
**Need:** Work at home AND school  
**Solution:** Configured both networks
```bash
# Home WiFi (preconfigured in imager)
# Mobile hotspot (added via nmcli)
sudo nmcli dev wifi connect "An's network" password "..."
```

**Result:** Pi auto-switches between networks

---

## 📁 Project Structure

```
smart-home-light/
├── install.sh           # Installation script
├── .env.example         # Config template (commit this)
├── .env                 # Real secrets (DON'T commit!)
├── database.py          # DB schema & user management
├── app.py              # Flask server + JWT + GPIO
├── index.html          # Web UI
├── .gitignore          # Protects .env, *.db, venv/
└── README.md           # This file
```

---

## ⚙️ Configuration

### .env Setup
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
nano .env
```

```env
JWT_SECRET_KEY=your-64-char-hex-string-here
JWT_ACCESS_TOKEN_EXPIRES=3600
```

### Multi-Network
```bash
nmcli connection show  # List configured networks
sudo nmcli connection up "network-name"  # Switch network
```

---

## 🌐 API Endpoints

**All endpoints except auth require:** `Authorization: Bearer {token}`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/register | Create account |
| POST | /auth/login | Get JWT token |
| POST | /auth/logout | Revoke token |
| GET | /light/status | Get light state |
| POST | /light/toggle | Toggle light |
| POST | /light/timer | Set auto-off timer |
| GET | /light/history | View action log |

---

## 🔒 Security

- **Passwords:** bcrypt hashed with salt
- **Tokens:** JWT signed with HS256
- **Expiration:** 1 hour default
- **Revocation:** Logout blocklists tokens
- **Secrets:** Stored in `.env` (never committed)

---

## 🔧 Troubleshooting

### SSH Issues
```bash
ping smartlight-an.local -c 4  # Check if Pi is online
ssh username@IP_ADDRESS        # Try IP instead of hostname
```

### Package Install Fails
**SSL errors?** Switch to mobile hotspot:
```bash
sudo nmcli connection up "An's network"
sudo apt update && sudo apt install [packages]
```

### GPIO Not Working
```bash
sudo usermod -a -G gpio $USER
sudo reboot
```

### Time/SSL Issues
```bash
sudo date -s "2024-11-19 HH:MM:SS"
sudo timedatectl set-ntp true
```

### Can't Access Web Interface
- Verify server running: `python3 app.py`
- Check firewall: `sudo ufw status`
- Confirm same network: `hostname -I`

---

## 📚 Key Learnings

**Technical Decisions:**
- Headless > Desktop: Better for IoT, mirrors production
- System packages > venv: More reliable with Python 3.13 on embedded systems
- Custom JWT > flask-jwt-extended: Simpler dependencies
- Web app > Native app: Cross-platform, easier to maintain

**Network Lessons:**
- Managed networks (university/corporate) can block SSL downloads
- Mobile hotspot bypasses restrictions
- Multi-network config essential for portable demos
- Hardware RTC issues affect SSL certificate validation

**IoT Best Practices:**
- Edge computing (local processing)
- Headless operation
- Multi-network resilience
- Graceful GPIO fallback (simulation mode)

---

## 🚀 Usage Scenarios

**At Home:**
- Pi on home WiFi (10.200.27.134)
- Access from any device on home network

**At School/Demo:**
1. Turn on phone hotspot
2. Pi auto-connects
3. Connect laptop to hotspot
4. Access via new IP

**Remote Development:**
- SSH from Mac: `ssh username@smartlight-an.local`
- Edit code with nano
- Run server, test in browser

---

## 📖 Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [GPIO Zero Docs](https://gpiozero.readthedocs.io/)
- [Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/)
- [JWT Introduction](https://jwt.io/introduction)

---

## 📝 Files to Commit

✅ Commit to GitHub:
- README.md, .gitignore, .env.example
- install.sh, database.py, app.py, index.html

❌ Never commit:
- .env (has secrets!)
- *.db (user data)
- venv/ (if it existed)

---

**Built for Embedded Systems Course | November 2024**```

**Warning:** Never use `debug=True` in production!

### Getting Help

1. Check error messages in terminal
2. Review server logs
3. Test API endpoints with curl:
   ```bash
   curl http://10.200.27.134:5000/
   ```
4. Check system logs:
   ```bash
   journalctl -xe
   ```

---

## 📚 Learning Outcomes

### Technical Skills Acquired

**IoT & Embedded Systems:**
- Edge computing architecture
- GPIO hardware interfacing
- Real-time system control
- Sensor/actuator integration

**Web Development:**
- RESTful API design
- Client-server architecture
- HTTP methods and status codes
- JSON data interchange
- CORS configuration

**Backend Development:**
- Flask web framework
- Python programming
- Virtual environments
- Database operations (SQLite)
- SQL queries and schema design

**Security:**
- JWT authentication
- Password hashing (bcrypt)
- Token-based authorization
- Secure API endpoints
- Input validation

**Networking:**
- TCP/IP fundamentals
- IP addressing and subnets
- Port configuration
- WiFi setup and management
- SSH remote access
- Network troubleshooting

**Linux & DevOps:**
- Command line proficiency
- Package management (apt, pip)# Smart Home IoT Light Control System

A web-based IoT light control system with JWT authentication, built on Raspberry Pi 5.

## 🎯 Project Overview

Remote light control via web interface meeting these requirements:
1. ✅ Toggle lights ON/OFF from anywhere
2. ✅ Real-time status display
3. ✅ JWT authentication
4. ✅ Timer functionality
5. ✅ User-friendly interface

**Tech Stack:** Python 3.13, Flask, SQLite, GPIO, JWT, HTML/CSS/JS

---

## 🔧 Hardware

- Raspberry Pi 5 with 32GB microSD
- LED + 330Ω resistor + breadboard + jumper wires
- **Circuit:** GPIO 17 → 330Ω → LED(+) → LED(-) → GND

---

## 💻 Software

### System Packages (via apt)
```bash
python3-flask python3-flask-cors python3-bcrypt python3-werkzeug 
python3-jwt python3-dotenv python3-gpiozero python3-rpi.gpio
```

**Note:** Using system packages instead of venv due to Python 3.13 compatibility and SSL issues during setup.

---

## 📥 Quick Installation

```bash
# Clone repository
git clone https://github.com/yourusername/smart-home-light.git
cd smart-home-light

# Run install script
chmod +x install.sh
./install.sh

# Configure environment
cp .env.example .env
python3 -c "import secrets; print(secrets.token_hex(32))"  # Generate secret
nano .env  # Add your generated secret

# Initialize database
python3 database.py

# Start server
python3 app.py

# Access at http://YOUR_PI_IP:5000
```

---

## 🚧 Setup Challenges & Solutions

### 1. Headless Setup (No Monitor)
**Challenge:** No micro-HDMI adapter for Pi 5  
**Solution:** SSH-only setup via `ssh username@smartlight-an.local`  
**Benefit:** Professional IoT approach, no monitor needed permanently

### 2. SSL Certificate Failures
**Problem:** `[SSL: CERTIFICATE_VERIFY_FAILED]` on all downloads  
**Root Causes:**
- Hardware RTC stuck at 1970 → time showed 2025
- Home network (Sophie-BR1-5G) intercepting HTTPS

**Solutions:**
```bash
# Fixed time
sudo timedatectl set-ntp true
sudo date -s "2024-11-19 HH:MM:SS"

# Switched to mobile hotspot for downloads
sudo nmcli connection up "An's network"
```

### 3. Package Installation Issues
**Problems:**
- pip SSL errors on home network
- Python 3.13 wheel incompatibilities
- Hash mismatches (filesize: 0) on apt downloads

**Solution:** System packages via apt on mobile hotspot
```bash
sudo apt install python3-flask python3-bcrypt python3-jwt ...
```

**Why system packages:**
- Pre-compiled for Raspberry Pi OS
- No virtual environment complexity
- Reliable for single-purpose IoT device

### 4. Multi-Network Support
**Need:** Work at home AND school  
**Solution:** Configured both networks
```bash
# Home WiFi (preconfigured in imager)
# Mobile hotspot (added via nmcli)
sudo nmcli dev wifi connect "An's network" password "..."
```

**Result:** Pi auto-switches between networks

---

## 📁 Project Structure

```
smart-home-light/
├── install.sh           # Installation script
├── .env.example         # Config template (commit this)
├── .env                 # Real secrets (DON'T commit!)
├── database.py          # DB schema & user management
├── app.py              # Flask server + JWT + GPIO
├── index.html          # Web UI
├── .gitignore          # Protects .env, *.db, venv/
└── README.md           # This file
```

---

## ⚙️ Configuration

### .env Setup
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
nano .env
```

```env
JWT_SECRET_KEY=your-64-char-hex-string-here
JWT_ACCESS_TOKEN_EXPIRES=3600
```

### Multi-Network
```bash
nmcli connection show  # List configured networks
sudo nmcli connection up "network-name"  # Switch network
```

---

## 🌐 API Endpoints

**All endpoints except auth require:** `Authorization: Bearer {token}`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/register | Create account |
| POST | /auth/login | Get JWT token |
| POST | /auth/logout | Revoke token |
| GET | /light/status | Get light state |
| POST | /light/toggle | Toggle light |
| POST | /light/timer | Set auto-off timer |
| GET | /light/history | View action log |

---

## 🔒 Security

- **Passwords:** bcrypt hashed with salt
- **Tokens:** JWT signed with HS256
- **Expiration:** 1 hour default
- **Revocation:** Logout blocklists tokens
- **Secrets:** Stored in `.env` (never committed)

---

## 🔧 Troubleshooting

### SSH Issues
```bash
ping smartlight-an.local -c 4  # Check if Pi is online
ssh username@IP_ADDRESS        # Try IP instead of hostname
```

### Package Install Fails
**SSL errors?** Switch to mobile hotspot:
```bash
sudo nmcli connection up "An's network"
sudo apt update && sudo apt install [packages]
```

### GPIO Not Working
```bash
sudo usermod -a -G gpio $USER
sudo reboot
```

### Time/SSL Issues
```bash
sudo date -s "2024-11-19 HH:MM:SS"
sudo timedatectl set-ntp true
```

### Can't Access Web Interface
- Verify server running: `python3 app.py`
- Check firewall: `sudo ufw status`
- Confirm same network: `hostname -I`

---

## 📚 Key Learnings

**Technical Decisions:**
- Headless > Desktop: Better for IoT, mirrors production
- System packages > venv: More reliable with Python 3.13 on embedded systems
- Custom JWT > flask-jwt-extended: Simpler dependencies
- Web app > Native app: Cross-platform, easier to maintain

**Network Lessons:**
- Managed networks (university/corporate) can block SSL downloads
- Mobile hotspot bypasses restrictions
- Multi-network config essential for portable demos
- Hardware RTC issues affect SSL certificate validation

**IoT Best Practices:**
- Edge computing (local processing)
- Headless operation
- Multi-network resilience
- Graceful GPIO fallback (simulation mode)

---

## 🚀 Usage Scenarios

**At Home:**
- Pi on home WiFi (10.200.27.134)
- Access from any device on home network

**At School/Demo:**
1. Turn on phone hotspot
2. Pi auto-connects
3. Connect laptop to hotspot
4. Access via new IP

**Remote Development:**
- SSH from Mac: `ssh username@smartlight-an.local`
- Edit code with nano
- Run server, test in browser

---

## 📖 Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [GPIO Zero Docs](https://gpiozero.readthedocs.io/)
- [Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/)
- [JWT Introduction](https://jwt.io/introduction)

---

## 📝 Files to Commit

✅ Commit to GitHub:
- README.md, .gitignore, .env.example
- install.sh, database.py, app.py, index.html

❌ Never commit:
- .env (has secrets!)
- *.db (user data)
- venv/ (if it existed)

---

**Built for Embedded Systems Course | November 2024**
- Service management
- File system navigation
- Text editors (nano/vim)

**Version Control:**
- Git basics
- Repository management
- .gitignore configuration

### Concepts Mastered

- Client-server communication
- Stateless vs stateful architecture
- Authentication vs authorization
- Request/response cycle
- Event-driven programming
- Asynchronous operations
- Database normalization
- Error handling and logging

---

## 🚀 Future Enhancements

### Short-term Improvements

**1. Enhanced UI:**
- Dark mode toggle
- Animation effects
- Progress indicators
- Toast notifications
- Mobile-optimized layout

**2. Additional Features:**
- Multiple light support
- Room grouping
- Brightness control (PWM)
- Color control (RGB LED)
- Schedule recurring timers

**3. Better Logging:**
- Export logs to CSV
- Filter by date range
- Graph usage statistics
- Energy consumption tracking

### Medium-term Enhancements

**4. Advanced Authentication:**
- Multi-factor authentication (MFA)
- OAuth integration
- Role-based access control
- Session management

**5. Real-Time Updates:**
- WebSocket implementation
- Server-sent events (SSE)
- Push notifications
- Live status without polling

**6. Smart Features:**
- Motion sensor integration
- Sunrise/sunset scheduling
- Geofencing (location-based)
- Voice control (Alexa/Google)

**7. Mobile App:**
- React Native app
- iOS/Android support
- Push notifications
- Offline mode

### Long-term Vision

**8. Cloud Integration:**
- AWS/Azure hosting
- Remote access from anywhere
- Cloud database (PostgreSQL)
- Scalable architecture

**9. Home Automation:**
- MQTT protocol
- Home Assistant integration
- Multiple sensor types
- Automation rules engine

**10. Machine Learning:**
- Usage pattern learning
- Predictive scheduling
- Anomaly detection
- Energy optimization

**11. Commercial Features:**
- Multi-user support
- Subscription tiers
- Admin dashboard
- Analytics and reporting

---

## 🛠️ Development Setup (For Contributors)

### Prerequisites
- Raspberry Pi (4 or 5 recommended)
- Python 3.11+
- Git
- SSH client

### Clone Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/smart-home-light.git
cd smart-home-light

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip3 install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your settings

# Initialize database
python3 database.py

# Run application
python3 app_secure.py
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "Add new feature"

# Push to GitHub
git push origin feature/new-feature

# Create pull request on GitHub
```

### .gitignore

```gitignore
# Virtual Environment
venv/
env/

# Environment Variables
.env

# Database
*.db
*.sqlite

# Python
__pycache__/
*.py[cod]
*$py.class
*.so

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
```

---

## 📖 Additional Resources

### Documentation
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/)
- [GPIO Zero](https://gpiozero.readthedocs.io/)
- [Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/)

### Tutorials
- [Raspberry Pi Getting Started](https://projects.raspberrypi.org/)
- [RESTful API Design](https://restfulapi.net/)
- [JWT Introduction](https://jwt.io/introduction)

### Community
- [Raspberry Pi Forums](https://forums.raspberrypi.com/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/raspberry-pi)
- [Reddit r/raspberry_pi](https://www.reddit.com/r/raspberry_pi/)

---

## 🙏 Acknowledgments

- Raspberry Pi Foundation for hardware and documentation
- Flask community for excellent web framework
- GPIO Zero developers for simplified hardware control
- Contributors and testers

---

## 📝 Notes for Instructors/Reviewers

### Project Validation

**Setup Verification:**
1. Raspberry Pi OS properly installed
2. SSH and network configured
3. Virtual environment created
4. All dependencies installed

**Core Functionality:**
1. User registration and login working
2. JWT authentication enforced
3. Light toggle responds correctly
4. Timer function operates as expected
5. Database logs all actions

**Code Quality:**
1. Proper error handling
2. Input validation
3. Security best practices followed
4. Code comments and documentation
5. Modular, maintainable structure

### Demo Instructions

**Live Demonstration:**
1. Show user registration
2. Login and receive JWT token
3. Toggle light via web interface
4. Set and verify timer function
5. Display action history
6. Show multiple device access

**Technical Deep Dive:**
1. Explain architecture diagram
2. Walk through API endpoints
3. Demonstrate GPIO control
4. Show database operations
5. Discuss security implementation

---

## 🔗 Quick Links

- **Project Repository:** [GitHub Link]
- **Live Demo:** http://YOUR_PI_IP:5000
- **Documentation:** This README
- **Issues/Bugs:** [GitHub Issues]

---

## 📅 Project Timeline

**Week 1-2:** Setup and Configuration
- Raspberry Pi OS installation
- Network configuration
- SSH setup
- Development environment

**Week 3-4:** Backend Development
- Database schema
- Flask API endpoints
- JWT authentication
- GPIO integration

**Week 5:** Frontend Development
- HTML/CSS interface
- JavaScript functionality
- API integration

**Week 6:** Testing and Documentation
- End-to-end testing
- Bug fixes
- Documentation
- Final presentation

---

## ✅ Project Checklist

### Requirements Met
- [x] Remote light control
- [x] Real-time status display
- [x] User authentication
- [x] Timer functionality
- [x] User-friendly interface
- [x] Database logging
- [x] Secure API
- [x] Documentation

### Bonus Features
- [x] Action history
- [x] Multiple user support
- [x] Password hashing
- [x] JWT token management
- [x] Mobile hotspot support
- [x] Headless operation

---

**Built with ❤️ for Embedded Systems course**

*Last Updated: November 2024*
