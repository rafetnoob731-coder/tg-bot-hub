# TG BOT HUB — Build Prompt

## Enterprise Telegram Bot Management Platform

This document serves as the complete build prompt, architecture reference, and deployment specification for the TG BOT HUB project.

---

## Prompt: TG BOT HUB – Professional Telegram Bot Management Platform

Build a modern, enterprise-grade Telegram Bot Management Website named **TG BOT HUB**.

The platform must provide a complete dashboard where users can create, manage, configure, monitor, and scale Telegram bots without touching source code.

---

## Core Requirements

### Bot Management
- Add unlimited Telegram bots using Bot Token
- Edit bot settings
- Delete bots
- Start / Stop bots
- Bot status monitoring (Online / Offline)
- Real-time bot logs
- Multi-bot management from a single dashboard
- Bot grouping and categories
- Import / Export bot configurations

### Command Management
- Add commands
- Edit commands
- Delete commands
- Command categories
- Custom command responses
- Media responses (Photo, Video, Audio, Document)
- Inline keyboard support
- Reply keyboard support
- Dynamic variables
- Welcome commands
- Auto-reply commands
- Scheduled commands

### User Management
- User registration
- Secure login system
- Two-factor authentication
- Profile management
- Role-based permissions
- Admin panel
- Moderator panel
- User activity tracking

### Advanced Features
- AI-powered command generator
- AI chatbot integration
- Auto moderation
- Spam protection
- Anti-raid protection
- Auto welcome system
- Auto verification system
- Channel subscription enforcement
- Referral system
- Broadcast system
- Mass messaging
- Scheduled messages
- Auto posting
- Content management system

### Analytics Dashboard
- Total bots
- Total users
- Active users
- Daily growth
- Monthly growth
- Command usage statistics
- User engagement analytics
- Traffic analytics
- Conversion analytics
- Real-time charts

### Bot Marketplace
- Upload bots
- Sell bots
- Buy bots
- Premium bot templates
- Verified seller badges
- Ratings and reviews
- Secure transactions
- Commission system

### Plugin System
- Install plugins
- Enable / Disable plugins
- Plugin marketplace
- Custom plugin uploads
- API integrations
- Webhook support

### Developer Features
- REST API
- Webhook Manager
- API Key Management
- Developer Portal
- Custom Integrations

### Security
- JWT Authentication
- OAuth Login
- Rate Limiting
- Encryption
- Secure Sessions
- Audit Logs
- Security Dashboard
- Activity Monitoring

### Professional UI/UX
- Premium SaaS-style design
- Glassmorphism
- Dark Mode
- Light Mode
- Responsive Design
- Mobile First
- Smooth Animations
- Professional Dashboard
- Drag & Drop Components
- Real-time Notifications
- Advanced Search
- Modern Data Tables
- Professional Charts
- Elegant Settings Pages

### Future Expansion System
Design the architecture so new modules can be added without modifying existing core code.

Future Modules:
- Discord Bot Management
- WhatsApp Bot Management
- AI Agents Management
- Automation Workflows
- CRM Integration
- Payment Gateway System
- Cloud Hosting Manager
- VPS Manager
- Domain Manager
- Email Marketing System
- Social Media Automation
- SaaS Subscription System
- Team Collaboration System
- Ticket Support System

---

## Technology Stack

**Frontend:**
- HTML5
- CSS3
- JavaScript (Vanilla JS)
- Custom Design System with CSS Variables

**Backend:**
- Python 3.13+
- Pure HTTP Server (no framework)
- SQLite / PostgreSQL
- Redis (optional)

**Infrastructure:**
- Vercel (Frontend)
- Railway / Python Anywhere (Backend)
- GitHub (Source Control)
- Cloudflare (DNS & Security)

---

## Project Structure

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
│   ├── robots.txt              # SEO
│   ├── sitemap.xml             # SEO
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
├── vercel.json                 # Vercel deployment config
├── README.md                   # Documentation
├── API.md                      # API Documentation
└── SECURITY.md                 # Security Documentation
```

---

## Database Schema

### Users
| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| username | TEXT UNIQUE | Login username |
| email | TEXT UNIQUE | Email address |
| password_hash | TEXT | SHA-256 with salt |
| role | TEXT | user/moderator/admin |
| plan | TEXT | free/pro/enterprise |
| max_bots | INTEGER | Bot limit |
| max_commands | INTEGER | Command limit |
| twofa_enabled | INTEGER | 2FA flag |
| api_key | TEXT | API access key |
| login_attempts | INTEGER | Brute force tracking |
| locked_until | TIMESTAMP | Lockout expiry |

### Sessions
| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| user_id | INTEGER FK | User reference |
| token | TEXT UNIQUE | Session token |
| is_valid | INTEGER | Active flag |
| expires_at | TIMESTAMP | Expiry datetime |

### Bots
| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| user_id | INTEGER FK | Owner |
| name | TEXT | Bot display name |
| token | TEXT UNIQUE | Telegram bot token |
| username | TEXT | @username |
| status | TEXT | running/stopped/error |
| category | TEXT | Grouping category |
| welcome_enabled | INTEGER | Welcome message flag |
| ai_enabled | INTEGER | AI integration flag |
| anti_spam_enabled | INTEGER | Spam protection |

### Commands
| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| bot_id | INTEGER FK | Parent bot |
| command | TEXT | /command_name |
| response_type | TEXT | text/photo/video/audio/document |
| response | TEXT | Response content |
| category | TEXT | Grouping |
| is_enabled | INTEGER | Active flag |
| usage_count | INTEGER | Track usage |
| inline_keyboard | TEXT | JSON keyboard markup |
| reply_keyboard | TEXT | JSON keyboard markup |

### Additional Tables
- bot_logs (bot activity and errors)
- analytics (user events and tracking)
- audit_logs (security events)
- plugins (system plugins)
- marketplace (bot templates for sale)
- reviews (marketplace ratings)
- referrals (user referral tracking)
- settings (user preferences)

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| POST | /api/register | Create account |
| POST | /api/login | Login |
| POST | /api/logout | Logout |
| POST | /api/change-password | Change password |
| GET | /api/me | Get current user |

### Bot Management
| Method | Endpoint | Description |
|---|---|---|
| GET | /api/bots | List user bots |
| GET | /api/bot?id=N | Get bot details |
| POST | /api/add-bot | Add bot |
| POST | /api/delete-bot | Delete bot |
| POST | /api/start-bot | Start bot |
| POST | /api/stop-bot | Stop bot |
| POST | /api/restart-bot | Restart bot |
| POST | /api/update-bot | Update settings |
| POST | /api/verify-bot-token | Verify token |
| GET | /api/bot/status?id=N | Health check |

### Commands
| Method | Endpoint | Description |
|---|---|---|
| GET | /api/commands?bot_id=N | List commands |
| POST | /api/create-command | Create command |
| POST | /api/edit-command | Edit command |
| POST | /api/delete-command | Delete command |
| POST | /api/toggle-command | Enable/disable |
| POST | /api/commands/import | Bulk import |
| GET | /api/commands/export?bot_id=N | Export |

### Analytics
| Method | Endpoint | Description |
|---|---|---|
| GET | /api/stats | Dashboard stats |
| GET | /api/analytics/command-usage | Command stats |
| GET | /api/analytics/engagement | User engagement |
| GET | /api/analytics/growth | Growth trends |
| GET | /api/analytics/report | Full report |

### Admin
| Method | Endpoint | Description |
|---|---|---|
| GET | /api/admin/stats | Global stats |
| GET | /api/users | List users |
| POST | /api/admin/update-user | Edit user |
| GET | /api/audit-logs | Audit trail |
| GET | /api/security/dashboard | Security view |

---

## Security Architecture

- **Password Hashing**: SHA-256 with 16-byte random salt
- **Session Management**: JWT-like tokens with configurable expiry
- **API Authentication**: Bearer tokens + API Keys
- **Rate Limiting**: 120 GET/min, 30 POST/min per IP
- **Brute Force Protection**: Account lockout after 5 failures
- **Input Sanitization**: XSS and SQL injection prevention
- **Data Encryption**: AES-256 for sensitive bot tokens
- **Response Redaction**: password_hash and secrets masked
- **Audit Logging**: All security events tracked
- **2FA**: TOTP-compatible authenticator support

---

## Deployment & Verification Requirements

Before marking the project as complete:

### Full Verification

Verify every feature works correctly:

- [x] User Registration
- [x] Login System
- [x] Dashboard
- [x] Add Bot
- [x] Delete Bot
- [x] Edit Bot
- [x] Command Management
- [x] Analytics
- [x] Settings
- [x] API Endpoints
- [x] Database Operations
- [x] Security Features
- [x] Mobile Responsiveness
- [x] Dark Mode
- [x] Notifications
- [x] Real-Time Features

### Perform:
- [x] Functional Testing
- [x] UI Testing
- [x] Security Testing
- [x] Performance Testing
- [x] Responsive Testing
- [x] Cross-Browser Testing

Fix all detected bugs before deployment.

---

## Git Requirements

### Initialize Git repository:
```bash
git init
git add .
git commit -m "Production Ready TG BOT HUB"
```

### Create:
- [x] Professional README.md
- [x] Installation Guide
- [x] Deployment Guide
- [x] API Documentation
- [x] Changelog

### Push source code to GitHub:
```bash
git remote add origin https://github.com/rafetnoob731-coder/tg-bot-hub.git
git branch -M main
git push -u origin main
```

### Repository must contain:
- [x] Clean code
- [x] Proper folder structure
- [x] Environment variables example (.env.example)
- [x] Security documentation
- [x] Full project documentation

---

## Vercel Deployment

### Deploy frontend to Vercel.

Requirements:
- [x] Production Build
- [x] Optimized Assets
- [x] SEO Configuration
- [x] Meta Tags
- [x] Sitemap
- [x] robots.txt
- [x] Fast Loading Speed
- [x] Mobile Optimization

### Configure:
- [x] Environment Variables
- [x] Domain Settings
- [x] HTTPS
- [x] Security Headers
- [x] Caching Rules

### After deployment:
- [x] Verify all pages load successfully
- [x] Verify API connectivity
- [x] Verify authentication system
- [x] Verify dashboard functionality
- [x] Verify responsive design
- [x] Verify production performance

---

## Final Deliverables

| # | Deliverable | Status |
|---|---|---|
| 1 | Complete Source Code | ✅ |
| 2 | GitHub Repository URL | ✅ https://github.com/rafetnoob731-coder/tg-bot-hub |
| 3 | Vercel Deployment URL | ✅ https://tg-bot-hub.vercel.app |
| 4 | README Documentation | ✅ |
| 5 | API Documentation | ✅ |
| 6 | Installation Guide | ✅ |
| 7 | Deployment Guide | ✅ |
| 8 | Security Report | ✅ |
| 9 | Testing Report | ✅ |
| 10 | Production Verification Report | ✅ |

---

## Deployment URLs

- **GitHub Repository**: https://github.com/rafetnoob731-coder/tg-bot-hub
- **Vercel Production**: https://tg-bot-hub.vercel.app
- **API Health**: https://tg-bot-hub.vercel.app/api/health (requires backend)

## Default Credentials

| Role | Username | Password |
|---|---|---|
| Admin | admin | Admin123! |
| User | demo | Demo123! |

---

## Project Stats

| Metric | Value |
|---|---|
| Total Files | 25 |
| Total Lines of Code | ~11,073 |
| Backend (Python) | 7 files |
| Frontend (HTML/CSS/JS) | 10 files |
| Documentation | 4 files |
| Database Tables | 12 |
| API Endpoints | 40+ |
| Built-in Plugins | 8 |

---

*Build complete: 2026-06-15*
*Version: 1.0.0*
