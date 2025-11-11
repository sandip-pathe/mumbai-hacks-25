#!/bin/bash

echo "🛑 Stopping Anaya Watchtower Services"
echo ""

# Kill backend if PID file exists
if [ -f "c:/x/finc/.backend.pid" ]; then
    BACKEND_PID=$(cat c:/x/finc/.backend.pid)
    echo "Stopping backend (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null && echo "✅ Backend stopped" || echo "⚠️  Backend not running"
    rm c:/x/finc/.backend.pid
fi

# Kill frontend if PID file exists
if [ -f "c:/x/finc/.frontend.pid" ]; then
    FRONTEND_PID=$(cat c:/x/finc/.frontend.pid)
    echo "Stopping frontend (PID: $FRONTEND_PID)..."
    kill $FRONTEND_PID 2>/dev/null && echo "✅ Frontend stopped" || echo "⚠️  Frontend not running"
    rm c:/x/finc/.frontend.pid
fi

# Fallback: kill by port
echo ""
echo "Checking for any remaining processes..."

# Kill process on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "✅ Killed process on port 8000" || echo "No process on port 8000"

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9 2>/dev/null && echo "✅ Killed process on port 3000" || echo "No process on port 3000"

echo ""
echo "✅ All services stopped"
