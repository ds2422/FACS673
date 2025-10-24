# URL Summarization Service

A FastAPI-based service that provides summaries of web content from various URLs, including YouTube videos and regular web pages.

## Features

- Summarize YouTube videos using their transcripts
- Extract and summarize content from regular web pages
- Configurable summary length
- RESTful API endpoints
- CORS enabled for frontend integration

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd url_summarizer
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Service

```bash
uvicorn main:app --reload
```

The service will be available at `http://localhost:8000`

## API Endpoints

### Summarize a URL

**POST** `/summarize`

Request body:
```json
{
    "url": "https://example.com",
    "summary_length": 5
}
```

### Health Check

**GET** `/health`

## Example Usage

### Using cURL

```bash
curl -X POST "http://localhost:8000/summarize" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "summary_length": 3}'
```

### Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/summarize",
    json={"url": "https://example.com", "summary_length": 5}
)
print(response.json())
```

## Environment Variables

No environment variables are required for basic functionality. For production use, consider adding:

- `PORT`: Port to run the server on (default: 8000)
- `DEBUG`: Set to `False` in production

## License

MIT
