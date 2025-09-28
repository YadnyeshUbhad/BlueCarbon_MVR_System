"""
WSGI Entry Point for Blue Carbon MRV System
Production-ready configuration for public deployment
"""

import os
import sys
from pathlib import Path

# Add project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Set environment for production
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_CONFIG', 'demo')

# Import the application
try:
    from app import app
    
    # Configure for production
    app.config.update(
        DEBUG=False,
        TESTING=False,
        HOST='0.0.0.0',
        PORT=int(os.environ.get('PORT', 5000))
    )
    
    # Ensure demo mode is enabled for public access
    app.config['DEMO_MODE'] = True
    app.config['PUBLIC_ACCESS'] = True
    
    application = app
    
except Exception as e:
    print(f"Error importing application: {e}")
    # Create minimal fallback app
    from flask import Flask, jsonify
    
    application = Flask(__name__)
    
    @application.route('/')
    def home():
        return jsonify({
            'message': 'Blue Carbon MRV System',
            'status': 'error',
            'error': str(e),
            'note': 'System is starting up. Please try again in a moment.'
        })
    
    @application.route('/health')
    def health():
        return jsonify({'status': 'starting', 'message': 'Application is initializing'})

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port, debug=False)