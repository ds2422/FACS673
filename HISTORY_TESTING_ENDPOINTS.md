# History API Testing Guide

## 🧪 Testing Endpoints

Here are the exact endpoints to test the history functionality for each microservice:

---

## 1. URL Summarizer Service (Port 8003) ✅
**Base URL**: `http://localhost:8003`

### Endpoints:
```bash
# Get user's summary history
GET /history?page=1&page_size=10
Headers: Authorization: Bearer <JWT_TOKEN>

# Get specific summary from history
GET /history/{summary_id}
Headers: Authorization: Bearer <JWT_TOKEN>

# Delete summary from history
DELETE /history/{summary_id}
Headers: Authorization: Bearer <JWT_TOKEN>

# Create a summary (to test history)
POST /summarize
Headers: Authorization: Bearer <JWT_TOKEN>
Body: 
{
    "url": "https://example.com",
    "summary_length": 5
}
```

---

## 2. File Service (Port 8001) ✅
**Base URL**: `http://localhost:8001`

### Endpoints:
```bash
# Get user's file history (NEW)
GET /api/files/history/?page=1&page_size=10
Headers: Authorization: Bearer <JWT_TOKEN>

# Upload a file (to test history)
POST /api/files/upload/
Headers: Authorization: Bearer <JWT_TOKEN>
Content-Type: multipart/form-data
Body: file=<your_file>

# Get specific file details
GET /api/files/{file_id}/
Headers: Authorization: Bearer <JWT_TOKEN>

# Delete file
DELETE /api/files/{file_id}/
Headers: Authorization: Bearer <JWT_TOKEN>
```

---

## 3. Comparison Service (Port 8002) ✅
**Base URL**: `http://localhost:8002`

### Endpoints:
```bash
# Get user's comparison history (NEW)
GET /api/comparison/history/?user_id=123&page=1&page_size=10

# Delete comparison from history (NEW)
DELETE /api/comparison/history/{comparison_id}/?user_id=123

# Create comparison (to test history)
POST /api/comparison/compare/
Body:
{
    "source1_type": "text",
    "source1_content": "First document text",
    "source2_type": "text", 
    "source2_content": "Second document text",
    "user_id": 123
}

# Get specific comparison
GET /api/comparison/comparison/{comparison_id}/
```

---

## 4. Summarization Backend (Port 8000) ✅
**Base URL**: `http://localhost:8000`

### Endpoints:
```bash
# Get user's summary history (NEW)
GET /api/summaries/history/?page=1&page_size=10
Headers: Authorization: Bearer <JWT_TOKEN>

# Create summary (to test history)
POST /api/summaries/
Headers: Authorization: Bearer <JWT_TOKEN>
Body:
{
    "title": "Test Summary",
    "original_text": "This is the original text to summarize...",
    "summarized_text": "This is the summarized version..."
}

# Get specific summary
GET /api/summaries/{summary_id}/
Headers: Authorization: Bearer <JWT_TOKEN>

# Delete summary
DELETE /api/summaries/{summary_id}/
Headers: Authorization: Bearer <JWT_TOKEN>
```

---

## 🔧 Testing Checklist

### Step 1: Get JWT Token
```bash
# Get token from auth service
POST http://localhost:8004/token
Body:
{
    "username": "your_email@example.com",
    "password": "your_password"
}
```

### Step 2: Test Each Service

#### URL Summarizer Tests:
- [ ] Create a summary via POST /summarize
- [ ] Get history via GET /history
- [ ] Verify pagination (page=1, page_size=5)
- [ ] Get specific summary via GET /history/{id}
- [ ] Delete summary via DELETE /history/{id}
- [ ] Verify user isolation (different users see different data)

#### File Service Tests:
- [ ] Upload a file via POST /api/files/upload/
- [ ] Get file history via GET /api/files/history/
- [ ] Verify pagination works
- [ ] Verify chronological ordering (newest first)
- [ ] Delete file via DELETE /api/files/{id}/

#### Comparison Service Tests:
- [ ] Create comparison via POST /api/comparison/compare/
- [ ] Get history via GET /api/comparison/history/?user_id=123
- [ ] Verify pagination works
- [ ] Delete comparison via DELETE /api/comparison/history/{id}/
- [ ] Verify user_id filtering works

#### Summarization Backend Tests:
- [ ] Create summary via POST /api/summaries/
- [ ] Get history via GET /api/summaries/history/
- [ ] Verify pagination works
- [ ] Verify JWT authentication works
- [ ] Delete summary via DELETE /api/summaries/{id}/

---

## 📊 Expected Response Formats

### History List Response:
```json
{
    "results": [
        {
            "id": 1,
            "title": "Example",
            "created_at": "2025-01-19T10:30:00Z",
            "other_fields": "..."
        }
    ],
    "count": 25,
    "page": 1,
    "page_size": 10,
    "total_pages": 3,
    "has_next": true,
    "has_previous": false
}
```

### Success Response:
```json
{
    "message": "Item deleted successfully"
}
```

### Error Response:
```json
{
    "error": "Item not found in your history"
}
```

---

## 🚀 Quick Test Commands

### Using curl:

```bash
# Test URL Summarizer History
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     "http://localhost:8003/history?page=1&page_size=5"

# Test File Service History  
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     "http://localhost:8001/api/files/history/?page=1&page_size=5"

# Test Comparison Service History
curl "http://localhost:8002/api/comparison/history/?user_id=123&page=1&page_size=5"

# Test Summarization Backend History
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     "http://localhost:8000/api/summaries/history/?page=1&page_size=5"
```

---

## 🔍 Validation Points

### For Each Service Check:
1. **Authentication**: JWT tokens work correctly
2. **Pagination**: Page parameters work, metadata is correct
3. **User Isolation**: Users only see their own data
4. **Ordering**: Results are sorted by created_at descending
5. **Error Handling**: 404 for missing items, 400 for bad requests
6. **Response Format**: Consistent JSON structure

### Expected Status Codes:
- `200 OK` - Successful GET requests
- `201 Created` - Successful POST requests  
- `204 No Content` - Successful DELETE requests
- `400 Bad Request` - Invalid parameters
- `401 Unauthorized` - Missing/invalid JWT
- `404 Not Found` - Item not found
- `500 Internal Server Error` - Server errors

---

## 📝 Testing Script Template

```bash
#!/bin/bash
JWT_TOKEN="your_jwt_token_here"
USER_ID="123"

echo "Testing URL Summarizer History..."
curl -H "Authorization: Bearer $JWT_TOKEN" \
     "http://localhost:8003/history?page=1&page_size=5"

echo -e "\n\nTesting File Service History..."
curl -H "Authorization: Bearer $JWT_TOKEN" \
     "http://localhost:8001/api/files/history/?page=1&page_size=5"

echo -e "\n\nTesting Comparison Service History..."
curl "http://localhost:8002/api/comparison/history/?user_id=$USER_ID&page=1&page_size=5"

echo -e "\n\nTesting Summarization Backend History..."
curl -H "Authorization: Bearer $JWT_TOKEN" \
     "http://localhost:8000/api/summaries/history/?page=1&page_size=5"
```

Use this guide to systematically test all the history APIs I've implemented! 🧪
