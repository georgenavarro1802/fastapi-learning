from fastapi import APIRouter
import asyncio

router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"]
)


@router.post("/{doc_id}")
async def analyze_document(doc_id: int, prompt: str = "Summarize this document"):
    # Simulate call to LLM
    await asyncio.sleep(1)
    return {
        "doc_id": doc_id,
        "prompt": prompt,
        "result": f"Analysis complete for document {doc_id}",
        "confidence": 0.95
    }


@router.get("/{doc_id}/status")
def analysis_status(doc_id: int):
    return {
        "doc_id": doc_id,
        "status": "completed",
        "progress": 100
    }
