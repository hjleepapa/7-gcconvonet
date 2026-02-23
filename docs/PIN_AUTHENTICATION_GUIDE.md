# PIN Authentication System - Complete Guide

## 🔐 Overview

The Convonet Team Collaboration System now includes **PIN-based voice authentication** for Twilio phone calls. Users must enter a 4-6 digit PIN before accessing the AI assistant.

---

## 📋 Setup Instructions

### **Step 1: Run Database Migration**

The `voice_pin` column needs to be added to the `users_convonet` table:

```sql
ALTER TABLE users_convonet 
ADD COLUMN voice_pin VARCHAR(10) UNIQUE;

CREATE INDEX idx_users_voice_pin ON users_convonet(voice_pin);
```

### **Step 2: Setup Demo Admin User**

Run the admin user setup script:

```bash
cd "/Users/hj/Web Development Projects/1. Main"
python check_admin_user.py
```

This will:
- ✅ Verify admin@convonet.com exists
- ✅ Set password to 'admin123'
- ✅ Set voice PIN to '1234'
- ✅ Create admin user if doesn't exist

### **Step 3: Register New Users with PIN**

**Web Registration:**
1. Go to https://hjlees.com/anthropic/register
2. Fill in email, username, first name, last name, password
3. **Enter a 4-6 digit Voice PIN** (e.g., 5678)
4. Click "Create Account"

**Manual SQL (for existing users):**
```sql
UPDATE users_convonet 
SET voice_pin = '1234' 
WHERE email = 'admin@convonet.com';
```

---

## 🗣️ Voice Call Flow

### **Authentication Flow:**

```
1. User calls Twilio number
   ↓
2. System: "Welcome to Convonet productivity assistant. 
             Please enter or say your 4 to 6 digit PIN, then press pound."
   ↓
3. User Options:
   📱 DTMF: Press 1234# on keypad
   🗣️ Speech: Say "one two three four"
   ↓
4. System converts speech to digits:
   "one two three four" → "1234"
   ↓
5. System calls verify_user_pin("1234") MCP tool
   ↓
6. Database lookup: users_convonet WHERE voice_pin = '1234'
   ↓
7. If found:
   ✅ "AUTHENTICATED:{user_id}|{name}|{email}"
   ✅ "Welcome back, {first_name}!"
   ✅ Lists user's teams
   ↓
8. If not found:
   ❌ "Invalid PIN. Please try again."
   ❓ Redirects back to PIN prompt
   ↓
9. Authenticated session:
   - user_id passed in all URLs: ?user_id={uuid}
   - AgentState.authenticated_user_id = user_id
   - All todos created with creator_id = user_id
```

---

## 🎯 Supported PIN Formats

### **Spoken PIN (Speech Recognition):**
```
🗣️ "one two three four"        → 1234 ✅
🗣️ "five six seven eight"      → 5678 ✅
🗣️ "zero one two three"        → 0123 ✅
🗣️ "one 2 three 4"             → 1234 ✅
🗣️ "oh one two three"          → 0123 ✅ (oh = 0)
```

### **Keypad PIN (DTMF):**
```
📱 1234#  → 1234 ✅
📱 5678#  → 5678 ✅
📱 012345# → 012345 ✅ (6 digits)
```

### **Number Word Mapping:**
```python
{
    'zero': '0', 'oh': '0', 'o': '0',
    'one': '1', 'two': '2', 'three': '3',
    'four': '4', 'five': '5', 'six': '6',
    'seven': '7', 'eight': '8', 'nine': '9',
    'ten': '10', 'eleven': '11', 'twelve': '12'
}
```

---

## 🔧 Troubleshooting

### **Issue: "Invalid PIN" Error**

**Cause 1: PIN not set in database**
```sql
-- Check if user has a PIN
SELECT email, voice_pin FROM users_convonet WHERE email = 'admin@convonet.com';

-- If NULL, set it:
UPDATE users_convonet SET voice_pin = '1234' WHERE email = 'admin@convonet.com';
```

**Cause 2: Speech recognition returning unexpected text**
- Check logs for: `🔧 Original PIN: '...' → Cleaned PIN: '...'`
- If cleaned PIN is empty or wrong, speech might be: "PIN is one two three four" (extra words)
- Solution: Say ONLY the digits: "one two three four"

**Cause 3: PIN length validation**
- Must be 4-6 digits
- Check: `len(clean_pin) >= 4 and len(clean_pin) <= 6`

### **Issue: Team Dashboard Login Fails**

**Cause 1: Admin user doesn't exist**
```bash
# Run the setup script
python check_admin_user.py
```

**Cause 2: Password hash mismatch**
```python
# The script will fix this automatically
# Or manually:
from convonet.security.auth import jwt_auth
new_hash = jwt_auth.hash_password('admin123')
# Update in database
```

**Cause 3: User is inactive**
```sql
UPDATE users_convonet 
SET is_active = true 
WHERE email = 'admin@convonet.com';
```

### **Issue: "It also says put 6 digits"**

**Fixed by:**
- Removed `num_digits=6` parameter
- Added `finish_on_key='#'` instead
- Users can now enter 4, 5, or 6 digits
- Press # to finish (for DTMF)
- Speech input ends automatically after timeout

---

## 🎤 Voice Command Examples (After PIN Auth)

Once authenticated, users can:

### **Personal Productivity:**
```
🗣️ "Create a high priority todo to review the quarterly report"
🗣️ "Add a reminder to call mom tomorrow at 2 PM"
🗣️ "Show me all my todos"
```

### **Team Management:**
```
🗣️ "Create a hackathon team"
🗣️ "What teams are available?"
🗣️ "Add admin@convonet.com to the hackathon team as owner"
🗣️ "Who is in the development team?"
```

### **Team Todos:**
```
🗣️ "Create a high priority todo for the dev team"
🗣️ "Assign a code review task to John in the dev team"
```

---

## 📊 Database Schema

### **users_convonet table:**
```sql
CREATE TABLE users_convonet (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    voice_pin VARCHAR(10) UNIQUE,  -- NEW: 4-6 digit PIN
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE,
    last_login_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_users_voice_pin ON users_convonet(voice_pin);
```

---

## 🚀 Testing

### **Test 1: Voice PIN with Speech**
1. Call your Twilio number
2. Wait for: "Please enter or say your 4 to 6 digit PIN, then press pound"
3. Say: **"one two three four"**
4. Should hear: "Welcome back, Admin! How can I help you today?"

### **Test 2: Voice PIN with Keypad**
1. Call your Twilio number
2. Wait for PIN prompt
3. Press: **1234#** on keypad
4. Should hear: "Welcome back, Admin!"

### **Test 3: Web Dashboard Login**
1. Go to https://hjlees.com/anthropic/team-dashboard
2. Email: admin@convonet.com
3. Password: admin123
4. Should login successfully

### **Test 4: Create Todo with User Context**
1. After PIN authentication
2. Say: "Create a high priority todo to prepare the demo"
3. Check database:
```sql
SELECT title, creator_id FROM todos_convonet ORDER BY created_at DESC LIMIT 1;
-- creator_id should be the admin user's UUID
```

---

## 🎯 Next Steps

1. ✅ Run `python check_admin_user.py` to fix admin credentials
2. ✅ Deploy the updated code to Render.com
3. ✅ Add voice_pin column to production database
4. ✅ Test PIN authentication via phone call
5. ✅ Verify web dashboard login works
6. ✅ Test todo creation with user association

---

## 📞 Demo Credentials

**Web Dashboard:**
- URL: https://hjlees.com/anthropic/team-dashboard
- Email: admin@convonet.com
- Password: admin123

**Voice Authentication:**
- Call: Your Twilio number
- PIN (Speech): "one two three four"
- PIN (Keypad): 1234#

---

## ✅ Benefits

- 🔐 **Secure**: Each user has unique PIN
- 👤 **User-Aware**: All todos track creator
- 🏢 **Team-Aware**: Validates team membership
- 🗣️ **Natural**: Speak PIN naturally ("one two three four")
- 📱 **Flexible**: Keypad or voice input
- 🔄 **Persistent**: user_id maintained throughout call

