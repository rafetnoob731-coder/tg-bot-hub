"""
TG BOT HUB - Database Module
Enterprise-grade database management with SQLite/PostgreSQL support
"""
import sqlite3
import os
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from threading import Lock

DATABASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
os.makedirs(DATABASE_DIR, exist_ok=True)

DB_PATH = os.path.join(DATABASE_DIR, 'tgbothub.db')

class Database:
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.conn = None
            return cls._instance
    
    def __init__(self):
        if self.conn is None:
            self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self.conn.execute("PRAGMA journal_mode=WAL")
            self.conn.execute("PRAGMA foreign_keys=ON")
            self.init_tables()
    
    def init_tables(self):
        cursor = self.conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT DEFAULT '',
                avatar TEXT DEFAULT '',
                role TEXT DEFAULT 'user',
                plan TEXT DEFAULT 'free',
                is_active INTEGER DEFAULT 1,
                is_verified INTEGER DEFAULT 0,
                twofa_secret TEXT DEFAULT '',
                twofa_enabled INTEGER DEFAULT 0,
                api_key TEXT DEFAULT '',
                api_key_enabled INTEGER DEFAULT 0,
                max_bots INTEGER DEFAULT 5,
                max_commands INTEGER DEFAULT 50,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                login_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                ip_address TEXT DEFAULT '',
                user_agent TEXT DEFAULT '',
                is_valid INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Bots table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                token TEXT UNIQUE NOT NULL,
                username TEXT DEFAULT '',
                description TEXT DEFAULT '',
                avatar TEXT DEFAULT '',
                status TEXT DEFAULT 'stopped',
                category TEXT DEFAULT 'General',
                welcome_message TEXT DEFAULT '',
                welcome_enabled INTEGER DEFAULT 0,
                force_subscribe_channel TEXT DEFAULT '',
                force_subscribe_enabled INTEGER DEFAULT 0,
                auto_reply_enabled INTEGER DEFAULT 0,
                anti_spam_enabled INTEGER DEFAULT 0,
                anti_flood_enabled INTEGER DEFAULT 0,
                verification_enabled INTEGER DEFAULT 0,
                referral_enabled INTEGER DEFAULT 0,
                ticket_enabled INTEGER DEFAULT 0,
                ai_enabled INTEGER DEFAULT 0,
                ai_model TEXT DEFAULT 'gpt-3.5-turbo',
                ai_api_key TEXT DEFAULT '',
                moderation_enabled INTEGER DEFAULT 0,
                broadcast_enabled INTEGER DEFAULT 0,
                webhook_url TEXT DEFAULT '',
                webhook_enabled INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Commands table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                command TEXT NOT NULL,
                response_type TEXT DEFAULT 'text',
                response TEXT NOT NULL,
                category TEXT DEFAULT 'General',
                description TEXT DEFAULT '',
                is_enabled INTEGER DEFAULT 1,
                is_welcome INTEGER DEFAULT 0,
                is_auto_reply INTEGER DEFAULT 0,
                is_scheduled INTEGER DEFAULT 0,
                schedule_interval TEXT DEFAULT '',
                schedule_time TEXT DEFAULT '',
                media_url TEXT DEFAULT '',
                inline_keyboard TEXT DEFAULT '',
                reply_keyboard TEXT DEFAULT '',
                variables TEXT DEFAULT '',
                cooldown INTEGER DEFAULT 0,
                user_cooldown INTEGER DEFAULT 0,
                required_role TEXT DEFAULT '',
                usage_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bot_id) REFERENCES bots(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Bot logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_id INTEGER NOT NULL,
                level TEXT DEFAULT 'info',
                message TEXT NOT NULL,
                data TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bot_id) REFERENCES bots(id) ON DELETE CASCADE
            )
        ''')
        
        # Analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                bot_id INTEGER,
                event_type TEXT NOT NULL,
                event_data TEXT DEFAULT '',
                ip_address TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Audit logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                details TEXT DEFAULT '',
                ip_address TEXT DEFAULT '',
                user_agent TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            )
        ''')
        
        # Plugin settings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plugins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT DEFAULT '',
                version TEXT DEFAULT '1.0.0',
                author TEXT DEFAULT 'TG BOT HUB',
                is_enabled INTEGER DEFAULT 1,
                settings TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Marketplace items
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS marketplace (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seller_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                price REAL DEFAULT 0,
                type TEXT DEFAULT 'bot',
                category TEXT DEFAULT 'General',
                file_url TEXT DEFAULT '',
                version TEXT DEFAULT '1.0.0',
                is_verified INTEGER DEFAULT 0,
                is_featured INTEGER DEFAULT 0,
                rating REAL DEFAULT 0,
                downloads INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Reviews
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                item_id INTEGER NOT NULL,
                rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
                comment TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (item_id) REFERENCES marketplace(id) ON DELETE CASCADE
            )
        ''')
        
        # Referrals
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER NOT NULL,
                referred_id INTEGER NOT NULL,
                reward REAL DEFAULT 0,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (referrer_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (referred_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(user_id, key)
            )
        ''')
        
        self.conn.commit()
    
    # ========== USER OPERATIONS ==========
    
    def create_user(self, username, email, password_hash, full_name=''):
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO users (username, email, password_hash, full_name, api_key) VALUES (?, ?, ?, ?, ?)',
                (username, email, password_hash, full_name, secrets.token_hex(32))
            )
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            raise Exception(f"User already exists: {str(e)}")
    
    def get_user(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        return cursor.fetchone()
    
    def get_user_by_username(self, username):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        return cursor.fetchone()
    
    def get_user_by_email(self, email):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        return cursor.fetchone()
    
    def update_user(self, user_id, **kwargs):
        allowed = ['full_name', 'avatar', 'role', 'plan', 'is_active', 'is_verified', 
                   'twofa_secret', 'twofa_enabled', 'api_key', 'api_key_enabled',
                   'max_bots', 'max_commands', 'last_login', 'login_attempts', 'locked_until']
        sets = []
        values = []
        for k, v in kwargs.items():
            if k in allowed:
                sets.append(f"{k} = ?")
                values.append(v)
        if sets:
            values.append(user_id)
            cursor = self.conn.cursor()
            cursor.execute(f"UPDATE users SET {', '.join(sets)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
            self.conn.commit()
            return cursor.rowcount > 0
        return False
    
    def get_all_users(self, page=1, per_page=20, search=''):
        cursor = self.conn.cursor()
        offset = (page - 1) * per_page
        if search:
            cursor.execute(
                "SELECT * FROM users WHERE username LIKE ? OR email LIKE ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (f"%{search}%", f"%{search}%", per_page, offset)
            )
        else:
            cursor.execute("SELECT * FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?", (per_page, offset))
        return cursor.fetchall()
    
    def get_user_count(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM users')
        return cursor.fetchone()['count']
    
    # ========== SESSION OPERATIONS ==========
    
    def create_session(self, user_id, token, ip_address='', user_agent='', expires_days=30):
        cursor = self.conn.cursor()
        expires_at = (datetime.now() + timedelta(days=expires_days)).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            'INSERT INTO sessions (user_id, token, ip_address, user_agent, expires_at) VALUES (?, ?, ?, ?, ?)',
            (user_id, token, ip_address, user_agent, expires_at)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_session(self, token):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT s.*, u.username, u.role, u.is_active FROM sessions s JOIN users u ON s.user_id = u.id WHERE s.token = ? AND s.is_valid = 1 AND datetime(s.expires_at) > datetime("now")',
            (token,)
        )
        return cursor.fetchone()
    
    def invalidate_session(self, token):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE sessions SET is_valid = 0 WHERE token = ?', (token,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def invalidate_user_sessions(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE sessions SET is_valid = 0 WHERE user_id = ?', (user_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    # ========== BOT OPERATIONS ==========
    
    def create_bot(self, user_id, name, token, username='', description=''):
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO bots (user_id, name, token, username, description) VALUES (?, ?, ?, ?, ?)',
                (user_id, name, token, username, description)
            )
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            raise Exception("Bot with this token already exists")
    
    def get_bot(self, bot_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM bots WHERE id = ?', (bot_id,))
        return cursor.fetchone()
    
    def get_user_bots(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM bots WHERE user_id = ? AND is_active = 1 ORDER BY created_at DESC', (user_id,))
        return cursor.fetchall()
    
    def get_all_bots(self, page=1, per_page=20):
        cursor = self.conn.cursor()
        offset = (page - 1) * per_page
        cursor.execute(
            'SELECT b.*, u.username as owner FROM bots b JOIN users u ON b.user_id = u.id ORDER BY b.created_at DESC LIMIT ? OFFSET ?',
            (per_page, offset)
        )
        return cursor.fetchall()
    
    def update_bot(self, bot_id, **kwargs):
        allowed = ['name', 'token', 'username', 'description', 'avatar', 'status', 'category',
                   'welcome_message', 'welcome_enabled', 'force_subscribe_channel', 'force_subscribe_enabled',
                   'auto_reply_enabled', 'anti_spam_enabled', 'anti_flood_enabled', 'verification_enabled',
                   'referral_enabled', 'ticket_enabled', 'ai_enabled', 'ai_model', 'ai_api_key',
                   'moderation_enabled', 'broadcast_enabled', 'webhook_url', 'webhook_enabled', 'is_active']
        sets = []
        values = []
        for k, v in kwargs.items():
            if k in allowed:
                sets.append(f"{k} = ?")
                values.append(v)
        if sets:
            values.append(bot_id)
            cursor = self.conn.cursor()
            cursor.execute(f"UPDATE bots SET {', '.join(sets)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
            self.conn.commit()
            return cursor.rowcount > 0
        return False
    
    def delete_bot(self, bot_id):
        cursor = self.conn.cursor()
        # Delete related data
        cursor.execute('DELETE FROM commands WHERE bot_id = ?', (bot_id,))
        cursor.execute('DELETE FROM bot_logs WHERE bot_id = ?', (bot_id,))
        cursor.execute('DELETE FROM analytics WHERE bot_id = ?', (bot_id,))
        cursor.execute('DELETE FROM bots WHERE id = ?', (bot_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def get_bot_count(self, user_id=None):
        cursor = self.conn.cursor()
        if user_id:
            cursor.execute('SELECT COUNT(*) as count FROM bots WHERE user_id = ? AND is_active = 1', (user_id,))
        else:
            cursor.execute('SELECT COUNT(*) as count FROM bots WHERE is_active = 1')
        return cursor.fetchone()['count']
    
    def get_bot_stats(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'running' THEN 1 ELSE 0 END) as running,
                SUM(CASE WHEN status = 'stopped' THEN 1 ELSE 0 END) as stopped,
                SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error
            FROM bots WHERE is_active = 1
        ''')
        return cursor.fetchone()
    
    # ========== COMMAND OPERATIONS ==========
    
    def create_command(self, bot_id, user_id, command, response_type, response, category='General', description=''):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO commands (bot_id, user_id, command, response_type, response, category, description) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (bot_id, user_id, command, response_type, response, category, description)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_command(self, command_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM commands WHERE id = ?', (command_id,))
        return cursor.fetchone()
    
    def get_bot_commands(self, bot_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM commands WHERE bot_id = ? ORDER BY created_at DESC', (bot_id,))
        return cursor.fetchall()
    
    def update_command(self, command_id, **kwargs):
        allowed = ['command', 'response_type', 'response', 'category', 'description',
                   'is_enabled', 'is_welcome', 'is_auto_reply', 'is_scheduled',
                   'schedule_interval', 'schedule_time', 'media_url',
                   'inline_keyboard', 'reply_keyboard', 'variables',
                   'cooldown', 'user_cooldown', 'required_role', 'usage_count']
        sets = []
        values = []
        for k, v in kwargs.items():
            if k in allowed:
                sets.append(f"{k} = ?")
                values.append(v)
        if sets:
            values.append(command_id)
            cursor = self.conn.cursor()
            cursor.execute(f"UPDATE commands SET {', '.join(sets)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
            self.conn.commit()
            return cursor.rowcount > 0
        return False
    
    def delete_command(self, command_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM commands WHERE id = ?', (command_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def get_command_count(self, bot_id=None):
        cursor = self.conn.cursor()
        if bot_id:
            cursor.execute('SELECT COUNT(*) as count FROM commands WHERE bot_id = ?', (bot_id,))
        else:
            cursor.execute('SELECT COUNT(*) as count FROM commands')
        return cursor.fetchone()['count']
    
    # ========== LOG OPERATIONS ==========
    
    def add_log(self, bot_id, level, message, data=''):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO bot_logs (bot_id, level, message, data) VALUES (?, ?, ?, ?)',
            (bot_id, level, message, data)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_bot_logs(self, bot_id, page=1, per_page=50):
        cursor = self.conn.cursor()
        offset = (page - 1) * per_page
        cursor.execute(
            'SELECT * FROM bot_logs WHERE bot_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?',
            (bot_id, per_page, offset)
        )
        return cursor.fetchall()
    
    def get_all_logs(self, page=1, per_page=50):
        cursor = self.conn.cursor()
        offset = (page - 1) * per_page
        cursor.execute(
            'SELECT l.*, b.name as bot_name, b.username as bot_username FROM bot_logs l JOIN bots b ON l.bot_id = b.id ORDER BY l.created_at DESC LIMIT ? OFFSET ?',
            (per_page, offset)
        )
        return cursor.fetchall()
    
    # ========== ANALYTICS OPERATIONS ==========
    
    def add_analytics(self, user_id, event_type, event_data='', bot_id=None, ip_address=''):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO analytics (user_id, bot_id, event_type, event_data, ip_address) VALUES (?, ?, ?, ?, ?)',
            (user_id, bot_id, event_type, event_data, ip_address)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_analytics(self, user_id=None, days=30):
        cursor = self.conn.cursor()
        if user_id:
            cursor.execute(
                '''SELECT event_type, COUNT(*) as count, DATE(created_at) as date 
                   FROM analytics 
                   WHERE user_id = ? AND created_at >= DATE('now', ? || ' days')
                   GROUP BY event_type, DATE(created_at)
                   ORDER BY date DESC''',
                (user_id, f'-{days}')
            )
        else:
            cursor.execute(
                '''SELECT event_type, COUNT(*) as count, DATE(created_at) as date 
                   FROM analytics 
                   WHERE created_at >= DATE('now', ? || ' days')
                   GROUP BY event_type, DATE(created_at)
                   ORDER BY date DESC''',
                (f'-{days}',)
            )
        return cursor.fetchall()
    
    def get_dashboard_stats(self, user_id=None):
        cursor = self.conn.cursor()
        stats = {}
        
        # User counts
        stats['total_users'] = self.get_user_count()
        
        # Bot counts
        if user_id:
            stats['total_bots'] = self.get_bot_count(user_id)
            stats['total_commands'] = cursor.execute(
                'SELECT COUNT(*) as count FROM commands WHERE user_id = ?', (user_id,)
            ).fetchone()['count']
            stats['total_logs'] = cursor.execute(
                'SELECT COUNT(*) as count FROM bot_logs l JOIN bots b ON l.bot_id = b.id WHERE b.user_id = ?',
                (user_id,)
            ).fetchone()['count']
        else:
            stats['total_bots'] = self.get_bot_count()
            stats['total_commands'] = cursor.execute('SELECT COUNT(*) as count FROM commands').fetchone()['count']
            stats['total_logs'] = cursor.execute('SELECT COUNT(*) as count FROM bot_logs').fetchone()['count']
        
        # Today's activity
        stats['today_activity'] = cursor.execute(
            "SELECT COUNT(*) as count FROM analytics WHERE DATE(created_at) = DATE('now')"
        ).fetchone()['count']
        
        # Growth (users created today)
        stats['today_users'] = cursor.execute(
            "SELECT COUNT(*) as count FROM users WHERE DATE(created_at) = DATE('now')"
        ).fetchone()['count']
        
        return stats
    
    # ========== AUDIT LOGS ==========
    
    def add_audit_log(self, user_id, action, details='', ip_address='', user_agent=''):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO audit_logs (user_id, action, details, ip_address, user_agent) VALUES (?, ?, ?, ?, ?)',
            (user_id, action, details, ip_address, user_agent)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_audit_logs(self, page=1, per_page=50):
        cursor = self.conn.cursor()
        offset = (page - 1) * per_page
        cursor.execute(
            '''SELECT a.*, u.username 
               FROM audit_logs a 
               LEFT JOIN users u ON a.user_id = u.id 
               ORDER BY a.created_at DESC LIMIT ? OFFSET ?''',
            (per_page, offset)
        )
        return cursor.fetchall()
    
    # ========== PLUGIN OPERATIONS ==========
    
    def add_plugin(self, name, description='', version='1.0.0', author='TG BOT HUB'):
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO plugins (name, description, version, author) VALUES (?, ?, ?, ?)',
                (name, description, version, author)
            )
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            raise Exception("Plugin already exists")
    
    def get_plugins(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM plugins ORDER BY name')
        return cursor.fetchall()
    
    def update_plugin(self, plugin_id, **kwargs):
        allowed = ['description', 'version', 'author', 'is_enabled', 'settings']
        sets = []
        values = []
        for k, v in kwargs.items():
            if k in allowed:
                sets.append(f"{k} = ?")
                values.append(v)
        if sets:
            values.append(plugin_id)
            cursor = self.conn.cursor()
            cursor.execute(f"UPDATE plugins SET {', '.join(sets)} WHERE id = ?", values)
            self.conn.commit()
            return cursor.rowcount > 0
        return False
    
    # ========== MARKETPLACE OPERATIONS ==========
    
    def add_marketplace_item(self, seller_id, name, description, price=0, type='bot', category='General'):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO marketplace (seller_id, name, description, price, type, category) VALUES (?, ?, ?, ?, ?, ?)',
            (seller_id, name, description, price, type, category)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_marketplace_items(self, page=1, per_page=20, category=''):
        cursor = self.conn.cursor()
        offset = (page - 1) * per_page
        if category:
            cursor.execute(
                '''SELECT m.*, u.username as seller_name 
                   FROM marketplace m JOIN users u ON m.seller_id = u.id 
                   WHERE m.status = 'active' AND m.category = ? 
                   ORDER BY m.is_featured DESC, m.created_at DESC LIMIT ? OFFSET ?''',
                (category, per_page, offset)
            )
        else:
            cursor.execute(
                '''SELECT m.*, u.username as seller_name 
                   FROM marketplace m JOIN users u ON m.seller_id = u.id 
                   WHERE m.status = 'active' 
                   ORDER BY m.is_featured DESC, m.created_at DESC LIMIT ? OFFSET ?''',
                (per_page, offset)
            )
        return cursor.fetchall()
    
    # ========== SETTINGS OPERATIONS ==========
    
    def set_setting(self, user_id, key, value):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT OR REPLACE INTO settings (user_id, key, value, updated_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP)',
            (user_id, key, str(value))
        )
        self.conn.commit()
    
    def get_setting(self, user_id, key, default=''):
        cursor = self.conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE user_id = ? AND key = ?', (user_id, key))
        row = cursor.fetchone()
        return row['value'] if row else default
    
    def get_all_settings(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM settings WHERE user_id = ?', (user_id,))
        return cursor.fetchall()
    
    # ========== REFERRAL OPERATIONS ==========
    
    def add_referral(self, referrer_id, referred_id):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO referrals (referrer_id, referred_id) VALUES (?, ?)',
            (referrer_id, referred_id)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_referrals(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT r.*, u.username as referred_username FROM referrals r JOIN users u ON r.referred_id = u.id WHERE r.referrer_id = ? ORDER BY r.created_at DESC',
            (user_id,)
        )
        return cursor.fetchall()
    
    def close(self):
        if self.conn:
            self.conn.close()
