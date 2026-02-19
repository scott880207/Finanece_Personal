import subprocess
import time
import webbrowser
import os
import sys
import signal

def main():
    # Define paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(base_dir, "backend")
    frontend_dir = os.path.join(base_dir, "frontend")

    print(f"Base Directory: {base_dir}")

    # Import Data
    print("Importing data (this may take a moment)...")
    import_cmd = [sys.executable, "import_data.py"]
    try:
        subprocess.run(import_cmd, cwd=base_dir, check=True)
        print("Data import successful.")
    except subprocess.CalledProcessError as e:
        print(f"Data import failed: {e}")
        # Decide if we want to stop or continue. Let's continue but warn.
        print("Continuing with system startup...")

    # Start Backend
    print("Starting Backend Server...")
    # Using sys.executable to ensure we use the same python environment
    # Running from base_dir to allow 'backend.main:app' import style
    backend_cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload"]
    backend_process = subprocess.Popen(
        backend_cmd,
        cwd=base_dir,
        shell=True # shell=True is often needed on Windows for path resolution
    )

    # Start Frontend
    print("Starting Frontend Server...")
    # npm is a batch file on Windows, so shell=True is required
    frontend_cmd = ["npm", "run", "dev"]
    frontend_process = subprocess.Popen(
        frontend_cmd,
        cwd=frontend_dir,
        shell=True
    )

    print("Services started. Waiting for them to initialize...")
    time.sleep(5) # Wait a few seconds for servers to spin up

    frontend_url = "http://localhost:5173"
    print(f"Opening Browser at {frontend_url}...")
    webbrowser.open(frontend_url)

    print("\nSystem is running!")
    print("Press Ctrl+C to stop all services.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping services...")
        # On Windows, terminate() might not kill the process tree if shell=True
        # But for simple dev usage, it's usually okay. 
        # A more robust solution involves psutil to kill children, but let's keep it simple first.
        backend_process.terminate()
        frontend_process.terminate()
        print("Services stopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()
