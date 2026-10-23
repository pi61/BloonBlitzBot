```bat
@echo off
setlocal
cd /d "%~dp0"

set "PYTHON=.venv\Scripts\python.exe"

echo ========================================
echo       BloonBlitzBot Setup
echo ========================================

if not exist "%PYTHON%" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 goto error
)

echo.
echo Upgrading pip...
"%PYTHON%" -m pip install --upgrade pip
if errorlevel 1 goto error

echo.
echo Installing project dependencies...
"%PYTHON%" -m pip install -r requirements.txt
if errorlevel 1 goto error

echo.
echo Removing conflicting OpenCV packages...
"%PYTHON%" -m pip uninstall -y opencv-python opencv-python-headless opencv-contrib-python opencv-contrib-python-headless

echo.
echo Installing full OpenCV...
"%PYTHON%" -m pip install --no-cache-dir --force-reinstall --no-deps opencv-python
if errorlevel 1 goto error

echo.
echo ========================================
echo Optional CUDA Installation
echo ========================================
echo This enables NVIDIA GPU acceleration for EasyOCR.
echo Choose N if you don't have a CUDA-capable NVIDIA GPU.
echo.
choice /C YN /M "Install CUDA-enabled PyTorch"

if errorlevel 2 goto verify
if errorlevel 1 goto cuda

:cuda
echo.
echo Installing CUDA-enabled PyTorch...
"%PYTHON%" -m pip install --upgrade torch torchvision --index-url https://download.pytorch.org/whl/cu126
if errorlevel 1 goto error

goto verify

:verify
echo.
echo Verifying OpenCV...
"%PYTHON%" -c "import cv2; print('OpenCV version:', cv2.__version__); print('OpenCV path:', cv2.__file__)"
if errorlevel 1 goto error

echo.
echo Verifying PyTorch...
"%PYTHON%" -c "import torch; print('PyTorch:', torch.__version__); print('CUDA build:', torch.version.cuda); print('CUDA available:', torch.cuda.is_available())"
if errorlevel 1 goto error

echo.
echo Checking dependency consistency...
"%PYTHON%" -m pip check
if errorlevel 1 (
    echo WARNING: Some dependency conflicts were detected.
    echo Review the messages above.
)

echo.
echo ========================================
echo       Setup completed!
echo ========================================
echo Run the bot using:
echo .venv\Scripts\python.exe main.py
echo.
pause
exit /b 0

:error
echo.
echo ========================================
echo Setup failed. See the errors above.
echo ========================================
pause
exit /b 1
```