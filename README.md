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

3. Running the bot:

```bash
python main.py
```

## Limitations
### Platform
This is only tested on Google Play Games emulator on Windows 11.

Everything related to screen coordinates are hard-coded, assuming screen resolution of 1920x1080 and centered emulator screen.
Any difference in screen resolution and position will definitely break the bot.
Will probably update this to support more resolutions.

### Performance 
Currently doesn't work very well with weak setups. If you have a strong healing build, this will likely beat all non-Ghost Bloon stages.
A weak build (for example, gold farming build) will likely die to most stages.
