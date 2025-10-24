@echo off
echo Starting all microservices...

REM Start URL Summarizer
start "URL Summarizer" cmd /k "cd /d c:\Users\rohan\OneDrive\Desktop\Project\url_summarizer && python -m uvicorn main:app --reload --port 8000"

echo URL Summarizer starting at http://localhost:8000

timeout /t 2 /nobreak >nul

REM Start Auth Service
start "Auth Service" cmd /k "cd /d c:\Users\rohan\OneDrive\Desktop\Project\auth-service && python -m uvicorn src.auth.main:app --reload --port 8001"

echo Auth Service starting at http://localhost:8001

timeout /t 2 /nobreak >nul

REM Start File Service
start "File Service" cmd /k "cd /d c:\Users\rohan\OneDrive\Desktop\Project\file_service && python manage.py runserver 8002"

echo File Service starting at http://localhost:8002

timeout /t 2 /nobreak >nul

REM Start Summarization Backend
start "Summarization Backend" cmd /k "cd /d c:\Users\rohan\OneDrive\Desktop\Project\summarization_backend\summarizer_project && python manage.py runserver 8003"

echo Summarization Backend starting at http://localhost:8003

echo All services started! Each service is running in a separate window.
pause
