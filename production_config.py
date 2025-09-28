"""
Production configuration module for Blue Carbon MRV System
This module provides production-ready configuration and utilities
"""

import os
import logging
from typing import Dict, Any, Optional
import sqlite3
from datetime import datetime

# Production configuration settings
production_config = {
    'debug': False,
    'host': '0.0.0.0',
    'port': int(os.environ.get('PORT', 5000)),
    'database_url': os.environ.get('DATABASE_URL', 'sqlite:///bluecarbon.db'),
    'secret_key': os.environ.get('SECRET_KEY', 'production-secret-key-change-me'),
    'environment': os.environ.get('ENVIRONMENT', 'production'),
    'log_level': os.environ.get('LOG_LEVEL', 'INFO'),
    'max_upload_size': int(os.environ.get('MAX_UPLOAD_SIZE', 16 * 1024 * 1024)),  # 16MB
    'session_timeout': int(os.environ.get('SESSION_TIMEOUT', 3600)),  # 1 hour
}

# Production database configuration
production_database = {
    'type': 'sqlite',
    'path': 'bluecarbon.db',
    'backup_enabled': True,
    'backup_interval': 24,  # hours
    'max_connections': 10,
    'connection_timeout': 30,
}

# External APIs configuration with feature flags
external_apis = {
    'firebase': {
        'enabled': os.environ.get('USE_FIREBASE', 'false').lower() == 'true',
        'project_id': os.environ.get('FIREBASE_PROJECT_ID', ''),
        'api_key': os.environ.get('FIREBASE_API_KEY', ''),
    },
    'satellite': {
        'enabled': os.environ.get('USE_REAL_SATELLITE', 'false').lower() == 'true',
        'google_earth_engine_key': os.environ.get('GOOGLE_EARTH_ENGINE_API_KEY', ''),
        'planet_labs_key': os.environ.get('PLANET_API_KEY', ''),
        'nasa_key': os.environ.get('NASA_API_KEY', ''),
        'rate_limit': 100,  # requests per hour
    },
    'drone': {
        'enabled': os.environ.get('USE_REAL_DRONE', 'false').lower() == 'true',
        'processing_enabled': os.environ.get('DRONE_PROCESSING_ENABLED', 'true').lower() == 'true',
    },
    'blockchain': {
        'enabled': os.environ.get('USE_REAL_BLOCKCHAIN', 'false').lower() == 'true',
        'network': os.environ.get('BLOCKCHAIN_NETWORK', 'testnet'),
        'contract_address': os.environ.get('CONTRACT_ADDRESS', ''),
        'rpc_url': os.environ.get('BLOCKCHAIN_RPC_URL', ''),
    },
    'email': {
        'enabled': os.environ.get('USE_EMAIL_NOTIFICATIONS', 'false').lower() == 'true',
        'smtp_server': os.environ.get('SMTP_SERVER', ''),
        'smtp_port': int(os.environ.get('SMTP_PORT', 587)),
        'username': os.environ.get('SMTP_USERNAME', ''),
        'password': os.environ.get('SMTP_PASSWORD', ''),
    },
    'pwa': {
        'enabled': os.environ.get('ENABLE_PWA_FEATURES', 'true').lower() == 'true',
        'push_notifications': os.environ.get('ENABLE_PUSH_NOTIFICATIONS', 'false').lower() == 'true',
        'background_sync': os.environ.get('ENABLE_BACKGROUND_SYNC', 'true').lower() == 'true',
    }
}

# Production monitoring configuration
production_monitoring = {
    'enabled': True,
    'metrics_collection': True,
    'error_tracking': True,
    'performance_monitoring': True,
    'log_retention_days': 30,
    'alert_thresholds': {
        'error_rate': 0.05,  # 5%
        'response_time': 2.0,  # seconds
        'memory_usage': 0.8,  # 80%
    }
}

# Global metrics storage
_metrics = {}

def is_production() -> bool:
    """Check if running in production environment"""
    return production_config['environment'] == 'production'

def get_database_connection():
    """Get database connection for production"""
    try:
        conn = sqlite3.connect(production_database['path'])
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logging.error(f"Database connection error: {e}")
        return None

def get_api_client(service: str) -> Optional[Dict[str, Any]]:
    """Get API client configuration for external services"""
    return external_apis.get(service)

def record_metric(metric_name: str, value: float, tags: Optional[Dict[str, str]] = None):
    """Record application metrics"""
    if not production_monitoring['metrics_collection']:
        return
    
    timestamp = datetime.now().isoformat()
    metric_data = {
        'name': metric_name,
        'value': value,
        'timestamp': timestamp,
        'tags': tags or {}
    }
    
    if metric_name not in _metrics:
        _metrics[metric_name] = []
    
    _metrics[metric_name].append(metric_data)
    
    # Keep only last 1000 entries per metric
    if len(_metrics[metric_name]) > 1000:
        _metrics[metric_name] = _metrics[metric_name][-1000:]

def initialize_production_services():
    """Initialize production services and configurations"""
    try:
        # Setup logging
        log_level = getattr(logging, production_config['log_level'].upper())
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('bluecarbon_mrv.log'),
                logging.StreamHandler()
            ]
        )
        
        # Initialize database
        conn = get_database_connection()
        if conn:
            conn.close()
            logging.info("Database connection initialized successfully")
        
        # Log startup
        logging.info(f"Production services initialized for environment: {production_config['environment']}")
        
        return True
    except Exception as e:
        logging.error(f"Failed to initialize production services: {e}")
        return False

def get_metrics() -> Dict[str, Any]:
    """Get collected metrics"""
    return _metrics.copy()

def clear_metrics():
    """Clear collected metrics"""
    global _metrics
    _metrics = {}

def is_feature_enabled(feature_name: str, service: str = None) -> bool:
    """Check if a feature is enabled via environment flags"""
    try:
        if service:
            return external_apis.get(service, {}).get(feature_name, False)
        
        # Direct feature check
        feature_map = {
            'firebase': external_apis['firebase']['enabled'],
            'satellite': external_apis['satellite']['enabled'],
            'drone': external_apis['drone']['enabled'],
            'blockchain': external_apis['blockchain']['enabled'],
            'email': external_apis['email']['enabled'],
            'pwa': external_apis['pwa']['enabled'],
            'push_notifications': external_apis['pwa']['push_notifications'],
            'background_sync': external_apis['pwa']['background_sync'],
        }
        
        return feature_map.get(feature_name, False)
    except Exception as e:
        logging.warning(f"Error checking feature {feature_name}: {e}")
        return False

def get_integration_config(service: str) -> Dict[str, Any]:
    """Get configuration for external service integration"""
    config = external_apis.get(service, {})
    if not config.get('enabled', False):
        return {'enabled': False, 'mock_mode': True}
    
    return {**config, 'mock_mode': False}

def safe_import_service(service_name: str, fallback_class=None):
    """Safely import service with fallback to mock"""
    try:
        if service_name == 'firebase' and is_feature_enabled('firebase'):
            from firebase_client import firebase_client
            return firebase_client
        elif service_name == 'supabase' and is_feature_enabled('firebase'):  # Using firebase flag for now
            from supabase_client import supabase_client
            return supabase_client
        elif service_name == 'satellite' and is_feature_enabled('satellite'):
            from real_satellite_apis import RealSatelliteIntegration
            return RealSatelliteIntegration()
        elif service_name == 'drone' and is_feature_enabled('drone'):
            from real_satellite_apis import DroneDataProcessor
            return DroneDataProcessor()
        else:
            # Return mock implementation
            return fallback_class() if fallback_class else None
    except ImportError as e:
        logging.warning(f"Failed to import {service_name}: {e}, using mock")
        return fallback_class() if fallback_class else None
    except Exception as e:
        logging.error(f"Error initializing {service_name}: {e}")
        return fallback_class() if fallback_class else None

# Initialize services on import
if __name__ != '__main__':
    initialize_production_services()

