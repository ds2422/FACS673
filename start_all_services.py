import subprocess
import time
import os
import signal

# Define all your services with their folder, command, and port
services = [
    ("auth-service", "uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload"),
    ("file_service", "python manage.py runserver 0.0.0.0:8001"),
    ("url_summarizer", "uvicorn main:app --reload --port 8002"),
    ("comparison_service", "uvicorn main:app --host 0.0.0.0 --port 8003 --reload"),
    ("summarization_backend", "python summarizer_project/manage.py runserver 0.0.0.0:8004"),
    ("gateway_services", "uvicorn main:app --host 0.0.0.0 --port 9000 --reload"),
]

processes = []

try:
    for folder, cmd in services:
        service_path = os.path.join(os.getcwd(), folder)

        if not os.path.isdir(service_path):
            print(f"❌ Folder not found: {service_path}")
            continue

        print(f"🚀 Starting {folder} → {cmd}")
        p = subprocess.Popen(cmd, shell=True, cwd=service_path)
        processes.append(p)
        time.sleep(2)  # small delay to avoid conflicts

    print("\n✅ All services started successfully!")
    print("🌐 Gateway available at http://localhost:9000")
    print("Press CTRL+C to stop all services.\n")

    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\n🛑 Shutting down all services...")
    for p in processes:
        try:
            p.send_signal(signal.SIGINT)
            p.wait(timeout=5)
        except Exception:
            p.kill()
    print("✅ All services stopped.")
