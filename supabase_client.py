"""
Supabase Client Integration for BlueCarbon MRV System
Provides database operations and real-time capabilities
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
import logging

# Try to import supabase, fallback to mock if not available
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    # Mock classes for when supabase is not available
    class Client:
        pass
    def create_client(*args, **kwargs):
        return None

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseClient:
    """Supabase client wrapper for BlueCarbon operations"""
    
    def __init__(self):
        """Initialize Supabase client"""
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_KEY')
        self.service_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not SUPABASE_AVAILABLE or not self.url or not self.key:
            logger.warning("Supabase not available or credentials not found, using mock mode")
            self.client = None
            self.mock_mode = True
        else:
            try:
                self.client: Client = create_client(self.url, self.key)
                self.mock_mode = False
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Supabase client: {e}, using mock mode")
                self.client = None
                self.mock_mode = True
    
    # User Management
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
        if self.mock_mode:
            return {"id": f"mock_user_{len(user_data)}", **user_data}
        
        try:
            result = self.client.table('users').insert(user_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    def get_user_by_email(self, email: str, role: str = None) -> Optional[Dict[str, Any]]:
        """Get user by email and optionally role"""
        if self.mock_mode:
            # Return mock user data
            return {
                'id': 'mock_user_1',
                'email': email,
                'role': role or 'admin',
                'name': 'Mock User',
                'created_at': datetime.now().isoformat()
            }
        
        try:
            query = self.client.table('users').select('*').eq('email', email)
            if role:
                query = query.eq('role', role)
            
            result = query.execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None
    
    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user information"""
        if self.mock_mode:
            logger.info(f"Mock: Updating user {user_id} with {update_data}")
            return True
        
        try:
            result = self.client.table('users').update(update_data).eq('id', user_id).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return False
    
    # Project Management
    def create_project(self, project_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new project"""
        if self.mock_mode:
            return {"id": f"mock_proj_{len(project_data)}", **project_data}
        
        try:
            # Add timestamps
            project_data['created_at'] = datetime.now().isoformat()
            project_data['updated_at'] = datetime.now().isoformat()
            
            result = self.client.table('projects').insert(project_data).execute()
            return result.data[0] if result.data else None
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
            query = self.client.table('projects').select('*')
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            result = query.limit(limit).execute()
            return result.data
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
                'updated_at': datetime.now().isoformat()
            }
            if notes:
                update_data['verification_notes'] = notes
            
            result = self.client.table('projects').update(update_data).eq('id', project_id).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error updating project status: {e}")
            return False
    
    # Token Management
    def create_token(self, token_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a blockchain token record"""
        if self.mock_mode:
            return {"id": f"mock_token_{len(token_data)}", **token_data}
        
        try:
            token_data['created_at'] = datetime.now().isoformat()
            result = self.client.table('tokens').insert(token_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error creating token: {e}")
            return None
    
    def get_tokens(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get tokens with optional filters"""
        if self.mock_mode:
            return [
                {
                    'id': 'TOKEN001',
                    'project_id': 'PROJ1001',
                    'token_id': 'BC123456',
                    'credits_amount': 450,
                    'owner_address': '0x1234567890abcdef',
                    'status': 'active',
                    'created_at': datetime.now().isoformat()
                }
            ]
        
        try:
            query = self.client.table('tokens').select('*')
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            result = query.execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting tokens: {e}")
            return []
    
    def transfer_token(self, token_id: str, from_address: str, to_address: str, amount: float) -> bool:
        """Record token transfer"""
        if self.mock_mode:
            logger.info(f"Mock: Transferring token {token_id} from {from_address} to {to_address}")
            return True
        
        try:
            # Update token owner
            self.client.table('tokens').update({
                'owner_address': to_address,
                'updated_at': datetime.now().isoformat()
            }).eq('token_id', token_id).execute()
            
            # Record transaction
            transaction_data = {
                'token_id': token_id,
                'from_address': from_address,
                'to_address': to_address,
                'amount': amount,
                'transaction_type': 'transfer',
                'created_at': datetime.now().isoformat()
            }
            self.client.table('token_transactions').insert(transaction_data).execute()
            
            return True
        except Exception as e:
            logger.error(f"Error transferring token: {e}")
            return False
    
    def retire_token(self, token_id: str, owner_address: str, reason: str) -> bool:
        """Mark token as retired"""
        if self.mock_mode:
            logger.info(f"Mock: Retiring token {token_id} for reason: {reason}")
            return True
        
        try:
            # Update token status
            self.client.table('tokens').update({
                'status': 'retired',
                'retirement_reason': reason,
                'retirement_date': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }).eq('token_id', token_id).execute()
            
            # Record retirement transaction
            transaction_data = {
                'token_id': token_id,
                'from_address': owner_address,
                'transaction_type': 'retire',
                'retirement_reason': reason,
                'created_at': datetime.now().isoformat()
            }
            self.client.table('token_transactions').insert(transaction_data).execute()
            
            return True
        except Exception as e:
            logger.error(f"Error retiring token: {e}")
            return False
    
    # Transaction Management
    def create_transaction(self, transaction_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a transaction record"""
        if self.mock_mode:
            return {"id": f"mock_txn_{len(transaction_data)}", **transaction_data}
        
        try:
            transaction_data['created_at'] = datetime.now().isoformat()
            result = self.client.table('transactions').insert(transaction_data).execute()
            return result.data[0] if result.data else None
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
                    'created_at': datetime.now().isoformat()
                }
            ]
        
        try:
            query = self.client.table('transactions').select('*')
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            result = query.limit(limit).order('created_at', desc=True).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting transactions: {e}")
            return []
    
    # Analytics & Reporting
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
        
        # Real implementation would query database for actual stats
        return {}
    
    # Real-time subscriptions
    def subscribe_to_projects(self, callback_func):
        """Subscribe to real-time project updates"""
        if self.mock_mode:
            logger.info("Mock: Subscribed to project updates")
            return None
        
        try:
            return self.client.table('projects').on('*', callback_func).subscribe()
        except Exception as e:
            logger.error(f"Error subscribing to projects: {e}")
            return None
    
    def subscribe_to_transactions(self, callback_func):
        """Subscribe to real-time transaction updates"""  
        if self.mock_mode:
            logger.info("Mock: Subscribed to transaction updates")
            return None
        
        try:
            return self.client.table('transactions').on('*', callback_func).subscribe()
        except Exception as e:
            logger.error(f"Error subscribing to transactions: {e}")
            return None


# Global instance
supabase_client = SupabaseClient()

# Database schema creation functions (for initial setup)
def create_database_schema():
    """Create the database schema in Supabase"""
    schema_sql = """
    -- Users table
    CREATE TABLE IF NOT EXISTS users (
        id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
        email VARCHAR UNIQUE NOT NULL,
        password_hash VARCHAR NOT NULL,
        role VARCHAR NOT NULL CHECK (role IN ('admin', 'ngo', 'industry', 'panchayat')),
        name VARCHAR NOT NULL,
        phone VARCHAR,
        organization VARCHAR,
        wallet_address VARCHAR,
        is_verified BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Projects table  
    CREATE TABLE IF NOT EXISTS projects (
        id VARCHAR PRIMARY KEY,
        name VARCHAR NOT NULL,
        description TEXT,
        ngo_id UUID REFERENCES users(id),
        ecosystem VARCHAR NOT NULL,
        location VARCHAR,
        state VARCHAR,
        district VARCHAR,
        area_hectares DECIMAL,
        number_of_trees INTEGER,
        tree_species VARCHAR,
        credits_requested DECIMAL,
        credits_approved DECIMAL DEFAULT 0,
        status VARCHAR DEFAULT 'Pending Review' CHECK (status IN ('Pending Review', 'Documents Missing', 'Under Verification', 'Verified', 'Rejected')),
        submission_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        approval_date TIMESTAMP WITH TIME ZONE,
        verification_notes TEXT,
        token_id VARCHAR,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Tokens table
    CREATE TABLE IF NOT EXISTS tokens (
        id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
        token_id VARCHAR UNIQUE NOT NULL,
        project_id VARCHAR REFERENCES projects(id),
        credits_amount DECIMAL NOT NULL,
        owner_address VARCHAR NOT NULL,
        status VARCHAR DEFAULT 'active' CHECK (status IN ('active', 'transferred', 'retired')),
        mint_transaction_hash VARCHAR,
        retirement_reason TEXT,
        retirement_date TIMESTAMP WITH TIME ZONE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Transactions table
    CREATE TABLE IF NOT EXISTS transactions (
        id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
        transaction_id VARCHAR UNIQUE NOT NULL,
        project_id VARCHAR REFERENCES projects(id),
        buyer_id UUID REFERENCES users(id),
        seller_id UUID REFERENCES users(id),
        credits_sold DECIMAL NOT NULL,
        price_per_credit DECIMAL NOT NULL,
        total_value DECIMAL NOT NULL,
        status VARCHAR DEFAULT 'Pending' CHECK (status IN ('Pending', 'Processing', 'Completed', 'Failed')),
        blockchain_hash VARCHAR,
        payment_method VARCHAR,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Token transactions table (for transfers, retirements)
    CREATE TABLE IF NOT EXISTS token_transactions (
        id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
        token_id VARCHAR REFERENCES tokens(token_id),
        from_address VARCHAR,
        to_address VARCHAR,
        amount DECIMAL,
        transaction_type VARCHAR NOT NULL CHECK (transaction_type IN ('mint', 'transfer', 'retire')),
        transaction_hash VARCHAR,
        retirement_reason TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Create indexes for better performance
    CREATE INDEX IF NOT EXISTS idx_projects_ngo_id ON projects(ngo_id);
    CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
    CREATE INDEX IF NOT EXISTS idx_tokens_project_id ON tokens(project_id);
    CREATE INDEX IF NOT EXISTS idx_tokens_owner ON tokens(owner_address);
    CREATE INDEX IF NOT EXISTS idx_transactions_buyer ON transactions(buyer_id);
    CREATE INDEX IF NOT EXISTS idx_transactions_project ON transactions(project_id);
    """
    
    logger.info("Database schema SQL generated. Execute this in Supabase SQL editor.")
    return schema_sql

if __name__ == "__main__":
    # Print schema for manual execution
    print("=== SUPABASE DATABASE SCHEMA ===")
    print(create_database_schema())
    print("\n=== COPY THE ABOVE SQL TO SUPABASE SQL EDITOR ===")