"""
TG BOT HUB - Main Application
FastAPI-based REST API server with comprehensive routes
"""
import json
import os
import sys
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote_plus
from database import Database
from auth import Auth, RateLimiter
from bot_manager import BotManager, bot_manager
from command_manager import CommandManager, command_manager
from analytics import Analytics, analytics
from security import Security, security

# CORS headers
CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-API-Key, X-CSRF-Token',
    'Access-Control-Allow-Credentials': 'true',
}

# Initialize modules
db = Database()
auth = Auth()
rate_limiter = RateLimiter()
bot_mgr = BotManager()
cmd_mgr = CommandManager()
analytics_mgr = Analytics()
security_mgr = Security()

class TGbotHubAPI(BaseHTTPRequestHandler):
    """HTTP Request Handler for TG BOT HUB API"""
    
    def log_message(self, format, *args):
        """Custom logging"""
        pass
    
    def _send_json(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        for key, value in CORS_HEADERS.items():
            self.send_header(key, value)
        self.send_header('Content-Type', 'application/json')
        self.send_header('X-API-Version', '1.0.0')
        self.end_headers()
        sanitized = security_mgr.sanitize_response(data)
        self.wfile.write(json.dumps(sanitized).encode())
    
    def _send_error(self, status, message):
        """Send error response"""
        self._send_json({'success': False, 'error': message}, status)
    
    def _send_html(self, html_content, status=200):
        """Send HTML response"""
        self.send_response(status)
        for key, value in CORS_HEADERS.items():
            self.send_header(key, value)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def _send_file(self, filepath, content_type='text/html'):
        """Send a static file"""
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            self.send_response(200)
            for key, value in CORS_HEADERS.items():
                self.send_header(key, value)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self._send_error(404, 'File not found')
    
    def _get_json_body(self):
        """Parse JSON request body"""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return {}
        try:
            body = self.rfile.read(content_length)
            return json.loads(body.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}
    
    def _get_form_body(self):
        """Parse form data"""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return {}
        try:
            body = self.rfile.read(content_length).decode()
            params = {}
            for part in body.split('&'):
                if '=' in part:
                    key, value = part.split('=', 1)
                    params[unquote_plus(key)] = unquote_plus(value)
            return params
        except:
            return {}
    
    def _get_client_ip(self):
        """Get client IP address"""
        ip = self.headers.get('X-Forwarded-For', '').split(',')[0].strip()
        if not ip:
            ip = self.client_address[0]
        return ip
    
    def _get_auth_user(self):
        """Authenticate request from headers"""
        # Check session token
        auth_header = self.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            user = auth.validate_session(token)
            if user:
                return user
        
        # Check API key
        api_key = self.headers.get('X-API-Key', '')
        if api_key:
            user = auth.validate_api_key(api_key)
            if user:
                return user
        
        # Check cookie
        cookies = self.headers.get('Cookie', '')
        for cookie in cookies.split(';'):
            if '=' in cookie:
                key, value = cookie.split('=', 1)
                if key.strip() == 'session':
                    user = auth.validate_session(value.strip())
                    if user:
                        return user
        
        return None
    
    def _require_auth(self):
        """Require authentication, return user or send error"""
        user = self._get_auth_user()
        if not user:
            self._send_error(401, 'Authentication required')
            return None
        return user
    
    def _require_admin(self):
        """Require admin role"""
        user = self._require_auth()
        if not user:
            return None
        if user['role'] not in ('admin', 'superadmin'):
            self._send_error(403, 'Admin access required')
            return None
        return user
    
    def _parse_path(self):
        """Parse URL path"""
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        params = parse_qs(parsed.query)
        # Flatten single-value params
        params = {k: v[0] if len(v) == 1 else v for k, v in params.items()}
        return path, params
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        for key, value in CORS_HEADERS.items():
            self.send_header(key, value)
        self.send_header('Content-Length', '0')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        path, params = self._parse_path()
        
        # Rate limiting
        client_ip = self._get_client_ip()
        allowed, _ = rate_limiter.check(f"get:{client_ip}", 120, 60)
        if not allowed:
            self._send_error(429, 'Too many requests')
            return
        
        # API Routes
        if path.startswith('/api/'):
            self._handle_api_get(path, params)
            return
        
        # Serve static files
        self._serve_static(path)
    
    def do_POST(self):
        """Handle POST requests"""
        path, params = self._parse_path()
        
        # Rate limiting
        client_ip = self._get_client_ip()
        allowed, _ = rate_limiter.check(f"post:{client_ip}", 30, 60)
        if not allowed:
            self._send_error(429, 'Too many requests')
            return
        
        # Parse body based on content type
        content_type = self.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            body = self._get_json_body()
        elif 'application/x-www-form-urlencoded' in content_type:
            body = self._get_form_body()
        else:
            body = self._get_json_body()
        
        if path.startswith('/api/'):
            self._handle_api_post(path, body)
    
    def do_PUT(self):
        """Handle PUT requests"""
        path, params = self._parse_path()
        body = self._get_json_body()
        
        if path.startswith('/api/'):
            self._handle_api_put(path, body)
    
    def do_DELETE(self):
        """Handle DELETE requests"""
        path, params = self._parse_path()
        body = self._get_json_body()
        
        if path.startswith('/api/'):
            self._handle_api_delete(path, body)
    
    # ========== STATIC FILE SERVING ==========
    
    def _serve_static(self, path):
        """Serve frontend static files"""
        frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
        
        if not path or path == '/':
            path = '/index.html'
        
        filepath = os.path.normpath(os.path.join(frontend_dir, path.lstrip('/')))
        
        # Security check - prevent directory traversal
        if not filepath.startswith(frontend_dir):
            self._send_error(403, 'Access denied')
            return
        
        # Determine content type
        ext = os.path.splitext(filepath)[1].lower()
        content_types = {
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.ico': 'image/x-icon',
            '.webp': 'image/webp',
            '.woff2': 'font/woff2',
            '.ttf': 'font/ttf',
        }
        content_type = content_types.get(ext, 'application/octet-stream')
        
        self._send_file(filepath, content_type)
    
    # ========== API GET HANDLERS ==========
    
    def _handle_api_get(self, path, params):
        """Handle GET API requests"""
        
        # Auth routes
        if path == '/api/me':
            user = self._require_auth()
            if user:
                self._send_json({'success': True, 'user': user})
        
        elif path == '/api/users':
            admin = self._require_admin()
            if admin:
                page = int(params.get('page', 1))
                search = params.get('search', '')
                users = db.get_all_users(page=page, search=search)
                self._send_json({
                    'success': True,
                    'users': [dict(u) for u in users],
                    'total': db.get_user_count()
                })
        
        elif path == '/api/user':
            user = self._require_auth()
            if user:
                target_id = int(params.get('id', user['id']))
                if target_id != user['id'] and user['role'] != 'admin':
                    self._send_error(403, 'Access denied')
                    return
                target_user = db.get_user(target_id)
                if target_user:
                    self._send_json({'success': True, 'user': dict(target_user)})
                else:
                    self._send_error(404, 'User not found')
        
        # Bot routes
        elif path == '/api/bots':
            user = self._require_auth()
            if user:
                bots = db.get_user_bots(user['id'])
                self._send_json({
                    'success': True,
                    'bots': [dict(b) for b in bots],
                    'total': len(bots)
                })
        
        elif path == '/api/all-bots':
            admin = self._require_admin()
            if admin:
                page = int(params.get('page', 1))
                bots = db.get_all_bots(page=page)
                self._send_json({
                    'success': True,
                    'bots': [dict(b) for b in bots],
                    'total': db.get_bot_count()
                })
        
        elif path == '/api/bot':
            user = self._require_auth()
            if user:
                bot_id = int(params.get('id', 0))
                bot = db.get_bot(bot_id)
                if bot and (bot['user_id'] == user['id'] or user['role'] == 'admin'):
                    # Get commands and logs
                    commands = db.get_bot_commands(bot_id)
                    logs = db.get_bot_logs(bot_id)
                    commands_list = [dict(c) for c in commands]
                    logs_list = [dict(l) for l in logs]
                    
                    # Get activity summary
                    summary = bot_mgr.get_bot_activity_summary(bot_id)
                    
                    self._send_json({
                        'success': True,
                        'bot': dict(bot),
                        'commands': commands_list,
                        'logs': logs_list,
                        'summary': summary
                    })
                else:
                    self._send_error(404, 'Bot not found')
        
        elif path == '/api/bot/status':
            user = self._require_auth()
            if user:
                bot_id = int(params.get('id', 0))
                bot = db.get_bot(bot_id)
                if bot and (bot['user_id'] == user['id'] or user['role'] == 'admin'):
                    status = bot_mgr.health_check(bot_id)
                    self._send_json({'success': True, 'status': status})
                else:
                    self._send_error(404, 'Bot not found')
        
        elif path == '/api/bot/logs':
            user = self._require_auth()
            if user:
                bot_id = int(params.get('id', 0))
                page = int(params.get('page', 1))
                bot = db.get_bot(bot_id)
                if bot and (bot['user_id'] == user['id'] or user['role'] == 'admin'):
                    logs = db.get_bot_logs(bot_id, page=page)
                    self._send_json({'success': True, 'logs': [dict(l) for l in logs]})
                else:
                    self._send_error(404, 'Bot not found')
        
        # Command routes
        elif path == '/api/commands':
            user = self._require_auth()
            if user:
                bot_id = int(params.get('bot_id', 0))
                bot = db.get_bot(bot_id)
                if bot and (bot['user_id'] == user['id'] or user['role'] == 'admin'):
                    commands = cmd_mgr.get_commands(bot_id)
                    categories = cmd_mgr.get_categories(bot_id)
                    self._send_json({
                        'success': True,
                        'commands': [dict(c) for c in commands],
                        'categories': categories,
                        'total': len(commands)
                    })
                else:
                    self._send_error(404, 'Bot not found')
        
        elif path == '/api/command':
            user = self._require_auth()
            if user:
                cmd_id = int(params.get('id', 0))
                cmd = db.get_command(cmd_id)
                if cmd:
                    bot = db.get_bot(cmd['bot_id'])
                    if bot and (bot['user_id'] == user['id'] or user['role'] == 'admin'):
                        self._send_json({'success': True, 'command': dict(cmd)})
                    else:
                        self._send_error(403, 'Access denied')
                else:
                    self._send_error(404, 'Command not found')
        
        # Analytics routes
        elif path == '/api/stats':
            user = self._require_auth()
            if user:
                stats = analytics_mgr.get_dashboard_stats(user['id'])
                self._send_json({'success': True, 'stats': stats})
        
        elif path == '/api/admin/stats':
            admin = self._require_admin()
            if admin:
                stats = analytics_mgr.get_dashboard_stats()
                self._send_json({'success': True, 'stats': stats})
        
        elif path == '/api/analytics/command-usage':
            user = self._require_auth()
            if user:
                data = analytics_mgr.get_command_usage_stats(user['id'])
                self._send_json({'success': True, 'data': data})
        
        elif path == '/api/analytics/engagement':
            user = self._require_auth()
            if user:
                data = analytics_mgr.get_user_engagement(user['id'])
                self._send_json({'success': True, 'data': data})
        
        elif path == '/api/analytics/growth':
            user = self._require_auth()
            if user:
                data = analytics_mgr.get_dashboard_stats(user['id']).get('growth', {})
                self._send_json({'success': True, 'data': data})
        
        elif path == '/api/analytics/traffic':
            admin = self._require_admin()
            if admin:
                data = analytics_mgr.get_traffic_analytics()
                self._send_json({'success': True, 'data': data})
        
        elif path == '/api/analytics/report':
            user = self._require_auth()
            if user:
                report_type = params.get('type', 'full')
                report = analytics_mgr.generate_report(user['id'], report_type)
                self._send_json({'success': True, 'report': report})
        
        # Plugin routes
        elif path == '/api/plugins':
            user = self._require_auth()
            if user:
                plugins = db.get_plugins()
                self._send_json({'success': True, 'plugins': [dict(p) for p in plugins]})
        
        # Marketplace routes
        elif path == '/api/marketplace':
            page = int(params.get('page', 1))
            category = params.get('category', '')
            items = db.get_marketplace_items(page=page, category=category)
            self._send_json({
                'success': True,
                'items': [dict(i) for i in items]
            })
        
        # Logs routes
        elif path == '/api/logs':
            user = self._require_auth()
            if user:
                page = int(params.get('page', 1))
                logs = db.get_all_logs(page=page)
                self._send_json({
                    'success': True,
                    'logs': [dict(l) for l in logs],
                    'total': len(logs)
                })
        
        elif path == '/api/audit-logs':
            admin = self._require_admin()
            if admin:
                page = int(params.get('page', 1))
                logs = db.get_audit_logs(page=page)
                self._send_json({
                    'success': True,
                    'logs': [dict(l) for l in logs]
                })
        
        # Security
        elif path == '/api/security/dashboard':
            admin = self._require_admin()
            if admin:
                data = security_mgr.get_security_dashboard()
                self._send_json({'success': True, 'data': data})
        
        # Export commands
        elif path == '/api/commands/export':
            user = self._require_auth()
            if user:
                bot_id = int(params.get('bot_id', 0))
                bot = db.get_bot(bot_id)
                if bot and (bot['user_id'] == user['id'] or user['role'] == 'admin'):
                    data = cmd_mgr.export_commands(bot_id)
                    self._send_json({'success': True, 'commands': data})
                else:
                    self._send_error(404, 'Bot not found')
        
        # API Keys
        elif path == '/api/api-keys':
            user = self._require_auth()
            if user:
                self._send_json({
                    'success': True,
                    'api_key': user.get('api_key', ''),
                    'enabled': True
                })
        
        # Health check
        elif path == '/api/health':
            self._send_json({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0',
                'uptime': 'running'
            })
        
        else:
            self._send_error(404, f'Route not found: {path}')
    
    # ========== API POST HANDLERS ==========
    
    def _handle_api_post(self, path, body):
        """Handle POST API requests"""
        client_ip = self._get_client_ip()
        user_agent = self.headers.get('User-Agent', '')
        
        # ===== AUTH ROUTES =====
        
        if path == '/api/register':
            username = security_mgr.sanitize_input(body.get('username', ''))
            email = security_mgr.sanitize_input(body.get('email', '')).lower()
            password = body.get('password', '')
            full_name = security_mgr.sanitize_input(body.get('full_name', ''))
            
            result = auth.register(username, email, password, full_name, client_ip)
            if result['success']:
                analytics_mgr.track_event(result['user']['id'], 'user.register', ip_address=client_ip)
                # Set session cookie
                self._send_json(result)
            else:
                security_mgr.log_security_event('failed_register', str(result['errors']), client_ip)
                self._send_json(result, 400)
        
        elif path == '/api/login':
            username = body.get('username', '')
            password = body.get('password', '')
            
            # Check brute force
            if security_mgr.check_brute_force(client_ip):
                self._send_error(429, 'Too many login attempts. Try again later.')
                return
            
            result = auth.login(username, password, client_ip, user_agent)
            if result['success']:
                analytics_mgr.track_event(result['user']['id'], 'user.login', ip_address=client_ip)
                self._send_json(result)
            else:
                security_mgr.log_security_event('failed_login', f"User: {username}", client_ip)
                self._send_json(result, 401)
        
        elif path == '/api/logout':
            token = body.get('token', '')
            if not token:
                auth_header = self.headers.get('Authorization', '')
                if auth_header.startswith('Bearer '):
                    token = auth_header[7:]
            if token:
                auth.logout(token)
            self._send_json({'success': True, 'message': 'Logged out'})
        
        elif path == '/api/change-password':
            user = self._require_auth()
            if user:
                result = auth.change_password(
                    user['id'],
                    body.get('current_password', ''),
                    body.get('new_password', '')
                )
                self._send_json(result)
        
        elif path == '/api/reset-password-request':
            email = body.get('email', '')
            result = auth.reset_password_request(email)
            self._send_json(result)
        
        elif path == '/api/reset-password':
            result = auth.reset_password(
                body.get('email', ''),
                body.get('token', ''),
                body.get('new_password', '')
            )
            self._send_json(result)
        
        # ===== BOT ROUTES =====
        
        elif path == '/api/add-bot':
            user = self._require_auth()
            if user:
                # Check bot limit
                bot_count = db.get_bot_count(user['id'])
                if bot_count >= user['max_bots']:
                    self._send_error(403, f"Bot limit reached ({user['max_bots']}). Upgrade your plan.")
                    return
                
                name = security_mgr.sanitize_input(body.get('name', ''))
                token = body.get('token', '')
                description = security_mgr.sanitize_input(body.get('description', ''))
                
                # Validate token format
                if not security_mgr.validate_bot_token(token):
                    self._send_error(400, 'Invalid bot token format')
                    return
                
                result = bot_mgr.add_bot(user['id'], name, token, description)
                if result['success']:
                    analytics_mgr.track_event(user['id'], 'bot.add', bot_id=result['bot_id'])
                self._send_json(result)
        
        elif path == '/api/start-bot':
            user = self._require_auth()
            if user:
                bot_id = int(body.get('bot_id', 0))
                bot = db.get_bot(bot_id)
                if bot and (bot['user_id'] == user['id'] or user['role'] == 'admin'):
                    result = bot_mgr.start_bot(bot_id, user['id'])
                    if result['success']:
                        analytics_mgr.track_event(user['id'], 'bot.start', bot_id=bot_id)
                    self._send_json(result)
                else:
                    self._send_error(404, 'Bot not found')
        
        elif path == '/api/stop-bot':
            user = self._require_auth()
            if user:
                bot_id = int(body.get('bot_id', 0))
                bot = db.get_bot(bot_id)
                if bot and (bot['user_id'] == user['id'] or user['role'] == 'admin'):
                    result = bot_mgr.stop_bot(bot_id, user['id'])
                    self._send_json(result)
                else:
                    self._send_error(404, 'Bot not found')
        
        elif path == '/api/restart-bot':
            user = self._require_auth()
            if user:
                bot_id = int(body.get('bot_id', 0))
                bot = db.get_bot(bot_id)
                if bot and (bot['user_id'] == user['id'] or user['role'] == 'admin'):
                    result = bot_mgr.restart_bot(bot_id, user['id'])
                    self._send_json(result)
                else:
                    self._send_error(404, 'Bot not found')
        
        elif path == '/api/verify-bot-token':
            user = self._require_auth()
            if user:
                token = body.get('token', '')
                result = bot_mgr.verify_token(token)
                self._send_json(result)
        
        elif path == '/api/delete-bot':
            user = self._require_auth()
            if user:
                bot_id = int(body.get('bot_id', 0))
                bot = db.get_bot(bot_id)
                if bot and (bot['user_id'] == user['id'] or user['role'] == 'admin'):
                    result = bot_mgr.delete_bot(bot_id, user['id'])
                    self._send_json(result)
                else:
                    self._send_error(404, 'Bot not found')
        
        elif path == '/api/bot/set-webhook':
            user = self._require_auth()
            if user:
                bot_id = int(body.get('bot_id', 0))
                webhook_url = body.get('webhook_url', '')
                bot = db.get_bot(bot_id)
                if bot and (bot['user_id'] == user['id'] or user['role'] == 'admin'):
                    result = bot_mgr.set_webhook(bot_id, webhook_url)
                    self._send_json(result)
                else:
                    self._send_error(404, 'Bot not found')
        
        elif path == '/api/bot/delete-webhook':
            user = self._require_auth()
            if user:
                bot_id = int(body.get('bot_id', 0))
                bot = db.get_bot(bot_id)
                if bot and (bot['user_id'] == user['id'] or user['role'] == 'admin'):
                    result = bot_mgr.delete_webhook(bot_id)
                    self._send_json(result)
                else:
                    self._send_error(404, 'Bot not found')
        
        # ===== COMMAND ROUTES =====
        
        elif path == '/api/create-command':
            user = self._require_auth()
            if user:
                bot_id = int(body.get('bot_id', 0))
                bot = db.get_bot(bot_id)
                if bot and (bot['user_id'] == user['id'] or user['role'] == 'admin'):
                    result = cmd_mgr.create_command(
                        bot_id=bot_id,
                        user_id=user['id'],
                        command=body.get('command', ''),
                        response_type=body.get('response_type', 'text'),
                        response=body.get('response', ''),
                        category=body.get('category', 'General'),
                        description=body.get('description', ''),
                        is_welcome=body.get('is_welcome', 0),
                        is_auto_reply=body.get('is_auto_reply', 0),
                        is_scheduled=body.get('is_scheduled', 0),
                        media_url=body.get('media_url', ''),
                        inline_keyboard=body.get('inline_keyboard', ''),
                        reply_keyboard=body.get('reply_keyboard', ''),
                        variables=body.get('variables', ''),
                    )
                    if result['success']:
                        analytics_mgr.track_event(user['id'], 'command.create', bot_id=bot_id)
                    self._send_json(result)
                else:
                    self._send_error(404, 'Bot not found')
        
        elif path == '/api/edit-command':
            user = self._require_auth()
            if user:
                cmd_id = int(body.get('command_id', 0))
                cmd = db.get_command(cmd_id)
                if cmd:
                    bot = db.get_bot(cmd['bot_id'])
                    if bot and (bot['user_id'] == user['id'] or user['role'] == 'admin'):
                        update_data = {}
                        for field in ['command', 'response_type', 'response', 'category', 'description',
                                      'is_enabled', 'is_welcome', 'is_auto_reply', 'is_scheduled',
                                      'schedule_interval', 'schedule_time', 'media_url',
                                      'inline_keyboard', 'reply_keyboard', 'variables',
                                      'cooldown', 'user_cooldown', 'required_role']:
                            if field in body:
                                update_data[field] = body[field]
                        
                        result = cmd_mgr.edit_command(cmd_id, user['id'], **update_data)
                        self._send_json(result)
                    else:
                        self._send_error(403, 'Access denied')
                else:
                    self._send_error(404, 'Command not found')
        
        elif path == '/api/delete-command':
            user = self._require_auth()
            if user:
                cmd_id = int(body.get('command_id', 0))
                cmd = db.get_command(cmd_id)
                if cmd:
                    bot = db.get_bot(cmd['bot_id'])
                    if bot and (bot['user_id'] == user['id'] or user['role'] == 'admin'):
                        result = cmd_mgr.delete_command(cmd_id, user['id'])
                        self._send_json(result)
                    else:
                        self._send_error(403, 'Access denied')
                else:
                    self._send_error(404, 'Command not found')
        
        elif path == '/api/toggle-command':
            user = self._require_auth()
            if user:
                cmd_id = int(body.get('command_id', 0))
                cmd = db.get_command(cmd_id)
                if cmd:
                    bot = db.get_bot(cmd['bot_id'])
                    if bot and (bot['user_id'] == user['id'] or user['role'] == 'admin'):
                        result = cmd_mgr.toggle_command(cmd_id, user['id'])
                        self._send_json(result)
                    else:
                        self._send_error(403, 'Access denied')
                else:
                    self._send_error(404, 'Command not found')
        
        elif path == '/api/commands/import':
            user = self._require_auth()
            if user:
                bot_id = int(body.get('bot_id', 0))
                bot = db.get_bot(bot_id)
                if bot and (bot['user_id'] == user['id'] or user['role'] == 'admin'):
                    commands_json = body.get('commands', '[]')
                    result = cmd_mgr.import_commands(bot_id, user['id'], commands_json)
                    self._send_json(result)
                else:
                    self._send_error(404, 'Bot not found')
        
        # ===== PROFILE ROUTES =====
        
        elif path == '/api/update-profile':
            user = self._require_auth()
            if user:
                full_name = security_mgr.sanitize_input(body.get('full_name', ''))
                avatar = body.get('avatar', '')
                db.update_user(user['id'], full_name=full_name, avatar=avatar)
                self._send_json({'success': True, 'message': 'Profile updated'})
        
        elif path == '/api/enable-2fa':
            user = self._require_auth()
            if user:
                # In production, generate actual 2FA secret
                secret = secrets.token_hex(16)
                db.update_user(user['id'], twofa_secret=secret, twofa_enabled=1)
                self._send_json({
                    'success': True,
                    'secret': secret,
                    'message': '2FA enabled. Use an authenticator app.'
                })
        
        elif path == '/api/disable-2fa':
            user = self._require_auth()
            if user:
                db.update_user(user['id'], twofa_secret='', twofa_enabled=0)
                self._send_json({'success': True, 'message': '2FA disabled'})
        
        # ===== SETTINGS ROUTES =====
        
        elif path == '/api/settings':
            user = self._require_auth()
            if user:
                key = body.get('key', '')
                value = body.get('value', '')
                if key:
                    db.set_setting(user['id'], key, value)
                    self._send_json({'success': True, 'message': 'Setting saved'})
                else:
                    self._send_error(400, 'Key required')
        
        # ===== BROADCAST =====
        
        elif path == '/api/broadcast':
            user = self._require_auth()
            if user:
                bot_id = int(body.get('bot_id', 0))
                message = body.get('message', '')
                chat_ids = body.get('chat_ids', [])
                bot = db.get_bot(bot_id)
                if bot and (bot['user_id'] == user['id'] or user['role'] == 'admin'):
                    result = bot_mgr.broadcast_message(bot_id, chat_ids, message)
                    self._send_json(result)
                else:
                    self._send_error(404, 'Bot not found')
        
        # ===== MARKETPLACE =====
        
        elif path == '/api/marketplace/add':
            user = self._require_auth()
            if user:
                result = db.add_marketplace_item(
                    seller_id=user['id'],
                    name=body.get('name', ''),
                    description=body.get('description', ''),
                    price=float(body.get('price', 0)),
                    type=body.get('type', 'bot'),
                    category=body.get('category', 'General')
                )
                self._send_json({'success': True, 'item_id': result})
        
        # ===== PLUGINS =====
        
        elif path == '/api/plugins/toggle':
            admin = self._require_admin()
            if admin:
                plugin_id = int(body.get('plugin_id', 0))
                is_enabled = body.get('is_enabled', 1)
                db.update_plugin(plugin_id, is_enabled=is_enabled)
                self._send_json({'success': True, 'message': 'Plugin toggled'})
        
        # ===== UPDATE BOT SETTINGS =====
        
        elif path == '/api/update-bot':
            user = self._require_auth()
            if user:
                bot_id = int(body.get('bot_id', 0))
                bot = db.get_bot(bot_id)
                if bot and (bot['user_id'] == user['id'] or user['role'] == 'admin'):
                    update_data = {}
                    for field in ['name', 'description', 'category', 'welcome_message',
                                  'welcome_enabled', 'force_subscribe_channel', 'force_subscribe_enabled',
                                  'auto_reply_enabled', 'anti_spam_enabled', 'anti_flood_enabled',
                                  'verification_enabled', 'referral_enabled', 'ticket_enabled',
                                  'ai_enabled', 'ai_model', 'ai_api_key', 'moderation_enabled',
                                  'broadcast_enabled']:
                        if field in body:
                            update_data[field] = body[field]
                    
                    if update_data:
                        db.update_bot(bot_id, **update_data)
                        analytics_mgr.track_event(user['id'], 'bot.update', bot_id=bot_id)
                        self._send_json({'success': True, 'message': 'Bot updated'})
                    else:
                        self._send_json({'success': True, 'message': 'No changes'})
                else:
                    self._send_error(404, 'Bot not found')
        
        # ===== ADMIN ROUTES =====
        
        elif path == '/api/admin/update-user':
            admin = self._require_admin()
            if admin:
                target_id = int(body.get('user_id', 0))
                update_data = {}
                for field in ['role', 'plan', 'is_active', 'is_verified', 'max_bots', 'max_commands']:
                    if field in body:
                        update_data[field] = body[field]
                if update_data:
                    db.update_user(target_id, **update_data)
                    security_mgr.log_security_event('user_updated', f"User {target_id} updated by admin {admin['id']}", self._get_client_ip())
                    self._send_json({'success': True, 'message': 'User updated'})
                else:
                    self._send_error(400, 'No fields to update')
        
        # ===== TELEGRAM WEBHOOK =====
        
        elif path.startswith('/webhook/'):
            # Handle incoming Telegram webhook updates
            bot_id = int(path.split('/')[-1])
            update = body
            # Process update (simplified - in production, route to proper bot handler)
            self._send_json({'ok': True})
        
        else:
            self._send_error(404, f'Route not found: {path}')
    
    def _handle_api_put(self, path, body):
        """Handle PUT API requests"""
        # Similar to POST for updates
        self._send_error(405, 'Method not allowed')
    
    def _handle_api_delete(self, path, body):
        """Handle DELETE API requests"""
        # Handled via POST with _method=DELETE or specific delete endpoints
        self._send_error(405, 'Method not allowed')

def run_server(host='0.0.0.0', port=8000):
    """Start the TG BOT HUB server"""
    server = HTTPServer((host, port), TGbotHubAPI)
    
    # Register default plugins
    try:
        plugins_data = [
            {'name': 'ai-chat', 'description': 'AI-powered chat commands', 'version': '1.0.0'},
            {'name': 'anti-spam', 'description': 'Spam protection system', 'version': '1.0.0'},
            {'name': 'auto-moderation', 'description': 'Automatic content moderation', 'version': '1.0.0'},
            {'name': 'verification', 'description': 'User verification system', 'version': '1.0.0'},
            {'name': 'analytics', 'description': 'Advanced analytics and reporting', 'version': '1.0.0'},
            {'name': 'broadcast', 'description': 'Broadcast messaging system', 'version': '1.0.0'},
            {'name': 'referral', 'description': 'Referral and rewards system', 'version': '1.0.0'},
            {'name': 'ticket', 'description': 'Support ticket system', 'version': '1.0.0'},
        ]
        for plugin in plugins_data:
            try:
                db.add_plugin(**plugin)
            except:
                pass
    except:
        pass
    
    # Create admin user if not exists
    try:
        admin = db.get_user_by_username('admin')
        if not admin:
            admin_id = auth.register('admin', 'admin@tgbothub.com', 'Admin123!', 'Administrator')
            if admin_id.get('success'):
                db.update_user(admin_id['user']['id'], role='admin', max_bots=999, max_commands=9999)
    except:
        pass
    
    print(f"""
╔══════════════════════════════════════════════╗
║           TG BOT HUB - Server Ready          ║
║══════════════════════════════════════════════║
║  🌐 http://{host}:{port}                      ║
║  📡 API: http://{host}:{port}/api/            ║
║  ⚡ Status: Running                           ║
║  🗄️  Database: SQLite                         ║
╚══════════════════════════════════════════════╝
    """)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        bot_mgr.stop_all_bots()
        server.server_close()
        print("✅ Server stopped")

if __name__ == '__main__':
    run_server()
