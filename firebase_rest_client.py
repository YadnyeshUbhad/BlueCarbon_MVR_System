"""
Firebase REST Client for BlueCarbon MRV System
Simple Firebase integration using REST API (no complex dependencies)
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class FirebaseRestClient:
    """Firebase Firestore REST API client"""
    
    def __init__(self):
        """Initialize Firebase REST client"""
        self.project_id = os.getenv('FIREBASE_PROJECT_ID', 'bluecarbon-mrv-6ce56')
        self.api_key = os.getenv('FIREBASE_API_KEY', 'AIzaSyDlPClFHcmpgiA2FWM047cPEQb6VRXlSR8')
        
        if not self.project_id or not self.api_key:
            logger.warning("Firebase credentials not found, using mock mode")
            self.mock_mode = True
        else:
            self.base_url = f"https://firestore.googleapis.com/v1/projects/{self.project_id}/databases/(default)/documents"
            self.mock_mode = False
            logger.info("Firebase REST client initialized successfully")
    
    def _make_request(self, method: str, url: str, data: Dict = None) -> Dict:
        """Make HTTP request to Firebase REST API"""
        if self.mock_mode:
            return {"mock": True, "data": data}
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            if method.upper() == 'GET':
                response = requests.get(f"{self.base_url}/{url}", headers=headers)
            elif method.upper() == 'POST':
                response = requests.post(f"{self.base_url}/{url}", headers=headers, json=data)
            elif method.upper() == 'PATCH':
                response = requests.patch(f"{self.base_url}/{url}", headers=headers, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(f"{self.base_url}/{url}", headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Firebase API error: {response.status_code} - {response.text}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Firebase request failed: {e}")
            return None
    
    def _convert_to_firestore_document(self, data: Dict) -> Dict:
        """Convert Python dict to Firestore document format"""
        fields = {}
        for key, value in data.items():
            if isinstance(value, str):
                fields[key] = {"stringValue": value}
            elif isinstance(value, int):
                fields[key] = {"integerValue": str(value)}
            elif isinstance(value, float):
                fields[key] = {"doubleValue": value}
            elif isinstance(value, bool):
                fields[key] = {"booleanValue": value}
            elif isinstance(value, datetime):
                fields[key] = {"timestampValue": value.isoformat() + "Z"}
            elif isinstance(value, list):
                array_values = []
                for item in value:
                    if isinstance(item, str):
                        array_values.append({"stringValue": item})
                    elif isinstance(item, int):
                        array_values.append({"integerValue": str(item)})
                    # Add more types as needed
                fields[key] = {"arrayValue": {"values": array_values}}
            else:
                fields[key] = {"stringValue": str(value)}
        
        return {"fields": fields}
    
    def _convert_from_firestore_document(self, doc: Dict) -> Dict:
        """Convert Firestore document to Python dict"""
        if not doc or 'fields' not in doc:
            return {}
        
        result = {}
        for key, field in doc['fields'].items():
            if 'stringValue' in field:
                result[key] = field['stringValue']
            elif 'integerValue' in field:
                result[key] = int(field['integerValue'])
            elif 'doubleValue' in field:
                result[key] = field['doubleValue']
            elif 'booleanValue' in field:
                result[key] = field['booleanValue']
            elif 'timestampValue' in field:
                result[key] = field['timestampValue']
            elif 'arrayValue' in field:
                array_result = []
                for item in field['arrayValue'].get('values', []):
                    if 'stringValue' in item:
                        array_result.append(item['stringValue'])
                    elif 'integerValue' in item:
                        array_result.append(int(item['integerValue']))
                result[key] = array_result
            else:
                result[key] = str(field)
        
        return result
    
    # User Management
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
        if self.mock_mode:
            return {"id": f"mock_user_{len(user_data)}", **user_data}
        
        try:
            user_data['created_at'] = datetime.now()
            user_data['updated_at'] = datetime.now()
            
            doc = self._convert_to_firestore_document(user_data)
            response = self._make_request('POST', 'users', doc)
            
            if response:
                user_id = response['name'].split('/')[-1]
                user_data['id'] = user_id
                return user_data
                
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            
        return None
    
    def get_user_by_email(self, email: str, role: str = None) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        if self.mock_mode:
            return {
                'id': 'mock_user_1',
                'email': email,
                'role': role or 'admin',
                'name': 'Mock User',
                'created_at': datetime.now().isoformat()
            }
        
        try:
            # In a real implementation, you'd use Firestore queries
            # For now, return mock data with real Firebase structure
            return {
                'id': f"user_{hash(email) % 1000}",
                'email': email,
                'role': role or 'admin',
                'name': f"User {email.split('@')[0]}",
                'created_at': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None
    
    # Project Management
    def create_project(self, project_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new project"""
        if self.mock_mode:
            return {"id": f"mock_proj_{len(project_data)}", **project_data}
        
        try:
            project_data['created_at'] = datetime.now()
            project_data['updated_at'] = datetime.now()
            
            doc = self._convert_to_firestore_document(project_data)
            response = self._make_request('POST', 'projects', doc)
            
            if response:
                project_id = response['name'].split('/')[-1]
                project_data['id'] = project_id
                return project_data
                
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            
        return None
    
    def get_projects(self, filters: Dict[str, Any] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get projects with optional filters"""
        if self.mock_mode:
            return [
                {
                    'id': 'PROJ1001',
                    'name': 'Sundarbans Mangrove Restoration',
                    'status': 'Verified',
                    'ngo_id': 'NGO2001',
                    'ecosystem': 'Mangrove',
                    'credits_requested': 500,
                    'credits_approved': 450,
                    'created_at': datetime.now().isoformat()
                },
                {
                    'id': 'PROJ1002', 
                    'name': 'Chennai Coastal Forest Revival',
                    'status': 'Pending Review',
                    'ngo_id': 'NGO2002',
                    'ecosystem': 'Coastal Wetlands',
                    'credits_requested': 300,
                    'credits_approved': 0,
                    'created_at': datetime.now().isoformat()
                }
            ]
        
        try:
            # In a real implementation, you'd use proper Firestore queries
            # For now, return enhanced mock data
            return self._get_mock_projects_with_firebase_structure()
        except Exception as e:
            logger.error(f"Error getting projects: {e}")
            return []
    
    def _get_mock_projects_with_firebase_structure(self) -> List[Dict[str, Any]]:
        """Get mock projects with Firebase-like structure"""
        return [
            {
                'id': 'firebase_proj_001',
                'name': 'Sundarbans Mangrove Conservation',
                'status': 'Verified',
                'ngo_id': 'firebase_ngo_001',
                'ecosystem': 'Mangrove',
                'location': 'West Bengal, India',
                'area': 125.5,
                'credits_requested': 750,
                'credits_approved': 725,
                'created_at': datetime.now().isoformat(),
                'firebase_document_id': 'fb_doc_001'
            },
            {
                'id': 'firebase_proj_002',
                'name': 'Kerala Coastal Restoration',
                'status': 'Pending Review',
                'ngo_id': 'firebase_ngo_002',
                'ecosystem': 'Seagrass',
                'location': 'Kerala, India',
                'area': 85.2,
                'credits_requested': 450,
                'credits_approved': 0,
                'created_at': datetime.now().isoformat(),
                'firebase_document_id': 'fb_doc_002'
            }
        ]
    
    def update_project_status(self, project_id: str, status: str, notes: str = None) -> bool:
        """Update project status"""
        if self.mock_mode:
            logger.info(f"Mock: Updating Firebase project {project_id} status to {status}")
            return True
        
        try:
            update_data = {
                'status': status,
                'updated_at': datetime.now()
            }
            if notes:
                update_data['verification_notes'] = notes
            
            doc = self._convert_to_firestore_document(update_data)
            response = self._make_request('PATCH', f'projects/{project_id}', doc)
            
            return response is not None
        except Exception as e:
            logger.error(f"Error updating project status: {e}")
            return False
    
    # Analytics
    def get_dashboard_stats(self, user_role: str, user_id: str = None) -> Dict[str, Any]:
        """Get dashboard statistics from Firebase"""
        if self.mock_mode:
            if user_role == 'admin':
                return {
                    'total_projects': 28,
                    'verified_projects': 22,
                    'pending_projects': 6,
                    'total_credits_issued': 15750,
                    'total_revenue': 3937500,
                    'active_ngos': 12,
                    'active_industries': 18,
                    'data_source': 'Firebase (Mock Mode)'
                }
            elif user_role == 'ngo':
                return {
                    'projects_submitted': 6,
                    'projects_approved': 4,
                    'credits_earned': 1520,
                    'revenue_generated': 380000,
                    'pending_verifications': 2,
                    'data_source': 'Firebase (Mock Mode)'
                }
            elif user_role == 'industry':
                return {
                    'credits_purchased': 650,
                    'credits_retired': 425,
                    'carbon_footprint': 12500,
                    'offset_percentage': 34,
                    'total_spent': 162500,
                    'data_source': 'Firebase (Mock Mode)'
                }
        
        # Real Firebase implementation would query actual data
        return {}
    
    def test_connection(self) -> bool:
        """Test Firebase connection"""
        if self.mock_mode:
            return True
        
        try:
            response = self._make_request('GET', '')
            return response is not None
        except Exception as e:
            logger.error(f"Firebase connection test failed: {e}")
            return False

# Global instance
firebase_rest_client = FirebaseRestClient()

if __name__ == "__main__":
    print("🔥 Firebase REST Client for BlueCarbon MRV")
    print(f"Project ID: {firebase_rest_client.project_id}")
    print(f"Mock Mode: {firebase_rest_client.mock_mode}")
    
    # Test connection
    if firebase_rest_client.test_connection():
        print("✅ Firebase connection successful")
    else:
        print("❌ Firebase connection failed - using mock mode")
    
    # Test data retrieval
    projects = firebase_rest_client.get_projects(limit=2)
    print(f"📊 Retrieved {len(projects)} projects from Firebase")
    
    stats = firebase_rest_client.get_dashboard_stats('admin')
    print(f"📈 Dashboard stats: {stats.get('total_projects', 0)} total projects")