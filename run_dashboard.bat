@echo off
echo Starting Twitter DM Dashboard...
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Installing Google API dependencies...
pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2
echo.
echo Starting dashboard...
echo Dashboard will open in your browser at http://localhost:8501
echo.
streamlit run dashboard.py
pause 