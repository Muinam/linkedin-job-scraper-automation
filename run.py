import subprocess
import sys
import os
import time

def run():
    print("Starting LinkedIn Scraper...")
    
    procs = []
    
    # Redis check
    print("Redis check...")
    
    # Celery start
    celery = subprocess.Popen([
        sys.executable, "-m", "celery", 
        "-A", "tasks", "worker", 
        "--loglevel=info", 
        "--pool=solo"
    ])
    procs.append(celery)
    print("Celery started!")
    time.sleep(3)
    
    # FastAPI start
    uvicorn = subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "api:app", 
        "--reload",
        "--port", "8000"
    ])
    procs.append(uvicorn)
    print("FastAPI started!")
    time.sleep(2)
    
    print("\n" + "="*50)
    print("Sab kuch chal raha hai!")
    print("Frontend: http://127.0.0.1:8000")
    print("="*50 + "\n")
    
    try:
        for p in procs:
            p.wait()
    except KeyboardInterrupt:
        print("\nBand kar raha hoon...")
        for p in procs:
            p.terminate()

if __name__ == "__main__":
    run()