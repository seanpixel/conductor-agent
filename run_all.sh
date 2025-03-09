#!/bin/bash

# Check if the terminal supports tmux
if command -v tmux &> /dev/null; then
    # Start a new tmux session
    tmux new-session -d -s conductor
    
    # Create a window for the backend
    tmux rename-window -t conductor:0 'Backend'
    tmux send-keys -t conductor:0 'cd /workspaces/conductor-agent && ./run_backend.sh' C-m
    
    # Create a window for the frontend
    tmux new-window -t conductor:1 -n 'Frontend'
    tmux send-keys -t conductor:1 'cd /workspaces/conductor-agent && ./run_frontend.sh' C-m
    
    # Attach to the session
    tmux attach-session -t conductor
else
    # If tmux is not available, use separate terminals
    echo "Starting backend and frontend in separate terminals..."
    
    # Start backend in background
    cd /workspaces/conductor-agent && ./run_backend.sh &
    
    # Wait for backend to start
    sleep 3
    
    # Start frontend
    cd /workspaces/conductor-agent && ./run_frontend.sh
fi