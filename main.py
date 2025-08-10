#!/usr/bin/env python3
"""
Deeper Seek - Geospatial Similarity Search

Entry point for the application.
"""

import http.server
import socketserver
import webbrowser
from pathlib import Path


def serve_frontend(port=8000):
    """Serve the frontend on localhost."""
    frontend_dir = Path(__file__).parent / "frontend_old"
    
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(frontend_dir), **kwargs)
    
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"Serving frontend at http://localhost:{port}")
        print(f"Open http://localhost:{port}/geoguessr.html to start")
        try:
            webbrowser.open(f"http://localhost:{port}/geoguessr.html")
        except Exception:
            pass
        httpd.serve_forever()


def main():
    """Main entry point."""
    print("Deeper Seek - Geospatial Similarity Search")
    print("Starting local server...")
    serve_frontend()


if __name__ == "__main__":
    main()
