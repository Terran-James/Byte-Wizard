import sys
import socket
import psutil
import platform
import datetime

from collections import deque

from byte_wizard import (
    get_network_information,
    get_system_information,
    get_uptime,
    get_operating_system,
    check_threshold,
)

import pyqtgraph as pg
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QStackedWidget,
    QFrame,
    QProgressBar,
)


class ByteWizardGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        # Store the most recent 60 readings
        self.cpu_history = deque([0] * 60, maxlen=60)
        self.memory_history = deque([0] * 60, maxlen=60)

        # Configure the main window
        self.setWindowTitle("Byte Wizard")
        self.resize(1200, 850)
        self.setMinimumSize(1000, 700)

        # Apply the dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #111214;
            }

            QWidget {
                color: #E8E8ED;
                font-family: Arial;
                font-size: 14px;
            }

            QLabel {
                background-color: transparent;
            }

            QPushButton {
                background-color: #1B1C20;
                color: #E8E8ED;
                border: 1px solid #303036;
                border-radius: 6px;
                padding: 10px 16px;
                text-align: left;
            }

            QPushButton:hover {
                background-color: #25252C;
                border: 1px solid #A78BFA;
            }

            QPushButton:pressed {
                background-color: #302A3D;
            }

            QFrame#statCard {
                background-color: #1B1C20;
                border: 1px solid #303036;
                border-radius: 10px;
            }

            QProgressBar {
                background-color: #111214;
                border: none;
                border-radius: 4px;
                height: 8px;
                text-align: center;
            }

            QProgressBar::chunk {
                background-color: #A78BFA;
                border-radius: 4px;
            }
        """)

        # Main content widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)

        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #16171A;
            }
        """)

        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(16, 20, 16, 20)
        sidebar_layout.setSpacing(10)
        sidebar.setLayout(sidebar_layout)

        title = QLabel("BYTE WIZARD")
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #A78BFA;
            padding: 8px 0;
        """)
        sidebar_layout.addWidget(title)

        subtitle = QLabel("SYSTEM TOOLKIT")
        subtitle.setStyleSheet("""
            font-size: 10px;
            color: #888892;
            letter-spacing: 2px;
        """)
        sidebar_layout.addWidget(subtitle)
        sidebar_layout.addSpacing(24)

        # Navigation buttons
        self.dashboard_button = QPushButton("Dashboard")
        self.quick_scan_button = QPushButton("Quick Scan")
        self.diagnostics_button = QPushButton("Diagnostics")
        self.system_info_button = QPushButton("System Information")
        self.security_button = QPushButton("Security")

        self.dashboard_button.clicked.connect(
            lambda: self.content_area.setCurrentIndex(0)
        )
        self.quick_scan_button.clicked.connect(
            lambda: self.content_area.setCurrentIndex(1)
        )
        self.diagnostics_button.clicked.connect(
            lambda: self.content_area.setCurrentIndex(2)
        )
        self.system_info_button.clicked.connect(
            lambda: self.content_area.setCurrentIndex(3)
        )
        self.security_button.clicked.connect(
            lambda: self.content_area.setCurrentIndex(4)
        )

        for button in (
            self.dashboard_button,
            self.quick_scan_button,
            self.diagnostics_button,
            self.system_info_button,
            self.security_button,
        ):
            sidebar_layout.addWidget(button)

        sidebar_layout.addStretch()

        # Main page container
        self.content_area = QStackedWidget()
        self.content_area.setStyleSheet("""
            QStackedWidget {
                background-color: #111214;
            }
        """)

        # Create pages
        self.dashboard_page = self.create_page(
            "Dashboard",
            "Welcome to Byte Wizard. Your personal system diagnostic toolkit."
        )

        self.quick_scan_page = self.create_page(
            "Quick Scan",
            "Run a quick check of your system health and network connectivity."
        )

        self.diagnostic_page = self.create_page(
            "Diagnostics",
            "Inspect system resources and identify potential problems."
        )

        self.system_info_page = self.create_page(
            "System Information",
            "View details about your operating system and hardware."
        )

        self.security_page = self.create_page(
            "Security",
            "View security features and basic system protections."
        )

        # System Information page content
        self.system_info_results = QLabel(
            "Click Refresh to collect your system information."
        )
        self.system_info_results.setWordWrap(True)
        self.system_info_results.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.system_info_results.setStyleSheet("""
            background-color: #1B1C20;
            border: 1px solid #303036;
            border-radius: 8px;
            padding: 16px;
            line-height: 1.5;
        """)
        self.system_info_results.setMinimumHeight(180)
        self.system_info_results.setMaximumHeight(500)

        self.system_info_button_refresh = QPushButton(
            "Refresh System Information"
        )
        self.system_info_button_refresh.clicked.connect(
            self.update_system_information
        )

        self.system_info_page.layout().addWidget(
            self.system_info_button_refresh
        )
        self.system_info_page.layout().addWidget(
            self.system_info_results
        )
        self.system_info_page.layout().addStretch()

        # Diagnostics page content
        self.diagnostics_button = QPushButton("Run System Diagnostic")
        self.diagnostics_button.clicked.connect(
            self.run_system_diagnostic
        )

        self.diagnostic_results = QLabel(
            "Run a diagnostic to check CPU, memory, disk and uptime."
        )
        self.diagnostic_results.setWordWrap(True)
        self.diagnostic_results.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.diagnostic_results.setStyleSheet("""
            background-color: #1B1C20;
            border: 1px solid #303036;
            border-radius: 8px;
            padding: 16px;
        """)
        self.diagnostic_results.setMinimumHeight(250)

        self.diagnostic_page.layout().addWidget(
            self.diagnostics_button
        )
        self.diagnostic_page.layout().addWidget(
            self.diagnostic_results
        )
        self.diagnostic_page.layout().addStretch()

        # Add pages to the stack
        self.content_area.addWidget(self.dashboard_page)
        self.content_area.addWidget(self.quick_scan_page)
        self.content_area.addWidget(self.diagnostic_page)
        self.content_area.addWidget(self.system_info_page)
        self.content_area.addWidget(self.security_page)

        # Quick Scan button
        self.scan_button = QPushButton("Run Quick Scan")
        self.scan_button.setMaximumHeight(45)
        self.scan_button.clicked.connect(self.run_quick_scan)

        self.scan_results = QLabel(
            "Ready to scan your system.\n"
            "Click the button above to begin."
        )
        self.scan_results.setWordWrap(True)
        self.scan_results.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scan_results.setStyleSheet("""
            background-color: #1B1C20;
            border: 1px solid #303036;
            border-radius: 8px;
            padding: 16px;
            color: #E8E8ED;
        """)

        quick_scan_layout = self.quick_scan_page.layout()
        quick_scan_layout.addWidget(self.scan_button)
        quick_scan_layout.addWidget(self.scan_results)

        # Dashboard layout
        dashboard_layout = self.dashboard_page.layout()
        dashboard_layout.setSpacing(20)

        # Resource cards
        card_row = QHBoxLayout()
        card_row.setSpacing(16)

        cpu_card, self.cpu_value, self.cpu_bar = self.create_stat_card(
            "CPU USAGE", "--%", "Processor utilization"
        )

        memory_card, self.memory_value, self.memory_bar = self.create_stat_card(
            "MEMORY USAGE", "--%", "System memory in use"
        )

        disk_card, self.disk_value, self.disk_bar = self.create_stat_card(
            "DISK SPACE", "--%", "Primary drive used"
        )

        network_card, self.network_value, _ = self.create_stat_card(
            "NETWORK", "Checking...", "Connection status",
            show_progress=False
        )

        for card in (
            cpu_card,
            memory_card,
            disk_card,
            network_card,
        ):
            card_row.addWidget(card)

        dashboard_layout.addLayout(card_row)

        # Live CPU and memory charts
        chart_row = QHBoxLayout()
        chart_row.setSpacing(16)

        self.cpu_chart, self.cpu_line = self.create_live_chart(
            "CPU USAGE HISTORY"
        )

        self.memory_chart, self.memory_line = self.create_live_chart(
            "MEMORY USAGE HISTORY"
        )

        chart_row.addWidget(self.cpu_chart)
        chart_row.addWidget(self.memory_chart)

        dashboard_layout.addLayout(chart_row)

        # System Health panel
        self.health_panel = QFrame()
        self.health_panel.setObjectName("statCard")

        health_layout = QVBoxLayout()
        health_layout.setContentsMargins(20, 16, 20, 16)
        health_layout.setSpacing(8)
        self.health_panel.setLayout(health_layout)

        health_heading = QLabel("SYSTEM HEALTH")
        health_heading.setStyleSheet("""
            color: #888892;
            font-size: 12px;
            font-weight: bold;
            letter-spacing: 1px;
        """)

        self.health_status = QLabel("Checking system health...")
        self.health_status.setStyleSheet("""
            color: #A78BFA;
            font-size: 18px;
            font-weight: bold;
        """)

        self.health_detail = QLabel(
            "Monitoring processor, memory, and disk usage."
        )
        self.health_detail.setStyleSheet("color: #888892;")
        self.health_detail.setWordWrap(True)

        health_layout.addWidget(health_heading)
        health_layout.addWidget(self.health_status)
        health_layout.addWidget(self.health_detail)
        health_layout.addStretch()

        # Network Overview panel
        self.network_panel = QFrame()
        self.network_panel.setObjectName("statCard")

        network_layout = QVBoxLayout()
        network_layout.setContentsMargins(20, 16, 20, 16)
        network_layout.setSpacing(10)
        self.network_panel.setLayout(network_layout)

        network_heading = QLabel("NETWORK OVERVIEW")
        network_heading.setStyleSheet("""
            color: #888892;
            font-size: 12px;
            font-weight: bold;
            letter-spacing: 1px;
        """)

        self.connection_status = QLabel("Checking connection...")
        self.connection_status.setStyleSheet("""
            color: #A78BFA;
            font-size: 18px;
            font-weight: bold;
        """)

        self.ip_address_label = QLabel("Local IP: Checking...")
        self.gateway_label = QLabel("Default Gateway: Checking...")
        self.dns_label = QLabel("DNS: Checking...")

        for label in (
            self.ip_address_label,
            self.gateway_label,
            self.dns_label,
        ):
            label.setStyleSheet("color: #888892;")
            label.setWordWrap(True)

        network_layout.addWidget(network_heading)
        network_layout.addWidget(self.connection_status)
        network_layout.addWidget(self.ip_address_label)
        network_layout.addWidget(self.gateway_label)
        network_layout.addWidget(self.dns_label)
        network_layout.addStretch()

        # Put both overview panels side by side
        overview_row = QHBoxLayout()
        overview_row.setSpacing(16)
        overview_row.addWidget(self.health_panel)
        overview_row.addWidget(self.network_panel)

        dashboard_layout.addLayout(overview_row)
        dashboard_layout.addStretch()

        # Set up automatic system monitoring
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.update_system_stats)

        # Initial readings
        self.update_system_stats()
        self.update_network_overview()

        # Refresh resource stats every 2 seconds
        self.refresh_timer.start(2000)

        # Add sidebar and pages to the main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_area)

    def create_page(self, title_text, description_text):
        page = QWidget()

        page_layout = QVBoxLayout()
        page_layout.setContentsMargins(28, 24, 28, 24)
        page_layout.setSpacing(18)

        heading = QLabel(title_text)
        heading.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
        """)

        description = QLabel(description_text)
        description.setStyleSheet("color: #888892;")

        page_layout.addWidget(heading)
        page_layout.addWidget(description)

        page.setLayout(page_layout)
        return page

    def create_stat_card(
        self, title_text, value_text, detail_text, show_progress=True
    ):
        card = QFrame()
        card.setObjectName("statCard")
        card.setMinimumHeight(150)

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(18, 16, 18, 16)
        card_layout.setSpacing(8)
        card.setLayout(card_layout)

        title = QLabel(title_text)
        title.setStyleSheet("color: #888892; font-size: 13px;")

        value = QLabel(value_text)
        value.setStyleSheet("""
            color: #A78BFA;
            font-size: 26px;
            font-weight: bold;
        """)

        progress_bar = None

        if show_progress:
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress_bar.setValue(0)
            progress_bar.setTextVisible(False)
            progress_bar.setFixedHeight(8)

        detail = QLabel(detail_text)
        detail.setStyleSheet("color: #888892; font-size: 12px;")
        detail.setWordWrap(True)

        card_layout.addWidget(title)
        card_layout.addWidget(value)

        if progress_bar is not None:
            card_layout.addWidget(progress_bar)

        card_layout.addWidget(detail)
        card_layout.addStretch()

        return card, value, progress_bar

    def create_live_chart(self, title_text):
        """Create a themed chart for live system resource usage"""

        chart = pg.PlotWidget()
        chart.setBackground("#1B1C20")
        chart.setMinimumHeight(200)

        # Style the chart axes
        chart.showGrid(x=True, y=True, alpha=0.2)
        chart.setYRange(0, 100)
        chart.setLabel("left", "Usage", units="%")
        chart.setLabel("bottom", "Recent readings")
        chart.setTitle(
            title_text,
            color="#E8E8ED",
            size="12pt"
        )

        # Style axis text and lines
        for axis_name in ("left", "bottom"):
            axis = chart.getAxis(axis_name)
            axis.setTextPen("#888892")
            axis.setPen("#44444D")

        # Draw the purple line
        line = chart.plot(
            pen=pg.mkPen(color="#A78BFA", width=2)
        )

        return chart, line

    def update_progress_bar(self, progress_bar, percentage):
        progress_bar.setValue(int(percentage))

        if percentage < 70:
            color = "#A78BFA"
        elif percentage <= 90:
            color = "#FBBF24"
        else:
            color = "#F87171"

        progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #111214;
                border: none;
                border-radius: 4px;
                height: 8px;
            }}

            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 4px;
            }}
        """)

    def update_system_stats(self):
        # Collect current system resource readings
        cpu_percent = psutil.cpu_percent(interval=None)
        memory_percent = psutil.virtual_memory().percent
        disk_percent = psutil.disk_usage("/").percent

        # Store the latest readings in rolling history
        self.cpu_history.append(cpu_percent)
        self.memory_history.append(memory_percent)

        # Update the chart lines
        self.cpu_line.setData(list(self.cpu_history))
        self.memory_line.setData(list(self.memory_history))

        # Update card values
        self.cpu_value.setText(f"{cpu_percent:.1f}%")
        self.memory_value.setText(f"{memory_percent:.1f}%")
        self.disk_value.setText(f"{disk_percent:.1f}%")

        self.update_progress_bar(self.cpu_bar, cpu_percent)
        self.update_progress_bar(self.memory_bar, memory_percent)
        self.update_progress_bar(self.disk_bar, disk_percent)

        # Quick connectivity check
        try:
            connection = socket.create_connection(
                ("8.8.8.8", 53), timeout=2
            )
            connection.close()
            self.network_value.setText("Online")
        except OSError:
            self.network_value.setText("Offline")

        # Evaluate system resource usage
        resources = {
            "CPU": cpu_percent,
            "Memory": memory_percent,
            "Disk": disk_percent,
        }

        high_resources = [
            name for name, value in resources.items()
            if value > 90
        ]

        elevated_resources = [
            name for name, value in resources.items()
            if value >= 70
        ]

        if high_resources:
            status = "High Resource Usage"
            color = "#F87171"
            detail = "High usage detected: " + ", ".join(high_resources)

        elif elevated_resources:
            status = "Elevated Resource Usage"
            color = "#FBBF24"
            detail = "Elevated usage: " + ", ".join(elevated_resources)

        else:
            status = "System Resources Normal"
            color = "#A78BFA"
            detail = (
                "CPU, memory, and disk usage are within normal thresholds."
            )

        self.health_status.setText(status)
        self.health_status.setStyleSheet(f"""
            color: {color};
            font-size: 18px;
            font-weight: bold;
        """)
        self.health_detail.setText(detail)

    def update_network_overview(self):
        try:
            network_info = get_network_information()

            if network_info["internet"]:
                self.connection_status.setText("Connected")
                color = "#A78BFA"
            else:
                self.connection_status.setText("Connection Issue")
                color = "#FBBF24"

            self.connection_status.setStyleSheet(f"""
                color: {color};
                font-size: 18px;
                font-weight: bold;
            """)

            # Update details regardless of internet status
            ip_address = network_info.get("ip_address") or "Unavailable"
            gateway = (
                network_info.get("gateway_address") or "Not detected"
            )
            dns_status = (
                "Working" if network_info["dns_working"] else "Failed"
            )

            self.ip_address_label.setText(f"Local IP: {ip_address}")
            self.gateway_label.setText(f"Default Gateway: {gateway}")
            self.dns_label.setText(f"DNS: {dns_status}")

        except Exception as error:
            self.connection_status.setText("Unable to check connection")
            self.ip_address_label.setText("Local IP: Unavailable")
            self.gateway_label.setText("Default Gateway: Unavailable")
            self.dns_label.setText(f"Network check error: {error}")

    def run_quick_scan(self):
        self.scan_button.setEnabled(False)
        self.scan_button.setText("Scanning...")
        self.scan_results.setText("Running system checks...")

        try:
            cpu_percent = psutil.cpu_percent(interval=0.5)
            memory_percent = psutil.virtual_memory().percent
            disk_percent = psutil.disk_usage("/").percent

            # Apply the same thresholds as the original CLI program
            cpu_result = check_threshold(cpu_percent, 70, 90)
            memory_result = check_threshold(memory_percent, 80, 90)
            disk_result = check_threshold(disk_percent, 80, 90)

            # Reuse the network checks from the original CLI program
            network_info = get_network_information()

            internet_status = (
                "Online" if network_info["internet"] else "Offline"
            )
            dns_status = (
                "Working" if network_info["dns_working"] else "Failed"
            )
            https_status = (
                "Working" if network_info["https_working"] else "Failed"
            )
            gateway = (
                network_info.get("gateway_address") or "Not detected"
            )

            report = (
                "BYTE WIZARD — QUICK SCAN RESULTS\n\n"
                "SYSTEM HEALTH\n"
                f"CPU Usage:       {cpu_percent:.1f}% — {cpu_result}\n"
                f"Memory Usage:    {memory_percent:.1f}% — {memory_result}\n"
                f"Disk Usage:      {disk_percent:.1f}% — {disk_result}\n\n"
                "NETWORK CHECKS\n"
                f"Internet:        {internet_status}\n"
                f"DNS:             {dns_status}\n"
                f"HTTPS:           {https_status}\n"
                f"Default Gateway: {gateway}\n\n"
                "Scan complete."
            )

            self.scan_results.setText(report)

        except Exception as error:
            self.scan_results.setText(
                f"An error occurred during the scan:\n{error}"
            )

        finally:
            self.scan_button.setEnabled(True)
            self.scan_button.setText("Run Quick Scan")

    def update_system_information(self):
        """Display system information using the original Byte Wizard functions."""

        try:
            system = get_system_information()
            uptime = get_uptime()

            report = (
                "SYSTEM INFORMATION\n\n"
                f"Operating System: {get_operating_system()}\n"
                f"OS Version: {platform.release()}\n"
                f"Machine Type: {platform.machine()}\n"
                f"Hostname: {platform.node()}\n"
                f"Python Version: {platform.python_version()}\n\n"
                "HARDWARE & RESOURCES\n\n"
                f"CPU Cores: {psutil.cpu_count()}\n"
                f"Total Memory: {system['Memory Total']:.2f} GB\n"
                f"Memory Usage: {system['Memory Usage']:.1f}%\n"
                f"Total Storage: {system['Disk Total']:.2f} GB\n"
                f"Storage Used: {system['Disk Usage']:.1f}%\n"
                f"Storage Free: {system['Disk Free']:.2f} GB\n\n"
                f"System Uptime: {uptime}\n"
            )

            self.system_info_results.setText(report)

        except Exception as error:
            self.system_info_results.setText(
                f"Unable to collect system information:\n{error}"
            )

    def run_system_diagnostic(self):
        """Run the original Byte Wizard system checks and display their results."""

        self.diagnostics_button.setEnabled(False)
        self.diagnostics_button.setText("Running Diagnostic...")

        try:
            system = get_system_information()
            uptime = get_uptime()

            cpu_result = check_threshold(
                system["CPU Usage"], 70, 90
            )
            memory_result = check_threshold(
                system["Memory Usage"], 80, 90
            )
            disk_result = check_threshold(
                system["Disk Usage"], 80, 90
            )

            if uptime < datetime.timedelta(days=14):
                uptime_result = "[PASS]"
            elif uptime <= datetime.timedelta(days=30):
                uptime_result = "[WARNING]"
            else:
                uptime_result = "[FAIL]"

            results = {
                "CPU": cpu_result,
                "Memory": memory_result,
                "Disk": disk_result,
                "Uptime": uptime_result,
            }

            if "[FAIL]" in results.values():
                overall = "[FAIL]"
            elif "[WARNING]" in results.values():
                overall = "[WARNING]"
            else:
                overall = "[PASS]"

            report = (
                "SYSTEM DIAGNOSTIC RESULTS\n\n"
                f"CPU Usage: {system['CPU Usage']:.1f}% — {cpu_result}\n"
                f"Memory Usage: {system['Memory Usage']:.1f}% — {memory_result}\n"
                f"Disk Usage: {system['Disk Usage']:.1f}% — {disk_result}\n"
                f"System Uptime: {uptime} — {uptime_result}\n\n"
                f"OVERALL STATUS: {overall}\n"
            )

            issues = []

            if cpu_result != "[PASS]":
                issues.append(
                    "CPU usage is elevated. Check for resource-intensive applications."
                )

            if memory_result != "[PASS]":
                issues.append(
                    "Memory usage is elevated. Consider closing unnecessary applications."
                )

            if disk_result != "[PASS]":
                issues.append(
                    "Storage usage is high. Consider freeing up disk space."
                )

            if uptime_result != "[PASS]":
                issues.append(
                    "System uptime is high. Consider restarting when convenient."
                )

            report += "\nRECOMMENDATIONS\n\n"

            if issues:
                report += "\n".join(f"• {issue}" for issue in issues)
            else:
                report += "No system issues were detected by these checks."

            self.diagnostic_results.setText(report)

        except Exception as error:
            self.diagnostic_results.setText(
                f"Unable to complete the diagnostic:\n{error}"
            )

        finally:
            self.diagnostics_button.setEnabled(True)
            self.diagnostics_button.setText("Run System Diagnostic")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = ByteWizardGUI()
    window.show()

    sys.exit(app.exec())