#!/usr/bin/env python3
"""
Quick start script for Paper Search Interface
"""

import sys
import os
from pathlib import Path

# Add the tools directory to the Python path
tools_dir = Path(__file__).parent / "tools"
sys.path.insert(0, str(tools_dir))

# Import and run the web interface
from web_interface import app

if __name__ == "__main__":
    print("Starting Paper Search Interface...")
    print("Open your browser and go to: http://localhost:5001")
    print("Press Ctrl+C to stop the server")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Error starting server: {e}")
        print("Make sure you have installed the requirements:")
        print("pip install -r requirements.txt") 