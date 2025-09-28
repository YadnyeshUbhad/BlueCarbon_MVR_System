"""
Firebase Firestore Client for BlueCarbon MRV System
Provides real-time database operations with offline support
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FirebaseClient:
    """Firebase Firestore client wrapper for BlueCarbon operations"""
    
    def __init__(self):
        """Initialize Firebase client"""
        self.project_id = os.getenv('FIREBASE_PROJECT_ID')
        self.api_key = os.getenv('FIREBASE_API_KEY')
        
        if not self.project_id or not self.api_key:
            logger.warning("Firebase credentials not found, using mock mode")
            self.mock_mode = True
        else:
            try:
                # Try to import firebase_admin (install with: pip install firebase-admin)
                import firebase_admin
                from firebase_admin import credentials, firestore
                
                # Initialize Firebase (in production, use service account)
                if not firebase_admin._apps:
                    # For development, you can use project ID only
                    cred = credentials.ApplicationDefault()  # Uses GOOGLE_APPLICATION_CREDENTIALS
                    firebase_admin.initialize_app(cred, {
                        'projectId': self.project_id
                    })
                
                self.db = firestore.client()
                self.mock_mode = False
                logger.info("Firebase client initialized successfully")
                
            except ImportError:
                logger.warning("firebase-admin not installed, using mock mode")
                self.mock_mode = True
            except Exception as e:
                logger.error(f"Firebase initialization failed: {e}")
                self.mock_mode = True
    
    # User Management
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
        if self.mock_mode:
            return {"id": f"mock_user_{len(user_data)}", **user_data}
        
        try:
            doc_ref = self.db.collection('users').document()
            user_data['id'] = doc_ref.id
            user_data['created_at'] = datetime.now()
            user_data['updated_at'] = datetime.now()
            
            doc_ref.set(user_data)
            return user_data
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    def get_user_by_email(self, email: str, role: str = None) -> Optional[Dict[str, Any]]:
        """Get user by email and optionally role"""
        if self.mock_mode:
            return {
                'id': 'mock_user_1',
                'email': email,
                'role': role or 'admin',
                'name': 'Mock User',
                'created_at': datetime.now()
            }
        
        try:
            query = self.db.collection('users').where('email', '==', email)
            if role:
                query = query.where('role', '==', role)
            
            docs = query.limit(1).stream()
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None
    
    # Project Management
    def create_project(self, project_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new project"""
        if self.mock_mode:
            return {"id": f"mock_proj_{len(project_data)}", **project_data}
        
        try:
            # Use project ID as document ID for consistency
            project_id = project_data.get('id', self.db.collection('projects').document().id)
            project_data['id'] = project_id
            project_data['created_at'] = datetime.now()
            project_data['updated_at'] = datetime.now()
            
            doc_ref = self.db.collection('projects').document(project_id)
            doc_ref.set(project_data)
            return project_data
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return None
    
    def get_projects(self, filters: Dict[str, Any] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get projects with optional filters"""
        if self.mock_mode:
            # Return mock project data
            return [
                {
                    'id': 'PROJ1001',
                    'name': 'Sundarbans Mangrove Restoration',
                    'status': 'Verified',
                    'ngo_id': 'NGO2001',
                    'ecosystem': 'Mangrove',
                    'credits_requested': 500,
                    'credits_approved': 450,
                    'created_at': datetime.now()
                },
                {
                    'id': 'PROJ1002', 
                    'name': 'Chennai Coastal Forest Revival',
                    'status': 'Pending Review',
                    'ngo_id': 'NGO2002',
                    'ecosystem': 'Coastal Wetlands',
                    'credits_requested': 300,
                    'credits_approved': 0,
                    'created_at': datetime.now()
                }
            ]
        
        try:
            query = self.db.collection('projects')
            
            if filters:
                for key, value in filters.items():
                    query = query.where(key, '==', value)
            
            docs = query.limit(limit).stream()
            projects = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                projects.append(data)
            return projects
        except Exception as e:
            logger.error(f"Error getting projects: {e}")
            return []
    
    def update_project_status(self, project_id: str, status: str, notes: str = None) -> bool:
        """Update project status"""
        if self.mock_mode:
            logger.info(f"Mock: Updating project {project_id} status to {status}")
            return True
        
        try:
            update_data = {
                'status': status,
                'updated_at': datetime.now()
            }
            if notes:
                update_data['verification_notes'] = notes
            
            doc_ref = self.db.collection('projects').document(project_id)
            doc_ref.update(update_data)
            return True
        except Exception as e:
            logger.error(f"Error updating project status: {e}")
            return False
    
    # Transaction Management
    def create_transaction(self, transaction_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a transaction record"""
        if self.mock_mode:
            return {"id": f"mock_txn_{len(transaction_data)}", **transaction_data}
        
        try:
            doc_ref = self.db.collection('transactions').document()
            transaction_data['id'] = doc_ref.id
            transaction_data['created_at'] = datetime.now()
            transaction_data['updated_at'] = datetime.now()
            
            doc_ref.set(transaction_data)
            return transaction_data
        except Exception as e:
            logger.error(f"Error creating transaction: {e}")
            return None
    
    def get_transactions(self, filters: Dict[str, Any] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get transactions with optional filters"""
        if self.mock_mode:
            return [
                {
                    'id': 'TXN001',
                    'project_id': 'PROJ1001',
                    'buyer_id': 'IND3001',
                    'credits_sold': 100,
                    'price_per_credit': 250,
                    'total_value': 25000,
                    'status': 'Completed',
                    'created_at': datetime.now()
                }
            ]
        
        try:
            query = self.db.collection('transactions').order_by('created_at', direction='DESCENDING')
            
            if filters:
                for key, value in filters.items():
                    query = query.where(key, '==', value)
            
            docs = query.limit(limit).stream()
            transactions = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                transactions.append(data)
            return transactions
        except Exception as e:
            logger.error(f"Error getting transactions: {e}")
            return []
    
    # Real-time listeners
    def listen_to_projects(self, callback_func):
        """Setup real-time listener for project changes"""
        if self.mock_mode:
            logger.info("Mock: Project listener setup")
            return None
        
        try:
            def on_snapshot(docs, changes, read_time):
                for change in changes:
                    if change.type.name == 'ADDED':
                        callback_func('added', change.document.to_dict())
                    elif change.type.name == 'MODIFIED':
                        callback_func('modified', change.document.to_dict())
                    elif change.type.name == 'REMOVED':
                        callback_func('removed', change.document.to_dict())
            
            return self.db.collection('projects').on_snapshot(on_snapshot)
        except Exception as e:
            logger.error(f"Error setting up project listener: {e}")
            return None
    
    # Analytics
    def get_dashboard_stats(self, user_role: str, user_id: str = None) -> Dict[str, Any]:
        """Get dashboard statistics based on user role"""
        if self.mock_mode:
            if user_role == 'admin':
                return {
                    'total_projects': 25,
                    'verified_projects': 18,
                    'pending_projects': 7,
                    'total_credits_issued': 12500,
                    'total_revenue': 3125000,
                    'active_ngos': 10,
                    'active_industries': 15
                }
            elif user_role == 'ngo':
                return {
                    'projects_submitted': 5,
                    'projects_approved': 3,
                    'credits_earned': 1250,
                    'revenue_generated': 312500,
                    'pending_verifications': 2
                }
            elif user_role == 'industry':
                return {
                    'credits_purchased': 500,
                    'credits_retired': 300,
                    'carbon_footprint': 10000,
                    'offset_percentage': 30,
                    'total_spent': 125000
                }
        
        # Real implementation would query Firestore for actual stats
        try:
            if user_role == 'admin':
                projects = self.db.collection('projects').stream()
                total_projects = sum(1 for _ in projects)
                
                verified_projects = self.db.collection('projects').where('status', '==', 'Verified').stream()
                verified_count = sum(1 for _ in verified_projects)
                
                return {
                    'total_projects': total_projects,
                    'verified_projects': verified_count,
                    'pending_projects': total_projects - verified_count
                }
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
        
        return {}

# Global instance
firebase_client = FirebaseClient()

if __name__ == "__main__":
    print("Firebase Firestore Client for BlueCarbon MRV")
    print(f"Mock Mode: {firebase_client.mock_mode}")
    
    # Test connection
    if not firebase_client.mock_mode:
        test_data = firebase_client.get_projects(limit=1)
        print(f"Connection test: {len(test_data)} projects found")
    else:
        print("Setup Firebase credentials to enable real database connection")
        print("\nRequired environment variables:")
        print("FIREBASE_PROJECT_ID=your-project-id")
        print("FIREBASE_API_KEY=your-api-key")
        print("\nOr install firebase-admin: pip install firebase-admin")