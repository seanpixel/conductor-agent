from modules.worker import Worker
from modules.task import Task
from datetime import datetime
import logging
from typing import List, Dict, Optional, Set, Any

logger = logging.getLogger("Organization")

class Organization:
    def __init__(self, name: str):
        """
        :param name: Name of the organization/team
        """
        self.name = name
        self.workers = []  # List of Worker objects
        self.tasks = []  # List of Task objects
        self.skill_directory = {}  # Maps skills to workers who have them
        self.completed_tasks = []  # Archive of completed tasks
        
    def add_worker(self, worker: Worker):
        """
        Add a worker to the organization and update skill directory
        
        :param worker: Worker to add
        """
        self.workers.append(worker)
        
        # Update skill directory
        for skill in worker.skills:
            if skill not in self.skill_directory:
                self.skill_directory[skill] = []
            self.skill_directory[skill].append(worker)
            
        logger.info(f"Added worker: {worker.name} with skills: {', '.join(worker.skills)}")
    
    def add_task(self, task: Task, auto_assign: bool = False):
        """
        Add a task to the organization and optionally auto-assign it
        
        :param task: Task to add
        :param auto_assign: Whether to automatically assign the task
        :return: The task object (possibly with worker assigned)
        """
        self.tasks.append(task)
        
        # Update any related tasks
        if task.related_tasks:
            for related_task in task.related_tasks:
                if related_task not in self.tasks and related_task not in self.completed_tasks:
                    # Only update existing tasks
                    continue
                if task not in related_task.related_tasks:
                    related_task.related_tasks.append(task)
        
        # Auto-assign if requested
        if auto_assign:
            self._auto_assign_task(task)
            
        logger.info(f"Added task: {task.title} (Priority: {task.priority})")
        return task
        
    def _auto_assign_task(self, task: Task) -> Optional[Worker]:
        """
        Automatically assign a task to the most suitable worker
        
        :param task: Task to assign
        :return: Worker that was assigned, or None if no suitable worker
        """
        best_worker = None
        best_score = -1
        
        # Consider all workers (not just those with exact skill matches)
        candidates = set(self.workers)
        
        for worker in candidates:
            # Simple prioritization based on workload
            workload_factor = 1.0 / (1.0 + worker.get_workload())  # Lower workload is better
            
            # Get task deadline urgency
            urgency = task.urgency_score()
            
            # Instead of complex matching, use simpler heuristics
            # Have some skills in common
            has_some_skills = any(skill in worker.skills for skill in task.required_skills) if task.required_skills else True
            
            # Boost score for matching any skills
            skill_boost = 1.5 if has_some_skills else 1.0
            
            # Calculate final score (simpler approach)
            score = workload_factor * urgency * skill_boost
            
            if score > best_score:
                best_score = score
                best_worker = worker
        
        # Assign task if we found a suitable worker
        if best_worker:
            best_worker.assign_task(task)
            task.update_status()
            logger.info(f"Auto-assigned task '{task.title}' to {best_worker.name}")
            return best_worker
            
        logger.info(f"Could not auto-assign task '{task.title}' - no suitable worker found")
        return None

    def get_workers_txt(self) -> str:
        """
        Returns a formatted string with information about all workers in the organization.
        This can be fed into the conductor agent.
        
        :return: String containing all worker information
        """
        if not self.workers:
            return "No workers in the organization."
        
        workers_info = [f"Total Workers: {len(self.workers)}"]
        
        for i, worker in enumerate(self.workers, 1):
            worker_type = "Human" if worker.is_human else "AI"
            skills_str = ", ".join(worker.skills)
            task_count = len(worker.assigned_tasks)
            
            worker_info = [
                f"Worker {i}: {worker.name}",
                f"Type: {worker_type}",
                f"Skills: {skills_str}",
                f"Assigned Tasks: {task_count}"
            ]
            
            workers_info.append("\n".join(worker_info))
        
        return "\n\n".join(workers_info)
    
    def get_tasks_txt(self) -> str:
        """
        Returns a formatted string with information about all tasks in the organization.
        This can be fed into the conductor agent.
        
        :return: String containing all task information
        """
        if not self.tasks:
            return "No tasks in the organization."
        
        tasks_info = [f"Total Tasks: {len(self.tasks)}"]
        
        # Group tasks by assignment status
        unassigned_tasks = []
        assigned_tasks = []
        
        for task in self.tasks:
            if task.assigned_worker is None:
                unassigned_tasks.append(task)
            else:
                assigned_tasks.append(task)
        
        # Add unassigned tasks
        if unassigned_tasks:
            tasks_info.append(f"\nUnassigned Tasks ({len(unassigned_tasks)}):")
            for i, task in enumerate(unassigned_tasks, 1):
                deadline_str = task.deadline.strftime('%Y-%m-%d %H:%M') if task.deadline else "No deadline"
                
                task_info = [
                    f"Task {i}: {task.description}",
                    f"Priority: {task.priority}",
                    f"Deadline: {deadline_str}"
                ]
                
                tasks_info.append("\n".join(task_info))
        
        # Add assigned tasks
        if assigned_tasks:
            tasks_info.append(f"\nAssigned Tasks ({len(assigned_tasks)}):")
            for i, task in enumerate(assigned_tasks, 1):
                deadline_str = task.deadline.strftime('%Y-%m-%d %H:%M') if task.deadline else "No deadline"
                assigned_to = task.assigned_worker.name if task.assigned_worker else "Unassigned"
                
                task_info = [
                    f"Task {i}: {task.description}",
                    f"Priority: {task.priority}",
                    f"Deadline: {deadline_str}",
                    f"Assigned to: {assigned_to}"
                ]
                
                tasks_info.append("\n".join(task_info))
        
        return "\n\n".join(tasks_info)

    def __repr__(self):
        return f"Organization({self.name}, Workers={len(self.workers)}, Tasks={len(self.tasks)})"