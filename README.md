# 🏠 Smart Home IoT Light Control System

A modern web-based IoT system for remote light control with JWT authentication, built on **Raspberry Pi 5** using **FastAPI** + **React**.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)
![React](https://img.shields.io/badge/React-18+-61DAFB)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔐 **Secure Authentication** | JWT-based user login system with bcrypt password hashing |
| 💡 **Remote Control** | Toggle lights ON/OFF from any device on your network |
| ⏱️ **Timer Function** | Schedule automatic light shutoff |
| 📊 **Real-Time Status** | Live updates of light state via WebSocket (coming soon) |
| 📜 **Action History** | Track all control actions with timestamps |
| 📱 **Responsive UI** | Modern React interface works on desktop and mobile |
| 🔌 **GPIO Control** | Direct hardware control via Raspberry Pi GPIO pins |

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework with auto-generated API docs
- **SQLAlchemy** - SQL toolkit and ORM
- **SQLite** - Lightweight database
- **JWT (python-jose)** - Token-based authentication
- **Passlib** - Password hashing with bcrypt
- **GPIO Zero** - Simple GPIO control library

### Frontend
- **React 18** - Component-based UI framework
- **Vite** - Next-generation frontend tooling
- **JavaScript/JSX** - Modern ES6+ syntax
- **Fetch API** - HTTP requests to backend

---

## 📋 Prerequisites

### Hardware
- Raspberry Pi 5 (or Pi 4/3B+)
- 32GB microSD card (minimum 16GB)
- LED + 330Ω resistor
- Breadboard + jumper wires
- Power supply for Raspberry Pi

### Software
- Raspberry Pi OS (64-bit) - Latest version
- SSH enabled (for headless setup)
- Network connection (WiFi or Ethernet)

---

## ⚡ Quick Start

### 1. Hardware Setup

Connect your LED to the Raspberry Pi:

```
GPIO 17 (Pin 11) → 330Ω Resistor → LED Anode (+) Long Leg
GND (Pin 6)      → LED Cathode (-) Short Leg
```

### 2. Software Installation

```bash
# SSH into your Raspberry Pi
ssh username@smartlight-an.local

# Clone the repository
git clone https://github.com/aqn96/smart-home-light.git
cd smart-home-light

# Run automated installation
chmod +x install.sh
./install.sh
```

### 3. Configure Environment

```bash
# Generate JWT secret key
python3 -c "import secrets; print(secrets.token_hex(32))"

# Edit backend/.env and add the generated key
nano backend/.env
```

**backend/.env should contain:**
```env
JWT_SECRET_KEY=<paste-your-generated-key-here>
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

### 5. Start the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev -- --host
```

### 6. Access the Application

- **Frontend UI:** `http://<your-pi-ip>:5173`
- **Backend API:** `http://<your-pi-ip>:8000`
- **API Documentation:** `http://<your-pi-ip>:8000/docs` ⭐ (Auto-generated Swagger UI!)

Find your Pi's IP with: `hostname -I`

---

## 📡 API Reference

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Create new user account | ❌ |
| POST | `/auth/login` | Login and receive JWT token | ❌ |
| POST | `/auth/logout` | Revoke current token | ✅ |

### Light Control Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/light/status` | Get current light state | ✅ |
| POST | `/light/toggle` | Toggle light ON/OFF | ✅ |
| POST | `/light/timer` | Set auto-off timer (seconds) | ✅ |
| GET | `/light/history` | View action log | ✅ |

### Example Usage

**Register a new user:**
```bash
curl -X POST http://10.200.27.134:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"john","email":"john@example.com","password":"securepass123"}'
```

**Login and get token:**
```bash
curl -X POST http://10.200.27.134:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"john","password":"securepass123"}'
```

**Toggle light (use token from login):**
```bash
curl -X POST http://10.200.27.134:8000/light/toggle \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 📁 Project Structure

```
smart-home-light/
├── backend/                    # FastAPI Backend
│   ├── venv/                  # Virtual environment (not in git)
│   ├── .env                   # Environment variables (not in git)
│   ├── main.py                # FastAPI application & routes
│   ├── database.py            # SQLAlchemy models & DB setup
│   ├── auth.py                # JWT authentication logic
│   ├── gpio_control.py        # LED hardware control
│   ├── requirements.txt       # Python dependencies
│   └── smart_light.db         # SQLite database (created on init)
│
├── frontend/                  # React Frontend
│   ├── src/
│   │   ├── App.jsx           # Main React component
│   │   ├── components/       # Reusable UI components
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── LightControl.jsx
│   │   │   ├── Timer.jsx
│   │   │   └── History.jsx
│   │   └── main.jsx          # React entry point
│   ├── package.json          # Node dependencies
│   └── vite.config.js        # Vite configuration
│
├── .gitignore                # Git ignore rules
├── .env.example              # Environment template
├── install.sh                # Automated installation script
└── README.md                 # This file
```

---

## 🔧 Development Guide

### Backend Development

```bash
# Activate virtual environment
cd backend
source venv/bin/activate

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Access interactive API docs at:
# http://localhost:8000/docs
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start dev server with hot reload
npm run dev -- --host

# Build for production
npm run build
```

### Adding New Dependencies

**Python (Backend):**
```bash
cd backend
source venv/bin/activate
pip install <package-name>
pip freeze > requirements.txt
```

**JavaScript (Frontend):**
```bash
cd frontend
npm install <package-name>
```

---

## 🐛 Troubleshooting

### Can't Connect via SSH
```bash
# Check Pi is reachable
ping smartlight-an.local -c 4

# Try IP address instead
ssh username@<pi-ip-address>
```

### Backend Won't Start
```bash
# Check virtual environment is activated
source backend/venv/bin/activate

# Verify all packages installed
pip install -r requirements.txt

# Check .env file exists
cat backend/.env
```

### Frontend Won't Start
```bash
# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### LED Not Working
```bash
# Add user to GPIO group
sudo usermod -a -G gpio $USER
sudo reboot

# Test GPIO directly
python3 -c "from gpiozero import LED; led = LED(17); led.on()"
```

### JWT Token Errors (401 Unauthorized)
- Login again to get fresh token (tokens expire after 1 hour)
- Clear browser localStorage
- Verify `JWT_SECRET_KEY` in backend/.env

### Port Already in Use
```bash
# Kill process on port 8000
sudo lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

---

## 🔒 Security Features

- ✅ **Password Hashing:** Bcrypt with salt (10 rounds)
- ✅ **JWT Tokens:** HS256 signed, 1-hour expiration
- ✅ **Token Revocation:** Logout blocklists tokens in database
- ✅ **SQL Injection Prevention:** Parameterized queries via SQLAlchemy ORM
- ✅ **CORS Protection:** Configured allowed origins
- ✅ **Environment Variables:** Secrets stored in .env (not in git)

⚠️ **Note:** This setup is suitable for local networks and learning. For production deployment, add:
- HTTPS/TLS encryption
- Rate limiting
- Stronger password requirements
- Input validation & sanitization
- Security headers

---

## 🚀 Future Enhancements

- [ ] WebSocket real-time updates (no polling)
- [ ] Multiple light support with room grouping
- [ ] PWM brightness control (0-100%)
- [ ] RGB color control
- [ ] Mobile app (React Native)
- [ ] Voice control (Alexa/Google Home integration)
- [ ] Motion sensor automation
- [ ] Usage analytics dashboard
- [ ] Docker containerization
- [ ] Cloud deployment (AWS/Azure)

---

## 📚 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [GPIO Zero Documentation](https://gpiozero.readthedocs.io/)
- [JWT Introduction](https://jwt.io/introduction)
- [Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/)

---

## 🎓 Project Context

Built for **Embedded Systems Course | November 2024**

This project demonstrates:
- Modern full-stack development practices
- IoT hardware integration
- RESTful API design
- Secure authentication implementation
- Real-time embedded systems control

---

## 📄 License

MIT License - Feel free to use this project for learning!

---

## 🤝 Contributing

This is an educational project, but suggestions are welcome! Open an issue or submit a pull request.

---

## 📧 Contact

**Project by:** aqn96  
**GitHub:** [github.com/aqn96/smart-home-light](https://github.com/aqn96/smart-home-light)

---

⭐ **Star this repo if you found it helpful!**
