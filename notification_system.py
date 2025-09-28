"""
In-App Notification System for BlueCarbon MRV
Replaces SMTP email with modern browser notifications and real-time alerts
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any
from flask import session
import logging

logger = logging.getLogger(__name__)

class NotificationSystem:
    """Modern notification system using browser notifications and real-time updates"""
    
    def __init__(self):
        # In-memory storage for development (use Redis in production)
        self.notifications = {}  # user_id -> list of notifications
        self.subscribers = {}    # user_id -> WebSocket connections
    
    def send_notification(self, user_id: str, notification_data: Dict[str, Any]) -> bool:
        """Send notification to a specific user"""
        try:
            # Add timestamp and ID
            notification = {
                'id': f"notif_{int(time.time())}_{user_id}",
                'timestamp': datetime.now().isoformat(),
                'read': False,
                **notification_data
            }
            
            # Store notification
            if user_id not in self.notifications:
                self.notifications[user_id] = []
            
            self.notifications[user_id].append(notification)
            
            # Keep only last 50 notifications per user
            if len(self.notifications[user_id]) > 50:
                self.notifications[user_id] = self.notifications[user_id][-50:]
            
            # Send to WebSocket if user is online
            self._send_to_websocket(user_id, notification)
            
            logger.info(f"Notification sent to user {user_id}: {notification_data.get('title')}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False
    
    def send_project_approved_notification(self, user_id: str, project_name: str, credits_approved: int):
        """Send project approval notification"""
        return self.send_notification(user_id, {
            'type': 'project_approved',
            'title': '🎉 Project Approved!',
            'message': f'Your project "{project_name}" has been approved with {credits_approved} carbon credits.',
            'action_url': '/ngo/projects',
            'priority': 'high',
            'icon': '/static/icons/success.png'
        })
    
    def send_project_rejected_notification(self, user_id: str, project_name: str, reason: str):
        """Send project rejection notification"""
        return self.send_notification(user_id, {
            'type': 'project_rejected',
            'title': '❌ Project Needs Revision',
            'message': f'Your project "{project_name}" needs revision: {reason}',
            'action_url': '/ngo/projects',
            'priority': 'high',
            'icon': '/static/icons/warning.png'
        })
    
    def send_credits_purchased_notification(self, user_id: str, project_name: str, credits: int, buyer: str):
        """Send credits purchase notification to NGO"""
        return self.send_notification(user_id, {
            'type': 'credits_sold',
            'title': '💰 Credits Sold!',
            'message': f'{buyer} purchased {credits} credits from your project "{project_name}".',
            'action_url': '/ngo/revenue',
            'priority': 'medium',
            'icon': '/static/icons/money.png'
        })
    
    def send_system_alert(self, user_id: str, alert_type: str, message: str):
        """Send system alert notification"""
        return self.send_notification(user_id, {
            'type': 'system_alert',
            'title': f'🔔 System Alert: {alert_type}',
            'message': message,
            'priority': 'medium',
            'icon': '/static/icons/alert.png'
        })
    
    def send_blockchain_notification(self, user_id: str, transaction_type: str, details: Dict[str, Any]):
        """Send blockchain transaction notification"""
        icons = {
            'mint': '🪙',
            'transfer': '↔️', 
            'retire': '♻️'
        }
        
        return self.send_notification(user_id, {
            'type': 'blockchain_tx',
            'title': f'{icons.get(transaction_type, "⛓️")} Blockchain Transaction',
            'message': f'Transaction confirmed: {details.get("description", "Blockchain operation completed")}',
            'action_url': f'/blockchain/tx/{details.get("tx_hash")}',
            'priority': 'low',
            'icon': '/static/icons/blockchain.png'
        })
    
    def get_user_notifications(self, user_id: str, limit: int = 20, unread_only: bool = False) -> List[Dict[str, Any]]:
        """Get notifications for a user"""
        user_notifications = self.notifications.get(user_id, [])
        
        if unread_only:
            user_notifications = [n for n in user_notifications if not n.get('read', False)]
        
        # Sort by timestamp (newest first)
        user_notifications.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return user_notifications[:limit]
    
    def mark_notification_read(self, user_id: str, notification_id: str) -> bool:
        """Mark a notification as read"""
        try:
            user_notifications = self.notifications.get(user_id, [])
            for notification in user_notifications:
                if notification['id'] == notification_id:
                    notification['read'] = True
                    return True
            return False
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            return False
    
    def mark_all_read(self, user_id: str) -> bool:
        """Mark all notifications as read for a user"""
        try:
            user_notifications = self.notifications.get(user_id, [])
            for notification in user_notifications:
                notification['read'] = True
            return True
        except Exception as e:
            logger.error(f"Error marking all notifications as read: {e}")
            return False
    
    def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications"""
        user_notifications = self.notifications.get(user_id, [])
        return sum(1 for n in user_notifications if not n.get('read', False))
    
    def _send_to_websocket(self, user_id: str, notification: Dict[str, Any]):
        """Send notification via WebSocket if user is connected"""
        # This would integrate with Flask-SocketIO in a real implementation
        # For now, we'll store for real-time polling
        pass
    
    def broadcast_to_role(self, role: str, notification_data: Dict[str, Any]):
        """Broadcast notification to all users with a specific role"""
        # This would query the database for users with the role
        # For now, it's a placeholder for the feature
        logger.info(f"Broadcasting to role {role}: {notification_data.get('title')}")
    
    def cleanup_old_notifications(self, days_old: int = 30):
        """Clean up old notifications (run as periodic task)"""
        cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
        
        for user_id in self.notifications:
            self.notifications[user_id] = [
                n for n in self.notifications[user_id]
                if datetime.fromisoformat(n['timestamp']).timestamp() > cutoff_time
            ]

# Global notification system instance
notification_system = NotificationSystem()

# Flask route helpers
def send_success_notification(message: str, action_url: str = None):
    """Helper to send success notification to current user"""
    user_id = session.get('user_id')
    if user_id:
        return notification_system.send_notification(user_id, {
            'type': 'success',
            'title': '✅ Success',
            'message': message,
            'action_url': action_url,
            'priority': 'low',
            'icon': '/static/icons/success.png'
        })

def send_error_notification(message: str, action_url: str = None):
    """Helper to send error notification to current user"""
    user_id = session.get('user_id')
    if user_id:
        return notification_system.send_notification(user_id, {
            'type': 'error',
            'title': '❌ Error',
            'message': message,
            'action_url': action_url,
            'priority': 'high',
            'icon': '/static/icons/error.png'
        })

def send_info_notification(message: str, action_url: str = None):
    """Helper to send info notification to current user"""
    user_id = session.get('user_id')
    if user_id:
        return notification_system.send_notification(user_id, {
            'type': 'info',
            'title': 'ℹ️ Information',
            'message': message,
            'action_url': action_url,
            'priority': 'low',
            'icon': '/static/icons/info.png'
        })

if __name__ == "__main__":
    # Test the notification system
    ns = NotificationSystem()
    
    # Test sending notifications
    ns.send_project_approved_notification("user123", "Mangrove Restoration", 500)
    ns.send_credits_purchased_notification("user123", "Coastal Project", 100, "EcoTech Corp")
    
    # Test retrieving notifications
    notifications = ns.get_user_notifications("user123")
    print(f"User has {len(notifications)} notifications")
    
    unread_count = ns.get_unread_count("user123")
    print(f"Unread notifications: {unread_count}")
    
    print("\nNotification System Test Complete!")