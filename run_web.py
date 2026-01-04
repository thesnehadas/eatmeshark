"""
Startup script for the Shark Tank Intelligence Platform web application.
Run this script to start both the Flask API server and serve the frontend.
"""

import subprocess
import sys
import os

def main():
    print("=" * 60)
    print("Shark Tank Intelligence Platform - Web Application")
    print("=" * 60)
    print("\nStarting web server...")
    print("The application will be available at: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server.")
    print("=" * 60)
    print()
    
    # Run Flask app
    try:
        from api import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
    except Exception as e:
        print(f"\nError starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

