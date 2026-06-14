"""
TG BOT HUB - Bot Manager Module
Telegram Bot API integration with full lifecycle management
"""
import requests
import json
import threading
import time
from datetime import datetime
from database import Database

TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"

class BotManager:
    def __init__(self):
        self.db = Database()
        self.active_bots = {}  # bot_id -> (thread, stop_event)
        self.bot_instances = {}  # bot_id -> BotInstance
    
    def verify_token(self, token):
        """Verify Telegram Bot token by calling getMe API"""
        try:
            url = TELEGRAM_API.format(token=token, method="getMe")
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get('ok'):
                bot_info = data['result']
                return {
                    'valid': True,
                    'id': bot_info['id'],
                    'username': bot_info['username'],
                    'first_name': bot_info.get('first_name', ''),
                    'can_join_groups': bot_info.get('can_join_groups', False),
                    'can_read_all_group_messages': bot_info.get('can_read_all_group_messages', False),
                    'supports_inline_queries': bot_info.get('supports_inline_queries', False)
                }
            return {'valid': False, 'error': data.get('description', 'Invalid token')}
        except requests.exceptions.RequestException as e:
            return {'valid': False, 'error': str(e)}
    
    def add_bot(self, user_id, name, token, description=''):
        """Add a new bot after verification"""
        # Verify token first
        verification = self.verify_token(token)
        if not verification['valid']:
            return {'success': False, 'errors': [verification.get('error', 'Invalid bot token')]}
        
        # Create bot in database
        try:
            bot_id = self.db.create_bot(
                user_id=user_id,
                name=name,
                token=token,
                username=verification['username'],
                description=description
            )
            
            self.db.add_audit_log(user_id, 'bot.add', f"Bot '{name}' added successfully")
            self.db.add_log(bot_id, 'info', f"Bot '{name}' initialized and connected to Telegram")
            
            return {
                'success': True,
                'bot_id': bot_id,
                'bot': {
                    'id': bot_id,
                    'name': name,
                    'token': token[:10] + '...' + token[-5:],  # Masked
                    'username': verification['username'],
                    'status': 'stopped'
                }
            }
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}
    
    def start_bot(self, bot_id, user_id=None):
        """Start a bot's polling mechanism"""
        bot = self.db.get_bot(bot_id)
        if not bot:
            return {'success': False, 'errors': ['Bot not found']}
        
        if bot_id in self.active_bots and self.active_bots[bot_id][1].is_set() == False:
            return {'success': False, 'errors': ['Bot is already running']}
        
        # Create and start bot thread
        stop_event = threading.Event()
        bot_thread = threading.Thread(
            target=self._run_bot_polling,
            args=(bot, stop_event),
            daemon=True
        )
        bot_thread.start()
        
        self.active_bots[bot_id] = (bot_thread, stop_event)
        
        # Update status
        self.db.update_bot(bot_id, status='running')
        self.db.add_log(bot_id, 'info', 'Bot started successfully')
        if user_id:
            self.db.add_audit_log(user_id, 'bot.start', f"Bot '{bot['name']}' started")
        
        return {'success': True, 'message': 'Bot started'}
    
    def stop_bot(self, bot_id, user_id=None):
        """Stop a running bot"""
        if bot_id in self.active_bots:
            thread, stop_event = self.active_bots[bot_id]
            stop_event.set()
            thread.join(timeout=5)
            del self.active_bots[bot_id]
        
        self.db.update_bot(bot_id, status='stopped')
        self.db.add_log(bot_id, 'info', 'Bot stopped')
        if user_id:
            self.db.add_audit_log(user_id, 'bot.stop', f"Bot '{self.db.get_bot(bot_id)['name']}' stopped")
        
        return {'success': True, 'message': 'Bot stopped'}
    
    def restart_bot(self, bot_id, user_id=None):
        """Restart a bot"""
        self.stop_bot(bot_id, user_id)
        time.sleep(1)
        return self.start_bot(bot_id, user_id)
    
    def delete_bot(self, bot_id, user_id=None):
        """Delete a bot and all its data"""
        bot = self.db.get_bot(bot_id)
        if not bot:
            return {'success': False, 'errors': ['Bot not found']}
        
        # Stop if running
        self.stop_bot(bot_id)
        
        # Delete from database
        self.db.delete_bot(bot_id)
        
        if user_id:
            self.db.add_audit_log(user_id, 'bot.delete', f"Bot '{bot['name']}' deleted")
        
        return {'success': True, 'message': 'Bot deleted'}
    
    def get_bot_info(self, token):
        """Get bot information from Telegram API"""
        try:
            url = TELEGRAM_API.format(token=token, method="getMe")
            response = requests.get(url, timeout=10)
            return response.json()
        except:
            return {'ok': False}
    
    def set_webhook(self, bot_id, webhook_url):
        """Set webhook for a bot"""
        bot = self.db.get_bot(bot_id)
        if not bot:
            return {'success': False, 'errors': ['Bot not found']}
        
        try:
            url = TELEGRAM_API.format(token=bot['token'], method="setWebhook")
            response = requests.post(url, json={'url': webhook_url}, timeout=10)
            data = response.json()
            
            if data.get('ok'):
                self.db.update_bot(bot_id, webhook_url=webhook_url, webhook_enabled=1)
                self.db.add_log(bot_id, 'info', f"Webhook set to {webhook_url}")
                return {'success': True, 'message': 'Webhook set'}
            return {'success': False, 'errors': [data.get('description', 'Failed to set webhook')]}
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}
    
    def delete_webhook(self, bot_id):
        """Delete webhook for a bot"""
        bot = self.db.get_bot(bot_id)
        if not bot:
            return {'success': False, 'errors': ['Bot not found']}
        
        try:
            url = TELEGRAM_API.format(token=bot['token'], method="deleteWebhook")
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get('ok'):
                self.db.update_bot(bot_id, webhook_url='', webhook_enabled=0)
                self.db.add_log(bot_id, 'info', 'Webhook deleted')
                return {'success': True, 'message': 'Webhook deleted'}
            return {'success': False, 'errors': [data.get('description', 'Failed to delete webhook')]}
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}
    
    def health_check(self, bot_id):
        """Check if bot is responding"""
        bot = self.db.get_bot(bot_id)
        if not bot:
            return {'status': 'error', 'message': 'Bot not found'}
        
        try:
            url = TELEGRAM_API.format(token=bot['token'], method="getMe")
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return {'status': 'online', 'message': 'Bot is responding'}
            return {'status': 'error', 'message': f'HTTP {response.status_code}'}
        except requests.exceptions.RequestException as e:
            return {'status': 'offline', 'message': str(e)}
    
    def _run_bot_polling(self, bot, stop_event):
        """Internal method to run bot polling in a thread"""
        token = bot['token']
        offset = 0
        
        self.db.add_log(bot['id'], 'info', 'Bot polling started')
        
        while not stop_event.is_set():
            try:
                # Get updates
                url = TELEGRAM_API.format(token=token, method="getUpdates")
                response = requests.get(
                    url,
                    params={
                        'offset': offset,
                        'timeout': 30,
                        'allowed_updates': json.dumps([
                            'message', 'callback_query', 'inline_query',
                            'chosen_inline_result', 'channel_post'
                        ])
                    },
                    timeout=35
                )
                
                if response.status_code != 200:
                    time.sleep(5)
                    continue
                
                data = response.json()
                if not data.get('ok'):
                    time.sleep(5)
                    continue
                
                for update in data.get('result', []):
                    offset = update['update_id'] + 1
                    self._process_update(bot, update)
                    
            except requests.exceptions.Timeout:
                continue
            except requests.exceptions.ConnectionError:
                self.db.add_log(bot['id'], 'error', 'Connection lost, retrying in 10s')
                time.sleep(10)
            except Exception as e:
                self.db.add_log(bot['id'], 'error', f'Polling error: {str(e)}')
                time.sleep(5)
        
        self.db.add_log(bot['id'], 'info', 'Bot polling stopped')
    
    def _process_update(self, bot, update):
        """Process a Telegram update"""
        try:
            # Get commands for this bot
            commands = self.db.get_bot_commands(bot['id'])
            commands_dict = {cmd['command'].lower(): dict(cmd) for cmd in commands if cmd['is_enabled']}
            
            # Handle message
            if 'message' in update:
                message = update['message']
                chat_id = message['chat']['id']
                text = message.get('text', '')
                
                # Process command
                if text and text.startswith('/'):
                    cmd_parts = text.split()
                    cmd_name = cmd_parts[0].lower()
                    
                    if cmd_name in commands_dict:
                        cmd = commands_dict[cmd_name]
                        self._execute_command(bot, chat_id, cmd, cmd_parts[1:], message)
                        self.db.update_command(cmd['id'], usage_count=cmd['usage_count'] + 1)
                
                # Process auto-reply if enabled
                elif bot['auto_reply_enabled']:
                    for cmd_name, cmd in commands_dict.items():
                        if cmd['is_auto_reply'] and cmd_name[1:] in text.lower():
                            self._execute_command(bot, chat_id, cmd, [], message)
                
                # Handle welcome message for new members
                if 'new_chat_members' in message:
                    if bot['welcome_enabled'] and bot['welcome_message']:
                        self._send_message(bot['token'], chat_id, bot['welcome_message'])
            
            # Handle callback queries (inline keyboard)
            if 'callback_query' in update:
                callback = update['callback_query']
                chat_id = callback['message']['chat']['id']
                data = callback.get('data', '')
                
                # Process callback data
                self._send_message(bot['token'], chat_id, f"Callback received: {data}")
                
                # Answer callback query
                url = TELEGRAM_API.format(token=bot['token'], method="answerCallbackQuery")
                requests.post(url, json={
                    'callback_query_id': callback['id'],
                    'text': 'Processed!'
                }, timeout=5)
            
            # Track analytics
            self.db.add_analytics(
                user_id=bot['user_id'],
                bot_id=bot['id'],
                event_type='bot.update',
                event_data=json.dumps({'type': list(update.keys())[1] if len(update) > 1 else 'unknown'})
            )
            
        except Exception as e:
            self.db.add_log(bot['id'], 'error', f'Update processing error: {str(e)}')
    
    def _execute_command(self, bot, chat_id, cmd, args, message):
        """Execute a bot command"""
        try:
            response_text = cmd['response']
            
            # Process variables
            variables = {}
            if cmd['variables']:
                try:
                    variables = json.loads(cmd['variables'])
                except:
                    variables = {}
            
            # Replace variables in response
            response_text = response_text.replace('{username}', message.get('from', {}).get('username', 'User'))
            response_text = response_text.replace('{first_name}', message.get('from', {}).get('first_name', ''))
            response_text = response_text.replace('{last_name}', message.get('from', {}).get('last_name', ''))
            response_text = response_text.replace('{user_id}', str(message.get('from', {}).get('id', '')))
            response_text = response_text.replace('{chat_id}', str(chat_id))
            response_text = response_text.replace('{args}', ' '.join(args))
            response_text = response_text.replace('{date}', datetime.now().strftime('%Y-%m-%d'))
            response_text = response_text.replace('{time}', datetime.now().strftime('%H:%M:%S'))
            
            # Build inline keyboard if configured
            reply_markup = None
            if cmd['inline_keyboard']:
                try:
                    keyboard_data = json.loads(cmd['inline_keyboard'])
                    reply_markup = json.dumps({'inline_keyboard': keyboard_data})
                except:
                    pass
            
            # Build reply keyboard if configured
            if cmd['reply_keyboard'] and not reply_markup:
                try:
                    keyboard_data = json.loads(cmd['reply_keyboard'])
                    reply_markup = json.dumps({'keyboard': keyboard_data, 'resize_keyboard': True})
                except:
                    pass
            
            # Send based on response type
            response_type = cmd['response_type']
            
            if response_type == 'text':
                self._send_message(bot['token'], chat_id, response_text, reply_markup)
            elif response_type == 'photo' and cmd['media_url']:
                self._send_photo(bot['token'], chat_id, cmd['media_url'], response_text, reply_markup)
            elif response_type == 'video' and cmd['media_url']:
                self._send_video(bot['token'], chat_id, cmd['media_url'], response_text, reply_markup)
            elif response_type == 'audio' and cmd['media_url']:
                self._send_audio(bot['token'], chat_id, cmd['media_url'], response_text, reply_markup)
            elif response_type == 'document' and cmd['media_url']:
                self._send_document(bot['token'], chat_id, cmd['media_url'], response_text, reply_markup)
            else:
                self._send_message(bot['token'], chat_id, response_text, reply_markup)
            
            self.db.add_log(bot['id'], 'info', f"Command /{cmd['command']} executed in chat {chat_id}")
            
        except Exception as e:
            self.db.add_log(bot['id'], 'error', f"Command execution error: {str(e)}")
    
    def _send_message(self, token, chat_id, text, reply_markup=None):
        """Send a message via Telegram API"""
        url = TELEGRAM_API.format(token=token, method="sendMessage")
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        if reply_markup:
            payload['reply_markup'] = reply_markup
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.json()
        except:
            return None
    
    def _send_photo(self, token, chat_id, photo_url, caption='', reply_markup=None):
        """Send a photo via Telegram API"""
        url = TELEGRAM_API.format(token=token, method="sendPhoto")
        payload = {
            'chat_id': chat_id,
            'photo': photo_url,
            'caption': caption,
            'parse_mode': 'HTML'
        }
        if reply_markup:
            payload['reply_markup'] = reply_markup
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.json()
        except:
            return None
    
    def _send_video(self, token, chat_id, video_url, caption='', reply_markup=None):
        """Send a video via Telegram API"""
        url = TELEGRAM_API.format(token=token, method="sendVideo")
        payload = {
            'chat_id': chat_id,
            'video': video_url,
            'caption': caption,
            'parse_mode': 'HTML'
        }
        if reply_markup:
            payload['reply_markup'] = reply_markup
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            return response.json()
        except:
            return None
    
    def _send_audio(self, token, chat_id, audio_url, caption='', reply_markup=None):
        """Send audio via Telegram API"""
        url = TELEGRAM_API.format(token=token, method="sendAudio")
        payload = {
            'chat_id': chat_id,
            'audio': audio_url,
            'caption': caption,
            'parse_mode': 'HTML'
        }
        if reply_markup:
            payload['reply_markup'] = reply_markup
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            return response.json()
        except:
            return None
    
    def _send_document(self, token, chat_id, document_url, caption='', reply_markup=None):
        """Send a document via Telegram API"""
        url = TELEGRAM_API.format(token=token, method="sendDocument")
        payload = {
            'chat_id': chat_id,
            'document': document_url,
            'caption': caption,
            'parse_mode': 'HTML'
        }
        if reply_markup:
            payload['reply_markup'] = reply_markup
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            return response.json()
        except:
            return None
    
    def broadcast_message(self, bot_id, chat_ids, message):
        """Broadcast a message to multiple chats"""
        bot = self.db.get_bot(bot_id)
        if not bot:
            return {'success': False, 'errors': ['Bot not found']}
        
        results = {'success': 0, 'failed': 0, 'errors': []}
        
        for chat_id in chat_ids:
            try:
                result = self._send_message(bot['token'], chat_id, message)
                if result and result.get('ok'):
                    results['success'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Chat {chat_id}: {result.get('description', 'Unknown error')}")
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Chat {chat_id}: {str(e)}")
        
        # Broadcast via Telegram directly if we have a channel/group
        if len(chat_ids) == 1 and str(chat_ids[0]).startswith('-'):
            try:
                url = TELEGRAM_API.format(token=bot['token'], method="sendMessage")
                response = requests.post(url, json={
                    'chat_id': chat_ids[0],
                    'text': message,
                    'parse_mode': 'HTML'
                }, timeout=10)
                if response.json().get('ok'):
                    results['success'] += 1
            except:
                pass
        
        self.db.add_log(bot['id'], 'info', f"Broadcast completed: {results['success']} sent, {results['failed']} failed")
        return results
    
    def get_chat_info(self, bot_token, chat_id):
        """Get chat information"""
        try:
            url = TELEGRAM_API.format(token=bot_token, method="getChat")
            response = requests.get(url, params={'chat_id': chat_id}, timeout=10)
            return response.json()
        except:
            return {'ok': False}
    
    def get_updates_count(self, bot_id):
        """Get approximate updates count from bot health"""
        bot = self.db.get_bot(bot_id)
        if not bot:
            return 0
        return self.db.get_command_count(bot_id)
    
    def stop_all_bots(self):
        """Stop all running bots (used during shutdown)"""
        for bot_id in list(self.active_bots.keys()):
            self.stop_bot(bot_id)
    
    def get_bot_activity_summary(self, bot_id):
        """Get activity summary for a bot"""
        logs = self.db.get_bot_logs(bot_id, 1, 100)
        commands = self.db.get_bot_commands(bot_id)
        
        total_usage = sum(cmd['usage_count'] for cmd in commands) if commands else 0
        
        return {
            'total_logs': len(logs),
            'total_commands': len(commands),
            'total_command_usage': total_usage,
            'errors': len([l for l in logs if l['level'] == 'error']),
            'status': self.db.get_bot(bot_id)['status'] if self.db.get_bot(bot_id) else 'unknown'
        }

# Global bot manager instance
bot_manager = BotManager()
