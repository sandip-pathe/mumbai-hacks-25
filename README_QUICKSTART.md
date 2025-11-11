# 🚀 Quick Start Guide - Anaya Watchtower

## ✅ Integration Complete!

Your frontend and backend are now properly connected and ready to run together.

## 🎯 What Was Fixed

1. **Port Alignment**: Changed frontend to connect to port 8000 (matching backend)
2. **Error Handling**: Added proper error interceptors in API client
3. **WebSocket URL**: Updated to use correct backend WebSocket endpoint
4. **Environment Variables**: Aligned all URLs between frontend and backend

## 🏃 Quick Start (Choose One)

### Option A: Automated Start (Recommended)
```bash
cd c:/x/finc
./start-services.sh
```

### Option B: Manual Start

**Terminal 1 - Backend:**
```bash
cd c:/x/finc/backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd c:/x/finc/frontend
npm run dev
```

## 📍 Access Your App

Once both services are running:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws

## ✨ Features Ready to Use

### 1. Chat Interface (`/chat`)
- RAG-powered compliance assistant
- Searches RBI circulars and policies
- Real-time responses from Azure OpenAI

### 2. Dashboard (`/dashboard`)
- Live compliance score
- Key metrics and statistics
- Recent alerts feed
- Score trend chart

### 3. Document Scanner (`/scanner`)
- Upload PDFs for compliance review
- AI-powered content analysis
- Instant feedback

### 4. Alerts Feed (`/alerts`)
- Real-time regulatory alerts
- Filter by severity (critical, high, medium)
- Auto-refresh every 10 seconds

## 🧪 Test the Connection

```bash
# Run the test script
./test-connection.sh

# Or manually test:
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Anaya Watchtower"
}
```

## 🔧 Configuration Files

### Backend Environment (`.env`)
Required variables:
```bash
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_KEY=your_key
DATABASE_URL=your_neon_postgres_url
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=your_endpoint
AZURE_DOCUMENT_INTELLIGENCE_KEY=your_key
```

### Frontend Environment (`.env.local`) - ✅ Already configured
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────┐
│           Frontend (Next.js)                     │
│           Port 3000                              │
│                                                  │
│  - React Query for state                        │
│  - WebSocket for live updates                   │
│  - Axios for HTTP requests                      │
└───────────────┬─────────────────────────────────┘
                │
                │ HTTP + WebSocket
                │
┌───────────────▼─────────────────────────────────┐
│           Backend (FastAPI)                      │
│           Port 8000                              │
│                                                  │
│  - Multi-agent system                           │
│  - LangGraph workflows                          │
│  - RAG with vector search                       │
└───────────────┬─────────────────────────────────┘
                │
        ┌───────┴────────┐
        │                │
   ┌────▼─────┐    ┌────▼─────┐
   │  Neon    │    │  Redis   │
   │ Postgres │    │ PubSub   │
   └──────────┘    └──────────┘
        │                │
   ┌────▼─────┐    ┌────▼─────┐
   │ Qdrant   │    │  Azure   │
   │ Vector   │    │ OpenAI   │
   └──────────┘    └──────────┘
```

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port is in use
lsof -i :8000

# Verify Python environment
python --version  # Should be 3.11+

# Check dependencies
pip install -r backend/requirements.txt
```

### Frontend won't start
```bash
# Check if port is in use
lsof -i :3000

# Clear cache and reinstall
cd frontend
rm -rf .next node_modules
npm install
```

### API calls fail with CORS error
- Verify backend is running on port 8000
- Check backend logs for CORS configuration
- Ensure `CORS_ORIGINS` includes `http://localhost:3000`

### WebSocket not connecting
- Ensure Redis is running
- Check browser console for WebSocket errors
- Verify URL is `ws://localhost:8000/ws`

## 📝 Development Workflow

1. **Start Services**:
   ```bash
   ./start-services.sh
   ```

2. **Make Changes**:
   - Backend: Auto-reloads with `--reload` flag
   - Frontend: Next.js hot-reloads automatically

3. **Check Logs**:
   - Backend: `tail -f backend/backend.log`
   - Frontend: `tail -f frontend/frontend.log`
   - Browser: Open DevTools Console

4. **Stop Services**:
   ```bash
   ./stop-services.sh
   ```

## 🎯 Next Steps

1. ✅ Start both services
2. ✅ Open http://localhost:3000
3. ✅ Try the chat - ask about RBI regulations
4. ✅ Upload a document in the scanner
5. ✅ Check the dashboard for metrics
6. ✅ Monitor the alerts feed

## 📚 Additional Documentation

- **Full Integration Details**: `INTEGRATION_CHECKLIST.md`
- **Running Services**: `RUNNING_SERVICES.md`
- **Docker Setup**: `docker-compose.yml`

## ⚡ Pro Tips

1. **Use API Docs**: Visit http://localhost:8000/docs to test API endpoints directly
2. **WebSocket Status**: Green dot (🟢) in chat means WebSocket is connected
3. **React Query DevTools**: Available in browser for debugging state
4. **Hot Reload**: Both services support hot reload - no restart needed for code changes

## 🎉 You're All Set!

Your full-stack compliance platform is ready to run. The frontend and backend are properly integrated and will communicate seamlessly.

**Happy coding! 🚀**
