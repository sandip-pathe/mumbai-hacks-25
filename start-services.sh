#!/bin/bash

echo "🚀 Starting Anaya Watchtower Services"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0
    else
        return 1
    fi
}

echo -e "${BLUE}📋 Pre-flight checks...${NC}"

# Check if ports are already in use
if check_port 8000; then
    echo -e "${YELLOW}⚠️  Port 8000 is already in use. Backend may already be running.${NC}"
fi

if check_port 3000; then
    echo -e "${YELLOW}⚠️  Port 3000 is already in use. Frontend may already be running.${NC}"
fi

echo ""
echo -e "${GREEN}1️⃣ Starting Backend (Port 8000)${NC}"
cd c:/x/finc/backend

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Start backend in background
echo "Starting uvicorn server..."
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 3

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is running at http://localhost:8000${NC}"
else
    echo -e "${YELLOW}⚠️  Backend may still be starting... Check backend.log for details${NC}"
fi

echo ""
echo -e "${GREEN}2️⃣ Starting Frontend (Port 3000)${NC}"
cd c:/x/finc/frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start frontend in background
echo "Starting Next.js development server..."
npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

echo ""
echo -e "${GREEN}✅ Services starting!${NC}"
echo ""
echo "📊 Access Points:"
echo "  - Frontend:     http://localhost:3000"
echo "  - Backend API:  http://localhost:8000"
echo "  - API Docs:     http://localhost:8000/docs"
echo "  - WebSocket:    ws://localhost:8000/ws"
echo ""
echo "📝 Logs:"
echo "  - Backend:  c:/x/finc/backend/backend.log"
echo "  - Frontend: c:/x/finc/frontend/frontend.log"
echo ""
echo "🛑 To stop services:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "Or save these PIDs to a file for later:"
echo "echo $BACKEND_PID > c:/x/finc/.backend.pid"
echo "echo $FRONTEND_PID > c:/x/finc/.frontend.pid"
