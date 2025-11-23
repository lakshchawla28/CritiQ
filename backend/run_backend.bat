@echo off
echo Starting Backend Services...

:: --- Run Django Server ---
start "Django Server" cmd /k "python manage.py runserver"

:: --- Run Redis Server ---
start "Redis Server" cmd /k "cd /d D:\Redis-x64-3.0.504 && redis-server.exe"

:: --- Run Celery Worker ---
start "Celery Worker" cmd /k "celery -A popcult_project worker -l info --pool=solo"

:: --- Run Celery Beat ---
start "Celery Beat" cmd /k "celery -A popcult_project beat -l info"

:: --- Run Daphne ASGI Server ---
start "Daphne Server" cmd /k "daphne -b 0.0.0.0 -p 8001 popcult_project.asgi:application"

echo All services started in separate windows!
pause

