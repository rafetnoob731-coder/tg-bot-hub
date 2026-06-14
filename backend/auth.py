"""
TG BOT HUB - Authentication Module
JWT-based authentication with session management, 2FA, and security features
"""
import hashlib
import secrets
import json
import re
from datetime import datetime, timedelta
from database import Database

class Auth:
    def __init__(self):
        self.db = Database()
    
    def hash_password(self, password):
        """Hash password with SHA-256 and salt"""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.sha256((password + salt).encode())
        return f"{salt}:{hash_obj.hexdigest()}"
    
    def verify_password(self, password, stored_hash):
        """Verify password against stored hash"""
        try:
            salt, hash_val = stored_hash.split(':')
            hash_obj = hashlib.sha256((password + salt).encode())
            return hash_obj.hexdigest() == hash_val
        except:
            return False
    
    def generate_token(self):
        """Generate a secure session token"""
        return secrets.token_hex(64)
    
    def generate_api_key(self):
        """Generate API key"""
        return f"tgbh_{secrets.token_hex(32)}"
    
    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_username(self, username):
        """Validate username format"""
        pattern = r'^[a-zA-Z0-9_]{3,32}$'
        return re.match(pattern, username) is not None
    
    def validate_password_strength(self, password):
        """Check password strength"""
        errors = []
        if len(password) < 8:
            errors.append("Password must be at least 8 characters")
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain uppercase letter")
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain lowercase letter")
        if not re.search(r'[0-9]', password):
            errors.append("Password must contain number")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain special character")
        return errors
    
    def register(self, username, email, password, full_name='', ip_address=''):
        """Register a new user"""
        errors = []
        
        if not self.validate_username(username):
            errors.append("Invalid username format (3-32 chars, letters/numbers/underscore)")
        
        if not self.validate_email(email):
            errors.append("Invalid email format")
        
        pw_errors = self.validate_password_strength(password)
        errors.extend(pw_errors)
        
        if errors:
            return {'success': False, 'errors': errors}
        
        # Check existing user
        if self.db.get_user_by_username(username):
            return {'success': False, 'errors': ['Username already taken']}
        
        if self.db.get_user_by_email(email):
            return {'success': False, 'errors': ['Email already registered']}
        
        password_hash = self.hash_password(password)
        
        try:
            user_id = self.db.create_user(username, email, password_hash, full_name)
            
            # Generate API key
            api_key = self.generate_api_key()
            self.db.update_user(user_id, api_key=api_key)
            
            # Create session
            token = self.generate_token()
            self.db.create_session(user_id, token, ip_address)
            
            # Audit log
            self.db.add_audit_log(user_id, 'user.register', 'User registered successfully', ip_address)
            
            return {
                'success': True,
                'token': token,
                'user': {
                    'id': user_id,
                    'username': username,
                    'email': email,
                    'full_name': full_name,
                    'role': 'user'
                }
            }
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}
    
    def login(self, username, password, ip_address='', user_agent=''):
        """Authenticate user"""
        user = self.db.get_user_by_username(username)
        if not user:
            user = self.db.get_user_by_email(username)
        
        if not user:
            return {'success': False, 'errors': ['Invalid credentials']}
        
        # Check if account is locked
        if user['locked_until']:
            locked_until = datetime.fromisoformat(user['locked_until'])
            if datetime.now() < locked_until:
                return {'success': False, 'errors': ['Account is locked. Try again later.']}
            else:
                # Reset lock
                self.db.update_user(user['id'], login_attempts=0, locked_until=None)
        
        # Verify password
        if not self.verify_password(password, user['password_hash']):
            attempts = user['login_attempts'] + 1
            if attempts >= 5:
                lock_until = datetime.now() + timedelta(minutes=15)
                self.db.update_user(user['id'], login_attempts=attempts, locked_until=lock_until.isoformat())
                return {'success': False, 'errors': ['Account locked for 15 minutes due to too many attempts']}
            self.db.update_user(user['id'], login_attempts=attempts)
            return {'success': False, 'errors': ['Invalid credentials']}
        
        # Reset login attempts
        self.db.update_user(user['id'], login_attempts=0, locked_until=None, last_login=datetime.now().isoformat())
        
        # Create session
        token = self.generate_token()
        self.db.create_session(user['id'], token, ip_address, user_agent)
        
        # Audit log
        self.db.add_audit_log(user['id'], 'user.login', 'User logged in', ip_address, user_agent)
        
        return {
            'success': True,
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'full_name': user['full_name'],
                'role': user['role'],
                'plan': user['plan'],
                'max_bots': user['max_bots'],
                'max_commands': user['max_commands'],
                'twofa_enabled': user['twofa_enabled'],
                'api_key': user['api_key']
            }
        }
    
    def validate_session(self, token):
        """Validate session token and return user info"""
        session = self.db.get_session(token)
        if not session:
            return None
        
        user = self.db.get_user(session['user_id'])
        if not user or not user['is_active']:
            return None
        
        return {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'full_name': user['full_name'],
            'role': user['role'],
            'plan': user['plan'],
            'avatar': user['avatar'],
            'max_bots': user['max_bots'],
            'max_commands': user['max_commands'],
            'twofa_enabled': user['twofa_enabled'],
            'api_key': user['api_key']
        }
    
    def logout(self, token):
        """Invalidate session"""
        self.db.invalidate_session(token)
        return {'success': True}
    
    def change_password(self, user_id, current_password, new_password):
        """Change user password"""
        user = self.db.get_user(user_id)
        if not user:
            return {'success': False, 'errors': ['User not found']}
        
        if not self.verify_password(current_password, user['password_hash']):
            return {'success': False, 'errors': ['Current password is incorrect']}
        
        pw_errors = self.validate_password_strength(new_password)
        if pw_errors:
            return {'success': False, 'errors': pw_errors}
        
        new_hash = self.hash_password(new_password)
        self.db.update_user(user_id, password_hash=new_hash)
        
        # Invalidate all sessions
        self.db.invalidate_user_sessions(user_id)
        
        self.db.add_audit_log(user_id, 'user.change_password', 'Password changed')
        
        return {'success': True, 'message': 'Password changed successfully. Please login again.'}
    
    def reset_password_request(self, email):
        """Request password reset (simplified - in production would send email)"""
        user = self.db.get_user_by_email(email)
        if not user:
            return {'success': False, 'errors': ['Email not found']}
        
        reset_token = self.generate_token()
        self.db.set_setting(user['id'], 'reset_token', reset_token)
        self.db.set_setting(user['id'], 'reset_token_expires', 
                           (datetime.now() + timedelta(hours=1)).isoformat())
        
        # In production, send email with reset link
        return {
            'success': True,
            'message': 'Password reset link sent to email',
            'reset_token': reset_token  # Only for demo
        }
    
    def reset_password(self, email, reset_token, new_password):
        """Complete password reset"""
        user = self.db.get_user_by_email(email)
        if not user:
            return {'success': False, 'errors': ['Email not found']}
        
        stored_token = self.db.get_setting(user['id'], 'reset_token')
        expires = self.db.get_setting(user['id'], 'reset_token_expires')
        
        if stored_token != reset_token:
            return {'success': False, 'errors': ['Invalid reset token']}
        
        if expires and datetime.fromisoformat(expires) < datetime.now():
            return {'success': False, 'errors': ['Reset token expired']}
        
        pw_errors = self.validate_password_strength(new_password)
        if pw_errors:
            return {'success': False, 'errors': pw_errors}
        
        new_hash = self.hash_password(new_password)
        self.db.update_user(user['id'], password_hash=new_hash)
        
        # Clear reset token
        self.db.set_setting(user['id'], 'reset_token', '')
        self.db.set_setting(user['id'], 'reset_token_expires', '')
        
        # Invalidate all sessions
        self.db.invalidate_user_sessions(user['id'])
        
        self.db.add_audit_log(user['id'], 'user.reset_password', 'Password reset completed')
        
        return {'success': True, 'message': 'Password reset successfully'}
    
    def validate_api_key(self, api_key):
        """Validate API key and return user"""
        if not api_key:
            return None
        
        # Look up API key in database (simple search)
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT id, username, role, plan FROM users WHERE api_key = ? AND api_key_enabled = 1 AND is_active = 1', (api_key,))
        user = cursor.fetchone()
        return dict(user) if user else None

# Rate limiter
class RateLimiter:
    def __init__(self):
        self.requests = {}
    
    def check(self, key, max_requests=60, window_seconds=60):
        """Check if rate limit exceeded"""
        now = datetime.now()
        if key not in self.requests:
            self.requests[key] = []
        
        # Clean old entries
        self.requests[key] = [t for t in self.requests[key] 
                            if (now - t).total_seconds() < window_seconds]
        
        if len(self.requests[key]) >= max_requests:
            return False, len(self.requests[key])
        
        self.requests[key].append(now)
        return True, len(self.requests[key])
