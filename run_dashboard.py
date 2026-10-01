#!/usr/bin/env python3
"""
LogSentinel - Run Dashboard
============================
Run both API server and Streamlit dashboard.
"""

import subprocess
import sys
import time
import os

def main():
    print("=" * 60)
    print("🛡️ LogSentinel - Starting Dashboard")
    print("=" * 60)
    print()
    
    # Start API server
    print("🚀 Starting API server...")
    api_process = subprocess.Popen(
        [sys.executable, "run.py"],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    # Wait for API to start
    time.sleep(3)
    
    # Start Streamlit dashboard
    print("🎨 Starting Streamlit dashboard...")
    print()
    print("=" * 60)
    print("📊 Dashboard: http://localhost:8501")
    print("📚 API Docs:  http://localhost:8000/docs")
    print("=" * 60)
    print()
    
    dashboard_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", 
         "app/dashboard/app.py",
         "--server.port", "8501",
         "--server.address", "0.0.0.0"],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    try:
        # Wait for both processes
        api_process.wait()
        dashboard_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        api_process.terminate()
        dashboard_process.terminate()


if __name__ == "__main__":
    main()
