from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


class DocumentType(str, Enum):
    loan_disclosure = "loan_disclosure"
    appraisal = "appraisal"


class DocumentCreate(BaseModel):
    filename: str = Field(..., min_length=1)
    doc_type: DocumentType
    size: int = Field(gt=0)


class DocumentResponse(BaseModel):
    id: int
    filename: str
    doc_type: DocumentType
    status: str


# Fake database
fake_db: list[dict] = []


@router.post("/", response_model=DocumentResponse)
def create_document(doc: DocumentCreate):
    new_doc = {
        "id": len(fake_db) + 1,
        "filename": doc.filename,
        "doc_type": doc.doc_type,
        "status": "pending"
    }
    fake_db.append(new_doc)
    return new_doc


@router.get("/", response_model=list[DocumentResponse])
def list_documents():
    return fake_db


@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document(doc_id: int):
    for doc in fake_db:
        if doc["id"] == doc_id:
            return doc
    return {"error": "Not found"}
