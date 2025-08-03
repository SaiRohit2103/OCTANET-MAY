#!/usr/bin/env python3
"""
Delhi High Court Case Data Fetcher
Simple runner script to start the Flask application
"""

import os
import sys
import logging
from app import app, init_db

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import selenium
        import requests
        import flask
        import PIL
        import cv2
        import numpy
        print("✓ All Python dependencies are available")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def main():
    """Main function to start the application"""
    print("=" * 50)
    print("Delhi High Court Case Data Fetcher")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup logging
    setup_logging()
    
    # Initialize database
    print("Initializing database...")
    init_db()
    print("✓ Database initialized")
    
    # Start the application
    print("\n🚀 Starting Flask application...")
    print("📍 URL: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop\n")
    
    try:
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Application error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()