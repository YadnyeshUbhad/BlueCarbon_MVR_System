#!/usr/bin/env python3
"""
BlueCarbon MRV System - Production Startup Script
Optimized configuration for deployment
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set production environment variables
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('SECRET_KEY', 'CHANGE-THIS-IN-PRODUCTION-PLEASE')

def setup_production_logging():
    """Configure production logging"""
    log_dir = project_root / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'bluecarbon_production.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def validate_production_requirements():
    """Validate that all required components are ready"""
    required_files = [
        'app.py',
        'db.py', 
        'auth.py',
        'production_config.py',
        'templates/admin/',
        'templates/ngo/',
        'static/css/',
        'static/js/'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (project_root / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    
    print("✅ All required files present")
    return True

def main():
    """Main production startup function"""
    print("🌊 BlueCarbon MRV System - Production Startup")
    print("=" * 50)
    
    # Setup logging
    setup_production_logging()
    logger = logging.getLogger(__name__)
    
    # Validate requirements
    if not validate_production_requirements():
        print("❌ Production validation failed")
        sys.exit(1)
    
    # Initialize database
    try:
        from db import init_db
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)
    
    # Import and configure Flask app
    try:
        from app import app
        logger.info("Flask application loaded successfully")
        
        # Configure for production
        app.config.update(
            ENV='production',
            DEBUG=False,
            TESTING=False,
            TEMPLATES_AUTO_RELOAD=False
        )
        
        print("✅ Production configuration loaded")
        print(f"🚀 Starting server on http://127.0.0.1:5000")
        print("📊 Admin Portal: http://127.0.0.1:5000/admin/login")
        print("🌱 NGO Dashboard: http://127.0.0.1:5000/ngo/login")
        print("🏢 Industry Portal: http://127.0.0.1:5000/industry/register")
        print("=" * 50)
        
        # Start the application
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=False,
            use_reloader=False,
            threaded=True
        )
        
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()