"""
Smart service readiness checker for SIH 2026 (SIH26166) Launcher.
Monitors FastAPI (port 8000), Spring Boot (port 8080), and Vite (port 3000)
until all microservices are healthy before launching the browser.
"""

import sys
import time
import json
import urllib.request
import urllib.error


def check_url(url: str, timeout: float = 2.0) -> tuple[bool, int, dict]:
    """Check an HTTP endpoint and return (is_success, status_code, json_body)."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SIH26166-HealthCheck/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = resp.getcode()
            if code == 200:
                try:
                    data = json.loads(resp.read().decode("utf-8"))
                    return True, code, data
                except Exception:
                    return True, code, {}
            return False, code, {}
    except Exception:
        return False, 0, {}


def main():
    max_wait_seconds = 45
    poll_interval = 2.0
    start_time = time.time()

    py_url = "http://localhost:8000/api/v1/health"
    sb_url = "http://localhost:8080/api/v1/health"
    fe_url = "http://localhost:3000"

    print("  Polling service readiness:", flush=True)
    print("    - Python ML Engine:  http://localhost:8000/api/v1/health", flush=True)
    print("    - Spring Boot API:   http://localhost:8080/api/v1/health", flush=True)
    print("    - React Vite UI:     http://localhost:3000\n", flush=True)

    try:
        while True:
            elapsed = int(time.time() - start_time)

            py_ok, _, _ = check_url(py_url)
            sb_ok, _, _ = check_url(sb_url)
            fe_ok, _, _ = check_url(fe_url)

            # Check if all 3 are ready
            if py_ok and sb_ok and fe_ok:
                print(f"\n  [SUCCESS] All 3 services are healthy and responsive (ready in {elapsed}s)!\n", flush=True)
                sys.exit(0)

            # Informative status feedback
            status_parts = []
            if py_ok:
                status_parts.append("Python ML: OK")
            else:
                status_parts.append("Python ML: waiting")

            if sb_ok:
                status_parts.append("Spring Boot: OK")
            else:
                status_parts.append("Spring Boot: initializing")

            if fe_ok:
                status_parts.append("Frontend: OK")
            else:
                status_parts.append("Frontend: booting")

            print(f"  [{elapsed:2d}s] " + " | ".join(status_parts), flush=True)

            if elapsed >= max_wait_seconds:
                print(f"\n  [INFO] Reached wait timeout ({max_wait_seconds}s). Launching browser now...\n", flush=True)
                sys.exit(0)

            time.sleep(poll_interval)

    except KeyboardInterrupt:
        print("\n  [INFO] Launcher health check interrupted by user.\n", flush=True)
        sys.exit(0)


if __name__ == "__main__":
    main()
