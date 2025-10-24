# File Service

A Django REST framework based file upload and management service.

## Features

- File upload with support for multiple file types (images, PDFs, documents, etc.)
- File listing, retrieval, and deletion
- User authentication and authorization
- File metadata storage (size, type, upload date, etc.)
- Public/private file access control
- RESTful API endpoints

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd file-service
   ```

2. **Create and activate a virtual environment**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (optional, for admin access)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Upload a File
- **URL**: `/api/files/upload/`
- **Method**: `POST`
- **Authentication**: Required
- **Content-Type**: `multipart/form-data`
- **Body**:
  - `file`: The file to upload (required)
  - `description`: Optional description for the file
  - `is_public`: Boolean, whether the file should be public (default: false)

### List All Files
- **URL**: `/api/files/`
- **Method**: `GET`
- **Authentication**: Required
- **Response**: List of all files uploaded by the authenticated user

### Get File Details
- **URL**: `/api/files/{id}/`
- **Method**: `GET`
- **Authentication**: Required
- **Response**: Details of the specified file

### Delete a File
- **URL**: `/api/files/{id}/`
- **Method**: `DELETE`
- **Authentication**: Required
- **Response**: Success or error message

## Environment Variables

Create a `.env` file in the project root with the following variables:

```
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Running Tests

```bash
python manage.py test
```

## Admin Interface

Access the Django admin interface at `/admin/` to manage files and users.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
