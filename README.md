# FastAPI Learning

Hands-on examples covering FastAPI fundamentals — from basic endpoints to dependency injection, async patterns, and project organization with routers.

## Why FastAPI?

FastAPI has become the go-to framework for building modern Python APIs, especially for AI applications. Key advantages:

- **Async-first**: Built on ASGI, handles concurrent requests efficiently
- **Type-safe**: Leverages Python type hints for automatic validation
- **Auto-documentation**: OpenAPI/Swagger UI generated from your code
- **Pydantic integration**: First-class support for data validation

## What's Covered

| File | Concepts |
|------|----------|
| `main_tutorial.py` | Path/query params, Pydantic models, Field validation, Dependency Injection, async/await |
| `main.py` | Router integration, project organization |
| `routers/documents.py` | CRUD endpoints, response models |
| `routers/analysis.py` | Async endpoints for AI workloads |
| `routers/workflows.py` | Combining DI, enums, Pydantic, and HTTPException |
| `pydantic_advanced.py` | model_dump, model_validate, nested models, dynamic models, computed fields |

## Key Concepts Demonstrated

### 1. Automatic Validation
```python
@app.get("/users/{user_id}")
def get_user(user_id: int):  # Automatically validates and converts
    return {"user_id": user_id}
```

### 2. Pydantic Models for Request/Response
```python
class Document(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)
    size: int = Field(gt=0, le=50_000_000)
```

### 3. Dependency Injection
```python
def get_llm_client(provider: str = "openai"):
    return {"provider": provider, "status": "ready"}

@app.get("/analyze")
def analyze(llm: dict = Depends(get_llm_client)):
    return {"client": llm}
```

### 4. Async Endpoints
```python
@app.get("/process")
async def process_document():
    await asyncio.sleep(2)  # Non-blocking
    return {"status": "done"}
```

## Quick Start
```bash
# Clone the repo
git clone https://github.com/georgenavarro1802/fastapi-learning.git
cd fastapi-learning

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the API
uvicorn main:app --reload

# Open in browser
# http://127.0.0.1:8000/docs
```

## Requirements

- Python 3.11+
- Dependencies in `requirements.txt`

## Next Steps

This repo pairs well with:
- [litellm-learning](https://github.com/georgenavarro1802/litellm-learning) - Multi-provider LLM abstraction
- [langgraph-learning](https://github.com/georgenavarro1802/langgraph-learning) - Agentic workflows

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Pydantic Documentation](https://docs.pydantic.dev)

## License

MIT - Feel free to use, modify, and learn from this code.