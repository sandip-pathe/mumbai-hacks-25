# 🚀 Running Backend + Frontend Together

## Quick Start

### Option 1: Using the Startup Script (Recommended)

```bash
# Make script executable
chmod +x start-services.sh stop-services.sh

# Start both services
./start-services.sh

# Stop both services
./stop-services.sh
```

### Option 2: Manual Start

#### Terminal 1 - Backend
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Terminal 2 - Frontend
```bash
cd frontend
npm install  # First time only
npm run dev
```

## Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws

## Environment Variables

### Backend (.env)
```bash
# Required
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_KEY=your_key
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=your_endpoint
AZURE_DOCUMENT_INTELLIGENCE_KEY=your_key
DATABASE_URL=your_neon_postgres_url

# Optional
REDIS_URL=redis://localhost:6379/0
QDRANT_URL=your_qdrant_cloud_url
SLACK_WEBHOOK_URL=your_slack_webhook
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

## Testing the Connection

```bash
# Test backend health
curl http://localhost:8000/health

# Test API endpoints
curl http://localhost:8000/api/score
curl http://localhost:8000/api/alerts

# Run comprehensive test
chmod +x test-connection.sh
./test-connection.sh
```

## Features Integration Status

✅ **Fully Integrated:**
- Chat interface with RAG-powered compliance assistant
- Dashboard with real-time stats
- Alerts feed with live updates
- Document scanner/upload
- WebSocket for real-time updates

✅ **API Endpoints:**
- `POST /api/chat` - Chat with compliance assistant
- `POST /api/ingest` - Upload documents
- `GET /api/score` - Get compliance score
- `GET /api/alerts` - Get alerts (with filtering)
- `GET /api/circulars` - Get RBI circulars
- `GET /api/policy-diffs` - Get policy differences
- `GET /api/logs` - Get agent logs
- `WS /ws` - WebSocket for live updates

## Architecture

```
┌──────────────┐         ┌──────────────┐
│   Frontend   │ ◄─────► │   Backend    │
│  (Next.js)   │  HTTP   │  (FastAPI)   │
│  Port 3000   │  WS     │  Port 8000   │
└──────────────┘         └──────────────┘
       │                        │
       │                        ├─► Neon Postgres
       │                        ├─► Redis (PubSub)
       │                        ├─► Qdrant (Vector DB)
       │                        └─► Azure OpenAI
       │
       └─► React Query (state management)
           └─► WebSocket (live updates)
```

## Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Check logs
cat backend/backend.log

# Verify environment variables
cd backend && python -c "from config import settings; print(settings.DATABASE_URL)"
```

### Frontend won't start
```bash
# Check if port 3000 is in use
lsof -i :3000

# Reinstall dependencies
cd frontend
rm -rf node_modules .next
npm install

# Check logs
cat frontend/frontend.log
```

### API calls failing
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check frontend env
cat frontend/.env.local

# Check browser console for CORS errors
# Backend should allow http://localhost:3000
```

### WebSocket not connecting
```bash
# Test WebSocket endpoint
wscat -c ws://localhost:8000/ws

# Check browser dev tools Network tab
# Look for WS connection status
```

## Development Tips

1. **Hot Reload**: Both services support hot reload
   - Backend: `--reload` flag on uvicorn
   - Frontend: Next.js dev server auto-reloads

2. **Debugging**:
   - Backend: Check `backend/backend.log`
   - Frontend: Check browser console
   - API: Use http://localhost:8000/docs (Swagger UI)

3. **Database**: Make sure your Neon Postgres database is accessible
   ```bash
   # Test database connection
   cd backend
   python -c "from db.database import init_db; import asyncio; asyncio.run(init_db())"
   ```

4. **Redis**: If using local Redis:
   ```bash
   # Start Redis
   redis-server
   
   # Or use Docker
   docker run -d -p 6379:6379 redis:alpine
   ```

## Next Steps

1. ✅ Start both services
2. ✅ Open http://localhost:3000
3. ✅ Test the chat interface
4. ✅ Upload a document via scanner
5. ✅ Check dashboard for stats
6. ✅ Monitor alerts feed

## Common Issues

**Issue**: Frontend shows "Failed to fetch"
- **Fix**: Ensure backend is running on port 8000

**Issue**: CORS errors in browser
- **Fix**: Verify `CORS_ORIGINS` in backend config includes `http://localhost:3000`

**Issue**: WebSocket disconnected
- **Fix**: Check Redis is running (WebSocket uses Redis for pubsub)

**Issue**: No data in dashboard
- **Fix**: Database may be empty. Upload some documents or run migrations.
