@echo off
REM Smart Crop Bot — start API + public tunnel (Cloudflare)
REM Keep this window open while demoing.

cd /d c:\Krishi

echo.
echo [1/2] Starting FastAPI on http://127.0.0.1:8000 ...
start "SmartCrop-API" cmd /k "cd /d c:\Krishi && .venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8000"

timeout /t 4 /nobreak >nul

echo [2/2] Starting Cloudflare tunnel (public HTTPS)...
echo When the URL appears, copy it into:
echo   1) .env  APP_PUBLIC_URL=https://....trycloudflare.com
echo   2) Twilio Sandbox webhook = that URL + /webhooks/twilio/whatsapp
echo   3) Restart the API window after changing .env
echo.

npx --yes cloudflared tunnel --url http://127.0.0.1:8000
