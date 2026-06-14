"""
TG BOT HUB - Command Manager Module
Manage bot commands with advanced features
"""
import json
import re
from datetime import datetime
from database import Database

class CommandManager:
    def __init__(self):
        self.db = Database()
    
    def create_command(self, bot_id, user_id, command, response_type, response, 
                       category='General', description='', **kwargs):
        """Create a new command for a bot"""
        # Validate command format
        if not command.startswith('/'):
            command = '/' + command
        
        # Check if command already exists for this bot
        existing = self.db.get_bot_commands(bot_id)
        if any(c['command'].lower() == command.lower() for c in existing):
            return {'success': False, 'errors': [f"Command {command} already exists for this bot"]}
        
        # Validate response
        if not response:
            return {'success': False, 'errors': ['Response cannot be empty']}
        
        try:
            cmd_id = self.db.create_command(
                bot_id=bot_id,
                user_id=user_id,
                command=command,
                response_type=response_type,
                response=response,
                category=category,
                description=description
            )
            
            # Update additional fields
            if kwargs:
                self.db.update_command(cmd_id, **kwargs)
            
            self.db.add_audit_log(user_id, 'command.create', f"Command {command} created")
            
            return {
                'success': True,
                'command_id': cmd_id,
                'command': command
            }
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}
    
    def edit_command(self, command_id, user_id, **kwargs):
        """Edit an existing command"""
        cmd = self.db.get_command(command_id)
        if not cmd:
            return {'success': False, 'errors': ['Command not found']}
        
        # If command text is being changed, validate
        if 'command' in kwargs:
            new_cmd = kwargs['command']
            if not new_cmd.startswith('/'):
                kwargs['command'] = '/' + new_cmd
        
        try:
            self.db.update_command(command_id, **kwargs)
            self.db.add_audit_log(user_id, 'command.edit', f"Command {cmd['command']} updated")
            return {'success': True, 'message': 'Command updated'}
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}
    
    def delete_command(self, command_id, user_id):
        """Delete a command"""
        cmd = self.db.get_command(command_id)
        if not cmd:
            return {'success': False, 'errors': ['Command not found']}
        
        self.db.delete_command(command_id)
        self.db.add_audit_log(user_id, 'command.delete', f"Command {cmd['command']} deleted")
        return {'success': True, 'message': 'Command deleted'}
    
    def get_commands(self, bot_id):
        """Get all commands for a bot"""
        return self.db.get_bot_commands(bot_id)
    
    def toggle_command(self, command_id, user_id):
        """Toggle command enabled/disabled"""
        cmd = self.db.get_command(command_id)
        if not cmd:
            return {'success': False, 'errors': ['Command not found']}
        
        new_status = 0 if cmd['is_enabled'] else 1
        self.db.update_command(command_id, is_enabled=new_status)
        self.db.add_audit_log(user_id, 'command.toggle', 
                             f"Command {cmd['command']} {'enabled' if new_status else 'disabled'}")
        return {'success': True, 'is_enabled': new_status}
    
    def import_commands(self, bot_id, user_id, commands_json):
        """Import commands from JSON"""
        try:
            commands = json.loads(commands_json) if isinstance(commands_json, str) else commands_json
        except json.JSONDecodeError:
            return {'success': False, 'errors': ['Invalid JSON format']}
        
        results = {'imported': 0, 'failed': 0, 'errors': []}
        
        for cmd_data in commands:
            try:
                command = cmd_data.get('command', '').strip()
                response = cmd_data.get('response', '')
                response_type = cmd_data.get('response_type', 'text')
                
                if not command or not response:
                    results['failed'] += 1
                    results['errors'].append(f"Invalid command data: {cmd_data}")
                    continue
                
                result = self.create_command(
                    bot_id=bot_id,
                    user_id=user_id,
                    command=command,
                    response_type=response_type,
                    response=response,
                    category=cmd_data.get('category', 'General'),
                    description=cmd_data.get('description', '')
                )
                
                if result['success']:
                    results['imported'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"{command}: {result['errors']}")
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(str(e))
        
        return results
    
    def export_commands(self, bot_id):
        """Export commands as JSON"""
        commands = self.db.get_bot_commands(bot_id)
        export_data = []
        
        for cmd in commands:
            export_data.append({
                'command': cmd['command'],
                'response_type': cmd['response_type'],
                'response': cmd['response'],
                'category': cmd['category'],
                'description': cmd['description'],
                'is_enabled': cmd['is_enabled'],
                'is_welcome': cmd['is_welcome'],
                'is_auto_reply': cmd['is_auto_reply'],
                'inline_keyboard': cmd['inline_keyboard'],
                'reply_keyboard': cmd['reply_keyboard'],
                'variables': cmd['variables'],
                'media_url': cmd['media_url'],
                'cooldown': cmd['cooldown']
            })
        
        return export_data
    
    def get_categories(self, bot_id):
        """Get unique command categories for a bot"""
        commands = self.db.get_bot_commands(bot_id)
        categories = set()
        for cmd in commands:
            if cmd['category']:
                categories.add(cmd['category'])
        return sorted(list(categories))
    
    def process_command_response(self, cmd, message_data):
        """Process command response with variables"""
        response = cmd['response']
        from_user = message_data.get('from', {})
        chat = message_data.get('chat', {})
        
        replacements = {
            '{username}': from_user.get('username', 'User'),
            '{first_name}': from_user.get('first_name', ''),
            '{last_name}': from_user.get('last_name', ''),
            '{user_id}': str(from_user.get('id', '')),
            '{chat_id}': str(chat.get('id', '')),
            '{chat_title}': chat.get('title', ''),
            '{date}': datetime.now().strftime('%Y-%m-%d'),
            '{time}': datetime.now().strftime('%H:%M:%S'),
            '{datetime}': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        for var, val in replacements.items():
            response = response.replace(var, val)
        
        # Process custom variables from command
        if cmd['variables']:
            try:
                custom_vars = json.loads(cmd['variables'])
                for key, value in custom_vars.items():
                    response = response.replace(f'{{{key}}}', str(value))
            except:
                pass
        
        return response

command_manager = CommandManager()
