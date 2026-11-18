@echo off
title Royal Heritage Jewellers - AI Receptionist
title Shashvat Jewels Pvt Ltd - Inbound AI Receptionist
cd /d I:\jewellery_voice_receptionist

echo ==========================================================
echo  💎 ROYAL HERITAGE JEWELLERS - AI CALLING RECEPTIONIST 💎
echo  💎 SHASHVAT JEWELS PVT LTD - INBOUND AI RECEPTIONIST 💎
echo ==========================================================
echo Running 100%% Local & Free on Drive I:
echo Python Virtual Environment: I:\jewellery_voice_receptionist\venv
echo Database: I:\jewellery_voice_receptionist\database\jewellery_store.db
echo Whisper Model Cache: I:\jewellery_voice_receptionist\models\whisper
echo ==========================================================

set HF_HOME=I:\jewellery_voice_receptionist\models\hf_cache
set PYTHONIOENCODING=utf-8

start http://localhost:8055

I:\jewellery_voice_receptionist\venv\Scripts\python.exe server.py
pause

