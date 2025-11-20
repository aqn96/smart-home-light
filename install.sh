#!/bin/bash

echo "🚀 Smart Home IoT Light Control System - Installation"
echo "=================================================="
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Warning: This script is designed for Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo "📦 Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install Python 3 and pip
echo "🐍 Installing Python 3 and dependencies..."
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Install Node.js and npm for React frontend
echo "📦 Installing Node.js (LTS)..."
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
    sudo apt install -y nodejs
else
    echo "✅ Node.js already installed: $(node --version)"
fi

# Install GPIO libraries
echo "🔌 Installing GPIO libraries..."
sudo apt install -y python3-gpiozero python3-rpi.gpio

# Setup Backend
echo ""
echo "🔧 Setting up Backend (FastAPI)..."
cd backend || exit

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python packages..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "⚠️  requirements.txt not found, installing manually..."
    pip install fastapi uvicorn[standard] python-jose[cryptography] passlib[bcrypt] python-multipart gpiozero python-dotenv sqlalchemy
    pip freeze > requirements.txt
fi

# Deactivate venv
deactivate

cd ..

# Setup Frontend
echo ""
echo "🎨 Setting up Frontend (React + Vite)..."
cd frontend || exit

if [ ! -f "package.json" ]; then
    echo "⚠️  Frontend not initialized yet. Run: npm create vite@latest . -- --template react"
else
    echo "Installing npm packages..."
    npm install
fi

cd ..

# Configure environment
echo ""
echo "🔐 Environment Configuration"
if [ ! -f "backend/.env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example backend/.env
        echo "✅ Created backend/.env from .env.example"
        echo ""
        echo "⚠️  IMPORTANT: Edit backend/.env and add your JWT secret!"
        echo "   Generate one with: python3 -c 'import secrets; print(secrets.token_hex(32))'"
    else
        echo "⚠️  .env.example not found"
    fi
else
    echo "✅ backend/.env already exists"
fi

# Add user to gpio group
echo ""
echo "👤 Adding user to GPIO group..."
sudo usermod -a -G gpio $USER

echo ""
echo "✅ Installation Complete!"
echo ""
echo "=================================================="
echo "📋 Next Steps:"
echo "=================================================="
echo ""
echo "1. Configure Environment:"
echo "   cd backend"
echo "   nano .env"
echo "   (Add JWT_SECRET_KEY - generate with: python3 -c 'import secrets; print(secrets.token_hex(32))')"
echo ""
echo "2. Initialize Database:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python database.py"
echo ""
echo "3. Start Backend Server:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "4. Start Frontend (in new terminal):"
echo "   cd frontend"
echo "   npm run dev -- --host"
echo ""
echo "5. Access Application:"
echo "   Backend API: http://$(hostname -I | awk '{print $1}'):8000"
echo "   Frontend UI: http://$(hostname -I | awk '{print $1}'):5173"
echo "   API Docs: http://$(hostname -I | awk '{print $1}'):8000/docs"
echo ""
echo "⚠️  You may need to reboot for GPIO permissions: sudo reboot"
echo ""
