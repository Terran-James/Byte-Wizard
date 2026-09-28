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
-  System diagnostic
-  Network diagnostic

## Requirements

- Python 3.x
- `pyfiglet`
- `psutil`

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

### System Diagnostic Improvements

- Added system information reporting using `platform`.
- Added CPU usage monitoring using `psutil`.
- Added memory usage monitoring using `psutil`.
- Added disk usage and available disk space reporting.
- Added system uptime monitoring.
- Added PASS/WARNING/FAIL status thresholds for system resources.
- Added an overall system diagnostic result based on individual test results.
- Added potential issue reporting when system resources exceed warning thresholds.
- Added improved issue tracking to prevent contradictory diagnostic messages.
- Added one-second CPU usage sampling for more accurate CPU measurements.

### Current System Diagnostic

The system diagnostic currently checks:

1. Operating system
2. OS version
3. Machine type
4. Hostname
5. Python version
6. CPU usage
7. Memory usage
8. Disk usage
9. Available disk space
10. System uptime

The diagnostic then assigns PASS, WARNING, or FAIL results based on predefined thresholds and provides potential troubleshooting recommendations when issues are detected.

### Network Diagnostic Improvements

- Added Internet connectivity testing using a direct connection test.
- Added DNS resolution testing using `socket.gethostbyname()`.
- Added default gateway detection with support for:
  - macOS
  - Windows
  - Linux
- Added HTTPS connectivity testing using `urllib.request`.
- Added a diagnostic summary displaying PASS/FAIL results for each network test.
- Improved summary formatting so diagnostic results line up cleanly.
- Added potential issue reporting based on failed network tests.
- Added conditional status tracking using Boolean values to allow the diagnostic results to be evaluated later.
- Added ASCII-formatted diagnostic headings using PyFiglet.

### Current Network Diagnostic

The network diagnostic currently checks:

1. Network connectivity
2. DNS resolution
3. Default gateway
4. HTTPS connectivity

The diagnostic then summarizes the results and identifies potential network issues.

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
