# Smart Home IoT Light Control System

A web-based IoT system for remote light control with JWT authentication, built on Raspberry Pi 5.

## 🎯 Features

- **Remote Control**: Toggle lights ON/OFF from any device on your network
- **Real-Time Status**: Live updates of light state
- **Secure Authentication**: JWT-based user login system
- **Timer Function**: Schedule automatic light shutoff
- **Action History**: Track all control actions with timestamps

**Tech Stack**: Python 3.13, Flask, SQLite, GPIO, JWT, HTML/CSS/JS

---

## 📦 Quick Start

### Prerequisites
- Raspberry Pi 5 with 32GB microSD card
- LED + 330Ω resistor + breadboard + jumper wires
- Raspberry Pi OS (64-bit) installed via Raspberry Pi Imager

### Hardware Setup
```
GPIO 17 (Pin 11) → 330Ω Resistor → LED (+) Long Leg
GND (Pin 6)      → LED (-) Short Leg
```

### Software Installation

```bash
# 1. SSH into your Pi
ssh username@smartlight-an.local

# 2. Clone and navigate
git clone https://github.com/yourusername/smart-home-light.git
cd smart-home-light

# 3. Run installation script
chmod +x install.sh
./install.sh

# 4. Configure environment
cp .env.example .env
python3 -c "import secrets; print(secrets.token_hex(32))"  # Copy this output
nano .env  # Paste the secret as JWT_SECRET_KEY

# 5. Initialize database
python3 database.py

# 6. Start server
python3 app.py
```

### Access
Open browser: `http://YOUR_PI_IP:5000` (find IP with `hostname -I`)

---

## 🌐 API Reference

All endpoints except `/auth/*` require: `Authorization: Bearer {token}`

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Create account | ❌ |
| POST | `/auth/login` | Get JWT token | ❌ |
| POST | `/auth/logout` | Revoke token | ✅ |
| GET | `/light/status` | Get light state | ✅ |
| POST | `/light/toggle` | Toggle light | ✅ |
| POST | `/light/timer` | Set auto-off timer | ✅ |
| GET | `/light/history` | View action log | ✅ |

### Example Usage
```bash
# Register
curl -X POST http://10.200.27.134:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"john","email":"john@example.com","password":"pass123"}'

# Login (get token)
curl -X POST http://10.200.27.134:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"john","password":"pass123"}'

# Toggle light (use token from login)
curl -X POST http://10.200.27.134:5000/light/toggle \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 🔧 Troubleshooting

### Can't connect via SSH
```bash
# Check Pi is reachable
ping smartlight-an.local -c 4

# Try IP address instead
ssh username@10.200.27.134
```

### Can't access web interface
```bash
# Verify server is running
python3 app.py

# Check you're on same network
hostname -I

# Allow port through firewall
sudo ufw allow 5000
```

### LED not working
1. **Check wiring**: GPIO 17 → Resistor → LED(+), GND → LED(-)
2. **Add user to GPIO group**: 
   ```bash
   sudo usermod -a -G gpio $USER
   sudo reboot
   ```
3. **Verify pin number in code**: Should be GPIO 17

### SSL/Package installation errors
```bash
# Fix time (if stuck in 1970)
sudo timedatectl set-ntp true
sudo date -s "2024-11-19 12:00:00"

# Switch to mobile hotspot if home network blocks downloads
sudo nmcli dev wifi connect "Your-Hotspot" password "pass"
sudo apt update
```

### JWT token errors (401 Unauthorized)
- Login again to get fresh token (expires after 1 hour)
- Clear browser localStorage
- Verify `JWT_SECRET_KEY` in `.env` matches server

---

## 📁 Project Structure

```
smart-home-light/
├── install.sh          # Automated setup script
├── .env.example        # Config template (commit this)
├── .env                # Your secrets (DON'T commit!)
├── database.py         # DB schema & user management
├── app.py              # Flask server + JWT + GPIO
├── index.html          # Web UI
├── .gitignore          # Protects secrets
└── README.md           # This file
```

### Files to commit ✅
`README.md`, `.gitignore`, `.env.example`, `install.sh`, `database.py`, `app.py`, `index.html`

### Never commit ❌
`.env` (secrets!), `*.db` (user data), `venv/` (dependencies)

---

## 🔒 Security Features

- **Password hashing**: bcrypt with salt
- **JWT tokens**: HS256 signed, 1-hour expiration
- **Token revocation**: Logout blocklists tokens
- **Parameterized queries**: SQL injection prevention
- **CORS protection**: Configured allowed origins

> ⚠️ **Note**: Current setup is suitable for local networks and learning. For production, add HTTPS, rate limiting, and stronger password requirements.

---

## 🚧 Setup Challenges & Solutions

### 1. Headless Setup
**Challenge**: No micro-HDMI adapter for Pi 5  
**Solution**: SSH-only setup via hostname  
**Benefit**: Professional IoT approach, no monitor needed

### 2. SSL Certificate Failures
**Problem**: `[SSL: CERTIFICATE_VERIFY_FAILED]` on downloads  
**Root Causes**: Hardware RTC stuck at 1970, home network intercepting HTTPS  
**Solution**: Fixed time with `timedatectl`, used mobile hotspot for downloads

### 3. Python 3.13 Compatibility
**Problem**: pip wheel incompatibilities  
**Solution**: Used system packages via `apt` instead of `pip` in venv  
**Why**: Pre-compiled for Raspberry Pi OS, more reliable for single-purpose devices

### 4. Multi-Network Support
**Need**: Demo at home AND school  
**Solution**: Configured both WiFi and mobile hotspot  
```bash
sudo nmcli dev wifi connect "Network-Name" password "pass"
```
**Result**: Pi auto-switches between available networks

---

## 🚀 Usage Scenarios

### At Home
- Pi on home WiFi (e.g., `10.200.27.134`)
- Access from laptop, phone, tablet on same network

### At School/Demo
1. Turn on phone hotspot
2. Pi auto-connects (if preconfigured)
3. Connect laptop to same hotspot
4. Access via Pi's new IP

### Remote Development
```bash
# SSH from anywhere
ssh username@smartlight-an.local

# Edit code
nano app.py

# Restart server
python3 app.py
```

---

## 📚 Key Learnings

### Technical Decisions
- **Headless over Desktop**: Better for IoT, mirrors production environments
- **System packages over venv**: More reliable with Python 3.13 on embedded systems
- **Web app over Native**: Cross-platform, easier to maintain
- **JWT over sessions**: Stateless, scalable architecture

### Network Lessons
- Managed networks (university/corporate) can block SSL downloads
- Mobile hotspot bypasses network restrictions
- Multi-network config essential for portable demos
- Hardware RTC issues affect SSL certificate validation

### IoT Best Practices
- Edge computing (local processing)
- Headless operation for production readiness
- Multi-network resilience
- Graceful GPIO fallback (simulation mode when hardware unavailable)

---

## 🔮 Future Enhancements

- [ ] Multiple light support with room grouping
- [ ] Brightness control using PWM
- [ ] RGB color control
- [ ] WebSocket for real-time updates
- [ ] Mobile app (React Native)
- [ ] Voice control integration
- [ ] Motion sensor automation
- [ ] Usage analytics dashboard

---

## 📖 Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [GPIO Zero Docs](https://gpiozero.readthedocs.io/)
- [Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/)
- [JWT Introduction](https://jwt.io/introduction)

---

## 📝 License

Built for Embedded Systems Course | November 2024

---

**Need help?** Check troubleshooting section above or open an issue on GitHub.
