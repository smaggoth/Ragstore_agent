import os
from dotenv import load_dotenv
from google import genai
from pathlib import Path
from ingestion.chunking import chunck_markdown

load_dotenv()

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))


def embeddings_call(chunks: list):
    """
    Function to create embeddings with Gemini from markdown documents
    Args:
        chunks: Chunks created from markdown documents
    """
    result = client.models.embed_content(
        model='gemini-embedding-001',
        contents=chunks
    )
    return result.embeddings, len(result.embeddings[0].values)

if __name__ == '__main__':
    files_path = Path(__file__).resolve().parent.parent/ "docs" / "README.md"
    chunks = chunck_markdown(files_path)
    embeddings, dimension = embeddings_call(chunks)
    print(len(embeddings), len(chunks))
    print(dimension)