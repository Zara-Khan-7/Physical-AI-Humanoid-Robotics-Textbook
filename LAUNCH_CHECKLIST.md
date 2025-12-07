# Launch Checklist

Complete checklist for launching the Physical AI Textbook to production.

## Pre-Launch (T-7 Days)

### Infrastructure Setup

- [ ] **Qdrant Cloud**
  - [ ] Create Qdrant Cloud account at [cloud.qdrant.io](https://cloud.qdrant.io)
  - [ ] Create free tier cluster
  - [ ] Note cluster URL and API key
  - [ ] Verify cluster is accessible

- [ ] **Google AI**
  - [ ] Get API key from [Google AI Studio](https://aistudio.google.com/apikey)
  - [ ] Verify key has access to Gemini and embeddings
  - [ ] Check rate limits (15 RPM free tier)

- [ ] **GitHub Repository**
  - [ ] Repository is public (required for GitHub Pages free tier)
  - [ ] Branch protection rules configured for main/master
  - [ ] Repository secrets configured (if using Actions for backend)

### Code Review

- [ ] **Security Audit**
  - [ ] No API keys committed to repository
  - [ ] `.env` files are in `.gitignore`
  - [ ] CORS is configured for specific origins only
  - [ ] Rate limiting is properly configured
  - [ ] No SQL injection vulnerabilities (N/A - using vector DB)
  - [ ] Input validation on all endpoints

- [ ] **Content Review**
  - [ ] All 6 chapters have content
  - [ ] No placeholder text remaining
  - [ ] Images and diagrams load correctly
  - [ ] Math equations render properly
  - [ ] Links are not broken

- [ ] **Code Quality**
  - [ ] `ruff check backend/app/` passes
  - [ ] `npm run build` succeeds in frontend
  - [ ] No TypeScript errors

---

## Launch Day (T-0)

### Backend Deployment

- [ ] **Deploy to Railway/Render**
  - [ ] Connect repository
  - [ ] Set environment variables:
    - [ ] `GOOGLE_API_KEY`
    - [ ] `QDRANT_URL`
    - [ ] `QDRANT_API_KEY`
    - [ ] `CORS_ORIGINS` (set to your GitHub Pages URL)
  - [ ] Deploy and verify startup logs

- [ ] **Verify Backend**
  ```bash
  # Health check
  curl https://your-backend.railway.app/api/v1/health
  # Expected: {"status": "healthy", ...}

  # Liveness probe
  curl https://your-backend.railway.app/api/v1/live
  # Expected: {"alive": true}

  # Readiness probe
  curl https://your-backend.railway.app/api/v1/ready
  # Expected: {"ready": true}
  ```

- [ ] **Index Content**
  ```bash
  cd backend
  python scripts/index_content.py
  # Verify: "Total chunks indexed: XX"
  ```

- [ ] **Test Chat Endpoint**
  ```bash
  curl -X POST https://your-backend.railway.app/api/v1/chat \
    -H "Content-Type: application/json" \
    -d '{"query": "What is Physical AI?", "language": "en"}'
  # Expected: JSON response with answer and citations
  ```

### Frontend Deployment

- [ ] **Update Configuration**
  - [ ] Edit `frontend/docusaurus.config.ts`:
    - [ ] Set `url` to your GitHub Pages URL
    - [ ] Set `baseUrl` to repository name (e.g., `/physical-ai-textbook/`)
    - [ ] Set `organizationName` to your GitHub username
    - [ ] Set `projectName` to repository name

- [ ] **Set GitHub Actions Variable**
  - [ ] Go to Repository → Settings → Secrets and variables → Actions → Variables
  - [ ] Add `API_URL` = `https://your-backend.railway.app/api/v1`

- [ ] **Enable GitHub Pages**
  - [ ] Repository → Settings → Pages
  - [ ] Source: GitHub Actions

- [ ] **Trigger Deployment**
  ```bash
  git add .
  git commit -m "Configure production deployment"
  git push origin main
  ```

- [ ] **Verify Deployment**
  - [ ] Check Actions tab - workflow should succeed
  - [ ] Visit `https://yourusername.github.io/repo-name/`
  - [ ] All pages load correctly
  - [ ] Navigation works
  - [ ] Dark mode toggle works

### Integration Testing

- [ ] **Chat Widget**
  - [ ] Chat button appears in bottom-right corner
  - [ ] Clicking opens chat window
  - [ ] Connection status shows "Connected"
  - [ ] Suggested questions are clickable
  - [ ] Sending a question returns an answer
  - [ ] Citations are displayed and clickable
  - [ ] Message history persists on page refresh
  - [ ] Clear button works

- [ ] **Search**
  - [ ] Search bar is visible
  - [ ] Typing shows autocomplete suggestions
  - [ ] Clicking result navigates to correct page
  - [ ] Search highlights terms on target page

- [ ] **Content**
  - [ ] All 6 chapters are accessible
  - [ ] Chapter navigation works
  - [ ] Table of contents is accurate
  - [ ] Code blocks have syntax highlighting
  - [ ] Math equations render correctly
  - [ ] Tables display properly

- [ ] **Language**
  - [ ] Language switcher is visible
  - [ ] Switching to Urdu changes interface direction (RTL)
  - [ ] Chat works in Urdu mode

---

## Post-Launch (T+1 Day)

### Monitoring Setup

- [ ] **Uptime Monitoring**
  - [ ] Set up UptimeRobot (free) or similar
  - [ ] Monitor: `https://your-backend.railway.app/api/v1/health`
  - [ ] Configure alerts (email/Slack)

- [ ] **Error Tracking** (Optional)
  - [ ] Set up Sentry account
  - [ ] Add Sentry SDK to backend
  - [ ] Configure error alerts

- [ ] **Analytics** (Optional)
  - [ ] Add Google Analytics to docusaurus.config.ts
  - [ ] Verify tracking is working

### Documentation

- [ ] **Update README**
  - [ ] Add live demo link
  - [ ] Update deployment URLs
  - [ ] Add contributing guidelines

- [ ] **Create Release**
  - [ ] Tag release: `git tag v1.0.0 && git push --tags`
  - [ ] Create GitHub Release with changelog

### Verification Checklist

- [ ] Site is accessible from different browsers (Chrome, Firefox, Safari)
- [ ] Site is accessible on mobile devices
- [ ] Chat works after 24 hours (API keys not expired)
- [ ] No console errors in browser DevTools
- [ ] Response times are acceptable (<3s for chat)

---

## Rollback Plan

If issues are discovered post-launch:

### Frontend Rollback
1. Go to GitHub Actions
2. Find last successful deployment
3. Click "Re-run all jobs"

### Backend Rollback (Railway)
```bash
railway rollback
```

### Backend Rollback (Render)
1. Go to Render dashboard
2. Select the service
3. Click on a previous successful deploy
4. Click "Rollback"

### Emergency Contacts

- Railway Support: support@railway.app
- Render Support: support@render.com
- Qdrant Support: support@qdrant.tech
- Google AI: cloud.google.com/support

---

## Launch Metrics

Track these metrics in the first week:

| Metric | Target | Actual |
|--------|--------|--------|
| Uptime | 99.5% | |
| Avg response time | <2s | |
| Chat success rate | >95% | |
| Page load time | <3s | |
| Error rate | <1% | |
| Unique visitors | - | |
| Chat messages | - | |

---

## Sign-off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Developer | | | |
| Reviewer | | | |
| Owner | | | |

---

*Last updated: 2025-12-07*
