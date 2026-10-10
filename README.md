# Byte Wizard

Byte Wizard is a Python-based IT troubleshooting and system diagnostics tool designed to help users inspect system health, troubleshoot network connectivity, and perform basic security checks.

Originally developed as a command-line application, Byte Wizard is now expanding into a graphical user interface (GUI) built with **PySide6**, featuring a dashboard for monitoring system resources and viewing diagnostic information.

## Features

- **System Information** — View operating system, hardware, and resource information.
- **System Diagnostics** — Check CPU, memory, disk usage, and system uptime.
- **Network Information** — Inspect local network configuration and connectivity.
- **Network Diagnostics** — Check internet access, DNS resolution, HTTPS connectivity, and gateway availability.
- **Security Checks** — Inspect firewall status on supported operating systems.
- **Quick Scan** — Run a combined system and network health check.
- **Process Monitoring** — Inspect running processes and identify the top 10 CPU-consuming processes.
- **Diagnostic Results** — Display PASS / WARNING / FAIL statuses and generate text reports.
- **Cross-Platform Support** — Designed for macOS, Windows, and Linux.
- **PySide6 GUI (In Development)** — Building a graphical dashboard with live CPU and memory charts, resource cards, and network status information.

## Requirements

- Python 3.x
- psutil
- pyfiglet
- PySide6 *(for the graphical interface)*
- PyQtGraph *(for live charts)*

## Installation

Clone the repository:

bash
git clone https://github.com/Terran-James/Byte-Wizard.git
cd Byte-Wizard


Install the dependencies:

bash
pip install -r requirements.txt


Run the command-line application:

bash
python byte_wizard.py


Launch the graphical interface:

bash
python byte_wizard_gui.py


*Note: The GUI requires PySide6 and PyQtGraph to be installed. Use a virtual environment when setting up the project.*

## What I Learned

Developing Byte Wizard has helped me build practical experience with:

- Python functions, classes, and modular programming
- Loops, conditional logic, and input validation
- Exception handling and defensive programming
- Dictionaries, lists, tuples, and data structures
- System resource and process monitoring
- Network connectivity and DNS troubleshooting
- Subprocess execution and operating-system commands
- Cross-platform programming
- Diagnostic thresholds and health checks
- Report generation and file handling
- GUI development with PySide6
- Live data visualization with PyQtGraph
- Packaging Python applications with PyInstaller
- Git and GitHub version control

## Technologies

**Languages:** Python

**Libraries:** psutil, PyFiglet, PySide6, PyQtGraph

**System & Networking:** socket, subprocess, platform

**Tools:** Git, GitHub, PyInstaller

## Future Improvements

- Expand system troubleshooting and security checks
- Add more detailed network diagnostics
- Improve diagnostic reporting and error handling
- Refine the GUI dashboard and visual design
- Expand cross-platform compatibility
- Explore additional system monitoring and visualization features

## Author

**Terran-James**

Built as part of my ongoing IT and cybersecurity development, with a focus on practical troubleshooting, Python programming, and system diagnostics.