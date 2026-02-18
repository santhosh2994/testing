#!/bin/bash

echo "🚀 Starting Clearoid Server..."
echo ""

cd /Users/santhoshkumar/Downloads/Testing-files--main

# Activate virtual environment
source venv/bin/activate

# Start server
echo "✅ Server starting on http://localhost:8000"
echo ""
echo "📱 Access URLs:"
echo "   Home:      http://localhost:8000/index.html"
echo "   Sign In:   http://localhost:8000/pages/signin.html"
echo "   Dashboard: http://localhost:8000/pages/dashboard.html"
echo "   Upload:    http://localhost:8000/pages/upload.html"
echo "   History:   http://localhost:8000/pages/history.html"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "🔐 Demo Account:"
echo "   Email:    demo@clearoid.com"
echo "   Password: demo123"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
