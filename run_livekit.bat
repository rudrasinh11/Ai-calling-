@echo off
TITLE LiveKit Local Server & Shashvat Jewels Voice Receptionist
chcp 65001 >nul
cd /d I:\jewellery_voice_receptionist

echo ===========================================================
echo  💎 LIVEKIT SERVER + SHASHVAT JEWELS INBOUND AI AGENT 💎
echo ===========================================================
echo.
echo [1/2] Starting LiveKit Server (ws://127.0.0.1:7880)...
start "LiveKit-Server" /min "I:\jewellery_voice_receptionist\livekit\livekit-server.exe" --dev

echo [2/2] Starting Inbound WebPhone Receptionist (http://localhost:8055)...
start "Shashvat-WebPhone" /min "I:\jewellery_voice_receptionist\venv\Scripts\python.exe" "I:\jewellery_voice_receptionist\server.py"

echo.
echo ===========================================================
echo  Both services are running in the background!
echo  - LiveKit Server: ws://localhost:7880 (Dev Key: devkey, Secret: secret)
echo  - Shashvat Jewels WebPhone: http://localhost:8055
echo ===========================================================
echo.
pause

