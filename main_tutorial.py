import asyncio
import time
from datetime import datetime
from enum import Enum
from math import prod
from typing import Optional
from xml.dom.minidom import Document

from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field, field_validator, model_validator

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI"}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id, "type": type(user_id).__name__}

@app.get("/search")
def search(q: str, limit: int = 10, skip: int = 0):
    return {
        "query": q,
        "limit": limit,
        "skip": skip
    }


class DocumentType(str, Enum):
    loan_disclosure = "loan_disclosure"
    appraisal = "appraisal"
    income_verification = "income_verification"


class Document(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)
    content_type: str
    size: int = Field(gt=0, le=50_000_000)
    doc_type: DocumentType
    uploaded_at: datetime = Field(default_factory=datetime.now)
    notes: Optional[str] = None

    @field_validator("filename")
    @classmethod
    def filename_must_have_extension(cls, v: str) -> str:
        if "." not in v:
            raise ValueError("Filename must have an extension")
        return v.lower()

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, v: str) -> str:
        allowed = ["application/pdf", "application/msword"]
        if v not in allowed:
            raise ValueError(f"content_type must be one of {allowed}")
        return v

    @model_validator(mode="after")
    def validate_size_by_doc_type(self) -> Document:
        size_limits = {
            DocumentType.loan_disclosure: 10_000_000,   # 10 MB
            DocumentType.appraisal: 50_000_000,         # 50 MB
            DocumentType.income_verification: 5_000_000 # 5MB
        }
        max_size = size_limits.get(self.doc_type, 50_000_000)
        if self.size > max_size:
            raise ValueError(
                f"{self.doc_type.value} max size is {max_size / 1_000_000}MB"
            )
        return self


@app.post("/documents")
def create_document(doc: Document):
    return {
        "received": doc.filename,
        "size_mb": doc.size / 1024 / 1024
    }



def get_settings():
    return {
        "app_name": "Document Processor",
        "max_file_size": 50_000_000,
        "llm_provider": "openai",
        "llm_api_key": "sk-xxxxx",
        "max_tokens": 4000
    }

@app.get("/settings")
def get_settings(settings: dict = Depends(get_settings)):
    return settings


def get_llm_client(settings: dict = Depends(get_settings)):
    return {
        "provider": settings["llm_provider"],
        "api_key": settings["llm_api_key"][:10] + "...", # masked
        "max_tokens": settings["max_tokens"]
    }

def get_document_processor(llm: dict = Depends(get_llm_client)):
    return {
        "llm": llm,
        "supported_formats": ["pdf", "docx"],
        "status": "ready"
    }

@app.get("/processor/status")
def processor_status(processor: dict = Depends(get_document_processor)):
    return processor

@app.get("/analyze")
def analyze_document(doc_name: str, llm: dict = Depends(get_llm_client)):
    return {
        "document": doc_name,
        "analyzed_with": llm["name"],
        "model": llm["model"]
    }


class LLMClient:

    def __init__(self, provider: str = "openai"):
        self.provider = provider
        self.models = {
            "openai": "gpt-4",
            "azure": "gpt-4-turbo",
            "local": "mistral"
        }

    def get_model(self) -> str:
        return self.models.get(self.provider, "gpt-4")

    def complete(self, prompt: str) -> str:
        # Here will go the real call to LLM provider
        return f"[{self.provider}:{self.get_model()}] Response to: {prompt[:50]}..."

@app.get("/complete")
def complete_prompt(prompt: str, llm: LLMClient = Depends()):
    return {
        "provider": llm.provider,
        "model": llm.get_model(),
        "response": llm.complete(prompt)
    }



class AsyncLLMClient:

    def __init__(self, provider: str = "openai"):
        self.provider = provider

    async def complete(self, prompt: str) -> str:
        await asyncio.sleep(2)  # simulate async call
        return f"[{self.provider}] Analyzed: {prompt[:30]}..."


async def get_async_llm(provider: str = "openai") -> AsyncLLMClient:
    # here we could make setup async (conections, auth, etc.)
    client = AsyncLLMClient(provider)
    return client

@app.get("/analyze-async")
async def analyze_async(prompt: str, llm: AsyncLLMClient = Depends(get_async_llm)):
    result = await llm.complete(prompt)
    return {"result": result}


@app.get("/slow-sync")
def slow_sync():
    time.sleep(2)
    return {"type": "sync", "message": "done"}


@app.get("/slow-async")
async def slow_async():
    await asyncio.sleep(2)
    return {"type": "async", "message": "done"}
