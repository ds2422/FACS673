# History API Documentation

The URL Summarizer service now includes a comprehensive history API that allows users to track, retrieve, and manage their summary history.

## Features

- **Automatic History Tracking**: All summaries are automatically saved to the database
- **User-Specific History**: Each user only sees their own summary history
- **Pagination Support**: Large history sets can be paginated
- **CRUD Operations**: Full create, read, update, delete functionality
- **Chronological Ordering**: History is displayed with most recent summaries first

## API Endpoints

### 1. Get User History
```
GET /history?skip=0&limit=100
```

**Description**: Retrieve the current user's complete summary history with pagination.

**Parameters**:
- `skip` (optional): Number of items to skip (default: 0)
- `limit` (optional): Maximum number of items to return (default: 100)

**Response**: Array of Summary objects ordered by most recent first

**Example**:
```bash
curl -X GET "http://localhost:8003/history?skip=0&limit=10" \
     -H "Authorization: Bearer <your-jwt-token>"
```

### 2. Get Specific History Item
```
GET /history/{summary_id}
```

**Description**: Retrieve a specific summary from the user's history by ID.

**Parameters**:
- `summary_id` (required): The ID of the summary to retrieve

**Response**: Single Summary object

**Example**:
```bash
curl -X GET "http://localhost:8003/history/123" \
     -H "Authorization: Bearer <your-jwt-token>"
```

### 3. Delete History Item
```
DELETE /history/{summary_id}
```

**Description**: Delete a specific summary from the user's history.

**Parameters**:
- `summary_id` (required): The ID of the summary to delete

**Response**: Success message

**Example**:
```bash
curl -X DELETE "http://localhost:8003/history/123" \
     -H "Authorization: Bearer <your-jwt-token>"
```

## Legacy Endpoints

The following endpoints are still available for backward compatibility:

- `GET /summaries/me/` - Same functionality as `GET /history`
- `GET /summaries/{summary_id}` - Same functionality as `GET /history/{summary_id}`

## Data Model

Each summary in the history contains:

```json
{
  "id": 123,
  "url": "https://example.com/article",
  "content": "Full extracted content (optional)",
  "summary": "Generated summary text",
  "summary_length": 5,
  "created_at": "2023-12-07T10:30:00.000Z",
  "user_id": 456
}
```

## Usage Examples

### Python Client Example

```python
import requests

# Base URL
BASE_URL = "http://localhost:8003"
HEADERS = {
    "Authorization": "Bearer <your-jwt-token>",
    "Content-Type": "application/json"
}

# Get user history
response = requests.get(f"{BASE_URL}/history?limit=10", headers=HEADERS)
history = response.json()
print(f"Found {len(history)} summaries in history")

# Get specific summary
summary_id = history[0]["id"]
response = requests.get(f"{BASE_URL}/history/{summary_id}", headers=HEADERS)
summary = response.json()
print(f"Summary: {summary['summary']}")

# Delete a summary
response = requests.delete(f"{BASE_URL}/history/{summary_id}", headers=HEADERS)
print(response.json())  # {"message": "Summary deleted successfully"}
```

### JavaScript/TypeScript Example

```typescript
interface Summary {
  id: number;
  url: string;
  summary: string;
  summary_length: number;
  created_at: string;
  user_id: number;
}

class HistoryAPI {
  private baseUrl = 'http://localhost:8003';
  private token: string;

  constructor(token: string) {
    this.token = token;
  }

  private getHeaders() {
    return {
      'Authorization': `Bearer ${this.token}`,
      'Content-Type': 'application/json'
    };
  }

  async getHistory(skip = 0, limit = 100): Promise<Summary[]> {
    const response = await fetch(
      `${this.baseUrl}/history?skip=${skip}&limit=${limit}`,
      { headers: this.getHeaders() }
    );
    return response.json();
  }

  async getSummary(id: number): Promise<Summary> {
    const response = await fetch(
      `${this.baseUrl}/history/${id}`,
      { headers: this.getHeaders() }
    );
    return response.json();
  }

  async deleteSummary(id: number): Promise<{message: string}> {
    const response = await fetch(
      `${this.baseUrl}/history/${id}`,
      { 
        method: 'DELETE',
        headers: this.getHeaders()
      }
    );
    return response.json();
  }
}
```

## Security

- All history endpoints require JWT authentication
- Users can only access their own summary history
- User isolation is enforced at the database level
- Tokens are validated against the auth-service

## Error Handling

Common error responses:

- `401 Unauthorized`: Invalid or missing JWT token
- `404 Not Found`: Summary not found in user's history
- `400 Bad Request`: Invalid parameters or database error
- `500 Internal Server Error`: Unexpected server error

## Performance Considerations

- History queries are optimized with database indexes
- Pagination prevents memory issues with large datasets
- Results are ordered by creation date for efficient retrieval
- Consider implementing caching for frequently accessed history
