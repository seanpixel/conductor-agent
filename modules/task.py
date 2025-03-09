from datetime import datetime
from typing import List, Optional, Set

class Task:
    def __init__(self, title: str, description: str, priority: int, deadline: Optional[datetime] = None, 
                 required_skills: Optional[List[str]] = None, tags: Optional[List[str]] = None,
                 dependencies: Optional[List['Task']] = None, estimated_hours: Optional[float] = None):
        """
        :param title: Title of the task
        :param description: Description of the task
        :param priority: Priority level (higher is more important)
        :param deadline: Optional deadline for the task
        :param required_skills: Skills needed to complete this task
        :param tags: Tags for categorizing and finding related tasks
        :param dependencies: Tasks that must be completed before this one
        :param estimated_hours: Estimated time to complete the task
        """
        self.title = title
        self.description = description
        self.priority = priority
        self.deadline = deadline
        self.required_skills = required_skills or []
        self.tags = tags or []
        self.dependencies = dependencies or []
        self.estimated_hours = estimated_hours
        
        # Assignment information
        self.assigned_worker = None
        self.assignment_time = None
        self.completed_time = None
        self.status = "pending"  # pending, in_progress, completed, blocked
        
        # Contextual information
        self.notes = []
        self.subtasks = []
        self.related_tasks = []
        
    def add_note(self, note: str):
        """Add a note to the task"""
        self.notes.append({
            "content": note,
            "timestamp": datetime.now()
        })
    
    def add_subtask(self, title: str, description: str = ""):
        """Add a subtask to this task"""
        subtask = {
            "title": title,
            "description": description,
            "completed": False,
            "created_at": datetime.now()
        }
        self.subtasks.append(subtask)
        return subtask
    
    def is_blocked(self) -> bool:
        """Check if task is blocked by dependencies"""
        for dependency in self.dependencies:
            if dependency.status != "completed":
                return True
        return False
    
    def update_status(self):
        """Update the status of the task based on its current state"""
        if self.status == "completed":
            return
            
        if self.is_blocked():
            self.status = "blocked"
        elif self.assigned_worker:
            self.status = "in_progress"
        else:
            self.status = "pending"
    
    def urgency_score(self) -> float:
        """
        Calculate urgency score based on deadline and priority
        
        :return: Urgency score (higher is more urgent)
        """
        # Base score from priority
        score = self.priority
        
        # Add urgency based on deadline proximity
        if self.deadline:
            time_left = (self.deadline - datetime.now()).total_seconds() / 3600  # hours
            if time_left <= 0:
                # Overdue tasks get very high urgency boost
                score += 10
            elif time_left < 24:
                # Due in less than a day
                score += 5
            elif time_left < 72:
                # Due in less than 3 days
                score += 3
            elif time_left < 168:
                # Due in less than a week
                score += 1
                
        return score
    
    def __repr__(self):
        worker_name = self.assigned_worker.name if self.assigned_worker else "Unassigned"
        return f"Task({self.title}, Priority={self.priority}, Status={self.status}, Worker={worker_name})"