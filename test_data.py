#!/usr/bin/env python3
"""
Script to load test data into the system.
"""

import os
import sys
import logging
from datetime import datetime, timedelta

from modules.organization import Organization
from modules.worker import Worker
from modules.task import Task
from conductor import Conductor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TestDataScript")

# Make sure environment variable is set for API key
if "CLAUDE_API_KEY" not in os.environ:
    print("Please set the CLAUDE_API_KEY environment variable")
    sys.exit(1)

def load_test_data():
    """
    Load test data to demonstrate the conductor features
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
    
    # Create tasks with dependencies
    logger.info("Creating tasks")
    
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
    
    # Add tasks to organization (no auto-assignment)
    org.add_task(db_schema)
    org.add_task(user_auth)
    org.add_task(customer_api)
    org.add_task(ui_design)
    org.add_task(frontend_task)
    org.add_task(devops_task)
    org.add_task(docs_task)
    
    logger.info("Tasks created and added to organization")
    
    # Return the organization and conductor for further use
    return org, conductor

if __name__ == "__main__":
    org, conductor = load_test_data()
    
    # Print the initial state
    print("\nInitial organization state:")
    conductor.print_organization_state()
    
    # Generate and apply task assignments
    print("\nGenerating task assignments...")
    assignments = conductor.generate_task_assignments()
    
    # Show updated state after assignments
    print("\nOrganization state after assignments:")
    conductor.print_organization_state()
    
    print("\nTest data loaded successfully. You can now run the web application to see it in action.")