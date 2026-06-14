"""
TG BOT HUB - Security Module
Security features: encryption, sanitization, rate limiting, CSRF protection
"""
import re
import json
import hashlib
import secrets
import hmac
import base64
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from database import Database

class Security:
    def __init__(self):
        self.db = Database()
        self._encryption_key = None
    
    def get_encryption_key(self):
        """Get or generate encryption key"""
        if self._encryption_key is None:
            # Store key in database settings
            cursor = self.db.conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = 'encryption_key' AND user_id IS NULL")
            row = cursor.fetchone()
            if row:
                self._encryption_key = row['value'].encode()
            else:
                self._encryption_key = Fernet.generate_key()
                cursor.execute(
                    "INSERT INTO settings (key, value) VALUES ('encryption_key', ?)",
                    (self._encryption_key.decode(),)
                )
                self.db.conn.commit()
        return self._encryption_key
    
    def encrypt(self, data):
        """Encrypt sensitive data"""
        f = Fernet(self.get_encryption_key())
        return f.encrypt(data.encode() if isinstance(data, str) else data).decode()
    
    def decrypt(self, encrypted_data):
        """Decrypt sensitive data"""
        f = Fernet(self.get_encryption_key())
        return f.decrypt(encrypted_data.encode() if isinstance(encrypted_data, str) else encrypted_data).decode()
    
    @staticmethod
    def sanitize_input(text, max_length=1000):
        """Sanitize user input to prevent XSS and SQL injection"""
        if not text or not isinstance(text, str):
            return ''
        
        # Trim to max length
        text = text[:max_length]
        
        # Remove HTML tags
        text = re.sub(r'<[^>]*>', '', text)
        
        # Remove script tags and event handlers
        text = re.sub(r'(?i)javascript:', '', text)
        text = re.sub(r'(?i)on\w+\s*=', '', text)
        
        # Remove SQL injection patterns
        text = re.sub(r'(?i)(\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bDROP\b|\bUNION\b)', '', text)
        
        # Escape special characters
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&#x27;')
        
        return text.strip()
    
    @staticmethod
    def validate_bot_token(token):
        """Validate Telegram Bot token format"""
        pattern = r'^\d{8,10}:[A-Za-z0-9_-]{35,45}$'
        return bool(re.match(pattern, token))
    
    @staticmethod
    def generate_csrf_token():
        """Generate CSRF token"""
        return secrets.token_hex(32)
    
    @staticmethod
    def validate_ip(ip_address):
        """Validate IP address format"""
        pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        if not re.match(pattern, ip_address):
            return False
        parts = ip_address.split('.')
        return all(0 <= int(part) <= 255 for part in parts)
    
    @staticmethod
    def mask_sensitive(text, visible_chars=4):
        """Mask sensitive data like tokens"""
        if not text or len(text) <= visible_chars * 2:
            return text
        return text[:visible_chars] + '*' * (len(text) - visible_chars * 2) + text[-visible_chars:]
    
    def check_brute_force(self, ip_address, max_attempts=10, window_minutes=15):
        """Check for brute force attempts from an IP"""
        cursor = self.db.conn.cursor()
        
        # Count recent failed attempts
        cursor.execute('''
            SELECT COUNT(*) as count FROM audit_logs 
            WHERE ip_address = ? 
            AND action IN ('auth.failed_login', 'auth.failed_register')
            AND created_at >= datetime('now', ? || ' minutes')
        ''', (ip_address, f'-{window_minutes}'))
        
        row = cursor.fetchone()
        return row['count'] >= max_attempts if row else False
    
    def log_security_event(self, event_type, details='', ip_address='', user_id=None):
        """Log security-related events"""
        self.db.add_audit_log(
            user_id=user_id,
            action=f'security.{event_type}',
            details=details,
            ip_address=ip_address
        )
    
    def validate_request(self, request_data, required_fields):
        """Validate that required fields are present and non-empty"""
        errors = []
        for field in required_fields:
            if field not in request_data or not request_data[field]:
                errors.append(f"{field} is required")
        return errors
    
    @staticmethod
    def sanitize_response(data):
        """Sanitize response data to prevent information leakage"""
        if isinstance(data, dict):
            sensitive_keys = ['password_hash', 'secret', 'encryption_key']
            for key in sensitive_keys:
                if key in data:
                    data[key] = '***REDACTED***'
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    Security.sanitize_response(value)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    Security.sanitize_response(item)
        return data
    
    def get_security_dashboard(self):
        """Get security dashboard data"""
        cursor = self.db.conn.cursor()
        
        # Recent security events
        cursor.execute('''
            SELECT * FROM audit_logs 
            WHERE action LIKE 'security.%' 
            ORDER BY created_at DESC LIMIT 20
        ''')
        security_events = [dict(row) for row in cursor.fetchall()]
        
        # Failed login attempts today
        cursor.execute('''
            SELECT COUNT(*) as count FROM audit_logs 
            WHERE action = 'auth.failed_login'
            AND DATE(created_at) = DATE('now')
        ''')
        failed_logins = cursor.fetchone()['count']
        
        # Active sessions count
        cursor.execute('''
            SELECT COUNT(*) as count FROM sessions 
            WHERE is_valid = 1 AND expires_at > CURRENT_TIMESTAMP
        ''')
        active_sessions = cursor.fetchone()['count']
        
        # Users with 2FA enabled
        cursor.execute('''
            SELECT COUNT(*) as count FROM users WHERE twofa_enabled = 1
        ''')
        twofa_users = cursor.fetchone()['count']
        
        return {
            'security_events': security_events,
            'failed_logins_today': failed_logins,
            'active_sessions': active_sessions,
            'twofa_users': twofa_users,
            'total_users': self.db.get_user_count()
        }

security = Security()
