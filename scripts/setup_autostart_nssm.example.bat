@echo off
REM Example only. Do not run blindly.
REM Replace <NSSM_PATH> with your local nssm.exe path.
REM Replace <PROJECT_ROOT> with the local checkout path.

<NSSM_PATH> install VoiceClonePlatform cmd.exe "/c <PROJECT_ROOT>\\start.bat"
<NSSM_PATH> set VoiceClonePlatform AppDirectory "<PROJECT_ROOT>"
<NSSM_PATH> set VoiceClonePlatform Start SERVICE_AUTO_START

echo NSSM service example created.
