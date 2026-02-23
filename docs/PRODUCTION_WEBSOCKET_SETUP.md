# Production WebSocket Setup for hjlees.com

## 🔧 **Current Setup Analysis**
- **Server**: Gunicorn (WSGI-only, no WebSocket support)
- **Proxy**: Cloudflare (supports WebSocket)
- **Need**: Switch to ASGI server for WebSocket support

## 🚀 **Solution 1: Switch to Uvicorn ASGI Server**

### **Step 1: Install Required Packages**
```bash
pip install uvicorn[standard] asgiref websockets
```

### **Step 2: Update Production Startup**
Replace Gunicorn with Uvicorn in your production deployment:

```bash
# Instead of:
gunicorn app:app

# Use:
uvicorn wsgi_to_asgi_converter:asgi_app \
    --host 0.0.0.0 \
    --port 8000 \
    --ws websockets \
    --workers 4 \
    --log-level info
```

### **Step 3: Update Cloudflare Configuration**
1. Go to Cloudflare Dashboard
2. Navigate to Network → WebSockets
3. Enable WebSocket support
4. Configure WebSocket proxy settings

### **Step 4: Test WebSocket**
```bash
# Test WebSocket endpoint
wscat -c wss://hjlees.com/anthropic/convonet_todo/ws
```

## 🔧 **Solution 2: Use Flask-SocketIO**

### **Step 1: Install Flask-SocketIO**
```bash
pip install flask-socketio
```

### **Step 2: Update App Configuration**
```python
from flask_socketio import SocketIO

socketio = SocketIO(app, cors_allowed_origins="*")

# Add WebSocket routes
@socketio.on('connect')
def handle_connect():
    emit('status', {'data': 'Connected'})
```

### **Step 3: Start with SocketIO**
```bash
python flask_socketio_setup.py
```

## 🌐 **Solution 3: Use WebSocket-Capable Hosting**

### **Recommended Platforms:**
1. **Railway**: Native WebSocket support
2. **Render**: WebSocket support available
3. **DigitalOcean App Platform**: ASGI support
4. **Heroku**: WebSocket support with proper configuration

### **Railway Deployment Example:**
```yaml
# railway.json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn wsgi_to_asgi_converter:asgi_app --host 0.0.0.0 --port $PORT --ws websockets",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

## 🔄 **Migration Steps for hjlees.com**

### **Option A: Update Existing Server**
1. **Backup current deployment**
2. **Install ASGI dependencies**
3. **Update startup script**
4. **Test WebSocket functionality**
5. **Update Cloudflare settings**

### **Option B: Deploy to New Platform**
1. **Choose WebSocket-capable platform**
2. **Deploy Convonet app**
3. **Update DNS to point to new deployment**
4. **Configure Twilio webhooks**

## 📋 **Required Changes**

### **1. Update requirements.txt**
```
uvicorn[standard]>=0.20.0
asgiref>=3.6.0
websockets>=11.0
```

### **2. Create Procfile (for Heroku/Railway)**
```
web: uvicorn wsgi_to_asgi_converter:asgi_app --host 0.0.0.0 --port $PORT --ws websockets
```

### **3. Update Environment Variables**
```bash
# Add to .env
WEBSOCKET_ENABLED=true
ASGI_SERVER=uvicorn
```

## 🧪 **Testing WebSocket**

### **Local Test:**
```bash
# Start ASGI server
python start_convonet_asgi.py

# Test WebSocket
wscat -c ws://localhost:8000/anthropic/convonet_todo/ws
```

### **Production Test:**
```bash
# Test production WebSocket
wscat -c wss://hjlees.com/anthropic/convonet_todo/ws
```

## ⚠️ **Important Notes**

1. **Cloudflare**: Ensure WebSocket support is enabled
2. **SSL**: WebSocket requires HTTPS/WSS
3. **Firewall**: Ensure WebSocket ports are open
4. **Load Balancer**: Configure for WebSocket sticky sessions
5. **Monitoring**: Add WebSocket connection monitoring

## 🎯 **Recommended Approach**

For hjlees.com, I recommend:

1. **Switch to Uvicorn ASGI server** (easiest migration)
2. **Enable WebSocket in Cloudflare**
3. **Test thoroughly before going live**
4. **Monitor WebSocket connections**

This approach maintains your current hosting while adding WebSocket capability.
