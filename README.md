# PDF Bot - Smart Query Chatbot

A chatbot application that can process both structured (CSV/Excel) and unstructured (PDF/DOCX) files and answer questions about them.

## Features

- Upload and query CSV/Excel files with natural language queries
- Upload and index PDF/DOCX/TXT files for semantic search
- Interactive chat interface built with Streamlit
- FastAPI backend for processing queries and file uploads
- Robust error handling and connection status monitoring
- Smart file routing based on file extensions

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables** (`.env` file should already exist):
   ```
   GEMINI_API_KEY=your_api_key
   QDRANT_HOST=your_qdrant_url
   QDRANT_API_KEY=your_qdrant_key
   ```

3. **Start the backend** (Terminal 1):
   ```bash
   python run_backend.py
   ```

4. **Start the frontend** (Terminal 2):
   ```bash
   streamlit run frontend/app.py
   ```

5. **Access the application**: Open http://localhost:8501 in your browser

## Supported File Formats

### Structured Data (SQL Queries)
- **CSV** (`.csv`) - Comma-separated values
- **Excel** (`.xlsx`, `.xls`) - Microsoft Excel files

### Unstructured Data (Semantic Search)  
- **PDF** (`.pdf`) - Portable Document Format
- **Word** (`.docx`) - Microsoft Word documents
- **Text** (`.txt`) - Plain text files

## Usage

1. **Upload Files**: Use the sidebar to upload supported file formats
2. **Ask Questions**: Type natural language questions in the chat interface
3. **Smart Routing**: The system automatically determines whether to use SQL queries or semantic search
4. **Get Answers**: Receive relevant answers from your uploaded data

## Status Check

Run the status check script to verify everything is working:
```bash
python status_check.py
```

## Testing

- **Comprehensive test**: `python comprehensive_test.py`
- **API test**: `python test_api.py`
- **External APIs**: `python test_external_apis.py`

## Error Handling

The application now includes comprehensive error handling:
- Connection errors are detected and displayed to users
- Invalid file formats are handled gracefully
- Network timeouts are caught and reported
- Server errors are displayed with helpful messages
- JSON parsing errors are handled properly

## Architecture

- **Backend**: FastAPI server with endpoints for file upload and query processing
- **Frontend**: Streamlit chat interface with connection monitoring
- **Database**: SQLite for structured data storage
- **Vector Database**: Qdrant for unstructured data indexing
- **AI**: Google Gemini for query classification and SQL generation
- **Embeddings**: SentenceTransformers for document embedding

## Troubleshooting

### Connection Error
If you see "Backend server is not running":
1. Make sure the backend is started with `python run_backend.py`
2. Check that port 8000 is not blocked by firewall
3. Verify the `.env` file contains valid API keys

### API Errors
If you see API-related errors:
1. Check your Gemini API key is valid and has quota
2. Verify your Qdrant credentials are correct
3. Ensure you have internet connectivity

### File Upload Issues
If file uploads fail:
1. Check the file format is supported:
   - **Structured**: CSV, XLSX, XLS
   - **Unstructured**: PDF, DOCX, TXT
2. Ensure the file is not corrupted
3. Check file size limits
4. Verify the file extension matches the content
