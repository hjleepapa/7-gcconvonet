# Custom Domain Mapping Guide for Render.com

## ⚠️ Important Limitation

**You cannot map the same custom domain (`www.hjlees.com`) to two different Render services simultaneously.** A domain can only point to one service at a time.

---

## 🎯 Recommended Solution: Replace Existing Service

Since all your endpoints are already prefixed with `/anthropic/`, the **best approach** is to:

### Step 1: Point `www.hjlees.com` to Anthropic-Convonet Service

1. **In Render Dashboard:**
   - Go to your **anthropic-convonet** service
   - Navigate to **Settings** → **Custom Domains**
   - Click **"Add Custom Domain"**
   - Enter: `www.hjlees.com`
   - Click **"Save"**

2. **DNS Configuration:**
   - Render will provide you with DNS records (CNAME or A record)
   - Update your DNS provider (where `hjlees.com` is registered) with these records
   - Wait for DNS propagation (usually 5-60 minutes)

3. **SSL Certificate:**
   - Render automatically provisions SSL certificates for custom domains
   - This usually takes a few minutes after DNS is configured

### Step 2: Handle the Old Convonet Service

You have two options:

#### Option A: Move Old Service to Subdomain (Recommended if you need both)

1. **Point old service to a subdomain:**
   - In the old **convonet** service settings
   - Add custom domain: `convonet.hjlees.com` (or `legacy.hjlees.com`)
   - Update DNS with the new CNAME record

2. **Benefits:**
   - Both services remain accessible
   - Clear separation between old and new
   - Easy to test and compare

#### Option B: Decommission Old Service

1. **If you no longer need the old service:**
   - Simply remove the custom domain from the old service
   - The old service will still be accessible via its Render URL (e.g., `convonet-todo-app.onrender.com`)
   - You can delete the service later if needed

---

## 🔄 Alternative Solutions

### Option 2: Use Subdomain for Anthropic Service

If you want to keep `www.hjlees.com` pointing to the old service:

1. **Map anthropic service to subdomain:**
   - Add custom domain: `anthropic.hjlees.com` or `convonet-anthropic.hjlees.com`
   - Update all your documentation and webhook URLs accordingly

2. **Update Environment Variables:**
   ```bash
   WEBHOOK_BASE_URL=https://anthropic.hjlees.com
   WEBSOCKET_BASE_URL=wss://anthropic.hjlees.com/anthropic/convonet_todo/ws
   ```

3. **Update Twilio Webhooks:**
   - Update Twilio phone number webhook to: `https://anthropic.hjlees.com/anthropic/convonet_todo/twilio/voice`

**⚠️ Note:** This requires updating all hardcoded URLs, which you've already done for `/anthropic/` prefix, but you'd need to change the base domain too.

---

## 📋 Step-by-Step: Mapping Domain to Anthropic Service

### In Render Dashboard:

1. **Navigate to your service:**
   - Go to https://dashboard.render.com/
   - Click on your **anthropic-convonet** service

2. **Add Custom Domain:**
   - Click **"Settings"** tab
   - Scroll to **"Custom Domains"** section
   - Click **"Add Custom Domain"**
   - Enter: `www.hjlees.com`
   - Click **"Save"**

3. **Get DNS Records:**
   - Render will show you DNS configuration needed
   - Usually a CNAME record pointing to: `[your-service].onrender.com`
   - Or an A record with specific IP addresses

### In Your DNS Provider (e.g., Cloudflare, GoDaddy, Namecheap):

1. **Log in to your DNS provider**
2. **Find DNS management for `hjlees.com`**
3. **Add/Update DNS Record:**
   - **Type:** CNAME (or A record as specified by Render)
   - **Name:** `www` (or `@` for root domain)
   - **Value:** The value provided by Render
   - **TTL:** 3600 (or auto)

4. **Save and wait for propagation**
   - DNS changes can take 5-60 minutes
   - Use `dig www.hjlees.com` or `nslookup www.hjlees.com` to verify

### Verify Domain is Active:

1. **Check Render Dashboard:**
   - Custom domain should show as "Active" (green checkmark)
   - SSL certificate should be "Active"

2. **Test in Browser:**
   - Visit: `https://www.hjlees.com`
   - Should load your anthropic-convonet service
   - Test endpoint: `https://www.hjlees.com/anthropic/team-dashboard`

---

## 🔐 SSL Certificate

Render automatically provisions SSL certificates via Let's Encrypt:
- **Automatic:** Happens after DNS is configured
- **Renewal:** Automatic (every 90 days)
- **Status:** Check in Render dashboard under Custom Domains

---

## 🌐 Current URL Structure

With `www.hjlees.com` mapped to anthropic-convonet service:

| Endpoint | URL |
|----------|-----|
| Team Dashboard | `https://www.hjlees.com/anthropic/team-dashboard` |
| WebRTC Voice | `https://www.hjlees.com/anthropic/webrtc/voice-assistant` |
| Call Center | `https://www.hjlees.com/anthropic/call-center/` |
| Audio Player | `https://www.hjlees.com/anthropic/audio-player/` |
| Register | `https://www.hjlees.com/anthropic/register` |
| API Auth | `https://www.hjlees.com/anthropic/api/auth/*` |
| API Teams | `https://www.hjlees.com/anthropic/api/teams/*` |
| Twilio Webhook | `https://www.hjlees.com/anthropic/convonet_todo/twilio/voice` |

---

## ⚙️ Environment Variables to Update

After mapping the domain, verify these environment variables in Render:

```bash
WEBHOOK_BASE_URL=https://www.hjlees.com
WEBSOCKET_BASE_URL=wss://www.hjlees.com/anthropic/convonet_todo/ws
```

**Note:** These should already be set correctly since all endpoints use `/anthropic/` prefix.

---

## 🧪 Testing After Domain Mapping

1. **Test Main Endpoints:**
   ```bash
   curl https://www.hjlees.com/anthropic/team-dashboard
   curl https://www.hjlees.com/anthropic/webrtc/voice-assistant
   ```

2. **Test API Endpoints:**
   ```bash
   curl https://www.hjlees.com/anthropic/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"test"}'
   ```

3. **Test WebSocket:**
   ```bash
   wscat -c wss://www.hjlees.com/anthropic/convonet_todo/ws
   ```

4. **Test Twilio Webhook:**
   - Update Twilio phone number webhook URL to:
     `https://www.hjlees.com/anthropic/convonet_todo/twilio/voice`
   - Make a test call to verify

---

## 🚨 Important Notes

1. **DNS Propagation:**
   - Changes can take up to 48 hours (usually 5-60 minutes)
   - Use DNS checker tools to verify globally

2. **SSL Certificate:**
   - Automatically provisioned by Render
   - May take a few minutes after DNS is active

3. **Old Service:**
   - Remove custom domain from old service BEFORE adding to new one
   - Or use a subdomain to keep both running

4. **Webhook URLs:**
   - Update Twilio webhook URLs after domain change
   - Update any other external services that call your webhooks

5. **Caching:**
   - Clear browser cache if you see old content
   - CDN/proxy caches may take time to update

---

## 📞 Support

If you encounter issues:

1. **Render Support:**
   - Check Render dashboard logs
   - Contact Render support via dashboard

2. **DNS Issues:**
   - Verify DNS records with: `dig www.hjlees.com`
   - Check DNS propagation: https://www.whatsmydns.net/

3. **SSL Issues:**
   - Wait 10-15 minutes after DNS is active
   - Check SSL status in Render dashboard

---

**Last Updated:** 2024-11-20  
**Service:** Anthropic-Convonet  
**Domain:** www.hjlees.com

