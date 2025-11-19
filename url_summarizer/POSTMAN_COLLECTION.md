# Postman Collection for URL Summarizer History API

## Base URL
```
http://localhost:8003
```

## Authentication Setup
1. Go to **Authorization** tab
2. Select **Type**: Bearer Token
3. Enter your JWT token in the **Token** field

## Endpoints

### 1. Health Check
**Method**: GET  
**URL**: `{{base_url}}/health`

**Headers**: None required

**Response**:
```json
{
  "status": "healthy"
}
```

---

### 2. Create Summary (Saves to History)
**Method**: POST  
**URL**: `{{base_url}}/summarize`

**Headers**:
- Content-Type: application/json
- Authorization: Bearer <your-jwt-token>

**Body** (raw JSON):
```json
{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "summary_length": 5
}
```

**Response**:
```json
{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "summary": "Generated summary text here...",
    "summary_id": 123,
    "user_id": 456
}
```

---

### 3. Get User History (NEW)
**Method**: GET  
**URL**: `{{base_url}}/history`

**Query Parameters** (optional):
- `skip`: 0 (default)
- `limit`: 100 (default)

**Example URLs**:
- `{{base_url}}/history`
- `{{base_url}}/history?skip=0&limit=10`
- `{{base_url}}/history?limit=5`

**Headers**:
- Authorization: Bearer <your-jwt-token>

**Response**:
```json
[
    {
        "id": 123,
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "content": null,
        "summary": "Generated summary text here...",
        "summary_length": 5,
        "created_at": "2023-12-07T10:30:00.000Z",
        "user_id": 456
    },
    {
        "id": 122,
        "url": "https://example.com/article",
        "content": null,
        "summary": "Another summary here...",
        "summary_length": 5,
        "created_at": "2023-12-07T09:15:00.000Z",
        "user_id": 456
    }
]
```

---

### 4. Get Specific History Item (NEW)
**Method**: GET  
**URL**: `{{base_url}}/history/{{summary_id}}`

**Path Variables**:
- `summary_id`: The ID from the history response (e.g., 123)

**Headers**:
- Authorization: Bearer <your-jwt-token>

**Response**:
```json
{
    "id": 123,
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "content": null,
    "summary": "Generated summary text here...",
    "summary_length": 5,
    "created_at": "2023-12-07T10:30:00.000Z",
    "user_id": 456
}
```

---

### 5. Delete History Item (NEW)
**Method**: DELETE  
**URL**: `{{base_url}}/history/{{summary_id}}`

**Path Variables**:
- `summary_id`: The ID from the history response (e.g., 123)

**Headers**:
- Authorization: Bearer <your-jwt-token>

**Response**:
```json
{
    "message": "Summary deleted successfully"
}
```

---

### 6. Legacy Endpoints (Still Available)

#### Get User Summaries (Legacy)
**Method**: GET  
**URL**: `{{base_url}}/summaries/me/`

**Query Parameters** (optional):
- `skip`: 0 (default)
- `limit`: 100 (default)

#### Get Specific Summary (Legacy)
**Method**: GET  
**URL**: `{{base_url}}/summaries/{{summary_id}}`

---

## Testing Workflow

### Step 1: Test Health Check
```http
GET http://localhost:8003/health
```

### Step 2: Create a Summary
```http
POST http://localhost:8003/summarize
Content-Type: application/json
Authorization: Bearer <your-jwt-token>

{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "summary_length": 3
}
```

### Step 3: Get History
```http
GET http://localhost:8003/history
Authorization: Bearer <your-jwt-token>
```

### Step 4: Get Specific Item
```http
GET http://localhost:8003/history/123
Authorization: Bearer <your-jwt-token>
```

### Step 5: Delete Item
```http
DELETE http://localhost:8003/history/123
Authorization: Bearer <your-jwt-token>
```

---

## Environment Variables Setup

In Postman, you can set up environment variables:

**Variables**:
- `base_url`: `http://localhost:8003`
- `jwt_token`: `<your-actual-jwt-token>`

**Then use in requests**:
- URL: `{{base_url}}/history`
- Authorization: Bearer {{jwt_token}}

---

## Sample Test Collection JSON

You can import this directly into Postman:

```json
{
    "info": {
        "name": "URL Summarizer History API",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "variable": [
        {
            "key": "base_url",
            "value": "http://localhost:8003"
        },
        {
            "key": "jwt_token",
            "value": "your-jwt-token-here"
        }
    ],
    "item": [
        {
            "name": "Health Check",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{base_url}}/health",
                    "host": ["{{base_url}}"],
                    "path": ["health"]
                }
            }
        },
        {
            "name": "Create Summary",
            "request": {
                "method": "POST",
                "header": [
                    {
                        "key": "Content-Type",
                        "value": "application/json"
                    },
                    {
                        "key": "Authorization",
                        "value": "Bearer {{jwt_token}}"
                    }
                ],
                "body": {
                    "mode": "raw",
                    "raw": "{\n    \"url\": \"https://www.youtube.com/watch?v=dQw4w9WgXcQ\",\n    \"summary_length\": 5\n}"
                },
                "url": {
                    "raw": "{{base_url}}/summarize",
                    "host": ["{{base_url}}"],
                    "path": ["summarize"]
                }
            }
        },
        {
            "name": "Get History",
            "request": {
                "method": "GET",
                "header": [
                    {
                        "key": "Authorization",
                        "value": "Bearer {{jwt_token}}"
                    }
                ],
                "url": {
                    "raw": "{{base_url}}/history?limit=10",
                    "host": ["{{base_url}}"],
                    "path": ["history"],
                    "query": [
                        {
                            "key": "limit",
                            "value": "10"
                        }
                    ]
                }
            }
        },
        {
            "name": "Get Specific History Item",
            "request": {
                "method": "GET",
                "header": [
                    {
                        "key": "Authorization",
                        "value": "Bearer {{jwt_token}}"
                    }
                ],
                "url": {
                    "raw": "{{base_url}}/history/123",
                    "host": ["{{base_url}}"],
                    "path": ["history", "123"]
                }
            }
        },
        {
            "name": "Delete History Item",
            "request": {
                "method": "DELETE",
                "header": [
                    {
                        "key": "Authorization",
                        "value": "Bearer {{jwt_token}}"
                    }
                ],
                "url": {
                    "raw": "{{base_url}}/history/123",
                    "host": ["{{base_url}}"],
                    "path": ["history", "123"]
                }
            }
        }
    ]
}
```

---

## Common Error Responses

### 401 Unauthorized
```json
{
    "detail": "Not authenticated"
}
```

### 404 Not Found
```json
{
    "detail": "Summary not found in your history"
}
```

### 400 Bad Request
```json
{
    "detail": "Error message here"
}
```

---

## Tips for Testing

1. **Start with Health Check** to ensure server is running
2. **Create a Summary first** to have data in history
3. **Copy the summary_id** from the create response for testing specific endpoints
4. **Use environment variables** to avoid retyping URLs and tokens
5. **Test pagination** by using different `skip` and `limit` values
6. **Verify user isolation** by testing with different JWT tokens
