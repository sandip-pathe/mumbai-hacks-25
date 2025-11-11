#!/bin/bash

echo "🔍 Testing Backend-Frontend Connection..."
echo ""

# Test Backend Health
echo "1️⃣ Testing Backend Health (http://localhost:8000/health)"
curl -s http://localhost:8000/health | jq || echo "❌ Backend not responding"
echo ""

# Test Backend Root
echo "2️⃣ Testing Backend Root (http://localhost:8000/)"
curl -s http://localhost:8000/ | jq || echo "❌ Backend not responding"
echo ""

# Test API Score Endpoint
echo "3️⃣ Testing Score API (http://localhost:8000/api/score)"
curl -s http://localhost:8000/api/score | jq || echo "⚠️  No score data (expected if DB is empty)"
echo ""

# Test API Alerts Endpoint
echo "4️⃣ Testing Alerts API (http://localhost:8000/api/alerts)"
curl -s http://localhost:8000/api/alerts | jq || echo "⚠️  No alerts data (expected if DB is empty)"
echo ""

# Check Frontend env
echo "5️⃣ Checking Frontend Environment Variables"
cat c:/x/finc/frontend/.env.local
echo ""

# Check if processes are running
echo "6️⃣ Checking Running Processes"
ps aux | grep -E "uvicorn|next|node" | grep -v grep || echo "⚠️  No processes found"
echo ""

echo "✅ Connection test complete!"
