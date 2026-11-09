@echo off
TITLE Push Shashvat Jewels Code to GitHub (Branch: demo-1)
chcp 65001 >nul
cd /d I:\jewellery_voice_receptionist

echo ==========================================================
echo  💎 PUSHING CODE TO GITHUB (BRANCH: demo-1) 💎
echo  Repository: https://github.com/rudrasinh11/Ai-calling-
echo ==========================================================
echo.
echo If a GitHub login window appears, please authorize as rudrasinh11.
echo.
git push -u origin demo-1

echo.
if %ERRORLEVEL% EQU 0 (
    echo ==========================================================
    echo  SUCCESS! Code pushed to branch 'demo-1' successfully!
    echo ==========================================================
) else (
    echo ==========================================================
    echo  Push failed or needs authentication!
    echo  If it says 'Permission denied to graphionicteam':
    echo  1. Add 'graphionicteam' as collaborator on GitHub repo:
    echo     https://github.com/rudrasinh11/Ai-calling-/settings/access
    echo  OR
    echo  2. Pass your GitHub Personal Access Token (PAT).
    echo ==========================================================
)
echo.
pause
