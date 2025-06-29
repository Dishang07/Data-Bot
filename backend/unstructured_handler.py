from PyPDF2 import PdfReader
from docx import Document
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize clients but don't connect immediately
qdrant = None
model = None

def get_qdrant_client():
    global qdrant
    if qdrant is None:
        try:
            qdrant = QdrantClient(
                url=os.getenv("QDRANT_HOST"),
                api_key=os.getenv("QDRANT_API_KEY")
            )
        except Exception as e:
            print(f"Warning: Could not connect to Qdrant: {e}")
            qdrant = None
    return qdrant

def get_model():
    global model
    if model is None:
        try:
            model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            print(f"Warning: Could not load SentenceTransformer model: {e}")
            model = None
    return model

COLLECTION_NAME = "documents"

def ensure_collection():
    client = get_qdrant_client()
    if client is None:
        return False
    
    try:
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
        return True
    except Exception as e:
        print(f"Warning: Could not create collection: {e}")
        return False

async def process_unstructured_file(file):
    try:
        client = get_qdrant_client()
        embedding_model = get_model()
        
        if client is None or embedding_model is None:
            return {"error": "Vector database or embedding model not available"}
        
        ensure_collection()
        
        ext = file.filename.split('.')[-1].lower()
        content = await file.read()
        text = ""

        if ext == "pdf":
            reader = PdfReader(BytesIO(content))
            text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
        elif ext == "docx":
            doc = Document(BytesIO(content))
            text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        elif ext == "txt":
            text = content.decode('utf-8')
        else:
            return {"error": f"Unsupported file format: {ext}"}

        if not text.strip():
            return {"error": "No text could be extracted from the file."}

        chunks = text.split(". ")
        chunks = [chunk.strip() for chunk in chunks if chunk.strip()]  # Remove empty chunks
        vectors = embedding_model.encode(chunks).tolist()

        # Create points in the correct format for Qdrant
        points = []
        for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
            point = PointStruct(
                id=i,
                vector=vector,
                payload={"text": chunk}
            )
            points.append(point)
        
        # Upload points to Qdrant
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        return {"message": f"{ext.upper()} file uploaded and indexed successfully."}
    except Exception as e:
        return {"error": f"Failed to process unstructured file: {str(e)}"}

def search_unstructured(query):
    try:
        client = get_qdrant_client()
        embedding_model = get_model()
        
        if client is None or embedding_model is None:
            return "Vector database or embedding model not available"
        
        q_vec = embedding_model.encode(query).tolist()
        results = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=q_vec,
            limit=3
        )
        return " ".join([res.payload['text'] for res in results])
    except Exception as e:
        return f"Search failed: {str(e)}"
