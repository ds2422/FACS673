# Document Comparison Service

A FastAPI-based microservice for comparing text documents and URLs.

## Features

- Compare text content from different sources (raw text, URLs)
- Calculate similarity scores between documents
- Identify common and unique keywords
- Generate comparison summaries
- RESTful API endpoints

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the service:
   ```bash
   uvicorn main:app --reload --port 8001
   ```

## API Documentation

Once running, access the interactive API documentation at:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Environment Variables

Create a `.env` file in the project root with the following variables:

```
# Server configuration
PORT=8001
DEBUG=True
```

## API Endpoints

### Compare Documents
- **URL**: `POST /api/compare`
- **Request Body**:
  ```json
  {
    "source1_type": "text",
    "source1_content": "First document content",
    "source2_type": "text",
    "source2_content": "Second document content",
    "user_id": "optional-user-id"
  }
  ```
- **Response**:
  ```json
  {
    "comparison_id": "comp_1",
    "similarity_score": 0.75,
    "common_keywords": ["shared", "words"],
    "unique_to_source1": ["unique1", "words1"],
    "unique_to_source2": ["unique2", "words2"],
    "summary": "The documents have a similarity score of...",
    "created_at": "2023-10-22T12:00:00.000000"
  }
  ```

### Get Comparison Result
- **URL**: `GET /api/compare/{comparison_id}`
- **Response**: Same as compare endpoint

### Health Check
- **URL**: `GET /health`
- **Response**:
  ```json
  {
    "status": "healthy",
    "service": "comparison-service"
  }
  ```

## Development

### Running Tests
```bash
pytest
```

### Linting
```bash
flake8 .
```

### Formatting
```bash
black .
```
