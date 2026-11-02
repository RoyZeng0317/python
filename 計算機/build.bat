@echo off
chcp 65001 >nul
echo ========================================
echo   計算機 - 打包為 .msi 安裝程式
echo ========================================
echo.

REM 設定路徑
set VENV=%~dp0..\.venv\Scripts
set PYINSTALLER=%VENV%\pyinstaller.exe

REM 檢查 PyInstaller
if not exist "%PYINSTALLER%" (
    echo [錯誤] 找不到 pyinstaller，請先安裝：
    echo   %VENV%\pip install pyinstaller
    pause
    exit /b 1
)

REM 檢查 WiX
where wix >nul 2>&1
if %errorlevel% neq 0 (
    echo [錯誤] 找不到 wix，請先安裝 WiX Toolset v5：
    echo   dotnet tool install --global wix
    pause
    exit /b 1
)

echo [1/3] 使用 PyInstaller 打包 exe...
"%PYINSTALLER%" --clean 計算機.spec
if %errorlevel% neq 0 (
    echo [錯誤] PyInstaller 打包失敗
    pause
    exit /b 1
)

echo.
echo [2/3] 使用 WiX 編譯 msi...
wix build -o 計算機.msi installer.wxs
if %errorlevel% neq 0 (
    echo [錯誤] WiX 編譯失敗
    pause
    exit /b 1
)

echo.
echo [3/3] 完成！
echo.
echo 輸出檔案：
echo   exe: dist\計算機\計算機.exe
echo   msi: 計算機.msi
echo.
pause
