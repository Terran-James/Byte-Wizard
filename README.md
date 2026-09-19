#  Byte Wizard

Byte Wizard is a Python-based command-line IT troubleshooting assistant designed to guide users through common computer problems.

## Features

-  Slow computer troubleshooting
-  No internet troubleshooting
-  No sound troubleshooting
-  Computer won't turn on troubleshooting
-  Other issues
-  User information and email validation
-  Return-to-menu functionality
-  System information
-  Network information

## Requirements

- Python 3.x
- `pyfiglet`

## Installation

1. Install Python 3.x.
2. Clone or download this repository.
3. Open a terminal in the Byte Wizard folder.
4. Install the required packages:

```bash
pip install -r requirements.txt
```

## Running Byte Wizard

Run:

```bash
python byte_wizard.py
```

## macOS executable

Byte Wizard can also be run without installing Python. Open Terminal in the
project folder and run:

```bash
./releases/macos/Byte-Wizard/Byte-Wizard
```

The macOS build is created with PyInstaller. To create a fresh build after
changing the code:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt pyinstaller
PYINSTALLER_CONFIG_DIR="$PWD/build/pyinstaller-cache" .venv/bin/python -m PyInstaller --noconfirm --clean --name Byte-Wizard --onedir --collect-all pyfiglet --distpath releases/macos --workpath build/pyinstaller --specpath build/pyinstaller byte_wizard.py
```

The resulting executable is in `releases/macos/Byte-Wizard/`.

## Windows executable

PyInstaller builds for the operating system it is run on. To make a Windows
`.exe`, run the following commands on a Windows computer from the project
folder:

```powershell
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt pyinstaller
.venv\Scripts\python -m PyInstaller --noconfirm --clean --name Byte-Wizard --onedir --collect-all pyfiglet --distpath releases\windows --workpath build\pyinstaller --specpath build\pyinstaller byte_wizard.py
```

The Windows executable will be at
`releases\windows\Byte-Wizard\Byte-Wizard.exe`.

## What I Learned

This project was built as a hands-on Python learning project. It helped me practice:

- Classes and objects
- Functions
- Loops and conditional statements
- Exception handling with `try`/`except`
- Input validation
- String manipulation
- User data handling
- Working with external Python packages
- Organizing a multi-feature command-line application

## Future Improvements

Planned improvements include:

- Additional troubleshooting workflows
- More advanced diagnostic features
- Expanded error handling
- Additional IT troubleshooting categories
- Potential graphical user interface (GUI)

## Author

**Terran-James**

Built as part of my ongoing IT and cybersecurity development.
