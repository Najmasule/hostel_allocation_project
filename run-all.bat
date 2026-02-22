@echo off
setlocal

set ROOT=c:\Users\NAJMA SULE\Desktop\hostel_project\hostel_allocation_project

echo Starting Django backend on 127.0.0.1:8000 ...
start "Hostel Backend" cmd /k "cd /d %ROOT% && python manage.py runserver 127.0.0.1:8000 --noreload"

timeout /t 2 >nul

echo Starting Vite frontend on 127.0.0.1:5174 ...
start "Hostel Frontend" cmd /k "cd /d %ROOT%\frontend && npm run dev"

echo.
echo Open: http://127.0.0.1:5174/
echo.
endlocal
