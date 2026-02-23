# Sentry Setup - Quick Start Guide

## ✅ Sentry Integration Complete!

I've integrated Sentry error monitoring into your Convonet project.

---

## 🚀 Setup Steps (5 Minutes)

### Step 1: Get Sentry DSN

1. **Go to https://sentry.io**
2. **Sign up / Login** (free tier available)
3. **Create New Project**:
   - Platform: Python
   - Framework: Flask
   - Project Name: convonet-voice-ai
4. **Copy your DSN** (looks like: `https://xxxxx@o123456.ingest.us.sentry.io/456789`)

### Step 2: Add to .env File

Add to your `.env` file:

```bash
# Sentry Error Monitoring
SENTRY_DSN=https://your-key@your-org.ingest.us.sentry.io/your-project-id
```

### Step 3: Add to Render Environment Variables

```
Render Dashboard → Your Service → Environment
Click "Add Environment Variable"

Key: SENTRY_DSN
Value: https://your-key@your-org.ingest.us.sentry.io/your-project-id

Save Changes
```

### Step 4: Deploy

```bash
cd "/Users/hj/Web Development Projects/1. Main"

git add app.py requirements.txt convonet/routes.py
git commit -m "Add Sentry error monitoring"
git push origin main
```

Wait ~5 minutes for Render to rebuild.

---

## 📊 What Sentry Will Track

### Automatic Tracking:

1. **All Errors & Exceptions**
   - BrokenResourceError
   - Tool timeout errors
   - tool_call_id incomplete errors
   - Database errors
   - API failures

2. **Performance Metrics**
   - Agent processing time
   - Tool execution duration
   - HTTP request latency
   - Database query times

3. **User Context**
   - User ID
   - Call SID
   - Transcribed text
   - Request parameters

### Custom Tracking Added:

1. **Voice Call Transactions**
   - Complete request flow tracking
   - Performance breakdown

2. **Thread Resets**
   - When and why threads are reset
   - Frequency of timeouts

3. **Agent Timeouts**
   - Warnings when agent takes >12s
   - Includes prompt that caused timeout

4. **Agent Errors**
   - Categorized by type (tool_call_incomplete, broken_resource, etc.)
   - Includes error context

---

## 🎯 Hackathon Demo Value

### During Your Demo:

1. **Show Error Dashboard**
   ```
   Judges: "How do you handle errors in production?"
   You: *Opens Sentry dashboard*
   "We use Sentry for real-time monitoring. Here you can see:
   - Error rates over time
   - Performance metrics
   - User sessions
   - Alert notifications"
   ```

2. **Trigger Sample Error** (Optional)
   ```
   During demo, trigger a timeout:
   "Ask me for calendar events" (slow operation)
   Show in Sentry:
   - Real-time error appears
   - Complete stack trace
   - User context
   - Performance breakdown
   ```

3. **Show Performance Tracking**
   ```
   "We track agent processing time for every call.
   You can see most responses are under 5 seconds,
   with automatic fallback for slower operations."
   ```

---

## 📈 Sentry Dashboard Features

### Issues Tab
- All errors grouped by type
- Frequency graphs
- Affected user count
- Stack traces with code context

### Performance Tab
- HTTP transaction tracking
- Database query performance
- LLM API call times
- Slowest operations

### Alerts
- Email/Slack when error rate spikes
- Custom alerts for specific errors
- Performance degradation alerts

---

## 🧪 Test Sentry Integration

### Step 1: Make Test Call

```
Call: +12344007818
Say: "Create a todo for test"
```

### Step 2: Check Sentry Dashboard

```
Sentry Dashboard → Issues
Should see new transaction: "process_audio"
Performance → Transactions
Should see metrics for voice_call
```

### Step 3: Trigger Timeout (Optional)

```
Call: +12344007818
Say: "What calendar events do I have?"
(If slow)
```

Check Sentry for:
- Warning: "Agent processing timeout"
- Message: "Conversation thread reset"

---

## 🔍 What Gets Tracked

### Normal Call Flow:
```
Transaction: voice_call/process_audio
- Duration: 2.5s
- Status: 200 OK
- User: 2481f0e8-4a36-41aa-b667-acdbab9549b8
- Custom measurements:
  - agent_processing_time: 2.3s
```

### Timeout Event:
```
Message: Agent processing timeout (warning)
Extras:
  - user_id: 2481f0e8...
  - call_sid: CA5c595e...
  - prompt: "Create marketing meeting..."
  - timeout_duration: 12.4s
```

### Error Event:
```
Error: Agent error: tool_call_incomplete
Extras:
  - error_type: tool_call_incomplete
  - error_message: "tool_call_id must be followed..."
  - user_id: 2481f0e8...
  - call_sid: CA5c595e...
```

---

## 🎓 Sentry Best Practices

### 1. Set Release Version

In Render environment:
```
RENDER_GIT_COMMIT = (auto-populated by Render)
```

Sentry uses this to track errors by version.

### 2. Configure Sample Rates

For production (after hackathon), reduce to save quota:
```python
traces_sample_rate=0.1,  # 10% instead of 100%
profiles_sample_rate=0.1,
```

### 3. Filter Sensitive Data

Sentry automatically scrubs passwords, but you can add custom filters:
```python
before_send=lambda event, hint: scrub_pin(event)
```

---

## 💡 Hackathon Presentation Tips

### Demo Flow:

1. **Show the app working**
   - Make successful voice call
   - Create todo/calendar event

2. **Open Sentry dashboard** (live)
   - Show transaction just appeared
   - Show performance metrics

3. **Explain monitoring**
   - "Every request is tracked"
   - "Errors are captured automatically"
   - "We get alerts if issues spike"

4. **Show error handling** (if comfortable)
   - Trigger timeout
   - Show how it appears in Sentry
   - Show thread reset recovery

### Talking Points:

✅ "Production-grade error monitoring"  
✅ "Real-time performance tracking"  
✅ "Proactive alerting system"  
✅ "Complete observability"  

---

## 📚 Resources

- **Sentry Docs**: https://docs.sentry.io/platforms/python/guides/flask/
- **Dashboard**: https://sentry.io/organizations/your-org/issues/
- **Performance**: https://sentry.io/organizations/your-org/performance/

---

## ✅ Next Steps

1. **Get Sentry DSN** from sentry.io
2. **Add to .env** locally for testing
3. **Add to Render** environment variables
4. **Deploy** (git push)
5. **Test** - Make a call and check Sentry dashboard
6. **Prepare demo** - Practice showing dashboard to judges

**Estimated time:** 5-10 minutes to full integration! 🎉

