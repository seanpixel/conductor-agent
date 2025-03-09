#!/usr/bin/env python3
import logging
import sys
from datetime import datetime, timedelta
import os

from modules.organization import Organization
from modules.worker import Worker
from modules.task import Task
from conductor import Conductor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TestScript")

# Make sure environment variable is set for API key
if "CLAUDE_API_KEY" not in os.environ:
    print("Please set the CLAUDE_API_KEY environment variable")
    sys.exit(1)

def test_new_features():
    """
    Test new conductor features including worker performance metrics, 
    task dependencies, and adaptive task assignment
    """
    
    # Create a new organization for a software development team
    logger.info("Creating organization: DevTeam")
    org = Organization("DevTeam")
    
    # Add workers with various skills
    logger.info("Adding workers to organization")
    
    alex = Worker("Alex", True, ["frontend_development", "javascript", "react", "UI_design"])
    emma = Worker("Emma", True, ["backend_development", "python", "django", "database"])
    michael = Worker("Michael", True, ["devops", "kubernetes", "docker", "infrastructure"])
    sophia = Worker("Sophia", True, ["product_management", "UX_design", "user_research"])
    assistant = Worker("AI Assistant", False, ["documentation", "research", "testing", "code_review"])
    
    org.add_worker(alex)
    org.add_worker(emma)
    org.add_worker(michael)
    org.add_worker(sophia)
    org.add_worker(assistant)
    
    # Create base prompt for the conductor
    base_prompt = """
    You are assisting a software development team working on a web application.
    The application is a customer relationship management (CRM) system with:
    - User authentication
    - Customer data management
    - Sales pipeline tracking
    - Reporting and analytics
    
    Team Goals:
    1. Complete core features for an MVP within 2 weeks
    2. Maintain high code quality and test coverage
    3. Create clear documentation for APIs and user interfaces
    4. Follow best security practices for data protection
    
    Task assignments should consider skill matching, deadlines, dependencies between tasks,
    and the right balance between human and AI contributions.
    """
    
    # Initialize conductor
    logger.info("Initializing conductor")
    conductor = Conductor(org, base_prompt)
    
    # Phase 1: Add initial tasks with dependencies
    logger.info("\n--- PHASE 1: Initial Task Creation ---")
    
    # Create database schema task
    db_schema = Task(
        title="Database Schema Design",
        description="Design the database schema for user accounts, customers, and sales data",
        priority=9,
        deadline=datetime.now() + timedelta(days=2),
        required_skills=["database", "backend_development"],
        estimated_hours=6,
        tags=["database", "architecture"]
    )
    
    # Create user auth task that depends on DB schema
    user_auth = Task(
        title="User Authentication System",
        description="Implement secure login, registration, and password reset",
        priority=8,
        deadline=datetime.now() + timedelta(days=3),
        required_skills=["backend_development", "security", "python"],
        estimated_hours=8,
        tags=["security", "users"],
        dependencies=[db_schema]  # This task depends on DB schema
    )
    
    # Create customer API task that depends on DB schema
    customer_api = Task(
        title="Customer API Endpoints",
        description="Create REST API endpoints for customer data CRUD operations",
        priority=7,
        deadline=datetime.now() + timedelta(days=4),
        required_skills=["backend_development", "python", "API_design"],
        estimated_hours=10,
        tags=["API", "customers"],
        dependencies=[db_schema]  # This task depends on DB schema
    )
    
    # Create UI design task (no dependencies)
    ui_design = Task(
        title="UI Design for Dashboard",
        description="Create wireframes and design mockups for the main dashboard",
        priority=7,
        deadline=datetime.now() + timedelta(days=3),
        required_skills=["UI_design", "UX_design"],
        estimated_hours=8,
        tags=["design", "UI"]
    )
    
    # Add tasks to organization (no auto-assignment yet)
    org.add_task(db_schema)
    org.add_task(user_auth)
    org.add_task(customer_api)
    org.add_task(ui_design)
    
    # Show initial state
    logger.info("Initial organization state:")
    conductor.print_organization_state()
    
    # Phase 2: Generate task assignments
    logger.info("\n--- PHASE 2: Initial Task Assignment ---")
    logger.info("Generating task assignments")
    
    # Verify tasks are unassigned before
    unassigned_before = sum(1 for task in org.tasks if task.assigned_worker is None)
    logger.info(f"Tasks unassigned before: {unassigned_before} of {len(org.tasks)}")
    
    # Generate and apply assignments
    assignments = conductor.generate_task_assignments()
    
    # Show assignments from the returned dictionary
    logger.info("Task assignments generated and applied to organization:")
    for worker_name, tasks in assignments.items():
        task_titles = ", ".join([task.title for task in tasks])
        logger.info(f"{worker_name}: {task_titles}")
    
    # Verify tasks are now assigned
    unassigned_after = sum(1 for task in org.tasks if task.assigned_worker is None)
    assigned = unassigned_before - unassigned_after
    logger.info(f"Tasks assigned: {assigned} of {len(org.tasks)}")
    
    # Verify by checking worker's assigned tasks
    logger.info("Verifying assignments by checking worker objects:")
    for worker in org.workers:
        if worker.assigned_tasks:
            task_titles = ", ".join([task.title for task in worker.assigned_tasks])
            logger.info(f"{worker.name} has tasks: {task_titles}")
    
    # Show updated state after assignments
    logger.info("Organization state after assignments:")
    conductor.print_organization_state()
    
    # Phase 3: Complete some tasks and track performance
    logger.info("\n--- PHASE 3: Task Completion ---")
    
    # Let's assume Emma completes the database schema task
    logger.info("Emma completes the Database Schema Design task")
    emma_task = next((task for task in emma.assigned_tasks if task.title == "Database Schema Design"), None)
    
    if emma_task:
        # Set completed time to simulate 5 hour completion (faster than estimated)
        emma_task.completed_time = emma_task.assignment_time + timedelta(hours=5)
        conductor.handle_task_completion(emma_task, "High quality schema design with proper indexing")
    
    # Show updated state after task completion
    logger.info("Organization state after task completion:")
    conductor.print_organization_state()
    
    # Check if dependent tasks were unblocked
    logger.info("Checking if dependent tasks were unblocked:")
    for task in org.tasks:
        if task.title in ["User Authentication System", "Customer API Endpoints"]:
            logger.info(f"Task '{task.title}' status: {task.status}")
    
    # Phase 4: Add a new high-priority task and test single task assignment
    logger.info("\n--- PHASE 4: New Task Assignment ---")
    
    # Create a new urgent task
    security_fix = Task(
        title="Security Vulnerability Fix",
        description="Fix critical security vulnerability in authentication flow",
        priority=10,
        deadline=datetime.now() + timedelta(days=1),
        required_skills=["security", "backend_development", "python"],
        estimated_hours=4,
        tags=["security", "urgent", "bugfix"]
    )
    
    # Add and auto-assign the task
    logger.info("Adding new urgent task and letting the conductor assign it")
    
    # Count tasks before
    tasks_count_before = len(org.tasks)
    
    # Assign the new task
    assigned_worker = conductor.assign_new_task(security_fix)
    
    # Verify task was added
    tasks_count_after = len(org.tasks)
    logger.info(f"Tasks added: {tasks_count_after - tasks_count_before}")
    
    # Verify assignment
    if assigned_worker:
        logger.info(f"New task assigned to: {assigned_worker.name}")
        
        # Check if the task is in the worker's assigned tasks
        if any(task.title == "Security Vulnerability Fix" for task in assigned_worker.assigned_tasks):
            logger.info(f"Verified: Task is in {assigned_worker.name}'s assigned tasks")
        else:
            logger.warning(f"Task not found in {assigned_worker.name}'s assigned tasks!")
    else:
        logger.info("Could not assign the new task")
    
    # Show updated state after new task
    logger.info("Organization state after new task assignment:")
    conductor.print_organization_state()
    
    # Phase 5: Add tasks with varying skills to test skill matching
    logger.info("\n--- PHASE 5: Testing Skill Matching ---")
    
    # Create frontend tasks for Alex
    frontend_task = Task(
        title="Implement Dashboard UI",
        description="Implement the React components for the main dashboard",
        priority=7,
        deadline=datetime.now() + timedelta(days=5),
        required_skills=["frontend_development", "react", "javascript"],
        estimated_hours=12,
        tags=["frontend", "UI"],
        dependencies=[ui_design]  # Depends on UI design
    )
    
    # Create DevOps task for Michael
    devops_task = Task(
        title="Setup CI/CD Pipeline",
        description="Configure CI/CD pipeline for automated testing and deployment",
        priority=6,
        deadline=datetime.now() + timedelta(days=6),
        required_skills=["devops", "kubernetes", "docker"],
        estimated_hours=10,
        tags=["infrastructure", "automation"]
    )
    
    # Create documentation task for AI Assistant
    docs_task = Task(
        title="API Documentation",
        description="Generate comprehensive API documentation for the backend endpoints",
        priority=5,
        deadline=datetime.now() + timedelta(days=7),
        required_skills=["documentation", "API_design"],
        estimated_hours=6,
        tags=["documentation", "API"]
    )
    
    # Count unassigned tasks before
    unassigned_before = sum(1 for task in org.tasks if task.assigned_worker is None)
    logger.info(f"Unassigned tasks before: {unassigned_before}")
    
    # Add and assign each task individually using assign_new_task
    logger.info("Adding and assigning new tasks individually using assign_new_task:")
    
    new_tasks = [frontend_task, devops_task, docs_task]
    assignments = {}
    
    for task in new_tasks:
        logger.info(f"Adding and assigning task: {task.title}")
        worker = conductor.assign_new_task(task)
        
        if worker:
            logger.info(f"Task '{task.title}' assigned to {worker.name}")
            if worker.name not in assignments:
                assignments[worker.name] = []
            assignments[worker.name].append(task)
        else:
            logger.info(f"Task '{task.title}' could not be assigned")
    
    # Count unassigned tasks after
    unassigned_after = sum(1 for task in org.tasks if task.assigned_worker is None)
    logger.info(f"Unassigned tasks after: {unassigned_after}")
    logger.info(f"Newly assigned tasks: {len(new_tasks) - (unassigned_after - unassigned_before)}")
    
    # Check each new assignment
    logger.info("New assignments:")
    for worker_name, tasks in assignments.items():
        task_titles = ", ".join([task.title for task in tasks])
        logger.info(f"{worker_name}: {task_titles}")
    
    # Show final state
    logger.info("Final organization state:")
    conductor.print_organization_state()
    
    # Summary
    logger.info("\n--- SUMMARY ---")
    
    # Task assignment effectiveness
    assigned_tasks = sum(1 for task in org.tasks if task.assigned_worker is not None)
    completed_tasks = len(org.completed_tasks)
    total_tasks = len(org.tasks) + completed_tasks
    
    logger.info(f"Total tasks: {total_tasks}")
    logger.info(f"Assigned tasks: {assigned_tasks}")
    logger.info(f"Completed tasks: {completed_tasks}")
    logger.info(f"Unassigned tasks: {len(org.tasks) - assigned_tasks}")
    
    # Worker stats
    for worker in org.workers:
        active_count = len(worker.assigned_tasks)
        completed_count = len(worker.completed_tasks)
        if active_count + completed_count > 0:
            logger.info(f"{worker.name}: {active_count} active tasks, {completed_count} completed tasks")
            if worker.performance_metrics["tasks_completed"] > 0:
                logger.info(f"  Average completion time: {worker.performance_metrics['avg_completion_time']:.2f} hours")

if __name__ == "__main__":
    test_new_features()