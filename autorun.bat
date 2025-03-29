@echo off
echo activating conda env
call "C:\ProgramData\Anaconda3\Scripts\activate.bat" machine_learning
echo Running Python script...
cd /d "C:\scihub_mutual_aid_auto_checkin"
echo Current working directory:
echo %CD%

python smartquant_auto_login.py

echo Done checking in.