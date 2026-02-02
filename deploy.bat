@echo off
cd /d C:\Users\elamuruganm\Desktop\Desktop\Zap\Cursor\saas_app

echo Linking Railway project...
railway link --project 5fad707a-bcd2-4fb6-805f-282da19a459a --environment production

echo.
echo Adding PostgreSQL...
(echo postgres) | railway add -d postgres
timeout /t 20 /nobreak

echo.
echo Adding backend...
(echo autobotela-sys/saas-copy-trading) | railway add -r autobotela-sys/saas-copy-trading -s backend

echo.
echo Adding frontend...
(echo autobotela-sys/saas-copy-trading) | railway add -r autobotela-sys/saas-copy-trading -s frontend

echo.
echo Deployment commands complete!
pause
