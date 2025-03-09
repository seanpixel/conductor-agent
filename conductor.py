import os
import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from modules.organization import Organization
from modules.worker import Worker
from modules.task import Task

from generator import generate

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Conductor")

class Conductor:
    """
    Conductor is the main orchestration agent that manages task assignment and execution
    by matching workers (humans or AI) with appropriate tasks based on skills, priority,
    and context.
    """
    
    def __init__(self, organization: Organization, base_prompt: str, api_key: Optional[str] = None):
        """
        Initialize the conductor with an organization, base prompt, and optional API key
        
        :param organization: The organization to manage
        :param base_prompt: Base context prompt describing the organization, its goals, and context
        :param api_key: Optional API key for Claude API access
        """
        self.organization = organization
        self.base_prompt = base_prompt
        self.api_key = api_key or os.environ.get("CLAUDE_API_KEY")
        
        logger.info(f"Conductor initialized for organization: {organization.name}")
        logger.info(f"Base prompt length: {len(base_prompt)} characters")
    
    def get_full_context(self) -> str:
        """
        Generate the full context for the AI, combining the base prompt with
        current organization information and worker experience.
        
        :return: Complete context string for the AI
        """
        workers_info = self.organization.get_workers_txt()
        tasks_info = self.organization.get_tasks_txt()
        
        # Gather worker experience summaries to provide rich context for the LLM
        worker_experience = "WORKER EXPERIENCE PROFILES:\n\n"
        for worker in self.organization.workers:
            worker_experience += worker.get_experience_summary() + "\n\n"
        
        full_context = f"""
            {self.base_prompt}

            CURRENT ORGANIZATION STATE:

            {workers_info}

            {tasks_info}
            
            {worker_experience}
        """
        
        return full_context
    
    def generate_task_assignments(self) -> Dict[str, List[Task]]:
        """
        Generate task assignments for all unassigned tasks in the organization.
        
        :return: Dictionary mapping worker names to lists of their assigned tasks
        """
        context = self.get_full_context()
        
        # We don't need to create simplified worker metrics anymore since we're including 
        # full experience profiles at the organization level. This avoids duplication and
        # ensures we're using the LLM's understanding rather than rigid metrics.
        
        # Just gather task dependencies for additional context
        task_context_text = "Task Dependencies and Information:\n"
        for i, task in enumerate(self.organization.tasks, 1):
            if task.assigned_worker is None:
                dependencies = ", ".join([f"Task {self.organization.tasks.index(dep) + 1}" 
                                       for dep in task.dependencies]) if task.dependencies else "None"
                required_skills = ", ".join(task.required_skills) if task.required_skills else "Any"
                estimated_hours = f"{task.estimated_hours:.1f}" if task.estimated_hours else "Unknown"
                
                task_context_text += f"Task {i}: Required Skills={required_skills}, " \
                                   f"Dependencies={dependencies}, Estimated Hours={estimated_hours}\n"
        
        prompt = f"""
            {context}
            
            {task_context_text}

            Based on the information above, assign the unassigned tasks to the most appropriate workers.
            Consider:
            1. Worker skills and task requirements
            2. Task priorities and deadlines
            3. Worker current workload
            4. Whether tasks are better suited for humans or AI
            5. Task dependencies (tasks with dependencies should be assigned to workers who can work on them together)
            6. Worker's past experience with similar tasks (refer to the worker experience profiles)
            7. Estimated time to complete the task vs. worker availability

            First, provide your reasoning for the assignments, and then list the final assignments.
            Use the task numbers (Task 1, Task 2, etc.) instead of task titles in your assignments.

            Return your response in this exact format:

            REASONING:
            [Your detailed reasoning for task assignments]

            ASSIGNMENTS:
            [Worker Name]: Task 1, Task 2, ...
            [Another Worker Name]: Task 3, ...
            ...
            """
        
        # Call Claude API with the assignment prompt
        response = generate(prompt)
        print(response)
        
        # Process the response to extract assignments
        assignments = self._parse_assignment_response(response)
        
        # Debug assignment information
        print("DEBUG - Assignment decisions before applying:")
        for worker_name, tasks in assignments.items():
            task_titles = [task.title for task in tasks]
            print(f"  {worker_name}: {task_titles}")
        
        # Apply assignments to the organization
        successful_assignments = {}
        for worker_name, tasks in assignments.items():
            worker = next((w for w in self.organization.workers if w.name == worker_name), None)
            if worker:
                # Initialize list for successful assignments
                successful_tasks = []
                
                for task in tasks:
                    # Double-check task is available for assignment
                    if task.assigned_worker is None:
                        print(f"DEBUG - Assigning task '{task.title}' to {worker_name}")
                        worker.assign_task(task)
                        task.update_status()
                        successful_tasks.append(task)
                    else:
                        print(f"DEBUG - Task '{task.title}' already assigned to {task.assigned_worker.name}, skipping assignment to {worker_name}")
                
                # Record only successful assignments
                if successful_tasks:
                    successful_assignments[worker_name] = successful_tasks
            else:
                print(f"DEBUG - Worker '{worker_name}' not found")
        
        # Debug final assignment results
        print("DEBUG - Final assignment results:")
        for worker_name, tasks in successful_assignments.items():
            task_titles = [task.title for task in tasks]
            print(f"  {worker_name}: {task_titles}")
        
        return successful_assignments
        
    def assign_new_task(self, task: Task) -> Optional[Worker]:
        """
        Add a new task and assign it to the most appropriate worker,
        either through automatic assignment or AI recommendation
        
        :param task: The new task to assign
        :return: The worker assigned to the task or None if no assignment
        """
        # Add the task to the organization
        self.organization.add_task(task)
        
        # Generate a context focused on just this task
        context = self.get_full_context()
        single_task_info = f"""
        New Task to Assign:
        Title: {task.title}
        Description: {task.description}
        Priority: {task.priority}
        Deadline: {task.deadline.strftime('%Y-%m-%d %H:%M') if task.deadline else "None"}
        Required Skills: {', '.join(task.required_skills) if task.required_skills else "Any"}
        Estimated Hours: {task.estimated_hours if task.estimated_hours else "Unknown"}
        Tags: {', '.join(task.tags) if hasattr(task, 'tags') and task.tags else "None"}
        """
        
        prompt = f"""
            {context}
            
            {single_task_info}
            
            Based on the information above, determine which worker would be the most appropriate 
            to assign this new task to. Consider each worker's skills, current workload, 
            past experience, and availability in relation to this task.
            
            First, provide your reasoning for the assignment recommendation, and then give your recommendation.
            Simply output the worker name after ASSIGNMENT: so that we can easily parse which worker this assignment goes to.

            REASONING:
            [Your detailed reasoning for the assignment recommendation]
            
            ASSIGNMENT:
            [Worker Name]
            """
        
        # Call Claude API
        response = generate(prompt)
        print(response)
        
        
        # Parse using new simple parser, name is always last
        parsed_worker = response.splitlines()[-1]
        worker = None

        try:
            for w in self.organization.workers:
                if parsed_worker == w.name:
                    w.assign_task(task)
                    worker = w

            print(f"ASSIGNED TASK {task} TO WORKER {parsed_worker}")
        except:
            worker = self.organization.workers[0]
    
        return worker
    
    def _parse_assignment_response(self, response: str) -> Dict[str, List[Task]]:
        """
        Parse the AI response to extract task assignments
        
        :param response: AI response as string
        :return: Dictionary mapping worker names to lists of tasks
        """
        assignments = {}
        
        # Extract response text from API response
        try:
            response_text = response
            
            # Find the ASSIGNMENTS section
            if "ASSIGNMENTS:" in response_text:
                assignments_section = response_text.split("ASSIGNMENTS:")[1].strip()
                
                # Log the raw assignments section for debugging
                print(f"DEBUG - Raw assignments section:\n{assignments_section}")
                
                # Parse each line of assignments
                for line in assignments_section.split("\n"):
                    if ":" in line:
                        worker_name, task_nums_str = line.split(":", 1)
                        worker_name = worker_name.strip()
                        
                        # Find the worker object
                        worker = next((w for w in self.organization.workers if w.name == worker_name), None)
                        
                        if worker:
                            print(f"DEBUG - Processing assignments for worker: {worker_name}")
                            
                            # Extract task numbers
                            task_assignments = []
                            
                            # Split by comma and handle any variations in task format
                            for task_ref in task_nums_str.split(","):
                                task_ref = task_ref.strip()
                                print(f"DEBUG - Processing task reference: '{task_ref}'")
                                
                                # Extract task number (e.g., "Task 1" -> 1)
                                if "Task" in task_ref or "task" in task_ref.lower():
                                    try:
                                        # Handle various formats: "Task 1", "task 1", "Task #1"
                                        task_ref_cleaned = task_ref.lower().replace("task", "").replace("#", "").strip()
                                        task_num = int(task_ref_cleaned)
                                        print(f"DEBUG - Parsed task number: {task_num}")
                                        
                                        # Tasks are 1-indexed in the output but 0-indexed in the list
                                        if 1 <= task_num <= len(self.organization.tasks):
                                            task = self.organization.tasks[task_num - 1]
                                            print(f"DEBUG - Found task: {task.title}")
                                            
                                            # Include task for assignment, even if already assigned - we'll handle this later
                                            task_assignments.append(task)
                                        else:
                                            print(f"DEBUG - Task number out of range: {task_num}")
                                    except ValueError as ve:
                                        print(f"DEBUG - Could not parse task number from: '{task_ref}', error: {ve}")
                                        logger.warning(f"Could not parse task number from: '{task_ref}', error: {ve}")
                            
                            assignments[worker_name] = task_assignments
                            print(f"DEBUG - Assigned {len(task_assignments)} tasks to {worker_name}")
                        else:
                            print(f"DEBUG - Worker not found: {worker_name}")
        
        except Exception as e:
            logger.error(f"Error parsing assignment response: {e}")
            print(f"DEBUG - Error parsing assignment response: {e}")
        
        return assignments
        
    def handle_task_completion(self, task, feedback=None):
        """
        Mark a task as completed and update worker metrics
        
        :param task: The task to mark as completed
        :param feedback: Optional feedback on the task completion (e.g., quality score, comments)
        """
        if task.assigned_worker:
            # Record completion time
            task.assigned_worker.complete_task(task)
            
            # Move task to completed list
            if task in self.organization.tasks:
                self.organization.tasks.remove(task)
                self.organization.completed_tasks.append(task)
            
            # Record feedback if provided
            if feedback:
                task.add_note(f"Completion feedback: {feedback}")
            
            logger.info(f"Task '{task.title}' marked as completed by {task.assigned_worker.name}")
            
            # Check for dependent tasks that might be unblocked now
            for dependent_task in self.organization.tasks:
                if task in dependent_task.dependencies:
                    dependent_task.dependencies.remove(task)
                    dependent_task.update_status()
                    
                    # If it was the last dependency, log that it's now unblocked
                    if not dependent_task.is_blocked() and dependent_task.status == "blocked":
                        dependent_task.status = "pending"
                        logger.info(f"Task '{dependent_task.title}' is now unblocked")
                    
            return True
        else:
            logger.warning(f"Cannot complete task '{task.title}' - no assigned worker")
            return False
    
    def print_organization_state(self):
        """
        Print the current state of the organization
        """
        print("\nWorkers:")
        for worker in self.organization.workers:
            assigned_tasks = [task.title for task in worker.assigned_tasks]
            completed_tasks = len(worker.completed_tasks)
            assigned_str = ", ".join(assigned_tasks) if assigned_tasks else ""
            print(f"  {worker.name} ({len(worker.assigned_tasks)} active, {completed_tasks} completed): {assigned_str}")
            
            if worker.performance_metrics["tasks_completed"] > 0:
                print(f"    Avg. completion time: {worker.performance_metrics['avg_completion_time']:.2f} hours")
                print(f"    Current workload: {worker.get_workload():.2f}")
                
                # Display a snippet of experience if available
                if worker.experience_description:
                    experience_snippet = worker.experience_description.split("\n\n")[0][:100]
                    if len(experience_snippet) == 100:
                        experience_snippet += "..."
                    print(f"    Recent experience: {experience_snippet}")
        
        print("\nTasks by status:")
        pending = [t for t in self.organization.tasks if t.status == "pending"]
        in_progress = [t for t in self.organization.tasks if t.status == "in_progress"]
        blocked = [t for t in self.organization.tasks if t.status == "blocked"]
        completed = self.organization.completed_tasks
        
        print(f"  Pending ({len(pending)}): {', '.join([t.title for t in pending]) if pending else 'None'}")
        print(f"  In Progress ({len(in_progress)}): {', '.join([t.title for t in in_progress]) if in_progress else 'None'}")
        print(f"  Blocked ({len(blocked)}): {', '.join([t.title for t in blocked]) if blocked else 'None'}")
        print(f"  Completed ({len(completed)}): {', '.join([t.title for t in completed[-5:]]) if completed else 'None'}{' ...' if len(completed) > 5 else ''}")
        
        if any(task.deadline and task.deadline < datetime.now() for task in self.organization.tasks):
            overdue = [t for t in self.organization.tasks if t.deadline and t.deadline < datetime.now()]
            print(f"\nWARNING: {len(overdue)} overdue tasks: {', '.join([t.title for t in overdue])}")
