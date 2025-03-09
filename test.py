from datetime import datetime, timedelta
import os
import json
import logging
from modules.organization import Organization
from modules.worker import Worker
from modules.task import Task
from conductor import Conductor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TestScript")

def main():
    # Create a startup organization building an e-learning platform
    logger.info("Creating organization: EdTech Startup")
    org = Organization("EdTech Startup")
    
    # Add workers (humans and AI)
    logger.info("Adding workers to organization")
    org.add_worker(Worker("Maya Rodriguez", is_human=True, 
                         skills=["product_management", "UX_design", "education"]))
    org.add_worker(Worker("Raj Patel", is_human=True, 
                         skills=["backend_development", "database", "python", "django"]))
    org.add_worker(Worker("Sarah Kim", is_human=True, 
                         skills=["frontend_development", "javascript", "react", "UI_design"]))
    org.add_worker(Worker("James Wilson", is_human=True, 
                         skills=["content_creation", "curriculum_design", "education", "writing"]))
    org.add_worker(Worker("Claude AI", is_human=False, 
                         skills=["data_analysis", "writing", "research", "content_generation", "coding_assistance"]))
    org.add_worker(Worker("Code Assistant", is_human=False, 
                         skills=["code_review", "debugging", "python", "javascript", "react", "django"]))
    
    # Add tasks for the e-learning platform
    logger.info("Adding tasks to organization")
    
    # High priority tasks
    task1 = Task("Database Schema Design", 
                "Design the database schema for user accounts, courses, lessons, and progress tracking", 
                priority=9, 
                deadline=datetime.now() + timedelta(days=2))
    
    task2 = Task("User Authentication API", 
                "Implement secure login, registration, and password reset endpoints", 
                priority=8, 
                deadline=datetime.now() + timedelta(days=3))
    
    task3 = Task("Course Creation Interface", 
                "Design and implement the teacher's interface for creating and organizing course content", 
                priority=8, 
                deadline=datetime.now() + timedelta(days=4))
    
    # Medium priority tasks
    task4 = Task("Student Dashboard UI",
                "Create wireframes and implement the student dashboard showing enrolled courses and progress",
                priority=6,
                deadline=datetime.now() + timedelta(days=5))
    
    task5 = Task("Content Guidelines",
                "Create comprehensive guidelines for educational content creators using our platform",
                priority=5,
                deadline=datetime.now() + timedelta(days=6))
    
    task6 = Task("Video Playback Component",
                "Implement a video player component with playback controls, bookmarking, and note-taking",
                priority=6,
                deadline=datetime.now() + timedelta(days=7))
    
    # Lower priority tasks
    task7 = Task("Market Research Report",
                "Analyze competing e-learning platforms and identify opportunities for differentiation",
                priority=4,
                deadline=datetime.now() + timedelta(days=10))
    
    task8 = Task("Documentation",
                "Create API documentation for the backend services to be used by the frontend team",
                priority=4,
                deadline=datetime.now() + timedelta(days=8))
                
    # Add tasks to organization
    for i, task in enumerate([task1, task2, task3, task4, task5, task6, task7, task8], 1):
        org.add_task(task)
        logger.info(f"Added task {i}: {task.title}")
    
    # Print worker information
    print("\n===== WORKER INFORMATION =====")
    workers_info = org.get_workers_txt()
    print(workers_info)
    
    # Print task information
    print("\n===== TASK INFORMATION =====")
    tasks_info = org.get_tasks_txt()
    print(tasks_info)
    
    # Create base prompt for the conductor
    base_prompt = """
    You are assisting an EdTech Startup that is building a new e-learning platform. The platform will allow
    educators to create and publish courses, and students to enroll in courses and track their progress.
    
    Company Goals:
    1. Create a user-friendly platform for both educators and students
    2. Design a scalable backend architecture that can handle growing content and user base
    3. Implement engaging learning features like interactive quizzes and progress tracking
    4. Ensure security and privacy of user data
    5. Create clear documentation for all components
    
    Task assignments should consider skill matching, deadlines, and the right balance between
    human and AI contributions. Human workers should focus on creative design, strategic decisions,
    and specialized development, while AI assistants can help with data analysis, content generation,
    documentation, and code assistance.
    """
    
    # Initialize the conductor with the organization and base prompt
    logger.info("Initializing conductor")
    conductor = Conductor(org, base_prompt)
    
    # Print the full context that will be sent to the LLM
    print("\n===== FULL CONTEXT FOR LLM =====")
    print(conductor.get_full_context())
    
    # Generate task assignments
    print("\n===== GENERATING TASK ASSIGNMENTS =====")
    assignments = conductor.generate_task_assignments()
    print(assignments)
    
    # Print the assignments
    print("\nAssignments generated:")
    for worker_name, tasks in assignments.items():
        task_titles = [task.title for task in tasks]
        print(f"  {worker_name}: {', '.join(task_titles)}")
    
    # Apply the assignments to the organization
    print("\n===== APPLYING ASSIGNMENTS TO ORGANIZATION =====")
    for worker_name, tasks in assignments.items():
        worker = next((w for w in org.workers if w.name == worker_name), None)
        if worker:
            for task in tasks:
                print(f"Assigning '{task.title}' to {worker.name}")
                task.assigned_worker = worker
                worker.assigned_tasks.append(task)
    
    # Print updated organization state
    print("\n===== UPDATED ORGANIZATION STATE =====")
    print("\nWorkers:")
    for worker in org.workers:
        task_count = len(worker.assigned_tasks)
        task_names = [task.title for task in worker.assigned_tasks]
        print(f"  {worker.name} ({task_count} tasks): {', '.join(task_names)}")
    
    print("\nRemaining unassigned tasks:")
    unassigned = [task for task in org.tasks if task.assigned_worker is None]
    if unassigned:
        for task in unassigned:
            print(f"  {task.title} (Priority: {task.priority})")
    else:
        print("  All tasks have been assigned!")

if __name__ == "__main__":
    main()