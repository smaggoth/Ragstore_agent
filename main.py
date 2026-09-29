#uv run uvicorn main:app --reload
import shutil
from pathlib import Path
from qdrant_client.http.exceptions import ResponseHandlingException
import google.genai.errors as genai_errors
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from pydantic import BaseModel
from brain.graph import build_graph
from ingestion.vectorstore import process_document, create_collection, save_chunks, COLLECTION_NAME

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.brain = await build_graph()
    yield

app = FastAPI(lifespan=lifespan)

class MessageInput(BaseModel):
    thread_id: str
    message: str

@app.post('/chat')
async def chat(request: Request, data: MessageInput):
    agent = request.app.state.brain
    config = {'configurable': {'thread_id': data.thread_id}}

    result = await agent.ainvoke(
        {'messages': [{'role': 'user', 'content': data.message}]},
        config
    )
    return {'Response': result['messages'][-1].content}

@app.post('/documents')
async def add_document(new_file: UploadFile=File(...)):
    if not new_file.filename.endswith('.md'):
        raise HTTPException(status_code=400, detail='Invalid format')
    temp_path = Path("docs") / new_file.filename
    temp_path.parent.mkdir(exist_ok=True)
    try:
        with open(temp_path, 'wb') as f:
            shutil.copyfileobj(new_file.file, f)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f'File cannot be saved in directory: {e}') from e

    try:
        chunks, embeddings, dimension = process_document(temp_path)
    except genai_errors.APIError as e:
        raise HTTPException(status_code=502, detail=f'Error during embedding process: {e}') from e

    try:
        save_chunks(chunks, embeddings, dimension)
    except ResponseHandlingException as e:
        raise HTTPException(status_code=503, detail=f'Impossible to connect with Qdrant collection: {e}') from e

    return {'message': f'File {new_file.filename} ingested', 'chunks_created': len(chunks)}