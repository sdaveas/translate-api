#!/bin/bash

# Stop the Flask server
if [ -f server.pid ]; then
    PID=$(cat server.pid)
    if ps -p $PID > /dev/null; then
        echo "Stopping server with PID: $PID"
        kill $PID
        rm server.pid
        echo "Server stopped."
    else
        echo "No server process found with PID: $PID"
        rm server.pid
    fi
else
    echo "No server.pid file found. Checking for Flask processes on port 8080..."
    lsof -ti:8080 | xargs kill -9 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "Stopped Flask processes on port 8080"
    else
        echo "No Flask server running on port 8080"
    fi
fi
