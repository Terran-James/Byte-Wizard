# Byte Wizard

Byte Wizard is a Python-based command-line IT troubleshooting assistant designed to guide users through common computer problems, perform system and network diagnostics, and provide useful information about the user's computer.

## Features

- Slow computer troubleshooting
- No internet troubleshooting
- No sound troubleshooting
- Computer won't turn on troubleshooting
- Other issue troubleshooting
- User information and email validation
- Return-to-menu functionality
- System information
- Network information
- System diagnostics
- Network diagnostics
- Running process monitoring
- Top 10 CPU-consuming processes
- Timestamped diagnostic reports
- Cross-platform network information gathering
- PASS/WARNING/FAIL diagnostic results

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

## macOS Executable

Byte Wizard can also be run without installing Python. Open Terminal in the project folder and run:

```bash
./releases/macos/Byte-Wizard/Byte-Wizard
```

The macOS build is created with PyInstaller. To create a fresh build after changing the code:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt pyinstaller
PYINSTALLER_CONFIG_DIR="$PWD/build/pyinstaller-cache" .venv/bin/python -m PyInstaller --noconfirm --clean --name Byte-Wizard --onedir --collect-all pyfiglet --distpath releases/macos --workpath build/pyinstaller --specpath build/pyinstaller byte_wizard.py
```

The resulting executable is in:

releases/macos/Byte-Wizard/


## Windows Executable

PyInstaller builds for the operating system it is run on. To make a Windows `.exe`, run the following commands on a Windows computer from the project folder:

```powershell
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt pyinstaller
.venv\Scripts\python -m PyInstaller --noconfirm --clean --name Byte-Wizard --onedir --collect-all pyfiglet --distpath releases\windows --workpath build\pyinstaller --specpath build\pyinstaller byte_wizard.py
```

The Windows executable will be at:

releases\windows\Byte-Wizard\Byte-Wizard.exe

## System Diagnostic Improvements

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
- Added formatted diagnostic output for easier readability.

## Current System Diagnostic

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

The diagnostic assigns PASS, WARNING, or FAIL results based on predefined thresholds and provides potential troubleshooting recommendations when issues are detected.

## Network Diagnostic Improvements

- Added Internet connectivity testing using a direct connection test.
- Added DNS resolution testing using `socket.gethostbyname()`.
- Added default gateway detection with support for:
  - macOS
  - Windows
  - Linux
- Added HTTPS connectivity testing using `urllib.request`.
- Added network interface detection using `psutil`.
- Added IPv4 address detection.
- Added subnet mask detection.
- Added MAC address detection.
- Added a diagnostic summary displaying PASS/FAIL results for each network test.
- Improved summary formatting so diagnostic results line up cleanly.
- Added potential issue reporting based on failed network tests.
- Added conditional status tracking using Boolean values.
- Added ASCII-formatted diagnostic headings using PyFiglet.

## Current Network Diagnostic

The network diagnostic currently checks:

1. Network connectivity
2. DNS resolution
3. Default gateway
4. HTTPS connectivity
5. Network interface
6. IPv4 address
7. Subnet mask
8. MAC address

The diagnostic summarizes the results and identifies potential network issues based on where the connection process fails.

## Running Process Monitor

Byte Wizard can display currently active processes and their CPU usage.

The process monitor:

- Retrieves running processes using `psutil`.
- Measures CPU usage without waiting individually for every process.
- Filters out processes using `0.0%` CPU.
- Stores process information for analysis.
- Sorts processes by CPU usage.
- Displays the top 10 CPU-consuming processes.
- Handles processes that disappear or become inaccessible during collection.

Example:

PID       Process Name                       CPU %
-------------------------------------------------------
1234      Google Chrome                      18.4
5678      WindowServer                        7.2
9012      Python                              3.6
3456      Finder                              1.4
```

## Diagnostic Reports

Byte Wizard can generate text reports containing diagnostic information.

Reports use timestamps in their filenames so multiple reports can be saved without overwriting previous results.

Example:

byte_wizard_quick_scan_2026-09-29_04-58-31.txt

## Troubleshooting Workflows

Byte Wizard currently provides guided troubleshooting for:

### Slow Computer

Checks common causes of poor performance, including:

- High CPU usage
- High memory usage
- Low available storage
- Application-specific slowdowns
- Restart history
- Software updates
- Security scans

### No Internet

Uses network diagnostic results to identify where connectivity may be failing:

Computer
   ↓
Default Gateway
   ↓
Internet
   ↓
DNS
   ↓
HTTPS


The troubleshooting workflow provides different recommendations depending on which stage fails.

### No Sound

Provides guided checks for:

- Muted or low volume
- Connected audio devices
- Output device selection
- Application-specific audio problems
- Restarts and updates
- Hardware troubleshooting

### Computer Won't Turn On

Provides safe troubleshooting steps for:

- Power connections
- Chargers
- External displays
- USB devices and docks
- Desktop power supplies
- Startup indicators
- Potential hardware problems

### Other Issues

Allows the user to describe another problem and provides the option to update their contact email.

## What I Learned

This project was built as a hands-on Python learning project. It has helped me practice:

- Classes and objects
- Functions
- Loops and conditional statements
- Exception handling with `try`/`except`
- Input validation
- String manipulation
- Lists and tuples
- Sorting data
- List slicing
- Working with timestamps
- Working with operating-system information
- Working with network information
- Process monitoring
- Working with external Python packages
- Organizing a multi-feature command-line application
- Designing reusable functions
- Cross-platform programming concepts

## Technologies Used

- Python
- `psutil`
- `pyfiglet`
- `platform`
- `socket`
- `subprocess`
- `urllib`
- `datetime`
- `time`
- PyInstaller

## Future Improvements

Planned improvements include:

- Additional troubleshooting workflows
- More advanced diagnostic features
- Expanded process monitoring
- Additional network diagnostics
- Expanded error handling
- Additional IT troubleshooting categories
- Improved report generation
- Additional cross-platform support
- Potential graphical user interface (GUI)

## Author

**Terran-James**

Built as part of my ongoing IT and cybersecurity development.