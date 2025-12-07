# Deployment Guide

Complete guide for deploying the Physical AI Textbook to production.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         GitHub                                   │
│  ┌─────────────┐                      ┌─────────────┐           │
│  │  frontend/  │                      │  backend/   │           │
│  └──────┬──────┘                      └──────┬──────┘           │
│         │                                    │                   │
└─────────┼────────────────────────────────────┼───────────────────┘
          │                                    │
          ▼                                    ▼
┌─────────────────────┐            ┌─────────────────────┐
│   GitHub Pages      │            │  Railway / Render   │
│   (Static Site)     │◄──────────►│  (FastAPI Backend)  │
└─────────────────────┘    API     └──────────┬──────────┘
                                              │
                                              ▼
                                   ┌─────────────────────┐
                                   │   Qdrant Cloud      │
                                   │   (Vector Store)    │
                                   └─────────────────────┘
```

## Prerequisites

Before deployment, ensure you have:

1. **GitHub Account** - For repository and GitHub Pages hosting
2. **Google AI API Key** - From [Google AI Studio](https://aistudio.google.com/apikey)
3. **Qdrant Cloud Account** - Free tier at [cloud.qdrant.io](https://cloud.qdrant.io)
4. **Railway or Render Account** - For backend hosting

## Environment Variables

### Backend Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `GOOGLE_API_KEY` | Yes | Google AI API key for Gemini & embeddings | `AIza...` |
| `QDRANT_URL` | Yes | Qdrant Cloud cluster URL | `https://xxx.qdrant.io:6333` |
| `QDRANT_API_KEY` | Yes | Qdrant Cloud API key | `eyJ...` |
| `QDRANT_COLLECTION` | No | Vector collection name | `textbook_chunks` |
| `EMBEDDING_MODEL` | No | Embedding model name | `models/text-embedding-004` |
| `EMBEDDING_DIM` | No | Embedding dimensions | `768` |
| `LLM_MODEL` | No | Gemini model name | `gemini-2.0-flash-001` |
| `CORS_ORIGINS` | Yes | Allowed frontend origins | `https://user.github.io` |
| `HOST` | No | Server host | `0.0.0.0` |
| `PORT` | No | Server port (set by platform) | `8000` |

### Frontend Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `REACT_APP_API_URL` | Yes | Backend API base URL | `https://api.example.com/api/v1` |

## Step-by-Step Deployment

### Step 1: Set Up Qdrant Cloud

1. Go to [cloud.qdrant.io](https://cloud.qdrant.io)
2. Create a free cluster
3. Note down:
   - Cluster URL (e.g., `https://xxx-xxx.aws.cloud.qdrant.io:6333`)
   - API Key from the cluster dashboard

### Step 2: Get Google AI API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Create a new API key
3. Note: Free tier has rate limits (15 RPM for Gemini)

### Step 3: Deploy Backend to Railway

#### Option A: Railway (Recommended)

1. **Connect Repository**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli

   # Login
   railway login

   # Initialize project
   cd backend
   railway init
   ```

2. **Set Environment Variables**
   ```bash
   railway variables set GOOGLE_API_KEY=your-key
   railway variables set QDRANT_URL=https://your-cluster.qdrant.io:6333
   railway variables set QDRANT_API_KEY=your-qdrant-key
   railway variables set CORS_ORIGINS=https://yourusername.github.io
   ```

3. **Deploy**
   ```bash
   railway up
   ```

4. **Get Deployment URL**
   ```bash
   railway domain
   # Note the URL like: https://physical-ai-backend.up.railway.app
   ```

#### Option B: Render

1. Go to [render.com](https://render.com)
2. Create new Web Service
3. Connect your GitHub repository
4. Set root directory to `backend`
5. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables in dashboard
7. Deploy

### Step 4: Index Content

Before the chatbot can answer questions, you need to index the textbook content:

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GOOGLE_API_KEY=your-key
export QDRANT_URL=https://your-cluster.qdrant.io:6333
export QDRANT_API_KEY=your-qdrant-key

# Run indexing script
python scripts/index_content.py
```

This will:
- Read all Markdown files from `frontend/docs/`
- Chunk them into 512-1000 token segments
- Generate embeddings using Google text-embedding-004
- Store vectors in Qdrant

### Step 5: Deploy Frontend to GitHub Pages

1. **Update Configuration**

   Edit `frontend/docusaurus.config.ts`:
   ```typescript
   const config: Config = {
     url: 'https://yourusername.github.io',
     baseUrl: '/physical-ai-textbook/',  // Your repo name
     organizationName: 'yourusername',
     projectName: 'physical-ai-textbook',
     // ...
   };
   ```

2. **Set Repository Variable**

   Go to GitHub Repository → Settings → Secrets and Variables → Actions → Variables

   Add: `API_URL` = `https://your-backend.railway.app/api/v1`

3. **Enable GitHub Pages**

   Repository → Settings → Pages → Source: GitHub Actions

4. **Push to Trigger Deploy**
   ```bash
   git add .
   git commit -m "Configure deployment"
   git push origin main
   ```

5. **Verify Deployment**

   Check Actions tab for build status, then visit:
   `https://yourusername.github.io/physical-ai-textbook/`

## Verification Checklist

### Backend Health Check

```bash
curl https://your-backend.railway.app/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "qdrant": "connected",
    "embeddings": "available",
    "gemini": "available"
  }
}
```

### Test Chat Endpoint

```bash
curl -X POST https://your-backend.railway.app/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Physical AI?", "language": "en"}'
```

### Frontend Verification

1. Visit the deployed site
2. Navigate through chapters
3. Click the chat button
4. Ask a question
5. Verify citations link correctly

## Troubleshooting

### CORS Errors

If you see CORS errors in browser console:
1. Verify `CORS_ORIGINS` includes your frontend URL (with protocol, no trailing slash)
2. Ensure the backend is restarted after changing environment variables

### Chat Returns Empty

1. Check backend logs for errors
2. Verify content has been indexed: `curl /api/v1/health` should show `points_count > 0`
3. Re-run `python scripts/index_content.py`

### Rate Limiting

- Chat endpoint is limited to 5 requests/minute per IP
- Google AI free tier: 15 requests/minute
- If hitting limits, implement caching or upgrade plans

### Build Failures

**Frontend:**
- Ensure Node.js 18+ is used
- Check for TypeScript errors: `npm run build` locally

**Backend:**
- Ensure Python 3.11+ is used
- Check `requirements.txt` versions are compatible

## Cost Estimates

| Service | Free Tier | Paid Tier |
|---------|-----------|-----------|
| GitHub Pages | Unlimited | N/A |
| Railway | $5/month credits | $0.000463/min |
| Render | 750 hours/month | $7/month |
| Qdrant Cloud | 1GB storage | $25/month |
| Google AI | 15 RPM | Pay-as-you-go |

**Estimated monthly cost for hobby project:** $0 (within free tiers)
**Estimated monthly cost for production:** $15-50

## Security Checklist

- [ ] API keys are stored as secrets, not in code
- [ ] CORS is configured for specific origins only
- [ ] Rate limiting is enabled
- [ ] HTTPS is enforced on all endpoints
- [ ] No sensitive data in error responses
- [ ] Regularly rotate API keys

## Monitoring

### Recommended Setup

1. **Uptime Monitoring**: Use [UptimeRobot](https://uptimerobot.com) (free) to monitor `/api/v1/health`
2. **Error Tracking**: Add [Sentry](https://sentry.io) for error reporting
3. **Analytics**: Docusaurus supports Google Analytics

### Health Check Endpoints

| Endpoint | Purpose |
|----------|---------|
| `/api/v1/health` | Overall service health |
| `GET /` | Frontend availability |

## Updating Content

To update textbook content:

1. Edit Markdown files in `frontend/docs/`
2. Push changes to trigger frontend rebuild
3. Re-run indexing script to update vectors:
   ```bash
   python scripts/index_content.py
   ```

## Rollback Procedure

**Frontend:**
- Go to Actions tab
- Find previous successful deployment
- Click "Re-run all jobs"

**Backend (Railway):**
```bash
railway rollback
```

**Backend (Render):**
- Go to Render dashboard
- Select previous deploy
- Click "Rollback"
