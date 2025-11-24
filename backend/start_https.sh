#!/bin/bash

# Smart Home Light Control - HTTPS Startup Script
# Usage: ./start_https.sh

cd "$(dirname "$0")"

echo "🔐 Starting Smart Home Light Control with HTTPS..."
echo ""

# Check if SSL certificates exist
if [ ! -f "key.pem" ] || [ ! -f "cert.pem" ]; then
    echo "⚠️  SSL certificates not found. Generating new ones..."
    openssl req -x509 -newkey rsa:4096 -nodes \
        -keyout key.pem -out cert.pem -days 365 \
        -subj "/CN=smartlight-an.local" 2>/dev/null
    echo "✅ Certificates generated!"
    echo ""
fi

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Run install.sh first!"
    exit 1
fi

# Get local IP
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "🚀 Starting server..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📱 Access your Smart Home at:"
echo ""
echo "   🔗 https://smartlight-an.local:8000"
echo "   🔗 https://$LOCAL_IP:8000"
echo "   🔗 https://localhost:8000 (from Pi)"
echo ""
echo "⚠️  You'll see a security warning - this is normal!"
echo "   Click 'Advanced' → 'Proceed' to continue"
echo ""
echo "📚 API Docs: https://$LOCAL_IP:8000/docs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start server with HTTPS
uvicorn main:app --reload --host 0.0.0.0 --port 8000 \
    --ssl-keyfile=./key.pem \
    --ssl-certfile=./cert.pem
