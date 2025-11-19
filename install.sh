#!/bin/bash
# Smart Home IoT Light Control System - Installation Script
# Raspberry Pi OS (Debian-based)

set -e  # Exit on error

echo "=================================================="
echo "  Smart Home Light Control - Installation"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo -e "${YELLOW}Warning: This script is designed for Raspberry Pi${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${GREEN}Step 1: Updating package lists...${NC}"
sudo apt update

echo ""
echo -e "${GREEN}Step 2: Installing Python and system dependencies...${NC}"
sudo apt install -y \
    python3 \
    python3-pip \
    python3-full \
    git

echo ""
echo -e "${GREEN}Step 3: Installing Flask web framework...${NC}"
sudo apt install -y \
    python3-flask \
    python3-flask-cors

echo ""
echo -e "${GREEN}Step 4: Installing security libraries...${NC}"
sudo apt install -y \
    python3-bcrypt \
    python3-werkzeug \
    python3-jwt \
    python3-dotenv

echo ""
echo -e "${GREEN}Step 5: Installing GPIO libraries...${NC}"
sudo apt install -y \
    python3-gpiozero \
    python3-rpi.gpio

echo ""
echo -e "${GREEN}Step 6: Verifying installations...${NC}"

# Test each package
python3 << EOF
import sys
try:
    import flask
    print("✅ Flask version:", flask.__version__)
except ImportError:
    print("❌ Flask not found")
    sys.exit(1)

try:
    import flask_cors
    print("✅ Flask-CORS installed")
except ImportError:
    print("❌ Flask-CORS not found")
    sys.exit(1)

try:
    import bcrypt
    print("✅ bcrypt installed")
except ImportError:
    print("❌ bcrypt not found")
    sys.exit(1)

try:
    import werkzeug
    print("✅ Werkzeug installed")
except ImportError:
    print("❌ Werkzeug not found")
    sys.exit(1)

try:
    import jwt
    print("✅ PyJWT installed")
except ImportError:
    print("❌ PyJWT not found")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    print("✅ python-dotenv installed")
except ImportError:
    print("❌ python-dotenv not found")
    sys.exit(1)

try:
    from gpiozero import LED
    print("✅ GPIO Zero installed")
except ImportError:
    print("❌ GPIO Zero not found")
    sys.exit(1)

try:
    import RPi.GPIO
    print("✅ RPi.GPIO installed")
except ImportError:
    print("❌ RPi.GPIO not found")
    sys.exit(1)

print("")
print("🎉 All dependencies installed successfully!")
EOF

echo ""
echo -e "${GREEN}Step 7: Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version)
echo "Python version: $PYTHON_VERSION"

echo ""
echo -e "${GREEN}Step 8: Getting network information...${NC}"
IP_ADDRESS=$(hostname -I | awk '{print $1}')
HOSTNAME=$(hostname)
echo "Hostname: $HOSTNAME"
echo "IP Address: $IP_ADDRESS"

echo ""
echo "=================================================="
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Create .env file with your configuration"
echo "2. Run: python3 database.py (to initialize database)"
echo "3. Run: python3 app.py (to start the server)"
echo "4. Access web interface at: http://$IP_ADDRESS:5000"
echo ""
echo "For documentation, see README.md"
echo "=================================================="#!/bin/bash
# Installation script for Smart Home Light Control

echo "Installing system packages..."
sudo apt update
sudo apt install -y \
  python3-flask \
  python3-flask-cors \
  python3-bcrypt \
  python3-werkzeug \
  python3-jwt \
  python3-dotenv \
  python3-gpiozero \
  python3-rpi.gpio

echo "✅ Installation complete!"
python3 -c "import flask; print('Flask version:', flask.__version__)"
