from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional, Any
import os
import sys
import logging
from datetime import datetime, timedelta

# Set up paths so we can import from parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from modules.organization import Organization
from modules.worker import Worker
from modules.task import Task
from conductor import Conductor

from .models import (
    WorkerCreate, 
    TaskCreate, 
    OrganizationResponse,
    AssignTaskRequest,
    CompleteTaskRequest,
    TaskResponse,
    WorkerResponse
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("api")

app = FastAPI(title="Conductor Agent API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for organization
organization = Organization("Default Organization")
base_prompt = """
You are assisting a team by assigning tasks to workers based on their skills and experience.
Consider the following:
1. Match worker skills with task requirements
2. Consider worker workload and availability
3. Consider task priority and deadline
4. Balance workload appropriately among team members
5. Consider worker experience with similar tasks
"""
conductor = Conductor(organization, base_prompt)

def set_organization_and_conductor(org: Organization, cond: Conductor):
    """
    Set the global organization and conductor objects.
    Used when loading test data.
    """
    global organization, conductor
    organization = org
    conductor = cond
    logger.info(f"Set organization to {organization.name} with {len(organization.workers)} workers and {len(organization.tasks)} tasks")
    return True

@app.get("/")
def read_root():
    return {"message": "Welcome to the Conductor Agent API"}

@app.get("/organization", response_model=OrganizationResponse)
def get_organization():
    """Get the current organization state"""
    return {
        "name": organization.name,
        "workers": [worker_to_response(w) for w in organization.workers],
        "tasks": [task_to_response(t) for t in organization.tasks],
        "completed_tasks": [task_to_response(t) for t in organization.completed_tasks]
    }

@app.post("/workers", response_model=WorkerResponse)
def create_worker(worker_data: WorkerCreate):
    """Create a new worker and add to organization"""
    worker = Worker(
        name=worker_data.name,
        is_human=worker_data.is_human,
        skills=worker_data.skills,
        experience_description=worker_data.experience_description
    )
    organization.add_worker(worker)
    return worker_to_response(worker)

@app.get("/workers", response_model=List[WorkerResponse])
def get_workers():
    """Get all workers in the organization"""
    return [worker_to_response(w) for w in organization.workers]

@app.get("/workers/{worker_id}", response_model=WorkerResponse)
def get_worker(worker_id: int):
    """Get a specific worker by ID"""
    if 0 <= worker_id < len(organization.workers):
        return worker_to_response(organization.workers[worker_id])
    raise HTTPException(status_code=404, detail="Worker not found")

@app.post("/tasks", response_model=TaskResponse)
def create_task(task_data: TaskCreate):
    """Create a new task and add to organization"""
    
    # Process deadline if provided
    deadline = None
    if task_data.deadline_days:
        deadline = datetime.now() + timedelta(days=task_data.deadline_days)
        
    # Process dependencies if provided
    dependencies = []
    if task_data.dependency_ids:
        for dep_id in task_data.dependency_ids:
            if 0 <= dep_id < len(organization.tasks):
                dependencies.append(organization.tasks[dep_id])
    
    task = Task(
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        deadline=deadline,
        required_skills=task_data.required_skills,
        tags=task_data.tags,
        dependencies=dependencies,
        estimated_hours=task_data.estimated_hours
    )
    
    # Add task to organization (no auto-assignment)
    organization.add_task(task)
    
    return task_to_response(task)

@app.get("/tasks", response_model=List[TaskResponse])
def get_tasks():
    """Get all tasks in the organization"""
    return [task_to_response(t) for t in organization.tasks]

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    """Get a specific task by ID"""
    if 0 <= task_id < len(organization.tasks):
        return task_to_response(organization.tasks[task_id])
    raise HTTPException(status_code=404, detail="Task not found")

@app.post("/tasks/assign", response_model=Dict[str, List[TaskResponse]])
def assign_tasks():
    """Generate and apply task assignments for all unassigned tasks"""
    logger.info("Starting task assignment process")
    
    # Get count of unassigned tasks before assignment
    unassigned_count = sum(1 for t in organization.tasks if t.assigned_worker is None)
    logger.info(f"Initial unassigned tasks: {unassigned_count}")
    
    # Generate assignments
    assignments = conductor.generate_task_assignments()
    logger.info(f"Assignment generation complete. Assigned to {len(assignments)} workers")
    
    # Convert to response format
    response = {}
    for worker_name, tasks in assignments.items():
        logger.info(f"Worker '{worker_name}' assigned {len(tasks)} tasks: {[t.title for t in tasks]}")
        response[worker_name] = [task_to_response(t) for t in tasks]
    
    # Get count of unassigned tasks after assignment
    unassigned_count_after = sum(1 for t in organization.tasks if t.assigned_worker is None)
    logger.info(f"Remaining unassigned tasks: {unassigned_count_after}")
    
    return response

@app.post("/tasks/{task_id}/assign", response_model=WorkerResponse)
def assign_task(task_id: int, assignment: AssignTaskRequest):
    """Assign a specific task to a worker"""
    logger.info(f"Request to assign task ID {task_id} to worker '{assignment.worker_name}'")
    
    if 0 <= task_id < len(organization.tasks):
        task = organization.tasks[task_id]
        logger.info(f"Found task: {task.title}")
        
        # Check if task is already assigned
        if task.assigned_worker:
            logger.warning(f"Task '{task.title}' already assigned to {task.assigned_worker.name}")
            # If already assigned to the same worker, just return
            if task.assigned_worker.name == assignment.worker_name:
                logger.info(f"Task already assigned to {assignment.worker_name}, returning worker data")
                return worker_to_response(task.assigned_worker)
            # If assigned to a different worker, unassign first
            old_worker = task.assigned_worker
            logger.info(f"Removing task assignment from {old_worker.name}")
            old_worker.assigned_tasks.remove(task)
            task.assigned_worker = None
            task.assignment_time = None
        
        # Find the worker
        worker = None
        for w in organization.workers:
            if w.name == assignment.worker_name:
                worker = w
                break
        
        if worker:
            logger.info(f"Assigning task '{task.title}' to {worker.name}")
            worker.assign_task(task)
            logger.info(f"Task successfully assigned. Worker now has {len(worker.assigned_tasks)} active tasks")
            return worker_to_response(worker)
        else:
            logger.error(f"Worker '{assignment.worker_name}' not found")
            raise HTTPException(status_code=404, detail="Worker not found")
    else:
        logger.error(f"Task ID {task_id} not found (valid range: 0-{len(organization.tasks)-1})")
        raise HTTPException(status_code=404, detail="Task not found")

@app.post("/tasks/new-assign", response_model=WorkerResponse)
def assign_new_task(task_data: TaskCreate):
    """Create a new task and assign it to the most appropriate worker"""
    
    # Process deadline if provided
    deadline = None
    if task_data.deadline_days:
        deadline = datetime.now() + timedelta(days=task_data.deadline_days)
        
    # Process dependencies if provided
    dependencies = []
    if task_data.dependency_ids:
        for dep_id in task_data.dependency_ids:
            if 0 <= dep_id < len(organization.tasks):
                dependencies.append(organization.tasks[dep_id])
    
    task = Task(
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        deadline=deadline,
        required_skills=task_data.required_skills,
        tags=task_data.tags,
        dependencies=dependencies,
        estimated_hours=task_data.estimated_hours
    )
    
    # Add and assign task
    assigned_worker = conductor.assign_new_task(task)
    
    if assigned_worker:
        return worker_to_response(assigned_worker)
    else:
        raise HTTPException(status_code=500, detail="Failed to assign task")

@app.post("/tasks/{task_id}/complete")
def complete_task(task_id: int, completion: CompleteTaskRequest):
    """Mark a task as completed with optional feedback"""
    if 0 <= task_id < len(organization.tasks):
        task = organization.tasks[task_id]
        result = conductor.handle_task_completion(task, completion.feedback)
        if result:
            return {"status": "success", "message": f"Task '{task.title}' marked as completed"}
        else:
            raise HTTPException(status_code=400, detail="Task could not be completed")
    else:
        raise HTTPException(status_code=404, detail="Task not found")

@app.get("/completed-tasks", response_model=List[TaskResponse])
def get_completed_tasks():
    """Get all completed tasks"""
    return [task_to_response(t) for t in organization.completed_tasks]

@app.get("/organization-state")
def get_organization_state():
    """Get a detailed text representation of the organization state"""
    # Redirect stdout to capture print output
    import io
    import sys
    
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    
    conductor.print_organization_state()
    
    # Reset stdout and get the captured output
    sys.stdout = old_stdout
    org_state = new_stdout.getvalue()
    
    return {"organization_state": org_state}

# Helper functions to convert objects to response models
def worker_to_response(worker: Worker) -> Dict:
    """Convert Worker object to API response"""
    return {
        "name": worker.name,
        "is_human": worker.is_human,
        "skills": worker.skills,
        "assigned_tasks": [task_to_response(t) for t in worker.assigned_tasks],
        "completed_tasks": [task_to_response(t) for t in worker.completed_tasks],
        "workload": worker.get_workload(),
        "experience_description": worker.experience_description,
        "performance_metrics": worker.performance_metrics
    }

def task_to_response(task: Task) -> Dict:
    """Convert Task object to API response"""
    return {
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "deadline": task.deadline,
        "required_skills": task.required_skills,
        "tags": task.tags,
        "estimated_hours": task.estimated_hours,
        "status": task.status,
        "assignment_time": task.assignment_time,
        "completed_time": task.completed_time,
        "assigned_worker": task.assigned_worker.name if task.assigned_worker else None,
        "notes": task.notes,
        "dependencies": [t.title for t in task.dependencies] if task.dependencies else []
    }