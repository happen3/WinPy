@echo off
:loop
choice /C "yN" /M "Are you sure to cleanup the entire workspace? This cannot be undone."

if errorlevel 2 exit /b 0
if errorlevel 1 goto delete

:delete
python runtime\cleanup.py