from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, models
from ingestion.chunking import chunck_markdown
from ingestion.embedding import embeddings_call
import uuid
from pathlib import Path

client = QdrantClient(url='http://localhost:6333')
COLLECTION_NAME = 'vector_store'


def process_document(path):
    """
    Function to process the incoming markdown document
    Args:
        path: Source path for document
    """
    chunks = chunck_markdown(path)
    embeddings, dimension = embeddings_call(chunks)
    return chunks, embeddings, dimension


def create_collection(name, dimension):
        """
        Function to create the Qdrant collection for the embeddings
        Args:
            name: Collection name
            dimension: Vectors dimension
        """
        if not client.collection_exists(name):
            client.create_collection(
                collection_name= name,
                vectors_config={
                     'dense': VectorParams(
                    size=dimension,
                    distance=Distance.COSINE)
                },
                sparse_vectors_config={
                     'bm25': models.SparseVectorParams(
                          modifier=models.Modifier.IDF
                     )
                },
            )
        return name


def  save_chunks(chunks:list, embeddings:list, dimension:int):
    """
    Function to create the Point Structure for Qdrant vector store
    Args:
        chunks: Chunks created from documents
        embeddings: Embeddings created for each document
    """
    points = []
    for _, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        points.append(PointStruct(
            id=uuid.uuid4(),
            vector={
                 'dense':embedding.values,
                 'bm25':models.Document(text=chunk, model='Qdrant/bm25')    
            },
            payload={'text':chunk}
        ))
    collection = create_collection(COLLECTION_NAME, dimension)
    client.upsert(collection_name=collection, points=points)

if __name__ == '__main__':

    files_path = Path(__file__).resolve().parent.parent/ "docs" / "README.md"
    chunks, embeddings, dimension = process_document(files_path)
    save_chunks(chunks, dimension, embeddings)