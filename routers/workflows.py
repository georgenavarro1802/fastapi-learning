from datetime import datetime
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/workflows",
    tags=["Workflows"]
)


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class WorkflowCreate(BaseModel):
    name: str = Field(..., min_length=3)
    doc_ids: list[int]
    priority: Priority = Priority.medium


class WorkflowResponse(BaseModel):
    id: int = Field(..., description="Unique identifier for the workflow")
    name: str = Field(..., min_length=3)
    doc_ids: list[int]
    priority: Priority
    status: str = Field(..., description="Current status of the workflow")
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: int = Field(..., description="User ID of the creator")

# Fake database
fake_db: list[dict] = []

# Dependency
def get_current_user(user_id: int) -> dict:
    return {"user_id": user_id, "role": "analyst"}

# Endpoints
@router.post("/", response_model=WorkflowResponse)
def create_workflow(workflow: WorkflowCreate, current_user: dict = Depends(get_current_user)):
    new_workflow = {
        "id": len(fake_db) + 1,
        "name": workflow.name,
        "doc_ids": workflow.doc_ids,
        "priority": workflow.priority,
        "status": "pending",
        "created_by": current_user["user_id"]
    }
    fake_db.append(new_workflow)
    return new_workflow


@router.get("/", response_model=list[WorkflowResponse])
def list_workflows():
    return fake_db


@router.get("/{workflow_id}", response_model=WorkflowResponse)
def get_workflow(workflow_id: int):
    for workflow in fake_db:
        if workflow["id"] == workflow_id:
            return workflow
    raise HTTPException(status_code=404, detail="Workflow not found")
