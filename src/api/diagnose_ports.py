"""
Diagnostic script for inspecting active network ports (8000, 8080, 3000, 3306),
process IDs, executable names, and HTTP health responses.
"""

import subprocess
import urllib.request
import urllib.error
import json

PORTS = [8000, 8080, 3000, 3306]

def check_port(port: int):
    print(f"\n--- PORT {port} ---")
    try:
        cmd = f'netstat -ano | findstr ":{port}"'
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        lines = [line.strip() for line in res.stdout.splitlines() if "LISTENING" in line]
        if lines:
            for l in lines:
                parts = l.split()
                pid = parts[-1]
                # Get process name
                t_res = subprocess.run(f'tasklist /FI "PID eq {pid}" /FO CSV /NH', shell=True, capture_output=True, text=True)
                t_out = t_res.stdout.strip()
                proc_name = t_out.split(',')[0].strip('"') if t_out and not t_out.startswith("INFO:") else "Unknown"
                print(f"  Listening: {l}")
                print(f"  PID: {pid}")
                print(f"  Process: {proc_name}")
        else:
            print("  No LISTENING process found.")
    except Exception as e:
        print(f"  Error checking port: {e}")

def check_http():
    print("\n--- HTTP HEALTH ENDPOINTS ---")
    
    # 1. Port 8000 (Python FastAPI)
    print("\nChecking Python FastAPI (http://localhost:8000/api/v1/health)...")
    try:
        req = urllib.request.Request("http://localhost:8000/api/v1/health")
        with urllib.request.urlopen(req, timeout=5) as resp:
            print(f"  Status: HTTP {resp.status}")
            print(f"  Response: {resp.read().decode()}")
    except Exception as e:
        print(f"  Error: {e}")

    # 2. Port 8080 (Spring Boot 3)
    print("\nChecking Spring Boot (http://localhost:8080/api/v1/health)...")
    try:
        req = urllib.request.Request("http://localhost:8080/api/v1/health")
        with urllib.request.urlopen(req, timeout=5) as resp:
            print(f"  Status: HTTP {resp.status}")
            body = resp.read().decode()
            print(f"  Response: {body}")
            try:
                parsed = json.loads(body)
                print(f"  Python Service Link: {parsed.get('pythonServiceStatus')}")
                print(f"  Database Link: {parsed.get('databaseStatus')}")
            except Exception:
                pass
    except Exception as e:
        print(f"  Error: {e}")

    # 3. Port 3000 (React Frontend)
    print("\nChecking React Frontend (http://localhost:3000)...")
    try:
        req = urllib.request.Request("http://localhost:3000")
        with urllib.request.urlopen(req, timeout=5) as resp:
            print(f"  Status: HTTP {resp.status}")
            content = resp.read().decode()
            print(f"  HTML Title/Length: {len(content)} bytes received")
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    print("================================================================================")
    print(" SIH26166 NETWORK PORT & PROCESS HEALTH DIAGNOSTIC ")
    print("================================================================================")
    for p in PORTS:
        check_port(p)
    check_http()
