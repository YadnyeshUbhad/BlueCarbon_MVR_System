@echo off
echo Starting BlueCarbon MRV System...
echo.
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Starting Flask development server...
echo Open http://127.0.0.1:5000 in your browser
echo Press Ctrl+C to stop the server
echo.

python app.py

pause