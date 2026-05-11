@echo off
pip install pyinstaller
if exist requirements.txt pip install -r requirements.txt
pyinstaller --onefile --windowed main.py
pause
