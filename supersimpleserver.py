#!/usr/bin/env python3
"""
Simple HTTP Server using Python's built-in http.server module.
This server can serve static files from the current directory.
"""

import http.server
import socketserver
import os
import urllib.parse
import mimetypes
from datetime import datetime

# Define the port to listen on
PORT = 8000

class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP request handler with additional features."""

    # Override the default server version string
    server_version = "SimpleServer/0.1"

    def log_message(self, format, *args):
        """Override to customize the log message format."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {self.address_string()} - {format % args}")

    def do_GET(self):
        """Handle GET requests."""
        # Parse the URL path
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        # Default to index.html for the root path
        if path == '/':
            path = '/index.html'

        # Try to serve the file from the current directory
        try:
            # Construct the file path relative to the current directory
            # Ensure we don't allow directory traversal attacks
            file_path = os.path.normpath(os.path.join(os.getcwd(), path.lstrip('/')))

            # Check that the path is within the allowed directory
            if not file_path.startswith(os.getcwd()):
                self.send_error(403, "Forbidden: Access denied.")
                return

            # Check if the file exists
            if not os.path.exists(file_path) or not os.path.isfile(file_path):
                self.send_error(404, "File not found")
                return

            # Determine the content type
            content_type, _ = mimetypes.guess_type(file_path)
            if content_type is None:
                content_type = 'application/octet-stream'

            # Send headers
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.send_header('Content-Length', str(os.path.getsize(file_path)))
            self.end_headers()

            # Send file content
            with open(file_path, 'rb') as file:
                self.wfile.write(file.read())

        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")

    def do_POST(self):
        """Handle POST requests (basic implementation)."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        # Log the received data
        self.log_message("POST request, Path: %s, Data: %s",
                         self.path, post_data.decode('utf-8'))

        # Respond with a simple confirmation
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        response = f"""
        <html>
        <head><title>POST Response</title></head>
        <body>
        <h1>POST Request Received</h1>
        <p>Path: {self.path}</p>
        <p>Data: {post_data.decode('utf-8')}</p>
        </body>
        </html>
        """

        self.wfile.write(response.encode('utf-8'))


def run_server():
    """Start the HTTP server."""
    handler = SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Server started at http://localhost:{PORT}")
        print("Press Ctrl+C to stop the server")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == "__main__":
    run_server()
