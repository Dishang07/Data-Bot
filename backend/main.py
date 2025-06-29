from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .query_router import route_query
from .data_handler import store_csv_excel
from .unstructured_handler import process_unstructured_file

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
async def health_check():
    return {"status": "ok", "message": "PDF Bot API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/query")
async def query_router(query: str):
    try:
        result = await route_query(query)
        return {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@app.post("/upload-structured")
async def upload_structured(file: UploadFile = File(...)):
    try:
        result = await store_csv_excel(file)
        return result
    except Exception as e:
        return {"error": f"Upload failed: {str(e)}"}

@app.post("/upload-unstructured")
async def upload_unstructured(file: UploadFile = File(...)):
    try:
        result = await process_unstructured_file(file)
        return result
    except Exception as e:
        return {"error": f"Upload failed: {str(e)}"}
