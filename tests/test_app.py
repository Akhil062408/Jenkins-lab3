import json
import os
import subprocess
import sys
import time
import urllib.request

def test_payment_application():
    env = os.environ.copy()
    env["APP_VERSION"] = "test-version"
    env["GIT_COMMIT"] = "test-commit"
    env["BRANCH_NAME"] = "test-branch"
    env["DOCKER_IMAGE"] = "mycompany/payment:test"
    env["BUILD_NUMBER"] = "999"

    process = subprocess.Popen(
        [sys.executable, "app.py"],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    try:
        for _ in range(30):
            try:
                with urllib.request.urlopen(
                    "http://127.0.0.1:8080/version", timeout=1
                ) as response:
                    data = json.loads(response.read().decode())
                    break
            except Exception:
                time.sleep(0.2)
        else:
            raise AssertionError("Application did not start")

        assert data["application"] == "payment"
        assert data["version"] == "test-version"
        assert data["git_commit"] == "test-commit"
        assert data["branch_name"] == "test-branch"
        assert data["docker_image"] == "mycompany/payment:test"
        assert data["jenkins_build"] == "999"
        assert data["status"] == "UP"

    finally:
        process.terminate()
        process.wait(timeout=5)