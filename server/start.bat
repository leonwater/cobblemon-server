@echo off
rem pokeserver: update mods + datapack from GitHub, then start the server.
cd /d "%~dp0"
set PACK=https://raw.githubusercontent.com/leonwater/cobblemon-server/main/pack/pack.toml
for /d %%d in (jdk*) do set JAVA=%%d\bin\java.exe
for %%f in (fabric-server-*.jar) do set SERVER=%%f
if not defined JAVA (echo [ERROR] jdk folder not found. See README. & pause & exit /b 1)
if not defined SERVER (echo [ERROR] fabric-server jar not found. See README. & pause & exit /b 1)
rem Safe default: only this PC can connect. Edit server.properties later to invite friends.
if not exist server.properties echo server-ip=127.0.0.1> server.properties
"%JAVA%" -jar packwiz-installer-bootstrap.jar -g -s server %PACK%
if errorlevel 1 (echo [ERROR] Update failed. Server not started. & pause & exit /b 1)
"%JAVA%" -Xmx4G -jar "%SERVER%" nogui
rem /reset (full wipe) leaves this file: start again right away with a new world
if exist pokeserver-wipe.txt "%~f0"
pause
