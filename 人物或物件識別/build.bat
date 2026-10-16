@echo off
chcp 65001 >nul
echo ========================================
echo   人物或物件識別 - 打包為 .msi 安裝程式
echo ========================================
echo.

set VENV=%~dp0..\.venv\Scripts
set PYINSTALLER=%VENV%\pyinstaller.exe

if not exist "%PYINSTALLER%" (
    echo [錯誤] 找不到 pyinstaller，請先安裝：
    echo   %VENV%\pip install pyinstaller
    pause
    exit /b 1
)

where wix >nul 2>&1
if %errorlevel% neq 0 (
    echo [錯誤] 找不到 wix，請先安裝 WiX Toolset v5：
    echo   dotnet tool install --global wix
    pause
    exit /b 1
)

echo [1/3] 使用 PyInstaller 打包 exe...
"%PYINSTALLER%" --clean 人物或物件識別.spec
if %errorlevel% neq 0 (
    echo [錯誤] PyInstaller 打包失敗
    pause
    exit /b 1
)

echo.
echo [2/3] 複製資料檔到 dist...
copy /Y hand_landmarker.task dist\人物或物件識別\ >nul
copy /Y daniel.jpg dist\人物或物件識別\ >nul
copy /Y cars.webp dist\人物或物件識別\ >nul
copy /Y ..\yolo11n.pt dist\人物或物件識別\ >nul 2>&1

echo.
echo [3/3] 使用 WiX 編譯 msi...
wix build -o 人物或物件識別.msi installer.wxs
if %errorlevel% neq 0 (
    echo [錯誤] WiX 編譯失敗
    pause
    exit /b 1
)

echo.
echo ========================================
echo   完成！
echo ========================================
echo.
echo 輸出檔案：
echo   exe: dist\人物或物件識別\人物或物件識別.exe
echo   msi: 人物或物件識別.msi
echo.
pause
