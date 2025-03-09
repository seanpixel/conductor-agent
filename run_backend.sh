#!/bin/bash
echo "Starting backend server on port 8080..."
echo "API documentation will be available at: http://localhost:8080/docs"
echo "Note: In GitHub Codespaces, use the 'Ports' tab to find the forwarded URL"
cd backend
python run.py --load-test-data
