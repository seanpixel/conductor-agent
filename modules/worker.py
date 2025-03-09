from datetime import datetime
from typing import List, Optional, Dict, Any

class Worker:
    def __init__(self, name: str, is_human: bool, skills: List[str], experience_description: str = ""):
        """
        :param name: Name of the worker (human or AI)
        :param is_human: Boolean indicating if it's a human or an AI
        :param skills: List of skills the worker has
        :param experience_description: Optional initial description of worker's experience
        """
        self.name = name
        self.is_human = is_human
        self.skills = skills
        self.assigned_tasks = []  # Tasks currently assigned
        self.completed_tasks = []  # Tasks previously completed
        self.task_history = []  # History of tasks with timestamps
        
        # Narrative description of experience, updated as tasks are completed
        self.experience_description = experience_description
        
        # Simple performance metrics (without complex proficiency calculations)
        self.performance_metrics = {
            "avg_completion_time": 0,
            "tasks_completed": 0
        }
    
    def assign_task(self, task):
        """
        Assign a task to this worker
        
        :param task: The task to assign
        """
        self.assigned_tasks.append(task)
        task.assigned_worker = self
        task.assignment_time = datetime.now()
        
        # Record in task history
        self.task_history.append({
            "task": task,
            "action": "assigned",
            "timestamp": datetime.now()
        })
    
    def complete_task(self, task):
        """
        Mark a task as completed by this worker
        
        :param task: The task to complete
        """
        if task in self.assigned_tasks:
            self.assigned_tasks.remove(task)
            self.completed_tasks.append(task)
            task.completed_time = datetime.now()
            task.status = "completed"
            
            # Record in task history
            self.task_history.append({
                "task": task,
                "action": "completed",
                "timestamp": datetime.now()
            })
            
            # Update performance metrics
            self._update_performance_metrics(task)
            
            # Update experience description
            self._update_experience_description(task)
    
    def _update_performance_metrics(self, task):
        """
        Update worker performance metrics based on completed task
        
        :param task: The completed task
        """
        # Calculate completion time
        if hasattr(task, 'assignment_time') and hasattr(task, 'completed_time'):
            completion_time = (task.completed_time - task.assignment_time).total_seconds() / 3600  # hours
            
            # Update average completion time
            total_time = self.performance_metrics["avg_completion_time"] * self.performance_metrics["tasks_completed"]
            self.performance_metrics["tasks_completed"] += 1
            self.performance_metrics["avg_completion_time"] = (total_time + completion_time) / self.performance_metrics["tasks_completed"]
    
    def _update_experience_description(self, task):
        """
        Update the worker's experience description based on a completed task
        
        :param task: The completed task
        """
        # Get estimated completion time if available
        completion_time = None
        if hasattr(task, 'assignment_time') and hasattr(task, 'completed_time'):
            completion_time = (task.completed_time - task.assignment_time).total_seconds() / 3600  # hours
            
        # Create a description of this task experience
        task_experience = f"Completed '{task.title}' "
        
        # Add skill information
        if hasattr(task, 'required_skills') and task.required_skills:
            task_experience += f"using skills in {', '.join(task.required_skills)} "
        
        # Add timing information
        if completion_time is not None and hasattr(task, 'estimated_hours') and task.estimated_hours:
            if completion_time < task.estimated_hours:
                task_experience += f"faster than expected ({completion_time:.1f} vs {task.estimated_hours:.1f} hours). "
            elif completion_time > task.estimated_hours:
                task_experience += f"taking longer than expected ({completion_time:.1f} vs {task.estimated_hours:.1f} hours). "
            else:
                task_experience += f"in the expected time ({completion_time:.1f} hours). "
        elif completion_time is not None:
            task_experience += f"in {completion_time:.1f} hours. "
        else:
            task_experience += ". "
            
        # Add context about related tasks
        if hasattr(task, 'related_tasks') and task.related_tasks:
            related_titles = [rt.title for rt in task.related_tasks if rt in self.completed_tasks]
            if related_titles:
                task_experience += f"This built on previous experience with {', '.join(related_titles)}. "
                
        # Add the task description for context
        task_experience += f"Task involved: {task.description}"
        
        # Add to experience description
        if self.experience_description:
            self.experience_description += f"\n\n{task_experience}"
        else:
            self.experience_description = task_experience
    
    def get_workload(self) -> float:
        """
        Calculate the current workload of the worker
        
        :return: Workload score (higher means more busy)
        """
        # Simple calculation based on number of tasks and their priorities
        if not self.assigned_tasks:
            return 0.0
        
        total_priority = sum(task.priority for task in self.assigned_tasks)
        return total_priority / 10.0 * len(self.assigned_tasks)
    
    def get_experience_summary(self) -> str:
        """
        Get a summary of worker's experience for LLM context
        
        :return: String describing worker's experience and current workload
        """
        summary = f"Worker: {self.name} ({'Human' if self.is_human else 'AI'})\n"
        summary += f"Skills: {', '.join(self.skills)}\n"
        summary += f"Tasks completed: {len(self.completed_tasks)}\n"
        summary += f"Current workload: {self.get_workload():.1f} (based on {len(self.assigned_tasks)} active tasks)\n"
        
        if self.performance_metrics["tasks_completed"] > 0:
            summary += f"Average completion time: {self.performance_metrics['avg_completion_time']:.1f} hours\n"
            
        # Add active tasks
        if self.assigned_tasks:
            active_tasks = [task.title for task in self.assigned_tasks]
            summary += f"Currently working on: {', '.join(active_tasks)}\n"
            
        # Add recent task experience
        if self.experience_description:
            summary += f"\nExperience:\n{self.experience_description}\n"
            
        return summary
    
    def __repr__(self):
        return f"Worker({self.name}, Human={self.is_human}, Skills={self.skills}, Active_Tasks={len(self.assigned_tasks)})"
