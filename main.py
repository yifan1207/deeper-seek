#!/usr/bin/env python3
"""
Deeper Seek - Geospatial Similarity Search with AI-Powered Earth Engine Queries

Entry point for the application.
"""

import subprocess
import sys
import webbrowser
import time
from pathlib import Path


def main():
    """Main entry point - starts the FastAPI server."""
    print("Deeper Seek - AI-Powered Geospatial Analysis")
    print("Starting FastAPI server with Earth Engine integration...")
    
    try:
        subprocess.run([sys.executable, "server.py"], cwd=Path(__file__).parent)
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Error starting server: {e}")


if __name__ == "__main__":
    main()
