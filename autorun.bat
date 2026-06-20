@echo off
cd /d "I:\Giang\Tools\scihub_mutual_aid_auto_checkin"
call .venv\Scripts\activate.bat
python smartquant_auto_login.py
echo Done checking in.
