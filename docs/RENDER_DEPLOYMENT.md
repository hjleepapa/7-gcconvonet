# Render.com Deployment Guide

## 🚀 Deploying Flask-SocketIO with WebSocket Support

Render.com uses **Dashboard Configuration** or **render.yaml**, NOT Procfile (Procfile is for Heroku).

---

## ⚙️ Method 1: Dashboard Configuration (Recommended)

### Step 1: Create New Web Service

1. Go to: https://dashboard.render.com/
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository

### Step 2: Configure Build Settings

| Setting | Value |
|---------|-------|
| **Name** | `convonet-todo-app` |
| **Region** | Choose closest to you |
| **Branch** | `main` |
| **Root Directory** | (leave empty) |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | See below ⬇️ |

### Step 3: Critical Start Command

**IMPORTANT:** Use this exact command:

```bash
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT passenger_wsgi:application
```

**Breakdown:**
- `gunicorn` - WSGI server
- `--worker-class eventlet` - Enable WebSocket support (CRITICAL!)
- `-w 1` - Single worker (required for Socket.IO)
- `--bind 0.0.0.0:$PORT` - Bind to Render's dynamic port
- `passenger_wsgi:application` - Entry point

### Step 4: Environment Variables

Add these in Render dashboard:

| Key | Value | Type |
|-----|-------|------|
| `PYTHON_VERSION` | `3.12.0` | Plain |
| `FLASK_KEY` | (your secret key) | Secret |
| `DB_URI` | (your PostgreSQL URL) | Secret |
| `OPENAI_API_KEY` | `sk-...` | Secret |
| `GOOGLE_CLIENT_ID` | (Google OAuth) | Secret |
| `GOOGLE_CLIENT_SECRET` | (Google OAuth) | Secret |
| `GOOGLE_OAUTH2_TOKEN_B64` | (Base64 token) | Secret |

### Step 5: Advanced Settings

**Auto-Deploy:** ✅ Enabled
**Health Check Path:** `/`
**Instance Type:** Free (or Starter for production)

---

## ⚙️ Method 2: render.yaml (Infrastructure as Code)

If you prefer version-controlled configuration, use `render.yaml`:

### Configuration File

I've created `render.yaml` in your project root:

```yaml
services:
  - type: web
    name: convonet-todo-app
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT passenger_wsgi:application
```

### Deploy with render.yaml

1. Commit `render.yaml` to your repo
2. In Render dashboard, click **"New +"** → **"Blueprint"**
3. Connect your repo
4. Render will auto-detect `render.yaml`
5. Configure environment variables in dashboard

**Note:** Environment variables must still be set in the dashboard (they're secrets).

---

## 🔍 Verify Deployment

### Check Build Logs

After deployment starts, check logs for:

```
✅ Installing dependencies from requirements.txt
✅ eventlet==0.33.0 installed
✅ Flask-SocketIO==5.0.0 installed
```

### Check Start Logs

Server should show:

```
[INFO] Starting gunicorn 21.2.0
[INFO] Using worker: eventlet          ← CRITICAL!
[INFO] Booting worker with pid: 123
✅ Eventlet monkey patch applied!
🔧 MCP config: Set DB_URI=...
✅ MCP client initialized successfully
```

**If you see:**
```
[INFO] Using worker: sync              ← WRONG!
```
→ Start command is incorrect. Fix it!

### Test WebSocket Connection

Open browser console and navigate to:
```
https://your-app.onrender.com/convonet_todo/webrtc/voice-assistant
```

Look for:
```
🔌 Initializing Socket.IO connection...
✅ Connected to voice server
```

**If you see connection error:**
- Check server logs for eventlet worker
- Verify start command has `--worker-class eventlet`
- Restart the service

---

## ⚠️ Common Issues

### Issue 1: "Using worker: sync"

**Problem:** Start command doesn't include `--worker-class eventlet`

**Solution:**
1. Go to Render dashboard
2. Navigate to your service
3. Go to **Settings**
4. Update **Start Command** to:
   ```bash
   gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT passenger_wsgi:application
   ```
5. Save and redeploy

### Issue 2: "ModuleNotFoundError: No module named 'eventlet'"

**Problem:** eventlet not installed

**Solution:**
Check `requirements.txt` includes:
```
eventlet>=0.33.0
Flask-SocketIO>=5.0.0
```

### Issue 3: "Address already in use"

**Problem:** Multiple instances trying to bind to same port

**Solution:**
- Ensure `-w 1` (single worker)
- Render automatically assigns `$PORT`
- Don't hardcode port number

### Issue 4: WebSocket times out

**Problem:** Render's load balancer not configured for WebSockets

**Solution:**
Render automatically supports WebSockets, but verify:
1. Using HTTPS (required): `https://your-app.onrender.com`
2. Browser allows WebSocket connections
3. No corporate firewall blocking WebSockets

---

## 🎯 Production Checklist

Before going live:

- [ ] Start command uses `--worker-class eventlet`
- [ ] Single worker: `-w 1`
- [ ] Environment variables configured
- [ ] `passenger_wsgi.py` has `eventlet.monkey_patch()`
- [ ] `app.py` uses `async_mode='eventlet'`
- [ ] Health check endpoint works: `/`
- [ ] HTTPS enabled (automatic on Render)
- [ ] WebSocket test passes
- [ ] Voice assistant page loads
- [ ] Authentication works

---

## 📊 Performance Considerations

### Single Worker Limitations

Current setup uses `-w 1` (single worker):
- **Capacity:** ~500-1000 concurrent connections
- **CPU:** 1 core utilized
- **Memory:** ~512MB typical

**For higher scale:**

1. **Add Redis** for session storage:
   ```python
   from redis import Redis
   socketio = SocketIO(
       app, 
       message_queue='redis://redis-url',
       async_mode='eventlet'
   )
   ```

2. **Use multiple workers:**
   ```bash
   gunicorn --worker-class eventlet -w 4 ...
   ```

3. **Upgrade instance type:**
   - Free: 512MB RAM, 0.1 CPU
   - Starter: 2GB RAM, 1 CPU
   - Standard: 4GB RAM, 2 CPU

---

## 🔄 Deployment Workflow

### Automatic Deployment

With **Auto-Deploy** enabled:

1. Push code to GitHub
2. Render detects changes
3. Automatically builds and deploys
4. ~2-5 minutes for deployment
5. Zero-downtime rollout

### Manual Deployment

If Auto-Deploy is off:

1. Go to Render dashboard
2. Select your service
3. Click **"Manual Deploy"**
4. Choose branch: `main`
5. Click **"Deploy"**

### Rollback

If deployment fails:

1. Go to **Events** tab
2. Find previous successful deploy
3. Click **"Rollback"**

---

## 📝 Environment Variables Best Practices

### Required Variables

```bash
# Flask
FLASK_KEY=your-secret-key-here

# Database
DB_URI=postgresql://user:pass@host:5432/db

# OpenAI (for WebRTC voice)
OPENAI_API_KEY=sk-...

# Google OAuth (for calendar)
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_OAUTH2_TOKEN_B64=...
```

### Optional Variables

```bash
# Debug mode (development only)
FLASK_DEBUG=false

# Python version
PYTHON_VERSION=3.12.0

# Gunicorn settings
GUNICORN_WORKERS=1
GUNICORN_TIMEOUT=120
```

---

## 🧪 Testing Locally

Before deploying, test locally with eventlet:

```bash
# Install dependencies
pip install -r requirements.txt

# Run with eventlet
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:10000 passenger_wsgi:application
```

Open: http://localhost:10000/convonet_todo/webrtc/voice-assistant

Should see:
```
✅ Connected to voice server
```

---

## 📞 Render.com Resources

- **Dashboard:** https://dashboard.render.com/
- **Docs:** https://render.com/docs
- **Status:** https://status.render.com/
- **Support:** https://render.com/support

---

## 🆘 Troubleshooting Commands

### View Live Logs

In Render dashboard:
1. Select your service
2. Click **"Logs"** tab
3. Watch real-time output

Or use Render CLI:
```bash
render logs
```

### Check Service Status

```bash
curl https://your-app.onrender.com/
```

Should return: `200 OK`

### Test WebSocket Endpoint

```bash
wscat -c wss://your-app.onrender.com/socket.io/?EIO=4&transport=websocket
```

Should return: `0` (Socket.IO handshake)

---

## 🎉 Success Indicators

You'll know everything is working when:

1. ✅ Render logs show: "Using worker: eventlet"
2. ✅ Page loads: https://your-app.onrender.com/convonet_todo/webrtc/voice-assistant
3. ✅ Console shows: "Connected to voice server"
4. ✅ Authentication works with PIN
5. ✅ Voice recording works
6. ✅ Agent responds with text + audio

**Then you're ready for your demo!** 🚀

---

## 📋 Quick Reference

### Correct Start Command
```bash
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT passenger_wsgi:application
```

### Files That Must Be Correct
- ✅ `passenger_wsgi.py` - Has `eventlet.monkey_patch()`
- ✅ `app.py` - Uses `async_mode='eventlet'`
- ✅ `requirements.txt` - Includes `eventlet>=0.33.0`
- ❌ `Procfile` - **NOT USED** (delete it if you want)

### Environment Variables
Set in Render dashboard, NOT in code!

---

**Created for SambaNova Hackathon**

*Because Render.com doesn't use Procfile, and eventlet is the key to WebSocket happiness!* ✨

