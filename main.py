from fastapi import FastAPI
from routers import documents, analysis, workflows

app = FastAPI(title="Document Processor API")

app.include_router(documents.router)
app.include_router(analysis.router)
app.include_router(workflows.router)


@app.get("/", tags=["Health"])
def root():
    return {"message": "Document Processor API", "docs": "/docs"}