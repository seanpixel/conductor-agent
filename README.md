# Conductor Agent

An intelligent task orchestration system for guiding teams of humans and AI to success.

![Conductor Agent Dashboard](https://via.placeholder.com/800x400?text=Conductor+Agent+Dashboard)

## Overview

Conductor Agent is an intelligent system that assigns tasks to the most appropriate workers (human or AI) based on skills, workload, context, and dependencies. It leverages the Claude API to make intelligent assignments that optimize team productivity and task completion.

## Key Features

- 🧠 **AI-Powered Task Assignment**: Uses Claude API to match tasks to the most suitable workers
- 🔄 **Smart Work Distribution**: Balances workload between humans and AI assistants
- 🎯 **Task Priority Management**: Handles task dependencies and deadlines
- 📈 **Performance Tracking**: Records worker performance metrics and experience
- 📊 **Dashboard Visualization**: View organization state and task assignments
- 🌐 **Web Interface**: Manage workers and tasks through a clean, intuitive UI

## Web Interface

This repository includes a web interface built with FastAPI (backend) and React (frontend) that allows you to:

- View the organization dashboard with key metrics
- Manage workers (add, view details)
- Manage tasks (create, assign, complete, view details)
- Automatically assign tasks using Claude AI
- Track worker performance and experience

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- Claude API key

### Installation

1. Set up your environment:

```bash
# Clone the repository
git clone https://github.com/yourusername/conductor-agent.git
cd conductor-agent

# Set up your Claude API key
export CLAUDE_API_KEY=your_key_here

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### Running the Application

You can run the application using one of the following methods:

#### Method 1: Run everything at once

```bash
./run_all.sh
```

This will start both the backend and frontend in a tmux session (if available) or in separate terminals.

#### Method 2: Run backend and frontend separately

In one terminal:
```bash
./run_backend.sh
```

In another terminal:
```bash
./run_frontend.sh
```

#### Method 3: Run with test data

The backend is configured to load test data automatically, but you can also run the test data script separately:

```bash
python test_data.py
```

### Accessing the Application

#### Local Environment
If running locally, access the application at:
- Frontend: http://localhost:5173
- Backend API docs: http://localhost:8080/docs

#### GitHub Codespaces
If using GitHub Codespaces:
1. Look for the "Ports" tab in the bottom pane of your Codespace
2. Find the forwarded ports (typically 5173 for frontend and 8080 for backend)
3. Click the "Open in Browser" icon next to each port
4. The frontend and backend will be accessible via the Codespace URLs

## Core Components

### Organization
- Manages collections of workers and tasks
- Maintains a skill directory for quick worker lookup
- Tracks task relationships and dependencies
- Archives completed tasks for historical reference

### Worker
- Represents both human and AI team members
- Tracks skills, task history, and performance metrics
- Calculates workload and maintains experience descriptions
- Builds a narrative history of worker experiences

### Task
- Contains comprehensive metadata (priority, deadline, required skills)
- Supports dependencies, estimated hours, and tags 
- Maintains status (pending, in_progress, completed, blocked)
- Calculates urgency scores based on deadline and priority

### Conductor
- Core orchestration agent managing task assignments
- Uses LLM (Claude API) to generate intelligent assignments
- Handles task completion and dependency management
- Provides detailed reporting on organization state

## Task Assignment Algorithm

The Conductor uses a sophisticated multi-step process to assign tasks:

1. **Context Building**: Constructs detailed context of the organization state
2. **LLM-Based Assignment**: Uses Claude API to match tasks with workers based on multiple factors
3. **Response Parsing**: Extracts and applies the assignments to the organization
4. **Performance Tracking**: Updates metrics and experience descriptions as tasks are completed

## Web Interface Screenshots

### Dashboard
![Dashboard](https://via.placeholder.com/400x200?text=Dashboard)

### Tasks Management
![Tasks](https://via.placeholder.com/400x200?text=Tasks)

### Workers Management
![Workers](https://via.placeholder.com/400x200?text=Workers)

## API Endpoints

The backend provides a RESTful API with comprehensive documentation available at http://localhost:8000/docs when running.

Key endpoints:
- **GET /organization** - Get current organization state
- **GET /workers** - Get all workers
- **POST /workers** - Create a new worker
- **GET /tasks** - Get all tasks
- **POST /tasks** - Create a new task
- **POST /tasks/assign** - Generate assignments for all unassigned tasks

## Troubleshooting

- **Backend fails to start**: Ensure your Claude API key is correctly set as an environment variable
- **No test data appears**: Try running `python test_data.py` before starting the application
- **Frontend can't connect to backend**: 
  - In local environment: Make sure the backend is running on port 8080
  - In GitHub Codespaces: Check that both ports (5173 and 8080) are forwarded in the Ports tab
- **Issues with the Anthropic client**: 
  - Run `python check_anthropic.py` to diagnose Anthropic client issues
  - If you get "TypeError: Client.__init__() got an unexpected keyword argument 'proxies'", try:
    ```
    pip uninstall -y anthropic
    pip install anthropic==0.5.0
    ```
  - The system is designed to work with different versions of the Anthropic client

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)
