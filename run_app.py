#!/usr/bin/env python3
"""
Entry point for running the climbing gear discount aggregator Flask application.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.main import app
from src.core.config import config

if __name__ == '__main__':
    mode = "PRODUCTION" if config.is_production() else "DEVELOPMENT"
    print(f"🚀 Starting Flask app in {mode} mode")
    print(f"📁 Mock files directory: {config.get_mock_files_dir()}")
    app.run(debug=False, host='0.0.0.0', port=5000) 