# Universal Document Intelligence Chatbot

A powerful RAG (Retrieval-Augmented Generation) chatbot that combines document analysis with web search capabilities. Upload PDF documents and ask questions - the system intelligently routes queries to use document content, web search, or both.

## Features

- **Multi-source Intelligence**: Answers questions using uploaded documents, web search, or hybrid approach
- **Intelligent Query Routing**: Automatically determines the best information source for each query
- **PDF Document Processing**: Upload and process PDF files with chunking and embedding
- **Vector Search**: FAISS-based similarity search for document retrieval
- **Web Search Integration**: Serper API with DuckDuckGo fallback
- **Streamlit Interface**: Clean, interactive web interface
- **Google Gemini Integration**: Uses Google's Gemini AI for high-quality responses

## Architecture

```
├── app.py                 # Main Streamlit application
├── config/
│   └── settings.py        # Configuration and environment variables
├── src/
│   ├── chatbot.py         # Main chatbot orchestration
│   ├── document_processor.py # PDF processing and chunking
│   ├── vector_store.py    # FAISS vector database management
│   ├── query_router.py    # Intelligent query routing
│   └── web_searcher.py    # Web search functionality
├── utils/
│   └── helpers.py         # Utility functions
└── data/
    ├── uploads/           # Uploaded PDF files
    └── vector_db/         # FAISS vector database
```

## Prerequisites

- Python 3.8+
- Google AI API key (for Gemini)
- Serper API key (optional, for web search)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd universal-chatbot
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Create a `requirements.txt` file with:

```txt
streamlit>=1.28.0
langchain>=0.1.0
langchain-google-genai>=1.0.0
langchain-community>=0.0.20
langchain-huggingface>=0.0.3
faiss-cpu>=1.7.4
sentence-transformers>=2.2.2
PyPDF2>=3.0.1
python-dotenv>=1.0.0
requests>=2.31.0
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Required: Google AI API Key
GEMINI_API_KEY=your_google_ai_api_key_here

# Optional: Web Search API Key (Serper)
SERPER_API_KEY=your_serper_api_key_here

# Model Settings (optional)
LLM_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Vector Store Settings (optional)
VECTOR_DB_PATH=data/vector_db
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Web Search Settings (optional)
MAX_SEARCH_RESULTS=5
```

### 5. Get API Keys

#### Google AI API Key (Required)
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key to your `.env` file

#### Serper API Key (Optional)
1. Visit [Serper.dev](https://serper.dev/)
2. Sign up for a free account
3. Get your API key from the dashboard
4. Copy the key to your `.env` file

Note: Web search will fall back to DuckDuckGo if Serper API key is not provided.

## Usage

### 1. Start the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### 2. Upload Documents

- Use the sidebar to upload PDF files
- Multiple files can be uploaded simultaneously
- Files are automatically processed and indexed

### 3. Ask Questions

- Type questions in the chat interface
- The system automatically determines whether to use:
  - **Document search**: For questions about uploaded content
  - **Web search**: For current events, general knowledge
  - **Hybrid**: For complex queries requiring both sources

### 4. View Sources

- Click "Sources" to see which documents or web pages were used
- Route indicators show how each query was processed

## Query Routing Logic

The system intelligently routes queries based on keywords and content:

- **Document Route**: Default for uploaded content, specific document references
- **Web Route**: Triggered by keywords like "latest", "current", "2024", "explain", "what is"
- **Hybrid Route**: For queries that might benefit from both document and web information

## Configuration Options

Modify `config/settings.py` or use environment variables:

```python
# Model settings
LLM_MODEL = "gemini-2.5-flash"  # or "gemini-pro"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Document processing
CHUNK_SIZE = 1000        # Size of document chunks
CHUNK_OVERLAP = 200      # Overlap between chunks

# Search settings
MAX_SEARCH_RESULTS = 5   # Maximum web search results
```

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Ensure your `.env` file is in the project root
   - Verify API keys are correct and active
   - Check API quotas and billing

2. **Module Import Errors**
   - Ensure virtual environment is activated
   - Install all requirements: `pip install -r requirements.txt`
   - Check Python version (3.8+ required)

3. **PDF Processing Issues**
   - Ensure PDFs are not password-protected
   - Try with different PDF files
   - Check file permissions

4. **Vector Store Issues**
   - Delete `data/vector_db` folder to reset
   - Re-upload documents to rebuild index

### Performance Tips

1. **Large Documents**: Adjust `CHUNK_SIZE` for better processing
2. **Memory Usage**: Use smaller embedding models for limited resources
3. **Search Speed**: Reduce `MAX_SEARCH_RESULTS` for faster responses

## File Structure Details

```
project/
├── app.py                      # Streamlit main app
├── .env                        # Environment variables (create this)
├── requirements.txt            # Python dependencies (create this)
├── config/
│   ├── __init__.py
│   └── settings.py             # Configuration settings
├── src/
│   ├── __init__.py
│   ├── chatbot.py              # Main chatbot class
│   ├── document_processor.py   # PDF processing
│   ├── vector_store.py         # FAISS vector database
│   ├── query_router.py         # Query routing logic
│   └── web_searcher.py         # Web search functionality
├── utils/
│   ├── __init__.py
│   └── helpers.py              # Utility functions
└── data/                       # Created automatically
    ├── uploads/                # Uploaded files
    └── vector_db/              # Vector database files
```

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Formatting
```bash
black .
isort .
```

### Adding New Features

1. Document processors: Extend `DocumentProcessor` for new file types
2. Search providers: Add new search APIs in `WebSearcher`
3. Routing logic: Modify `QueryRouter` for custom routing rules

## Security Notes

- Keep API keys secure and never commit them to version control
- The `.env` file is excluded from git by default
- Consider using environment-specific configurations for production

## License

This project is open source. Please check the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the configuration options
3. Ensure all dependencies are properly installed
4. Verify API keys are correctly set up
