@echo off
rem Update datapack while the server is running. Then type "reload" in the server window.
rem If mods changed, close the server and run start.bat instead.
cd /d "%~dp0"
set PACK=https://raw.githubusercontent.com/leonwater/cobblemon-server/main/pack/pack.toml
for /d %%d in (jdk*) do set JAVA=%%d\bin\java.exe
"%JAVA%" -jar packwiz-installer-bootstrap.jar -g -s server %PACK%
pause
