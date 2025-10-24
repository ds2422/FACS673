# Start URL Summarizer
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'c:\Users\rohan\OneDrive\Desktop\Project\url_summarizer'; python -m uvicorn main:app --reload --port 8000; pause"

# Start Auth Service
# Start Auth Service
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'c:\Users\rohan\OneDrive\Desktop\Project\auth-service'; python -m uvicorn src.main:app --reload --port 8001; pause"
# Start File Service
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'c:\Users\rohan\OneDrive\Desktop\Project\file_service'; $env:PYTHONPATH='c:\Users\rohan\OneDrive\Desktop\Project\file_service'; python manage.py runserver 8002; pause"

# Start Summarization Backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'c:\Users\rohan\OneDrive\Desktop\Project\summarization_backend\summarizer_project'; $env:PYTHONPATH='c:\Users\rohan\OneDrive\Desktop\Project\summarization_backend'; python manage.py runserver 8003; pause"