# TG BOT HUB - API Documentation

## Base URL

```
http://localhost:8000/api
```

## Authentication

### Headers
```
Authorization: Bearer <session_token>
Content-Type: application/json
```

### API Key Auth
```
X-API-Key: <api_key>
```

---

## Authentication Endpoints

### POST /api/register
Create a new user account.

**Request:**
```json
{
  "username": "string (3-32 chars, alphanumeric + underscore)",
  "email": "string (valid email)",
  "password": "string (min 8 chars, uppercase, lowercase, number, special char)",
  "full_name": "string (optional)"
}
```

**Response:**
```json
{
  "success": true,
  "token": "session_token_string",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "Administrator",
    "role": "user"
  }
}
```

**Errors:**
- 400: Validation errors (invalid username, email, weak password)
- 409: Username or email already exists

---

### POST /api/login
Authenticate and get session token.

**Request:**
```json
{
  "username": "string (username or email)",
  "password": "string"
}
```

**Response:**
```json
{
  "success": true,
  "token": "session_token_string",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "plan": "free",
    "max_bots": 999,
    "max_commands": 9999,
    "twofa_enabled": false,
    "api_key": "tgbh_xxx..."
  }
}
```

**Errors:**
- 401: Invalid credentials
- 429: Too many attempts (account locked)

---

### POST /api/logout
Invalidate current session.

**Request:**
```json
{
  "token": "session_token_string"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Logged out"
}
```

---

### POST /api/change-password
Change account password. Invalidates all sessions.

**Request:**
```json
{
  "current_password": "string",
  "new_password": "string (min 8 chars, complex)"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Password changed successfully. Please login again."
}
```

---

### GET /api/me
Get current authenticated user details.

**Headers:** Authorization: Bearer <token>

**Response:**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "plan": "free",
    "max_bots": 999,
    "max_commands": 9999,
    "twofa_enabled": false,
    "api_key": "tgbh_xxx..."
  }
}
```

---

## Bot Management

### POST /api/add-bot
Add a new Telegram bot after token verification.

**Request:**
```json
{
  "name": "My Bot",
  "token": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
  "description": "Optional description"
}
```

**Response:**
```json
{
  "success": true,
  "bot_id": 1,
  "bot": {
    "id": 1,
    "name": "My Bot",
    "token": "1234567890...vwxyz",
    "username": "my_bot",
    "status": "stopped"
  }
}
```

---

### GET /api/bots
List all bots for the authenticated user.

**Response:**
```json
{
  "success": true,
  "bots": [
    {
      "id": 1,
      "name": "My Bot",
      "token": "1234567890...vwxyz",
      "username": "my_bot",
      "status": "running",
      "category": "General",
      "created_at": "2026-06-15T00:00:00"
    }
  ],
  "total": 1
}
```

---

### GET /api/bot?id=N
Get detailed bot information including commands and logs.

**Response:**
```json
{
  "success": true,
  "bot": { "...full bot object..." },
  "commands": [ "...command objects..." ],
  "logs": [ "...log objects..." ],
  "summary": {
    "total_logs": 10,
    "total_commands": 5,
    "total_command_usage": 100,
    "errors": 0,
    "status": "running"
  }
}
```

---

### POST /api/start-bot
Start a bot's polling mechanism.

**Request:** `{ "bot_id": 1 }`

**Response:** `{ "success": true, "message": "Bot started" }`

---

### POST /api/stop-bot
Stop a running bot.

**Request:** `{ "bot_id": 1 }`

**Response:** `{ "success": true, "message": "Bot stopped" }`

---

### POST /api/delete-bot
Delete a bot and all associated data (commands, logs).

**Request:** `{ "bot_id": 1 }`

**Response:** `{ "success": true, "message": "Bot deleted" }`

---

### POST /api/update-bot
Update bot settings.

**Request:**
```json
{
  "bot_id": 1,
  "name": "New Name",
  "category": "Utility",
  "description": "Updated description",
  "welcome_enabled": 1,
  "ai_enabled": 1,
  "anti_spam_enabled": 1
}
```

---

### POST /api/verify-bot-token
Verify a Telegram bot token without adding it.

**Request:** `{ "token": "1234567890:ABC..." }`

**Response:**
```json
{
  "valid": true,
  "id": 1234567890,
  "username": "my_bot",
  "first_name": "My Bot"
}
```

---

### GET /api/bot/status?id=N
Check bot health status.

**Response:**
```json
{
  "success": true,
  "status": {
    "status": "online",
    "message": "Bot is responding"
  }
}
```

---

### POST /api/bot/set-webhook
Set a webhook URL for the bot.

**Request:** `{ "bot_id": 1, "webhook_url": "https://example.com/webhook" }`

---

## Command Management

### POST /api/create-command
Create a new bot command.

**Request:**
```json
{
  "bot_id": 1,
  "command": "/start",
  "response_type": "text",
  "response": "Welcome {username}!",
  "category": "General",
  "description": "Welcome message",
  "media_url": "",
  "inline_keyboard": "[[{\"text\":\"Button\",\"callback_data\":\"data\"}]]",
  "reply_keyboard": "",
  "variables": "{\"custom_var\": \"value\"}",
  "is_welcome": 0,
  "is_auto_reply": 0
}
```

**Response Types:** text, photo, video, audio, document

**Available Variables:** {username}, {first_name}, {last_name}, {user_id}, {chat_id}, {chat_title}, {date}, {time}, {datetime}, {args}

---

### GET /api/commands?bot_id=N
List all commands for a bot.

**Response:**
```json
{
  "success": true,
  "commands": [
    {
      "id": 1,
      "command": "/start",
      "response_type": "text",
      "response": "Welcome!",
      "category": "General",
      "is_enabled": 1,
      "usage_count": 42
    }
  ],
  "categories": ["General", "Admin"],
  "total": 1
}
```

---

### POST /api/edit-command
Edit an existing command.

**Request:**
```json
{
  "command_id": 1,
  "command": "/newstart",
  "response": "Updated response"
}
```

---

### POST /api/delete-command
Delete a command.

**Request:** `{ "command_id": 1 }`

---

### POST /api/toggle-command
Enable or disable a command.

**Request:** `{ "command_id": 1 }`

---

### POST /api/commands/import
Import commands in bulk from JSON.

**Request:**
```json
{
  "bot_id": 1,
  "commands": "[{\"command\":\"/start\",\"response\":\"Hello\",\"response_type\":\"text\"}]"
}
```

---

### GET /api/commands/export?bot_id=N
Export all commands as JSON.

---

## Analytics

### GET /api/stats
Get dashboard statistics for authenticated user.

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_users": 10,
    "total_bots": 5,
    "total_commands": 20,
    "total_logs": 100,
    "today_activity": 50,
    "today_users": 2,
    "bots": { "total": 5, "active": 3, "stopped": 2, "error": 0 },
    "growth": { "users": [...], "bots": [...] },
    "activity": [...]
  }
}
```

---

### GET /api/analytics/command-usage
Top commands by usage.

---

### GET /api/analytics/engagement
User engagement metrics.

---

### GET /api/analytics/growth
Growth trends over time.

---

### GET /api/analytics/report?type=full
Generate comprehensive analytics report.

**Types:** full, overview, commands, engagement, traffic, conversion

---

## System & Utility

### GET /api/health
Server health check.

```json
{
  "status": "healthy",
  "timestamp": "2026-06-15T00:00:00",
  "version": "1.0.0",
  "uptime": "running"
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "success": false,
  "error": "Description of the error"
}
```

Or for validation errors:

```json
{
  "success": false,
  "errors": ["Error 1", "Error 2"]
}
```

### HTTP Status Codes
- 200: Success
- 400: Bad request / Validation error
- 401: Authentication required
- 403: Forbidden (insufficient permissions)
- 404: Resource not found
- 405: Method not allowed
- 429: Rate limit exceeded
- 500: Internal server error

---

## Rate Limiting

- **GET requests:** 120 per minute per IP
- **POST requests:** 30 per minute per IP
- **Login attempts:** 5 per 15 minutes before lockout

---

## Webhook Integration

### Setting up a webhook
1. Start the bot in TG BOT HUB
2. Configure webhook URL: `POST /api/bot/set-webhook`
3. Telegram will send updates to your webhook URL
4. Process updates in your webhook handler

### Webhook URL format
```
https://your-server.com/webhook/{bot_id}
```

---

## SDK Examples

### Python
```python
import requests

API_BASE = "http://localhost:8000/api"

# Login
r = requests.post(f"{API_BASE}/login", json={
    "username": "admin",
    "password": "Admin123!"
})
token = r.json()["token"]

# Get bots
r = requests.get(f"{API_BASE}/bots", headers={
    "Authorization": f"Bearer {token}"
})
bots = r.json()["bots"]

# Create command
r = requests.post(f"{API_BASE}/create-command", 
    headers={"Authorization": f"Bearer {token}"},
    json={
        "bot_id": 1,
        "command": "/hello",
        "response_type": "text",
        "response": "Hello World!"
    }
)
```

### JavaScript
```javascript
const API = 'http://localhost:8000/api';

async function login(username, password) {
  const res = await fetch(`${API}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  const data = await res.json();
  return data;
}

async function getBots(token) {
  const res = await fetch(`${API}/bots`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return res.json();
}

async function createCommand(token, botId, command, response) {
  const res = await fetch(`${API}/create-command`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ bot_id: botId, command, response_type: 'text', response })
  });
  return res.json();
}
```

---

## Changelog

### v1.0.0 (2026-06-15)
- Initial API release
- Full CRUD for bots, commands, users
- Analytics and reporting endpoints
- Security and authentication
- Plugin and marketplace APIs
