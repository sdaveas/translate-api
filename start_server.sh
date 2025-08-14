#!/bin/bash

# Kill any existing Flask processes on port 8080
echo "Stopping any existing server on port 8080..."
lsof -ti:8080 | xargs kill -9 2>/dev/null

# Start the Flask server in the background with nohup
echo "Starting Flask server on port 8080..."
nohup pipenv run python api.py > server.log 2>&1 &

# Get the PID
PID=$!
echo "Server started with PID: $PID"

# Wait a moment for server to start
sleep 2

# Check if server is running
if ps -p $PID > /dev/null; then
    echo "Server is running successfully on http://localhost:8080"
    echo "PID saved to server.pid"
    echo $PID > server.pid
    echo "Logs are in server.log"
else
    echo "Failed to start server. Check server.log for errors."
    exit 1
fi
