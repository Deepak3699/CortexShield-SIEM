#!/bin/bash
# ============================================
# LogSentinel - Start Both Servers
# ============================================

echo "============================================================"
echo "🛡️ LogSentinel - Starting System"
echo "============================================================"
echo ""

# Check if in correct directory
if [ ! -f "run.py" ]; then
    echo "❌ Error: Please run from LogSentinel directory"
    echo "   cd /home/user/LogSentinel"
    exit 1
fi

echo "🚀 Step 1: Starting API server (port 8000)..."
python run.py &
API_PID=$!

sleep 3

echo "🎨 Step 2: Starting Dashboard (port 8501)..."
streamlit run app/dashboard/app.py --server.port 8501 --server.address 0.0.0.0 &
DASHBOARD_PID=$!

echo ""
echo "============================================================"
echo "✅ System Started!"
echo "============================================================"
echo ""
echo "📊 Dashboard: http://localhost:8501"
echo "📚 API Docs:  http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo "============================================================"

# Wait for user to stop
wait
