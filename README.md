# BloonBlitzBot
A bot that automatically plays hit NinjaKiwi game Bloon Blitz

## Installation
### Windows
1. Download all files and place them inside a folder

2. Run the setup script:

```bat
setup.bat
```
This should install all dependencies.
Note that easyocr requires opencv-python-headless package, but we will be using the full opencv-python. The setup file should correctly remove the headless package, but `python -m pip check` will see missing dependency. This doesn't prevent the bot from running.

During installation, it will ask whether you want to install CUDA-enabled PyTorch. Doing this will speed up EasyOCR by a significant amount, but only do this if you have a CUDA capable GPU.

3. Running the bot:
Edit behavior options in "main.py" if necessary, then run the main script

```bash
python main.py
```

## Limitations
### Platform
This is only tested on Google Play Games emulator on Windows 11.

Everything related to screen coordinates are hard-coded, assuming screen resolution of 1920x1080 and centered emulator screen. Any difference in screen resolution and position will definitely break the bot.

There is an experimental build that scales the existing game coordinates to the detected Google Play Games window. You can run it with  `main_multires.py`. Keep Bloon Blitz open before starting it; the window geometry is detected during initialization and monitored once per second for movement or resolution changes. This build uses its own `imagehandler_multires.py` and leaves `main.py` unchanged.

Note that the multires version is currently fully experimental and once again only works for 1080p resolution. It correctly handles moving the game window around, but breaks when resolution of the window changes.

### Performance 
Currently doesn't work very well with weak setups. If you have a strong healing build, this will likely beat all non-Ghost Bloon stages.
A weak build (for example, gold farming build) will likely die to most stages.

## Demo
https://www.youtube.com/watch?v=83Tk1HMSi1k
