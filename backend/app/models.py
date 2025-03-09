from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

class WorkerCreate(BaseModel):
    """Model for creating a new worker"""
    name: str
    is_human: bool
    skills: List[str] = []
    experience_description: str = ""

class WorkerBase(BaseModel):
    """Base model for worker responses"""
    name: str
    is_human: bool
    skills: List[str]
    workload: float
    experience_description: str
    performance_metrics: Dict[str, Any]

class TaskBase(BaseModel):
    """Base model for task responses"""
    title: str
    description: str
    priority: int 
    deadline: Optional[datetime] = None
    required_skills: List[str] = []
    tags: List[str] = []
    estimated_hours: Optional[float] = None
    status: str
    assignment_time: Optional[datetime] = None
    completed_time: Optional[datetime] = None
    assigned_worker: Optional[str] = None
    notes: List[Dict[str, Any]] = []
    dependencies: List[str] = []

class TaskCreate(BaseModel):
    """Model for creating a new task"""
    title: str
    description: str
    priority: int = Field(ge=1, le=10)
    deadline_days: Optional[int] = None
    required_skills: List[str] = []
    tags: List[str] = []
    estimated_hours: Optional[float] = None
    dependency_ids: List[int] = []

class TaskResponse(TaskBase):
    """Full task response model"""
    pass

class WorkerResponse(WorkerBase):
    """Full worker response model"""
    assigned_tasks: List[TaskResponse] = []
    completed_tasks: List[TaskResponse] = []

class OrganizationResponse(BaseModel):
    """Organization response model"""
    name: str
    workers: List[WorkerResponse] = []
    tasks: List[TaskResponse] = []
    completed_tasks: List[TaskResponse] = []

class AssignTaskRequest(BaseModel):
    """Request model for assigning a task"""
    worker_name: str

class CompleteTaskRequest(BaseModel):
    """Request model for completing a task"""
    feedback: Optional[str] = None