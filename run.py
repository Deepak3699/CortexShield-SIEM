#!/usr/bin/env python3
"""
LogSentinel - Run Script
========================
"""

import uvicorn

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 LogSentinel - AI-Powered Log Analyzer")
    print("=" * 50)
    print()
    print("📊 Dashboard: http://0.0.0.0:8000")
    print("📚 API Docs:  http://0.0.0.0:8000/docs")
    print()
    print("=" * 50)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
