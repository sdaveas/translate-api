#!/usr/bin/env python3
"""
Server startup script that handles the interrupted system call issue.
"""

import os
import sys
from api import app

if __name__ == '__main__':
    # Disable debug mode to avoid termios issues when running in background
    # For development, you can still use hot reload with watchdog
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Run the server
    try:
        app.run(
            host='0.0.0.0', 
            port=8080, 
            debug=debug_mode,
            use_reloader=False  # Disable reloader to avoid termios issues
        )
    except KeyboardInterrupt:
        print("\nServer stopped.")
        sys.exit(0)
