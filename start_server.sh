#!/bin/bash

# Start FastAPI Server for BDH Brain Explorer

echo "🚀 Starting BDH Brain Explorer API Server..."
echo ""

cd "$(dirname "$0")"
cd reference-bdh
source venv/bin/activate
cd ../backend/api

echo "📦 Loading model and starting server..."
echo "📡 Server will be available at: http://localhost:8000"
echo "📚 API documentation at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
