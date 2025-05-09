Crosshair Overlay Program: Description & Features
This Crosshair Overlay program provides an on-screen aiming aid with customizable styles, colors, and transparency. It is designed for practice use only and should not be used in online public matches or tournaments.
Disclaimer: The developer is not liable for any bans resulting from unauthorized use in competitive environments.


Key Features
✅ Customizable Crosshair Styles
- Cross, Dot, Cross+Dot, Circle, Circle+Dot
- Animated pulsing effect for enhanced visibility
- Adjustable size, thickness, and color via settings
✅ Transparent Overlay & Click-Through
- Stays on top of all windows
- Does not interfere with game interactions
✅ Settings Management & Auto Updates
- Uses a settings.json file for easy customization
- Detects changes without restarting
✅ System Tray Controls
- Quick style switching via a right-click menu
- Hotkeys for toggling visibility and changing styles
✅ Duplicate Instance Prevention
- Ensures only one instance runs at a time using a lock file
- Displays a warning if another instance is detected
✅ Hotkeys for Fast Adjustments
- F8 → Toggle crosshair visibility
- Shift + F8 → Exit application
- Page Up / Page Down → Cycle styles


**How to Build the Program into an Executable (.exe)**

Follow these steps to create a portable version of the program.
1️⃣ Install PyInstaller
Open a terminal (Command Prompt, PowerShell, or Git Bash) and run:
pip install pyinstaller


2️⃣ Navigate to Your Program Folder
Run:
cd "%USERPROFILE%\Documents\Crosshair"


3️⃣ Build the Executable
Use PyInstaller to package the program:
pyinstaller --onefile --windowed --icon=icon.ico crosshair_overlay.py


- --onefile → Bundles everything into a single .exe
- --windowed → Hides the terminal window
- --icon=icon.ico → Sets the application icon
4️⃣ Locate the Built .exe File
After the build completes, find the executable inside:
%USERPROFILE%\Documents\Crosshair\dist\crosshair_overlay.exe
