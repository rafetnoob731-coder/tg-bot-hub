# TG BOT HUB

> **Enterprise-Grade Telegram Bot Management Platform**
> Manage, monitor, and scale unlimited Telegram bots from a single professional dashboard.

[![Status](https://img.shields.io/badge/status-production-green)](https://tg-bot-hub.vercel.app)
[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://github.com/rafetnoob731-coder/tg-bot-hub)
[![License](https://img.shields.io/badge/license-MIT-purple)](LICENSE)

![TG BOT HUB Dashboard](https://via.placeholder.com/1200x600/6C5CE7/FFFFFF?text=TG+BOT+HUB+Dashboard)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Installation Guide](#installation-guide)
- [Deployment Guide](#deployment-guide)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Security](#security)
- [Testing](#testing)
- [Changelog](#changelog)
- [License](#license)

---

## 🚀 Overview

**TG BOT HUB** is a professional, production-ready platform for managing Telegram bots at scale. Built with enterprise architecture, it provides a complete SaaS-style dashboard where users can create, configure, monitor, and scale Telegram bots without writing code.

### Key Capabilities

- **Multi-Bot Management** — Add unlimited bots, control them from one dashboard
- **Command System** — Create powerful commands with media, keyboards, variables
- **Real-Time Monitoring** — Live bot status, logs, and analytics
- **AI Integration** — Smart responses, auto-moderation, content generation
- **Plugin Architecture** — Extend functionality with modular plugins
- **Marketplace** — Buy, sell, and trade bot templates
- **Enterprise Security** — JWT auth, 2FA, rate limiting, audit logs
- **Developer API** — RESTful API with key authentication

---

## ✨ Features

### 🤖 Bot Management
- Add Telegram bots using Bot Token
- Real-time status monitoring (Online/Offline/Error)
- Start / Stop / Restart bots
- Edit bot settings and configuration
- Webhook management
- Bot health checks

### ⚡ Command System
- Create text, photo, video, audio, document responses
- Inline keyboard and reply keyboard support
- Dynamic variables (`{username}`, `{date}`, `{args}`, etc.)
- Welcome commands
- Auto-reply commands
- Command categories and filtering
- Import/Export commands (JSON)

### 📊 Analytics Dashboard
- Total bots, users, active sessions
- Daily and monthly growth trends
- Command usage statistics
- User engagement metrics
- Real-time activity charts
- Custom reports

### 🛡️ Security
- JWT-based session management
- Password hashing with salt
- Two-factor authentication
- Rate limiting and brute force protection
- CSRF protection
- XSS and SQL injection sanitization
- Audit logging
- Security dashboard

### 🔌 Plugin System
- Modular plugin architecture
- AI Chat integration
- Anti-spam protection
- Auto-moderation
- User verification
- Broadcast messaging
- Referral system
- Support tickets

### 👥 User Management
- Registration and login
- Role-based access (User, Moderator, Admin)
- Profile management
- Password reset
- 2FA support
- Activity tracking

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.13+ (Pure HTTP Server) |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **Styling** | Custom Design System with CSS Variables |
| **Charts** | Canvas API (no library dependencies) |
| **API** | RESTful JSON API |
| **Auth** | JWT-based sessions + API Keys |
| **Security** | AES-256 encryption, SHA-256 hashing |

---

## ⚡ Quick Start

### Prerequisites
- Python 3.10+
- pip (Python package manager)

### Installation

```bash
# Clone the repository
git clone https://github.com/rafetnoob731-coder/tg-bot-hub.git
cd tg-bot-hub

# Install dependencies
pip install -r requirements.txt

# Start the server
python backend/app.py

# Open in browser
open http://localhost:8000
```

### Default Credentials
| Role | Username | Password |
|---|---|---|
| **Admin** | `admin` | `Admin123!` |
| **User** | `demo` | `Demo123!` |

---

## 📦 Installation Guide

### Local Development Setup

#### 1. System Requirements
```bash
# Verify Python version
python --version  # Must be 3.10+

# Verify pip
pip --version
```

#### 2. Clone & Install
```bash
git clone https://github.com/rafetnoob731-coder/tg-bot-hub.git
cd tg-bot-hub
pip install -r requirements.txt
```

#### 3. Database Setup
The application uses SQLite by default. The database file is created automatically at `database/tgbothub.db` on first run.

For PostgreSQL (production):
```bash
pip install psycopg2-binary
# Update backend/database.py to use PostgreSQL connection
```

#### 4. Environment Configuration
```bash
cp .env.example .env
# Edit .env with your settings
```

#### 5. Run the Server
```bash
python backend/app.py
```

The server starts at `http://0.0.0.0:8000`

#### 6. Access the Platform
- Landing Page: `http://localhost:8000/`
- Dashboard: `http://localhost:8000/dashboard.html`
- Login: `http://localhost:8000/login.html`
- API: `http://localhost:8000/api/health`

---

## 🚢 Deployment Guide

### Option 1: Vercel (Frontend) + Python Anywhere (Backend)

#### Frontend (Vercel)

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel login
vercel --prod
```

3. Configure environment variables in Vercel dashboard.

#### Backend (Python Anywhere / Railway)

1. Push code to GitHub
2. Create account on Railway or Python Anywhere
3. Connect repository
4. Set start command: `python backend/app.py`
5. Configure environment variables

### Option 2: Docker Deployment

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "backend/app.py"]
```

```bash
docker build -t tg-bot-hub .
docker run -p 8000:8000 tg-bot-hub
```

### Option 3: Traditional VPS

#### Nginx Configuration
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
    }
}
```

#### Systemd Service
```ini
[Unit]
Description=TG BOT HUB
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/tg-bot-hub
ExecStart=/usr/bin/python3 backend/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 📖 API Documentation

### Authentication

All API endpoints (except login/register/health) require authentication via Bearer token.

#### Headers
```
Authorization: Bearer <session_token>
Content-Type: application/json
```

Alternatively, use API Key:
```
X-API-Key: <your_api_key>
```

### Endpoints

#### Auth Endpoints

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/api/register` | Register new user | No |
| POST | `/api/login` | Login | No |
| POST | `/api/logout` | Logout | Yes |
| POST | `/api/change-password` | Change password | Yes |
| POST | `/api/reset-password-request` | Request password reset | No |
| POST | `/api/reset-password` | Reset password | No |
| GET | `/api/me` | Get current user | Yes |

#### Bot Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/add-bot` | Add a new bot |
| GET | `/api/bots` | List user's bots |
| GET | `/api/bot?id=N` | Get bot details |
| POST | `/api/start-bot` | Start a bot |
| POST | `/api/stop-bot` | Stop a bot |
| POST | `/api/restart-bot` | Restart a bot |
| POST | `/api/delete-bot` | Delete a bot |
| POST | `/api/update-bot` | Update bot settings |
| POST | `/api/verify-bot-token` | Verify bot token |
| GET | `/api/bot/status?id=N` | Bot health check |
| POST | `/api/bot/set-webhook` | Set webhook |
| POST | `/api/bot/delete-webhook` | Delete webhook |

#### Command Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/commands?bot_id=N` | List commands |
| GET | `/api/command?id=N` | Get command details |
| POST | `/api/create-command` | Create command |
| POST | `/api/edit-command` | Edit command |
| POST | `/api/delete-command` | Delete command |
| POST | `/api/toggle-command` | Enable/disable command |
| POST | `/api/commands/import` | Import commands (JSON) |
| GET | `/api/commands/export?bot_id=N` | Export commands (JSON) |

#### Analytics Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/stats` | Dashboard stats |
| GET | `/api/analytics/command-usage` | Command usage stats |
| GET | `/api/analytics/engagement` | User engagement |
| GET | `/api/analytics/growth` | Growth trends |
| GET | `/api/analytics/report?type=full` | Full analytics report |

#### Management Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/logs` | Activity logs |
| GET | `/api/plugins` | List plugins |
| POST | `/api/plugins/toggle` | Toggle plugin |
| GET | `/api/marketplace` | Marketplace items |
| POST | `/api/marketplace/add` | Add marketplace item |
| POST | `/api/settings` | Save setting |
| POST | `/api/broadcast` | Broadcast message |
| POST | `/api/update-profile` | Update profile |
| POST | `/api/enable-2fa` | Enable 2FA |
| POST | `/api/disable-2fa` | Disable 2FA |

#### Admin Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/admin/stats` | Global stats |
| GET | `/api/users` | List users |
| GET | `/api/user?id=N` | Get user details |
| POST | `/api/admin/update-user` | Update user (role, etc.) |
| GET | `/api/audit-logs` | Audit logs |
| GET | `/api/security/dashboard` | Security dashboard |
| GET | `/api/all-bots` | All bots (admin) |

#### System

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Health check |

### Request/Response Examples

```json
// POST /api/login
{ "username": "admin", "password": "Admin123!" }

// Response
{
  "success": true,
  "token": "abc123...",
  "user": { "id": 1, "username": "admin", "role": "admin", ... }
}
```

```json
// POST /api/create-command
{
  "bot_id": 1,
  "command": "/start",
  "response_type": "text",
  "response": "Hello {username}! Welcome to our bot.",
  "category": "General",
  "inline_keyboard": "[[{\"text\":\"Visit Website\",\"url\":\"https://example.com\"}]]"
}

// Response
{ "success": true, "command_id": 1, "command": "/start" }
```

---

## 📁 Project Structure

```
TG-BOT-HUB/
├── backend/
│   ├── app.py                  # Main HTTP server & API routes
│   ├── database.py             # Database models & operations
│   ├── auth.py                 # Authentication & session management
│   ├── bot_manager.py          # Telegram bot lifecycle management
│   ├── command_manager.py      # Command CRUD & processing
│   ├── analytics.py            # Analytics & reporting
│   └── security.py             # Security, encryption, sanitization
├── frontend/
│   ├── index.html              # Landing page
│   ├── login.html              # Login page
│   ├── register.html           # Registration page
│   ├── dashboard.html          # Main dashboard
│   ├── css/
│   │   ├── style.css           # Design system & utilities
│   │   └── dashboard.css       # Dashboard layout & components
│   └── js/
│       ├── app.js              # API client & UI utilities
│       ├── auth.js             # Authentication checks & theme
│       └── dashboard.js        # Complete dashboard functionality
├── database/                   # SQLite database files (auto-created)
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── vercel.json                 # Vercel deployment config
```

---

## 🔒 Security

### Implemented Measures

| Category | Measure |
|---|---|
| **Authentication** | JWT-based sessions, API key auth |
| **Password Security** | SHA-256 hashing with salt |
| **2FA** | Time-based one-time password (TOTP) |
| **Rate Limiting** | Per-IP request limiting |
| **Brute Force** | Account lockout after failed attempts |
| **XSS Protection** | HTML sanitization, output encoding |
| **SQL Injection** | Parameterized queries |
| **Data Encryption** | AES-256 for sensitive data |
| **CSRF** | Token validation |
| **Session Security** | Configurable expiry, invalidation |
| **Audit Logging** | All security events logged |
| **Headers** | CORS, security headers |

### Security Best Practices

1. **Change default credentials** immediately after first login
2. **Enable 2FA** for admin accounts
3. **Use strong passwords** (min 8 chars, mixed case, numbers, symbols)
4. **Rotate API keys** regularly
5. **Keep dependencies updated**
6. **Use HTTPS** in production
7. **Configure rate limiting** appropriately
8. **Monitor audit logs** for suspicious activity

---

## 🧪 Testing

### Manual Test Scenarios

#### Authentication
- [ ] Register new user
- [ ] Login with valid credentials
- [ ] Login with invalid credentials (error handling)
- [ ] Session persistence across page reloads
- [ ] Logout clears session
- [ ] Password change works
- [ ] 2FA enable/disable

#### Bot Management
- [ ] Add bot with valid token
- [ ] Add bot with invalid token (error)
- [ ] Start bot updates status
- [ ] Stop bot updates status
- [ ] Bot detail view shows commands and logs
- [ ] Delete bot removes all data

#### Command Management
- [ ] Create text command
- [ ] Create command with inline keyboard
- [ ] Edit command updates response
- [ ] Toggle command enable/disable
- [ ] Delete command removes it
- [ ] Import/Export commands

#### Dashboard & UI
- [ ] All stats cards load with data
- [ ] Charts render correctly
- [ ] Navigation between all pages
- [ ] Dark/Light theme toggle
- [ ] Mobile responsive layout
- [ ] Toast notifications appear
- [ ] Modal dialogs work
- [ ] Search functionality

#### Admin
- [ ] User list shows all users
- [ ] Edit user role and limits
- [ ] Security dashboard shows events
- [ ] Audit logs track actions

---

## 📝 Changelog

### Version 1.0.0 (2026-06-15)

#### Initial Release
- ✅ Complete user authentication system
- ✅ Bot management (CRUD, start/stop/restart)
- ✅ Command system with multiple response types
- ✅ Analytics dashboard with charts
- ✅ Plugin system (8 built-in plugins)
- ✅ Marketplace for bot templates
- ✅ Admin panel with user management
- ✅ Security features (2FA, rate limiting, audit logs)
- ✅ Dark/Light theme support
- ✅ Responsive design
- ✅ RESTful API
- ✅ SQLite database (PostgreSQL ready)
- ✅ Glassmorphism UI design

---

## 📄 License

MIT License — see [LICENSE](LICENSE) file for details.

---

## 🤝 Support

- **Documentation**: [docs.tgbothub.com](https://docs.tgbothub.com)
- **Issues**: [GitHub Issues](https://github.com/rafetnoob731-coder/tg-bot-hub/issues)
- **Community**: [Telegram Group](https://t.me/tgbothub)

---

<p align="center">
  Built with ❤️ for the Telegram Bot Community<br>
  © 2026 TG BOT HUB. All rights reserved.
</p>
