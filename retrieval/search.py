from ingestion.embedding import embeddings_call
from ingestion.vectorstore import COLLECTION_NAME
from qdrant_client import QdrantClient
from qdrant_client import models

client = QdrantClient(url='http://localhost:6333')

def search(query: str, limit: int=5) -> dict:
    """
    Function to calculate the best results from the hybrid search in the vector store
    Args:
        query: question from the user
        limit: Limit of results retrieved by the algorithm
    """
    output = {}
    embedding, _ = embeddings_call([query])
    query_embedding = embedding[0].values
    result = client.query_points(
        collection_name=COLLECTION_NAME,
        prefetch=[
            models.Prefetch(
                query=query_embedding,
                using='dense',
                limit=limit
            ),
            models.Prefetch(
                query=models.Document(text=query, model='Qdrant/bm25'),
                using='bm25',
                limit=limit
            ),
        ],
        query = models.FusionQuery(fusion=models.Fusion.RRF),
        limit = 3,
    )
    for point in result.points:
        output[point.id] = {'Score':point.score, 'payload':point.payload}
    return output

if __name__ == '__main__':
    query = 'fases del proyecto' 
    print(search(query))