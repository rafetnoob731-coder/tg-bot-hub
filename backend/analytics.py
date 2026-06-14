"""
TG BOT HUB - Analytics Module
Comprehensive analytics and reporting with chart data generation
"""
import json
from datetime import datetime, timedelta, date
from database import Database

class Analytics:
    def __init__(self):
        self.db = Database()
    
    def track_event(self, user_id, event_type, event_data='', bot_id=None, ip_address=''):
        """Track an analytics event"""
        return self.db.add_analytics(user_id, event_type, event_data, bot_id, ip_address)
    
    def get_dashboard_stats(self, user_id=None):
        """Get comprehensive dashboard statistics"""
        stats = self.db.get_dashboard_stats(user_id)
        
        # Add bot-specific stats
        if user_id:
            stats['bots'] = self._get_bot_stats(user_id)
        
        # Add growth trends
        stats['growth'] = self._get_growth_trends(user_id)
        
        # Add activity data
        stats['activity'] = self._get_activity_data(user_id)
        
        return stats
    
    def _get_bot_stats(self, user_id=None):
        """Get bot-specific statistics"""
        cursor = self.db.conn.cursor()
        
        if user_id:
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'running' THEN 1 ELSE 0 END) as active,
                    SUM(CASE WHEN status = 'stopped' THEN 1 ELSE 0 END) as stopped,
                    SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error
                FROM bots WHERE user_id = ? AND is_active = 1
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'running' THEN 1 ELSE 0 END) as active,
                    SUM(CASE WHEN status = 'stopped' THEN 1 ELSE 0 END) as stopped,
                    SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error
                FROM bots WHERE is_active = 1
            ''')
        
        return dict(cursor.fetchone())
    
    def _get_growth_trends(self, user_id=None, days=30):
        """Get growth trends over time"""
        cursor = self.db.conn.cursor()
        
        # User growth
        if user_id:
            cursor.execute('''
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM users WHERE created_at >= DATE('now', ? || ' days')
                GROUP BY DATE(created_at) ORDER BY date
            ''', (f'-{days}',))
            user_growth = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute('''
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM bots WHERE user_id = ? AND created_at >= DATE('now', ? || ' days')
                GROUP BY DATE(created_at) ORDER BY date
            ''', (user_id, f'-{days}'))
            bot_growth = [dict(row) for row in cursor.fetchall()]
        else:
            cursor.execute('''
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM users WHERE created_at >= DATE('now', ? || ' days')
                GROUP BY DATE(created_at) ORDER BY date
            ''', (f'-{days}',))
            user_growth = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute('''
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM bots WHERE created_at >= DATE('now', ? || ' days')
                GROUP BY DATE(created_at) ORDER BY date
            ''', (f'-{days}',))
            bot_growth = [dict(row) for row in cursor.fetchall()]
        
        # Fill in missing dates
        all_dates = [(date.today() - timedelta(days=i)).isoformat() for i in range(days - 1, -1, -1)]
        
        user_map = {r['date']: r['count'] for r in user_growth}
        bot_map = {r['date']: r['count'] for r in bot_growth}
        
        user_trend = []
        bot_trend = []
        cumulative_users = 0
        cumulative_bots = 0
        
        for d in all_dates:
            cumulative_users += user_map.get(d, 0)
            cumulative_bots += bot_map.get(d, 0)
            user_trend.append({'date': d, 'new': user_map.get(d, 0), 'total': cumulative_users})
            bot_trend.append({'date': d, 'new': bot_map.get(d, 0), 'total': cumulative_bots})
        
        return {
            'users': user_trend,
            'bots': bot_trend,
            'total_users': cumulative_users,
            'total_bots': cumulative_bots
        }
    
    def _get_activity_data(self, user_id=None, days=7):
        """Get activity data for charts"""
        cursor = self.db.conn.cursor()
        
        if user_id:
            cursor.execute('''
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM analytics 
                WHERE user_id = ? AND created_at >= DATE('now', ? || ' days')
                GROUP BY DATE(created_at) ORDER BY date
            ''', (user_id, f'-{days}'))
        else:
            cursor.execute('''
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM analytics 
                WHERE created_at >= DATE('now', ? || ' days')
                GROUP BY DATE(created_at) ORDER BY date
            ''', (f'-{days}',))
        
        rows = cursor.fetchall()
        
        # Fill in missing dates
        all_dates = [(date.today() - timedelta(days=i)).isoformat() for i in range(days - 1, -1, -1)]
        data_map = {r['date']: r['count'] for r in rows}
        
        activity = []
        for d in all_dates:
            activity.append({'date': d, 'count': data_map.get(d, 0)})
        
        return activity
    
    def get_command_usage_stats(self, user_id=None, days=30):
        """Get command usage statistics"""
        cursor = self.db.conn.cursor()
        
        if user_id:
            cursor.execute('''
                SELECT c.command, SUM(c.usage_count) as total_usage, COUNT(DISTINCT c.bot_id) as bot_count
                FROM commands c
                JOIN bots b ON c.bot_id = b.id
                WHERE b.user_id = ? AND c.created_at >= DATE('now', ? || ' days')
                GROUP BY c.command
                ORDER BY total_usage DESC
                LIMIT 20
            ''', (user_id, f'-{days}'))
        else:
            cursor.execute('''
                SELECT c.command, SUM(c.usage_count) as total_usage, COUNT(DISTINCT c.bot_id) as bot_count
                FROM commands c
                WHERE c.created_at >= DATE('now', ? || ' days')
                GROUP BY c.command
                ORDER BY total_usage DESC
                LIMIT 20
            ''', (f'-{days}',))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_user_engagement(self, user_id=None, days=30):
        """Get user engagement metrics"""
        cursor = self.db.conn.cursor()
        
        if user_id:
            # Bot uptime
            cursor.execute('''
                SELECT status, COUNT(*) as count
                FROM bots WHERE user_id = ?
                GROUP BY status
            ''', (user_id,))
            status_dist = [dict(row) for row in cursor.fetchall()]
            
            # Commands per bot
            cursor.execute('''
                SELECT b.name, COUNT(c.id) as command_count
                FROM bots b
                LEFT JOIN commands c ON c.bot_id = b.id
                WHERE b.user_id = ?
                GROUP BY b.id
            ''', (user_id,))
            commands_per_bot = [dict(row) for row in cursor.fetchall()]
        else:
            cursor.execute('''
                SELECT status, COUNT(*) as count
                FROM bots
                GROUP BY status
            ''')
            status_dist = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute('''
                SELECT b.name, u.username as owner, COUNT(c.id) as command_count
                FROM bots b
                LEFT JOIN commands c ON c.bot_id = b.id
                JOIN users u ON b.user_id = u.id
                GROUP BY b.id
                ORDER BY command_count DESC
                LIMIT 20
            ''')
            commands_per_bot = [dict(row) for row in cursor.fetchall()]
        
        return {
            'status_distribution': status_dist,
            'commands_per_bot': commands_per_bot
        }
    
    def get_traffic_analytics(self, days=7):
        """Get traffic analytics (page views, API calls etc)"""
        cursor = self.db.conn.cursor()
        
        # API calls per day
        cursor.execute('''
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM analytics
            WHERE event_type LIKE 'api.%' AND created_at >= DATE('now', ? || ' days')
            GROUP BY DATE(created_at) ORDER BY date
        ''', (f'-{days}',))
        
        api_calls = [dict(row) for row in cursor.fetchall()]
        
        # Event types distribution
        cursor.execute('''
            SELECT event_type, COUNT(*) as count
            FROM analytics
            WHERE created_at >= DATE('now', ? || ' days')
            GROUP BY event_type ORDER BY count DESC
        ''', (f'-{days}',))
        
        event_dist = [dict(row) for row in cursor.fetchall()]
        
        return {
            'api_calls': api_calls,
            'event_distribution': event_dist
        }
    
    def get_conversion_analytics(self):
        """Get conversion metrics (user registrations to active bots)"""
        cursor = self.db.conn.cursor()
        
        # Users with bots vs without
        cursor.execute('''
            SELECT 
                COUNT(DISTINCT u.id) as total_users,
                COUNT(DISTINCT CASE WHEN b.id IS NOT NULL THEN u.id END) as users_with_bots,
                COUNT(DISTINCT CASE WHEN b.id IS NULL THEN u.id END) as users_without_bots
            FROM users u
            LEFT JOIN bots b ON b.user_id = u.id AND b.is_active = 1
        ''')
        conversion = dict(cursor.fetchone())
        
        # Average bots per user
        cursor.execute('''
            SELECT AVG(bot_count) as avg_bots
            FROM (
                SELECT COUNT(*) as bot_count
                FROM bots
                WHERE is_active = 1
                GROUP BY user_id
            )
        ''')
        avg = cursor.fetchone()
        conversion['avg_bots_per_user'] = round(avg['avg_bots'], 2) if avg and avg['avg_bots'] else 0
        
        return conversion
    
    def generate_report(self, user_id=None, report_type='full'):
        """Generate a comprehensive analytics report"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'type': report_type
        }
        
        if report_type in ('full', 'overview'):
            report['dashboard'] = self.get_dashboard_stats(user_id)
        
        if report_type in ('full', 'commands'):
            report['command_usage'] = self.get_command_usage_stats(user_id)
        
        if report_type in ('full', 'engagement'):
            report['engagement'] = self.get_user_engagement(user_id)
        
        if report_type in ('full', 'traffic'):
            report['traffic'] = self.get_traffic_analytics()
        
        if report_type in ('full', 'conversion'):
            report['conversion'] = self.get_conversion_analytics()
        
        return report

analytics = Analytics()
