"""
Production Configuration for Blue Carbon MRV System
Optimized for public deployment
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'blue-carbon-mrv-2024-secure-key-change-in-production')
    
    # Database
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///bluecarbon_public.db')
    
    # Flask settings
    DEBUG = False
    TESTING = False
    
    # Public deployment settings
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 5000))
    
    # Blockchain settings for public access
    BLOCKCHAIN_MODE = os.environ.get('BLOCKCHAIN_MODE', 'sepolia')  # Use Sepolia testnet for free public access
    INFURA_PROJECT_ID = os.environ.get('INFURA_PROJECT_ID', '')
    ALCHEMY_API_KEY = os.environ.get('ALCHEMY_API_KEY', '')
    
    # Public testnet RPC URLs
    SEPOLIA_RPC_URL = f"https://sepolia.infura.io/v3/{INFURA_PROJECT_ID}" if INFURA_PROJECT_ID else "https://ethereum-sepolia-rpc.publicnode.com"
    MUMBAI_RPC_URL = "https://rpc.ankr.com/polygon_mumbai"
    
    # Email settings (optional for demo)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    
    # Public demo settings
    ENABLE_PUBLIC_DEMO = True
    DEMO_MODE = True
    PUBLIC_ACCESS = True
    
    # Rate limiting for public access
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
class DevelopmentConfig(Config):
    """Development configuration"""  
    DEBUG = True
    BLOCKCHAIN_MODE = 'localhost'
    
class DemoConfig(Config):
    """Public demo configuration"""
    DEBUG = False
    DEMO_MODE = True
    PUBLIC_ACCESS = True
    BLOCKCHAIN_MODE = 'sepolia'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'demo': DemoConfig,
    'default': DemoConfig
}