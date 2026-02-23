# Team Management Guide

## How to Associate Teams with Members

### Method 1: Team Dashboard UI (Recommended)

1. **Login to Team Dashboard**
   - Visit: `https://hjlees.com/anthropic/team-dashboard`
   - Login with admin credentials: `admin@convonet.com` / `admin123`

2. **Select a Team**
   - Choose a team from the dropdown menu
   - You'll see the team's todos and members

3. **Add Team Members**
   - Click **"Add Member"** button in Quick Actions
   - Search for users by email, username, or name
   - Select a user from search results
   - Choose their role (Member, Admin, Viewer)
   - Click **"Add Member"**

### Method 2: API Endpoints

#### Add Member to Team
```bash
POST /api/teams/{team_id}/members
Authorization: Bearer {access_token}
Content-Type: application/json

{
    "user_id": "user-uuid-here",
    "role": "member"  // or "admin", "viewer"
}
```

#### Search Users
```bash
GET /api/teams/search/users?q=search_term
Authorization: Bearer {access_token}
```

#### Get Team Members
```bash
GET /api/teams/{team_id}
Authorization: Bearer {access_token}
```

### Method 3: Create Users and Auto-Assign

#### Create Demo Users
```bash
python create_users.py
```

This creates users and automatically adds them to the Demo Team:
- **manager@convonet.com** / `manager123` (Admin role)
- **developer@convonet.com** / `dev123` (Member role)
- **designer@convonet.com** / `design123` (Member role)
- **tester@convonet.com** / `test123` (Viewer role)

### Method 4: During User Registration

When users register via `/register`, they can be manually added to teams by admins using Method 1 or 2.

## Team Roles and Permissions

### Owner
- Can manage team settings
- Can add/remove members
- Can change member roles
- Can delete the team
- Full access to all team todos

### Admin
- Can add/remove members
- Can change member roles (except owner)
- Can manage team todos
- Full access to team todos

### Member
- Can create and manage assigned todos
- Can view public team todos
- Can be assigned to todos
- Cannot manage team membership

### Viewer
- Can view public team todos
- Cannot create or edit todos
- Cannot be assigned to todos
- Read-only access

## Step-by-Step Demo Flow

### 1. Create Team
1. Login as admin
2. Click "Create New Team"
3. Enter team name and description
4. You become the team owner

### 2. Add Members
1. Click "Add Member" button
2. Search for existing users
3. Select user and assign role
4. Confirm addition

### 3. Create Team Todos
1. Click "Create Todo"
2. Set title, description, priority
3. Assign to team member
4. Set due date
5. Todo appears in team dashboard

### 4. Manage Todos
- Members can view assigned todos
- Admins can assign todos to members
- Owners can manage all aspects

## API Examples

### Complete Flow Example

```bash
# 1. Login and get token
curl -X POST https://hjlees.com/anthropic/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@convonet.com", "password": "admin123"}'

# 2. Create team
curl -X POST https://hjlees.com/anthropic/api/teams/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Development Team", "description": "Software development team"}'

# 3. Search for users
curl -X GET "https://hjlees.com/anthropic/api/teams/search/users?q=developer" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 4. Add member to team
curl -X POST https://hjlees.com/anthropic/api/teams/TEAM_ID/members \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "USER_ID", "role": "member"}'

# 5. Create team todo
curl -X POST https://hjlees.com/anthropic/api/team-todos/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement user authentication",
    "description": "Add JWT authentication to the API",
    "priority": "high",
    "assignee_id": "USER_ID",
    "team_id": "TEAM_ID"
  }'
```

## Troubleshooting

### User Not Found
- Make sure the user exists in the system
- Check if they registered via `/register`
- Verify the search query is correct

### Permission Denied
- Ensure you have admin or owner role
- Check if you're logged in with correct credentials
- Verify the team exists and you're a member

### Team Not Found
- Make sure the team ID is correct
- Check if the team exists in your account
- Verify you have access to the team

## Best Practices

1. **Start with Demo Users**: Use the demo users created by the script
2. **Use UI for Testing**: The dashboard UI is easiest for demos
3. **Check Permissions**: Ensure users have appropriate roles
4. **Test Team Collaboration**: Create todos and assign them to team members
5. **Verify Access**: Test that members can only see appropriate todos

## Demo Credentials Summary

| Email | Password | Role | Team |
|-------|----------|------|------|
| admin@convonet.com | admin123 | Owner | Demo Team |
| manager@convonet.com | manager123 | Admin | Demo Team |
| developer@convonet.com | dev123 | Member | Demo Team |
| designer@convonet.com | design123 | Member | Demo Team |
| tester@convonet.com | test123 | Viewer | Demo Team |
