import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer


class PaymentHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/version":
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error":"Not found"}')
            return

        data = {
            "application": "payment",
            "version": os.getenv("APP_VERSION", os.getenv("BUILD_NUMBER", "local")),
            "git_commit": os.getenv("GIT_COMMIT", "unknown"),
            "branch_name": os.getenv("BRANCH_NAME", "unknown"),
            "docker_image": os.getenv("DOCKER_IMAGE", "local"),
            "jenkins_build": os.getenv("BUILD_NUMBER", "local"),
            "status": "UP"
        }

        body = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        print("%s - %s" % (self.address_string(), format % args))


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8080), PaymentHandler)
    print("Payment application listening on port 8080")
    server.serve_forever()