# Used to create ASCII art for the Byte Wizard title
import pyfiglet

# Used to get Platform information for the user's computer
import platform
import os

# Used to get Network information for the user's computer
import socket
import ipaddress

# Used on MacOS to get route process for defauly gateway
import subprocess

# Used to get check HTTPS connectivity
import urllib.request

# Used to gather system information
import psutil

# Used to get date/time information
import datetime
import json

# Used to wait
import time

# Checks if a command exists on the system
import shutil

# Used to handle exceptions for urllib.request.urlopen
import urllib.error
import re


# ==============================
# Gets User's Operating System
# ==============================

def get_operating_system():
    """Return the operating system name in a user-friendly format."""
    operating_system = platform.system()

    if operating_system == "Darwin":
        return "macOS"

    return operating_system


def check_threshold(value, warning, failure):
    """Return a consistent status for a metric with warning/failure limits."""
    if value < warning:
        return "[PASS]"
    if value < failure:
        return "[WARNING]"
    return "[FAIL]"


# ==============================
# Gets User's System Information
# ==============================

def get_system_information():
    """Collect resource usage and capacity values for diagnostics and display."""
    # psutil reports CPU use over a one-second sample and memory/disk as bytes.
    cpu_usage = psutil.cpu_percent(interval=1)

    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    memory_total = memory.total / (1024 ** 3)

    disk_path = (
        os.environ.get("SystemDrive", os.path.abspath(os.sep))
        if platform.system() == "Windows"
        else "/"
    )
    disk_usage = psutil.disk_usage(disk_path)
    disk_percent = disk_usage.percent
    disk_free = disk_usage.free / (1024 ** 3)
    disk_total = disk_usage.total / (1024 ** 3)

    # Keep the values together so diagnostics and the information screen can reuse them.
    return {
        "CPU Usage": cpu_usage,
        "Memory Usage": memory_usage,
        "Memory Total": memory_total,
        "Disk Usage": disk_percent,
        "Disk Free": disk_free,
        "Disk Total": disk_total,
    }


# ==============================
# Uptime Information
# ==============================

def get_uptime():
    """Calculate how long the computer has been running since its last boot."""
    boot_time = psutil.boot_time()
    current_time = datetime.datetime.now().timestamp()
    uptime_seconds = current_time - boot_time
    return datetime.timedelta(seconds=int(uptime_seconds))


# ==============================
# Default Gateway Information
# ==============================

def get_default_gateway():
    """Read the default route using the command available on this OS."""
    operating_system = platform.system()

    try:
        if operating_system == "Darwin":
            result = subprocess.run(
                ["route", "-n", "get", "default"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if line.strip().startswith("gateway:"):
                        return line.split(":", 1)[1].strip() or None
            result = subprocess.run(
                ["route", "-n", "get", "-inet6", "default"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if line.strip().startswith("gateway:"):
                        return line.split(":", 1)[1].strip() or None

        elif operating_system == "Windows":
            powershell = shutil.which("powershell") or shutil.which("pwsh")
            if powershell:
                result = subprocess.run(
                    [
                        powershell,
                        "-NoProfile",
                        "-NonInteractive",
                        "-Command",
                        "Get-NetRoute -AddressFamily IPv4 "
                        "-DestinationPrefix '0.0.0.0/0' | "
                        "Sort-Object RouteMetric | Select-Object -First 1 "
                        "-ExpandProperty NextHop",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )
                if result.returncode == 0:
                    gateway = result.stdout.strip().splitlines()
                    if gateway:
                        candidate = gateway[0].strip()
                        try:
                            ipaddress.ip_address(candidate.split("%", 1)[0])
                            return candidate
                        except ValueError:
                            pass

            # Fall back to ipconfig on older or restricted Windows systems.
            result = subprocess.run(
                ["ipconfig"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            if result.returncode == 0:
                lines = result.stdout.splitlines()
                for index, line in enumerate(lines):
                    if "default gateway" in line.lower():
                        values = [line.split(":", 1)[-1].strip()]
                        if not values[0] and index + 1 < len(lines):
                            values.append(lines[index + 1].strip())
                        for gateway in values:
                            if gateway:
                                try:
                                    ipaddress.ip_address(
                                        gateway.split("%", 1)[0]
                                    )
                                    return gateway
                                except ValueError:
                                    continue

        elif operating_system == "Linux":
            for family in ("-4", "-6"):
                result = subprocess.run(
                    ["ip", family, "route", "show", "default"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )
                if result.returncode == 0:
                    for line in result.stdout.splitlines():
                        parts = line.split()
                        if "via" in parts:
                            return parts[parts.index("via") + 1]

    except (OSError, subprocess.SubprocessError, IndexError):
        return None

    return None


def get_network_status(internet, dns, https):
    """Summarize connectivity without hiding the individual DNS and HTTPS checks."""
    if not internet:
        return "Disconnected"
    if not dns or not https:
        return "Partially Connected"
    return "Connected"


def calculate_quick_scan_status(results):
    """Return the most severe status among the supplied scan results."""
    if "[FAIL]" in results:
        return "[FAIL]"
    if "[WARNING]" in results or "[UNKNOWN]" in results:
        return "[WARNING]"
    return "[PASS]"


# ==============================
# Network User's Network Information
# ==============================

def get_network_information():
    """Collect network details and connection checks for reuse by the program."""
    hostname = socket.gethostname()
    gateway = get_default_gateway()

    # Ask the operating system which local address it would use for internet
    # traffic, supporting both IPv4 and IPv6 routes.
    ip_address = None
    address_family = None
    route_destinations = (
        (socket.AF_INET, ("8.8.8.8", 53)),
        (socket.AF_INET6, ("2001:4860:4860::8888", 53, 0, 0)),
    )
    for family, destination in route_destinations:
        try:
            with socket.socket(family, socket.SOCK_DGRAM) as route_socket:
                route_socket.connect(destination)
                ip_address = route_socket.getsockname()[0]
                address_family = family
                break
        except OSError:
            continue

    if not ip_address:
        try:
            addresses = socket.getaddrinfo(
                hostname, None, type=socket.SOCK_DGRAM
            )
            for family, _, _, _, address in addresses:
                local_ip = address[0]
                if not ipaddress.ip_address(local_ip.split("%", 1)[0]).is_loopback:
                    ip_address = local_ip
                    address_family = family
                    break
        except (socket.gaierror, OSError, ValueError):
            pass

    # psutil provides the IP, subnet mask, MAC address, and up/down state
    # for each named network interface.
    try:
        interfaces = psutil.net_if_addrs()
        interface_stats = psutil.net_if_stats()
    except (psutil.Error, OSError):
        interfaces = {}
        interface_stats = {}

    interface = None
    subnet_mask = None
    mac_address = None
    for name, addresses in interfaces.items():
        local_address = next(
            (
                address for address in addresses
                if address.family == address_family
                and address.address == ip_address
            ),
            None,
        )
        if local_address:
            interface = name
            subnet_mask = local_address.netmask
            link_family = getattr(psutil, "AF_LINK", None)
            mac = next((address.address for address in addresses
                        if address.family == link_family), None)
            if mac and mac not in ("00:00:00:00:00:00", "00-00-00-00-00-00"):
                mac_address = mac
            break

    # Test a direct connection by IP so this check does not depend on DNS.
    internet_status = False
    for destination in (
        ("1.1.1.1", 443),
        ("2606:4700:4700::1111", 443),
    ):
        try:
            with socket.create_connection(destination, timeout=3):
                internet_status = True
                break
        except OSError:
            continue

    # A successful name lookup confirms that DNS resolution is available.
    try:
        socket.getaddrinfo("google.com", None, type=socket.SOCK_STREAM)
        dns_status = True
    except (socket.gaierror, OSError):
        dns_status = False

    # Request a secure web page to check end-to-end HTTPS access.
    try:
        with urllib.request.urlopen("https://google.com", timeout=5):
            https_connected = True
            
    except (urllib.error.URLError, TimeoutError, OSError):
        https_connected = False

    interface_up = bool(
        interface and interface_stats.get(interface)
        and interface_stats[interface].isup
    )
    gateway_status = bool(gateway)
    # Keep short compatibility keys for the diagnostic and descriptive keys
    # for the network information screen and any other callers.
    return {
        "hostname": hostname,
        "ip_address": ip_address,
        "subnet_mask": subnet_mask,
        "dns": dns_status,
        "dns_working": dns_status,
        "https": https_connected,
        "https_working": https_connected,
        "internet": internet_status,
        "status": get_network_status(
            internet_status, dns_status, https_connected
        ),
        "interface": interface,
        "interface_up": interface_up,
        "gateway": gateway,
        "gateway_address": gateway,
        "default_gateway": gateway,
        "gateway_status": gateway_status,
        "mac_address": mac_address,
    }


# ==============================
# Network Diagnostic
# ==============================

def network_diagnostic():
    """Show the collected network details, check results, and likely issues."""
    # Prints a summary of the network tests using the shared information getter.
    results = get_network_information()
    print("\n========================================\nNETWORK SUMMARY\n========================================")
    print("\nHostname: " + (results["hostname"] or "Unavailable"))
    print("IP Address: " + (results["ip_address"] or "Unavailable") + "\n")
    print("Internet Connection: " + ("Connected" if results["internet"] else "Not Connected"))
    print("DNS Resolution: " + ("Working" if results["dns"] else "Not working"))
    print("Default Gateway: " + (results["gateway"] or "Not Found"))
    print("HTTPS Connection: " + ("Working" if results["https"] else "Not Working"))
    print("Interface: " + (results["interface"] or "Unavailable"))
    print("Subnet Mask: " + (results["subnet_mask"] or "Unavailable"))
    print("MAC Address: " + (results["mac_address"] or "Unavailable"))
    print("Network Status: " + results["status"])
    if results["status"] == "Partially Connected":
        failed_checks = []
        if not results["dns"]:
            failed_checks.append("DNS resolution")
        if not results["https"]:
            failed_checks.append("HTTPS")
        print(
            "Internet access is available, but "
            + " and ".join(failed_checks)
            + " check(s) failed."
        )

    print("\nRunning diagnostic....\n")
    # Use one list of labels and results to print each check consistently.
    checks = (
        ("Internet Connection", results["internet"]),
        ("DNS Resolution", results["dns"]),
        ("Default Gateway", results["gateway_status"]),
        ("HTTPS Connectivity", results["https"]),
    )
    for label, passed in checks:
        print(f"{label:<25} {'[PASS]' if passed else '[FAIL]'}")

    print("\nPotential Issue(s)")
    if not results["internet"]:
        print("An Internet connection could not be established. Check your network connection, router, or Internet Service Provider.")
    if not results["dns"]:
        print("DNS resolution appears to be failing. Your computer may be unable to translate domain names into IP addresses.")
    if not results["gateway_status"]:
        print("Your default gateway could not be detected. Your computer may be having trouble communicating with the local network or router.")
    if not results["https"]:
        print("HTTPS connectivity failed. Your computer may be experiencing a problem connecting to a secure website.")
    # Report a clean result only when every connectivity check passed.
    if all(results[key] for key in ("internet", "dns", "gateway_status", "https")):
        print("No network issues were detected.")

    return results



# ==============================
# Security Status
# ==============================

def security_status(display=True):
    """Check the OS-reported firewall status.

    Returns:
        True: Firewall reports enabled.
        False: Firewall reports disabled.
        None: Status could not be determined reliably.
    """
    operating_system = platform.system()
    enabled = None
    detail = "Firewall status could not be determined."

    if display:
        print(
            "\n========================================"
            "\nSECURITY STATUS"
            "\n========================================"
        )

    try:
        if operating_system == "Darwin":
            # macOS Application Firewall
            result = subprocess.run(
                [
                    "/usr/libexec/ApplicationFirewall/socketfilterfw",
                    "--getglobalstate",
                ],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )

            output = result.stdout.strip().lower()

            if result.returncode == 0:
                reports_disabled = bool(
                    re.search(r"\bfirewall is disabled\b", output)
                )
                reports_enabled = bool(
                    re.search(r"\bfirewall is enabled\b", output)
                )
                if reports_disabled and not reports_enabled:
                    enabled = False
                elif reports_enabled and not reports_disabled:
                    enabled = True
                else:
                    detail = "Unrecognized or conflicting macOS firewall response."
            else:
                detail = "macOS firewall command failed."

        elif operating_system == "Windows":
            # Check all Windows firewall profiles.
            powershell = shutil.which("powershell") or shutil.which("pwsh")
            if not powershell:
                detail = "PowerShell is not available."
                result = None
            else:
                result = subprocess.run(
                    [
                        powershell,
                        "-NoProfile",
                        "-NonInteractive",
                        "-Command",
                        "Get-NetFirewallProfile | "
                        "ForEach-Object { $_.Enabled }",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=False,
                )

            if result is not None and result.returncode == 0:
                values = [
                    line.strip().lower()
                    for line in result.stdout.splitlines()
                    if line.strip()
                ]

                # Three profiles are normally expected:
                # Domain, Private, and Public.
                if len(values) == 3 and all(
                    value in ("true", "false") for value in values
                ):
                    if all(value == "true" for value in values):
                        enabled = True
                    elif all(value == "false" for value in values):
                        enabled = False
                    else:
                        detail = "Windows firewall profiles have mixed states."
                else:
                    detail = "Windows firewall profiles could not be verified."
            elif result is not None:
                detail = "Windows firewall command failed."

        elif operating_system == "Linux":
            managers = []
            ufw = shutil.which("ufw")
            firewalld = shutil.which("firewall-cmd")

            if ufw:
                result = subprocess.run(
                    [ufw, "status"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )
                output = result.stdout.strip().lower().splitlines()
                status_line = output[0].strip() if output else ""
                if (
                    result.returncode == 0
                    and not result.stderr.strip()
                    and status_line == "status: active"
                ):
                    managers.append(("UFW", True))
                elif (
                    result.returncode == 0
                    and not result.stderr.strip()
                    and status_line == "status: inactive"
                ):
                    managers.append(("UFW", False))
                else:
                    managers.append(("UFW", None))

            if firewalld:
                result = subprocess.run(
                    [firewalld, "--state"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )
                output = result.stdout.strip().lower()
                if (
                    result.returncode == 0
                    and not result.stderr.strip()
                    and output == "running"
                ):
                    managers.append(("firewalld", True))
                elif (
                    result.returncode == 0
                    and not result.stderr.strip()
                    and output == "not running"
                ):
                    managers.append(("firewalld", False))
                else:
                    managers.append(("firewalld", None))

            if not managers:
                detail = "No supported firewall manager was found."
            elif any(state is None for _, state in managers):
                detail = "At least one installed firewall manager could not be verified."
            else:
                states = {state for _, state in managers}
                if len(states) > 1:
                    detail = "Installed firewall managers report conflicting states."
                elif states == {True}:
                    enabled = True
                else:
                    # An inactive service does not prove that no independent
                    # firewall rules are installed in the kernel.
                    detail = (
                        "The firewall manager is inactive, but independent "
                        "firewall rules cannot be ruled out."
                    )

        else:
            detail = "Firewall detection is not supported on this OS."

    except (OSError, subprocess.SubprocessError) as error:
        # Includes missing commands, permission errors, and timeouts.
        detail = f"Firewall check failed: {type(error).__name__}."

    if display:
        if enabled is True:
            print("\nFirewall: ENABLED ✓")
        elif enabled is False:
            print("\nFirewall: DISABLED ✗")
        else:
            print(f"\nFirewall: UNKNOWN — {detail}")

    return enabled


# ==============================
# Disk Encryption Status
# ==============================

def disk_encryption_status(display=True):
    """Check OS-reported encryption for the system volume.

    Returns True when encryption is positively identified, False when the
    system volume is positively identified as unencrypted, and None when its
    status cannot be determined reliably.
    """
    operating_system = platform.system()
    enabled = None
    label = "Disk Encryption"
    detail = "Disk encryption status could not be determined."

    try:
        if operating_system == "Darwin":
            label = "FileVault"
            result = subprocess.run(
                ["fdesetup", "status"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            output = result.stdout.strip().lower()
            if result.returncode == 0:
                if "filevault is on" in output:
                    enabled = True
                elif "filevault is off" in output:
                    enabled = False
                else:
                    detail = "Unrecognized FileVault status response."
            else:
                detail = "FileVault status command failed."

        elif operating_system == "Windows":
            label = "BitLocker"
            powershell = shutil.which("powershell") or shutil.which("pwsh")
            command = (
                "$v = Get-BitLockerVolume -MountPoint $env:SystemDrive "
                "-ErrorAction Stop; "
                "$v | Select-Object MountPoint,VolumeStatus,ProtectionStatus "
                "| ConvertTo-Json -Compress"
            )
            if not powershell:
                detail = "PowerShell is not available."
            else:
                result = subprocess.run(
                    [
                        powershell,
                        "-NoProfile",
                        "-NonInteractive",
                        "-Command",
                        command,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=15,
                    check=False,
                )
            if powershell and result.returncode == 0:
                try:
                    volume = json.loads(result.stdout)
                    volume_status = str(volume.get("VolumeStatus", "")).lower()
                    protection_status = str(volume.get("ProtectionStatus", "")).lower()
                    if volume_status == "fullyencrypted" and protection_status == "on":
                        enabled = True
                    elif volume_status == "fullydecrypted":
                        enabled = False
                    else:
                        detail = "BitLocker status is incomplete or protection is suspended."
                except (ValueError, AttributeError):
                    detail = "Unrecognized BitLocker status response."
            elif powershell:
                detail = "BitLocker status could not be read."

        elif operating_system == "Linux":
            root_result = subprocess.run(
                [
                    "findmnt", "-n", "-o", "SOURCE,FSTYPE", "--target", "/"
                ],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            root_line = next(
                (line.strip() for line in root_result.stdout.splitlines()
                 if line.strip()),
                "",
            )
            root_fields = root_line.split(maxsplit=1)
            root_source = root_fields[0] if root_fields else ""
            filesystem = root_fields[1].split()[0] if len(root_fields) > 1 else ""
            # findmnt appends Btrfs subvolume details, e.g.
            # /dev/mapper/cryptroot[/@]. lsblk needs just the block device.
            root_source = root_source.split("[", 1)[0]
            if root_result.returncode != 0 or not root_source.startswith("/"):
                detail = "The root storage device could not be identified."
            elif "," in root_source or filesystem.lower() == "overlay":
                detail = "The root filesystem source is not a single supported block device."
            else:
                devices_result = subprocess.run(
                    [
                        "lsblk", "--json", "--inverse", "--paths",
                        "--output", "NAME,KNAME,TYPE,PKNAME,MAJ:MIN",
                        root_source,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )
                if devices_result.returncode != 0:
                    detail = "The root storage device layout could not be read."
                else:
                    try:
                        device_data = json.loads(devices_result.stdout)
                        root_devices = device_data.get("blockdevices", [])
                        nodes = []

                        def collect_nodes(devices):
                            for device in devices:
                                nodes.append(device)
                                collect_nodes(device.get("children", []))

                        collect_nodes(root_devices)
                        root_realpath = os.path.realpath(root_source)
                        root_basename = os.path.basename(root_source)
                        root_matches = [
                            node for node in nodes
                            if root_source in (
                                node.get("name"), node.get("kname")
                            )
                            or root_realpath in (
                                os.path.realpath(node.get("name", "")),
                                os.path.realpath(node.get("kname", "")),
                            )
                            or root_basename in (
                                os.path.basename(node.get("name", "")),
                                os.path.basename(node.get("kname", "")),
                            )
                        ]
                        if len(root_matches) != 1:
                            detail = "The root device could not be matched to its block-device layout."
                        else:
                            root_device = root_matches[0]
                            ancestors = []

                            def collect_device_tree(device):
                                ancestors.append(device)
                                for parent in device.get("children", []):
                                    collect_device_tree(parent)

                            collect_device_tree(root_device)
                            crypt_devices = [
                                device for device in ancestors
                                if str(device.get("type", "")).lower() == "crypt"
                            ]

                            if crypt_devices:
                                for device in crypt_devices:
                                    names = (
                                        os.path.basename(root_source),
                                        os.path.basename(device.get("name", "")),
                                        os.path.basename(device.get("kname", "")),
                                    )
                                    for mapping_name in dict.fromkeys(
                                        name for name in names if name
                                    ):
                                        crypt_result = subprocess.run(
                                            [
                                                "cryptsetup", "status",
                                                mapping_name,
                                            ],
                                            capture_output=True,
                                            text=True,
                                            timeout=5,
                                            check=False,
                                        )
                                        crypt_output = crypt_result.stdout.lower()
                                        if (
                                            crypt_result.returncode == 0
                                            and re.search(
                                                r"^\s*type:\s*luks(?:\d+)?\s*$",
                                                crypt_output,
                                                re.MULTILINE,
                                            )
                                        ):
                                            enabled = True
                                            break
                                    if enabled is True:
                                        break
                                if enabled is not True:
                                    detail = "A device-mapper layer was found, but LUKS could not be confirmed."
                            else:
                                detail = (
                                    "No LUKS mapping was confirmed for the root "
                                    "filesystem; other encryption methods cannot be ruled out."
                                )
                    except (ValueError, AttributeError, TypeError):
                        detail = "Unrecognized block-device layout response."
        else:
            detail = f"Disk encryption detection is not implemented for {get_operating_system()}."

    except (OSError, subprocess.SubprocessError) as error:
        detail = f"Encryption check failed: {type(error).__name__}."

    if display:
        if enabled is True:
            print(f"\n{label}: ENABLED ✓")
        elif enabled is False:
            print(f"\n{label}: DISABLED ✗")
        else:
            print(f"\nDisk Encryption: UNKNOWN — {detail}")

    return enabled


def check_os_updates(display=True):
    """Check whether the native OS update service reports pending updates.

    Returns True if updates are available, False if none are reported, and
    None when the platform or update service cannot be checked.
    """
    operating_system = platform.system()
    command = None
    detail = "OS update checks are not supported on this system."

    if operating_system == "Windows":
        powershell = shutil.which("powershell") or shutil.which("pwsh")
        if powershell:
            script = (
                "$ErrorActionPreference = 'Stop'; "
                "$session = New-Object -ComObject Microsoft.Update.Session; "
                "$result = $session.CreateUpdateSearcher().Search("
                "\"IsInstalled=0 and Type='Software'\"); "
                "if ($result.Updates.Count -gt 0) { "
                "'UpdatesAvailable' } else { 'UpToDate' }"
            )
            command = [powershell, "-NoProfile", "-NonInteractive", "-Command", script]
            detail = "Windows Update could not be queried."
        else:
            detail = "PowerShell is not available."

    elif operating_system == "Darwin":
        software_update = shutil.which("softwareupdate")
        if software_update:
            command = [software_update, "--list"]
            detail = "macOS Software Update could not be queried."
        else:
            detail = "The macOS Software Update command is not available."

    elif operating_system == "Linux":
        if shutil.which("apt-get"):
            command = ["apt-get", "-s", "upgrade"]
            detail = "The package update list could not be checked."
        elif shutil.which("dnf"):
            command = ["dnf", "check-update", "--quiet"]
            detail = "The DNF update list could not be checked."
        elif shutil.which("yum"):
            command = ["yum", "check-update"]
            detail = "The YUM update list could not be checked."
        else:
            detail = "No supported Linux package manager was found."

    available = None
    if command:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            available = _parse_update_check_result(operating_system, command[0], result)
            if available is None:
                detail = "The update service failed or returned an unrecognized status."
        except (OSError, subprocess.SubprocessError) as error:
            detail = f"OS update check failed: {type(error).__name__}."

    if display:
        if available is True:
            print("\nOperating System Updates: AVAILABLE")
            print("Install recommended updates using your system's update settings.")
        elif available is False:
            print("\nOperating System Updates: No updates reported")
        else:
            print(f"\nOperating System Updates: UNKNOWN — {detail}")
            if operating_system == "Linux":
                print("Update availability depends on the package manager's local package list.")
    return available


def _parse_update_check_result(operating_system, command, result):
    """Interpret only documented successful update-check outcomes."""
    if operating_system == "Windows":
        if result.returncode != 0 or result.stderr.strip():
            return None
        lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        if len(lines) != 1 or lines[0] not in ("UpdatesAvailable", "UpToDate"):
            return None
        return lines[0] == "UpdatesAvailable"

    if operating_system == "Darwin":
        if result.returncode != 0 or result.stderr.strip():
            return None
        output = result.stdout.lower()
        update_lines = [
            line for line in result.stdout.splitlines()
            if line.lstrip().startswith("* Label:")
        ]
        no_updates = bool(re.search(
            r"^\s*no new software available\.?\s*$",
            output,
            re.IGNORECASE | re.MULTILINE,
        ) or re.search(
            r"^\s*no updates are available\.?\s*$",
            output,
            re.IGNORECASE | re.MULTILINE,
        ))
        if update_lines and no_updates:
            return None
        if update_lines:
            return True
        if no_updates and not re.search(
            r"\b(error|failed|cannot|could not)\b", output
        ):
            return False
        return None

    if operating_system != "Linux":
        return None

    if command == "apt-get":
        if result.returncode != 0 or re.search(
            r"^\s*(?:Err:|E:)",
            f"{result.stdout}\n{result.stderr}",
            re.IGNORECASE | re.MULTILINE,
        ):
            return None
        if re.search(
            r"^\s*The following packages have been kept back:",
            result.stdout,
            re.IGNORECASE | re.MULTILINE,
        ):
            return True
        if re.search(r"^\s*Inst\s+", result.stdout, re.IGNORECASE | re.MULTILINE):
            return True
        summary = re.search(
            r"^\s*(\d+)\s+upgraded,\s+\d+\s+newly installed,"
            r"\s+\d+\s+to remove and\s+\d+\s+not upgraded\.?\s*$",
            result.stdout,
            re.IGNORECASE | re.MULTILINE,
        )
        if summary:
            return int(summary.group(1)) > 0
        return None

    if command in ("dnf", "yum"):
        if result.returncode == 100:
            if result.stderr.strip():
                return None
            package_rows = [
                line for line in result.stdout.splitlines()
                if re.match(r"^\s*\S+\.\S+\s+\S+\s+\S+\s*$", line)
            ]
            return True if package_rows else None
        if result.returncode != 0:
            return None
        if not result.stdout.strip() and not result.stderr.strip():
            return False
        return None

    return None


def security_assessment():
    """Summarize firewall, disk encryption, and operating-system update status."""
    print(
        "\n========================================"
        "\nSYSTEM SECURITY ASSESSMENT"
        "\n========================================"
    )

    firewall = security_status(display=False)
    encryption = disk_encryption_status(display=False)
    updates = check_os_updates(display=False)
    checks = []

    if firewall is True:
        checks.append(("Firewall", "[PASS]", "Reported enabled"))
    elif firewall is False:
        checks.append(("Firewall", "[FAIL]", "Reported disabled"))
    else:
        checks.append(("Firewall", "[UNKNOWN]", "Status unavailable"))

    if encryption is True:
        checks.append(("Disk Encryption", "[PASS]", "Reported enabled"))
    elif encryption is False:
        checks.append(("Disk Encryption", "[WARNING]", "Reported disabled"))
    else:
        checks.append(("Disk Encryption", "[UNKNOWN]", "Status unavailable"))

    if updates is True:
        checks.append(("OS Updates", "[WARNING]", "Updates are available"))
    elif updates is False:
        checks.append(("OS Updates", "[PASS]", "No updates reported"))
    else:
        checks.append(("OS Updates", "[UNKNOWN]", "Could not be checked"))

    for label, status, detail in checks:
        print(f"{label:<22} {status:<12} {detail}")

    if firewall is False:
        overall_result = "[FAIL]"
        print("\nReview firewall settings and enable an appropriate firewall.")
    elif (
        encryption is False
        or updates is True
        or any(status == "[UNKNOWN]" for _, status, _ in checks)
    ):
        overall_result = "[WARNING]"
        if encryption is False:
            print("Enable disk encryption to help protect data if the device is lost.")
        if updates is True:
            print("Install the available operating-system updates.")
        if any(status == "[UNKNOWN]" for _, status, _ in checks):
            print("Some security checks could not be verified on this system.")
    else:
        overall_result = "[PASS]"
        print("\nNo issues were identified by the available security checks.")

    print(f"\nOverall Security: {overall_result}")
    print("This assessment checks reported settings and available OS updates.")
    return {
        "Firewall": firewall,
        "Disk Encryption": encryption,
        "OS Updates": updates,
        "Overall Result": overall_result,
    }


# ==============================
# Quick System & Network Scan
# ==============================

def _quick_scan_check_rows(system, network, statuses, firewall_text):
    """Build the shared display and report rows for a Quick Scan."""
    encryption_value = statuses.get("Encryption Value")
    if encryption_value is None and "Encryption Results" in statuses:
        encryption_value = statuses["Encryption Results"]

    encryption_result = statuses.get("Encryption Result")
    if encryption_value is True:
        encryption_result = "[PASS]"
    elif encryption_value is False:
        encryption_result = "[WARNING]"
    elif encryption_result == "[PASS]":
        encryption_value = True
    elif encryption_result in ("[FAIL]", "[WARNING]"):
        encryption_value = False
        encryption_result = "[WARNING]"
    else:
        encryption_result = "[UNKNOWN]"

    encryption_text = (
        "Unknown" if encryption_value is None
        else "Enabled" if encryption_value is True
        else "Disabled"
    )
    updates = statuses.get("OS Updates")
    if updates is True:
        updates_text, updates_result = "Available", "[WARNING]"
    elif updates is False:
        updates_text, updates_result = "None reported", "[PASS]"
    else:
        updates_text, updates_result = "Unknown", "[UNKNOWN]"
    return (
        ("SYSTEM", (
            ("CPU Usage", f"{system['CPU Usage']:.1f}%", statuses["CPU Result"]),
            ("Memory Usage", f"{system['Memory Usage']:.1f}%", statuses["Memory Result"]),
            ("Storage Usage", f"{system['Disk Usage']:.1f}%", statuses["Disk Result"]),
        )),
        ("NETWORK", (
            (
                "Internet Connection",
                "Connected" if network["internet"] else "Not Connected",
                statuses["Internet Result"],
            ),
            (
                "DNS Resolution",
                "Working" if network["dns"] else "Not Working",
                statuses["DNS Result"],
            ),
            (
                "Default Gateway",
                "Found" if network["gateway_status"] else "Not Found",
                statuses["Gateway Result"],
            ),
            (
                "HTTPS Connectivity",
                "Working" if network["https"] else "Not Working",
                statuses["HTTPS Result"],
            ),
        )),
        ("SECURITY", (
            ("Firewall Status", firewall_text, statuses["Firewall Result"]),
            ("Disk Encryption", encryption_text, encryption_result),
            ("OS Updates", updates_text, updates_result),
        )),
    )


def quick_scan():
    """Run a quick system, network, and firewall health check."""
    print("\n========================================\nBYTE WIZARD SCAN\n========================================")

    system = get_system_information()
    network = get_network_information()
    firewall = security_status(display=False)
    encryption = disk_encryption_status(display=False)
    updates = check_os_updates(display=False)
    scan_time = datetime.datetime.now()

    cpu_result = check_threshold(system["CPU Usage"], 70, 90)
    memory_result = check_threshold(system["Memory Usage"], 80, 90)
    disk_result = check_threshold(system["Disk Usage"], 80, 90)
    internet_result = "[PASS]" if network["internet"] else "[FAIL]"
    dns_result = "[PASS]" if network["dns"] else "[FAIL]"
    gateway_result = "[PASS]" if network["gateway_status"] else "[FAIL]"
    https_result = "[PASS]" if network["https"] else "[FAIL]"
    firewall_result = "[UNKNOWN]" if firewall is None else ("[PASS]" if firewall else "[FAIL]")
    firewall_text = "Unknown" if firewall is None else ("Enabled" if firewall else "Disabled")
    encryption_result = (
        "[UNKNOWN]" if encryption is None
        else "[PASS]" if encryption is True
        else "[WARNING]"
    )
    updates_result = (
        "[UNKNOWN]" if updates is None
        else "[WARNING]" if updates
        else "[PASS]"
    )

    results = (
        cpu_result, memory_result, disk_result, internet_result, dns_result,
        gateway_result, https_result, firewall_result, encryption_result,
        updates_result,
    )
    overall_result = calculate_quick_scan_status(results)

    statuses = {
        "CPU Result": cpu_result,
        "Memory Result": memory_result,
        "Disk Result": disk_result,
        "Internet Result": internet_result,
        "DNS Result": dns_result,
        "Gateway Result": gateway_result,
        "HTTPS Result": https_result,
        "Firewall Result": firewall_result,
        "Encryption Result": encryption_result,
        "Encryption Value": encryption,
        "OS Updates": updates,
        "OS Updates Result": updates_result,
        "Overall Result": overall_result,
    }
    checks = _quick_scan_check_rows(system, network, statuses, firewall_text)
    statuses["Checks"] = checks

    print(f"Scan Time: {scan_time.strftime('%Y-%m-%d %H:%M:%S')}")
    for section, section_checks in checks:
        print(f"\n{section}\n")
        for label, value, status in section_checks:
            print(f"{label:<25} {value:<12} {status}")

    print("\n========================================")
    print(f"{'Overall Status:':<25} {overall_result}")
    print("========================================")

    if ask_yes_no("\nWould you like to save this scan as a .txt report?"):
        save_quick_scan_report(
            system, network, statuses, firewall_text, scan_time=scan_time
        )

    return statuses


# ==============================
# Quick System & Network Scan Save
# ==============================

def save_quick_scan_report(
    system, network, statuses, firewall_text="Unknown", scan_time=None
):
    """Save the same timestamped Quick Scan summary shown on screen."""
    scan_time = scan_time or datetime.datetime.now()
    timestamp = scan_time.strftime("%Y-%m-%d_%H-%M-%S")
    report_name = f"byte_wizard_quick_scan_{timestamp}.txt"
    checks = statuses.get("Checks") or _quick_scan_check_rows(
        system, network, statuses, firewall_text
    )

    try:
        with open(report_name, "w", encoding="utf-8") as report:
            report.write("========================================\n")
            report.write("           BYTE WIZARD SCAN\n")
            report.write("========================================\n")
            report.write(
                f"Date/Time: {scan_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            report.write(f"Hostname: {platform.node()}\n")
            report.write(f"Operating System: {get_operating_system()}\n\n")
            for section, section_checks in checks:
                report.write(f"{section}\n----------------------------------------\n")
                for label, value, status in section_checks:
                    report.write(f"{label:<25} {value:<12} {status}\n")
                report.write("\n")
            report.write("========================================\n")
            report.write(f"OVERALL STATUS: {statuses['Overall Result']}\n")
            report.write("========================================\n")
    except OSError as error:
        print(f"\nCould not save the Quick Scan report: {error}")
        return None

    print(f"\nReport saved as: {report_name}")
    return report_name


        
# ==============================
# System Diagnostic
# ==============================

def system_diagnostic():
    """Display resource usage and flag values that may need attention."""
    print("\n========================================\nSYSTEM SUMMARY\n========================================")

    results = get_system_information()
    
    operating_system = get_operating_system()

    print(f"\n{'Operating System:':<25}   {operating_system}")
    print(f"{'OS Version:':<25}   {platform.release()}")
    print(f"{'Machine Type:':<25}   {platform.machine()}")
    print(f"{'Hostname:':<25}   {platform.node()}")
    print(f"{'Python Version:':<25}  {platform.python_version()}\n")

    print(f"{'CPU Usage:':<25}  {results['CPU Usage']}%")

    # Lower usage is healthy; higher ranges produce a warning or failure.
    cpu_result = check_threshold(results["CPU Usage"], 70, 90)


    print(f"{'Memory Usage:':<25}  {results['Memory Usage']}%")
    memory_result = check_threshold(results["Memory Usage"], 80, 90)


    print(f"{'Storage Usage:':<25}   {results['Disk Usage']}% used")

    disk_result = check_threshold(results["Disk Usage"], 80, 90)

    print(f"{'Disk Free:':<25}  {results['Disk Free']:.2f} GB\n")
    

    uptime = get_uptime()
    print(f"{'System Uptime:':<25}  {uptime}")

    if uptime < datetime.timedelta(days=14):
        uptime_result = "[PASS]"
    elif uptime <= datetime.timedelta(days=30):
        uptime_result = "[WARNING]"
    else:
        uptime_result = "[FAIL]"


    # Combine individual results to calculate one overall status.
    diagnostic_results = (
        cpu_result,
        memory_result,
        disk_result,
        uptime_result
    )
    if any(result == "[FAIL]" for result in diagnostic_results):
        overall_result = "[FAIL]"
    elif any(result == "[WARNING]" for result in diagnostic_results):
        overall_result = "[WARNING]"
    else:
        overall_result = "[PASS]"
    
    # Runs a diagnostic
    print("\nRunning diagnostic....\n")

    print(f"{'CPU Usage':<25} {cpu_result}")
    print(f"{'Memory Results':<25} {memory_result}")
    print(f"{'Disk Results':<25} {disk_result}")
    print(f"{'Current Uptime':<25} {uptime_result}\n")

# Tells the user of potential issues if anything has failed
    print("Reason:")

    issues_found = False

    if cpu_result in ("[FAIL]", "[WARNING]"):
        print("CPU usage is high, consider closing some applications.")
        issues_found = True

    if memory_result in ("[FAIL]", "[WARNING]"):
        print("Your memory usage is high, consider upgrading memory if high usage persists.")
        issues_found = True

    if disk_result in ("[FAIL]", "[WARNING]"):
        print("Your disks are getting full, consider deleting some old files or applications.")
        issues_found = True

    if uptime_result in ("[FAIL]", "[WARNING]"):
        print("Current uptime is high, consider restarting your PC.")
        issues_found = True

    if not issues_found:
        print("No system issues were detected.")

    overall_label = "\nOverall Diagnostic:\n"
    print(f"{overall_label:<25} {overall_result}")

    return {
        "CPU Result": cpu_result,
        "Memory Result": memory_result,
        "Disk Result": disk_result,
        "Uptime Result": uptime_result,
        "Overall Result": overall_result
    }


# ==============================
# User Class
# ==============================

class User:
    """Store the user's name."""
    def __init__(self, name):
        self.name = name


# ==============================
# Main Menu
# ==============================

def main_menu():
    """Print the numbered choices handled by user_troubleshooting()."""
    print("\n========================================\nMAIN MENU\n========================================")

    print("\n1. Troubleshoot a Problem")
    print("2. System Options")
    print("3. Network Options")
    print("4. Security")
    print("5. System Health")
   
    print("\n6. Exit")


# ==============================
# Security Menu
# ==============================

def security_menu():
    """Print the numbered choices for security checks."""
    print("\n========================================\nSECURITY\n========================================")
    print("\n1. Run Security Assessment")
    print("2. Check for OS Updates")
    print("\n3. Return to Main Menu")


# ==============================
# Troubleshooting Menu
# ==============================

def troubleshoot_menu():
    """Print the numbered choices for troubleshooting."""
    print("\n========================================\nTROUBLESHOOTING\n========================================")

    print("\n1. Slow Computer")
    print("2. No Internet")
    print("3. No Sound")
    print("4. Computer Won't Turn On")
    print("5. Other Issue")
    print("\n6. Return to Main Menu")


# ==============================
# System Menu
# ==============================

def system_menu():
    """Print the numbered choices for system diagnostics."""
    print("\n========================================\nSYSTEM\n========================================")

    print("\n1. View System Information")
    print("2. Run System Diagnostic")
    
    print("\n3. Return to Main Menu")


# ==============================
# Network Menu
# ==============================

def network_menu():
    """Print the numbered choices for network diagnostics."""
    print("\n========================================\nNETWORK\n========================================")

    print("\n1. View Network Information")
    print("2. Run Network Diagnostic")
    
    print("\n3. Return to Main Menu")


# ==============================
# System Health Menu
# ==============================

def system_health_menu():
    """Print the numbered choices for system health checks."""
    print("\n========================================\nSYSTEM HEALTH\n========================================")

    print("\n1. Quick Scan")
    print("2. View Running Processes")
    
    print("\n3. Return to Main Menu")

# ==============================
# Troubleshooting Functions
# ==============================

def ask_yes_no(question):
    """Ask a yes/no question, accepting either words or the displayed numbers."""
    while True:
        answer = input(f"{question} (yes/no): ").strip().lower()
        if answer in ("yes", "y", "1"):
            return True
        if answer in ("no", "n", "2"):
            return False
        print("Invalid input. Please enter yes or no.")


def slow_computer(user):
    """Ask targeted questions and suggest next steps for a slow computer."""
    print("\n========================================\nSLOW COMPUTER\n========================================")

    if not ask_yes_no("Is your computer slow all the time?"):
        print("\nTry these troubleshooting steps:")
        print("- Check whether a specific program is causing the slowdown.")
        print("- Run a security scan and install available software updates.")
        print("- Free up storage by removing files or applications you no longer need.")
        if ask_yes_no("Would you like to run a system diagnostic?"):
            system_diagnostic()
        return

    if ask_yes_no("Is your CPU usage above 90%?"):
        print("\nA program or background process may be using too much CPU.")
        print("Recommended steps:")
        print("- Open Task Manager or Activity Monitor and identify high-CPU processes.")
        print("- Close unnecessary applications and restart if the high usage persists.")
        return

    if ask_yes_no("Does the slowdown happen with a specific application or game?"):
        print("\nThe slowdown may be related to that application.")
        print("- Check its CPU and memory usage, and install available updates.")
        print("- Check that your computer meets the application's requirements.")
        print("- Close other applications before running it.")
        return

    if ask_yes_no("Is your memory usage above 80%?"):
        print("\nYour system is using a high amount of memory.")
        print("- Close unnecessary applications and browser tabs.")
        print("- Check which processes are using the most memory.")
        print("- Restart the computer; consider additional RAM if this continues.")
        return

    if ask_yes_no("Does your computer have less than 20% free storage?"):
        print("\nYour storage drive is nearly full, which can affect performance.")
        print("- Remove unnecessary files, empty the Trash, or uninstall unused applications.")
        print("- Move large files to another storage location.")
        return

    if not ask_yes_no("Have you restarted your computer recently?"):
        print("\nA restart can clear temporary problems caused by applications or background processes.")
        print("Restart your computer and check whether performance improves.")
        return

    if not ask_yes_no("Are your operating system and applications up to date?"):
        print("\nInstall available operating system and application updates, then restart.")
        return

    if not ask_yes_no("Have you recently run a malware/security scan?"):
        print("\nRun a scan using your installed security software.")
        return

    print("\nByte Wizard couldn't identify an obvious system resource issue.")
    print("Consider checking startup applications, recently installed software, and hardware health, or getting technical assistance.")

def no_internet(user):
    """Use network check results to guide internet troubleshooting."""
    print("\n========================================\nNO INTERNET\n========================================")

    while True:
        connection_type = input("Are you using wired Ethernet or Wi-Fi? (wired/wireless): ").strip().lower()
        if connection_type in ("wired", "ethernet", "1"):
            connection_type = "wired"
            break
        if connection_type in ("wireless", "wi-fi", "wifi", "2"):
            connection_type = "wireless"
            break
        print("Please enter wired or wireless.")

    print("\nByte Wizard will check your local gateway, internet access, DNS, and HTTPS.")
    results = network_diagnostic()

    # Start with the earliest point in the connection path that failed.
    if not results["gateway"]:
        print("\nYour computer could not detect a default gateway, so it may not be connected to the local network.")
        if connection_type == "wired":
            print("- Reseat the Ethernet cable at both ends and check the router or computer port lights.")
            print("- If possible, try another Ethernet cable or router port.")
        else:
            print("- Confirm Wi-Fi is enabled and that you are connected to the correct network.")
            print("- Disconnect from the network, reconnect, and re-enter its password if prompted.")
        print("- Restart the router and modem, then wait a few minutes for them to reconnect.")
        print("- If this is a work, school, hotel, or public network, check whether sign-in is required.")
        return

    if not results["internet"]:
        print(f"\nA local gateway was found ({results['gateway_address']}), but an external internet connection failed.")
        print("- Check whether other devices on the same network can access the internet.")
        if connection_type == "wired":
            print("- Confirm the Ethernet cable is firmly connected and try another router port if available.")
        else:
            print("- Check that Wi-Fi shows you as connected, then disconnect and reconnect to the network.")
        print("- Restart the modem and router; allow them several minutes to come back online.")
        if ask_yes_no("Can other devices on this network access the internet?"):
            print("\nThe issue may be specific to this computer. Disable any VPN temporarily and check proxy settings.")
            print("You can also reconnect to the network or restart this computer.")
        else:
            print("\nThe issue likely affects the network or internet service. Check the modem/router status lights and contact your internet provider if it persists.")
        return

    if not results["dns"]:
        print("\nYour computer can reach the internet by address, but DNS lookup failed.")
        print("- Disconnect and reconnect to the network, then try again.")
        print("- Restart the router or modem to refresh its DNS connection.")
        print("- If you use a VPN or custom DNS service, disconnect it temporarily and retry.")
        print("- On a managed work or school network, ask its administrator before changing DNS settings.")
        return

    if not results["https"]:
        print("\nInternet access and DNS worked, but the secure HTTPS check failed.")
        print("- Open a browser and check whether the network requires a sign-in page.")
        print("- Check your computer's date and time, then retry.")
        print("- Temporarily disconnect a VPN or proxy if you use one; reconnect it after checking.")
        print("- Security software or a restricted network may be blocking the connection.")
        return

    print("\nThe network checks passed, so the connection may be limited to a particular app or website.")
    if ask_yes_no("Does the problem happen only in one app or website?"):
        print("- Try the same site in another browser or the same app on another network.")
        print("- Check the app's network permissions and whether it needs an update.")
        print("- If only one site is affected, it may be temporarily unavailable.")
    else:
        print("- Check whether a VPN, proxy, firewall, or security app is blocking traffic.")
        print("- Restart the affected app and reconnect to the network.")

def no_sound(user):
    """Guide the user through common volume, device, and app checks."""
    print("\n========================================\nNO SOUND\n========================================")
    print(f"Let's narrow this down, {user.name}. Try each suggested check and see whether sound returns.\n")

    if ask_yes_no("Is the sound muted, or is the volume very low?"):
        print("\nUnmute the computer and the app, then raise the volume a little.")
        print("Check any keyboard mute key, speaker controls, and headset volume wheel too.")
        if ask_yes_no("Did that restore the sound?"):
            print("Great—the volume or mute setting was the cause.")
            return

    if ask_yes_no("Are headphones, speakers, or another audio device connected?"):
        print("\nConfirm the device is powered on and connected firmly. For Bluetooth, check its battery and reconnect it.")
        print("In sound settings, select the headphones or speakers you want to use as the output device.")
        if ask_yes_no("Did that restore the sound?"):
            print("Great—the output device or connection was the cause.")
            return
    else:
        print("\nOpen your computer's sound settings and make sure its built-in speakers are selected as the output device.")

    if ask_yes_no("Does the problem happen in just one app or website?"):
        print("\nCheck that app's volume and mute controls, then try another video or sound in a different app.")
        print("If other apps work, restart or update the affected app and check its audio permissions.")
    else:
        print("\nRestart the computer and test sound again. Check for available operating system updates afterward.")

    print("If sound is still missing, try another pair of headphones or speakers if available.")
    print("If only one audio device fails, its cable, battery, or hardware may need attention.")


def computer_wont_turn_on(user):
    """Suggest safe power and display checks based on startup symptoms."""
    print("\n========================================\nCOMPUTER WON'T TURN ON\n========================================")
    print(f"Let's check the power safely, {user.name}.\n")

    if ask_yes_no("Is there any sign of power, such as lights, fan noise, or a startup sound?"):
        print("\nThe computer may be starting but not showing an image.")
        print("Raise the screen brightness and check that the monitor is on and connected to the correct input.")
        if ask_yes_no("Are you using an external monitor?"):
            print("Reconnect the display cable at both ends, or try another cable or monitor input if available.")
        print("Disconnect docks and other accessories, then restart and watch for an error message.")
        print("If you hear beeps or see blinking lights, note their pattern for the device maker's support instructions.")
        return

    print("\nCheck that the power adapter is firmly connected to the computer and a working outlet.")
    print("If possible, test the outlet with another device and check the adapter or charging light.")
    print("For a laptop, leave it connected to its correct charger for 15 minutes, then try the power button once.")
    print("Disconnect USB devices, docks, and other accessories before trying again.")
    print("For a desktop, check that the power supply switch at the back is on, if it has one.")
    print("If there was a spill, burning smell, unusual heat, or a swollen battery, unplug it and stop using it; arrange professional service.")
    print("If it still shows no power, the charger, battery, or computer may need professional repair.")


def other_issues(user):
    """Let the user summarize another issue and keep a record for technician review."""
    print("\n========================================\nOTHER ISSUE\n========================================")
    print("Describe the problem in a sentence or two. Avoid including passwords or other private information.\n")
    detailed_issue = input("> ").strip()
    while not detailed_issue:
        print("Please enter a short description so you can review it.")
        detailed_issue = input("> ").strip()

    print(f"\nThanks, {user.name}. Your issue summary is:\n\"{detailed_issue}\"\n")
    print("Byte Wizard does not send or save support requests, so keep this summary to share with a technician if needed.")


# ==============================
# System Information
# ==============================

def view_system_information():
    """Display operating system details and hardware capacity information."""
    print("\n========================================\nSYSTEM INFORMATION\n========================================")

    operating_system = get_operating_system()

    results = get_system_information()

    print(f"\n{'Operating System:':<25}   {operating_system}")
    print(f"{'OS Version:':<25}   {platform.release()}")
    print(f"{'Machine Type:':<25}   {platform.machine()}")
    print(f"{'Hostname:':<25}   {platform.node()}")
    print(f"{'Python Version:':<25}  {platform.python_version()}\n")

    print(f"{'CPU Cores:':<25}  {psutil.cpu_count()}")
    print(f"{'Total Memory:':<25}  {results['Memory Total']:.2f} GB")
    print(f"{'Total Storage:':<25}  {results['Disk Total']:.2f} GB")


# ==============================
# Network Information
# ==============================

def view_network_information():
    """Display the reusable network details returned by the network collector."""
    results = get_network_information()
    print("\n========================================\nNETWORK INFORMATION\n========================================")
    print(f"Hostname: {results['hostname'] or 'Unavailable'}")
    print(f"IP Address: {results['ip_address'] or 'Unavailable'}")
    print(f"Subnet Mask: {results['subnet_mask'] or 'Unavailable'}")
    print(f"DNS Working: {'Yes' if results['dns_working'] else 'No'}")
    print(f"HTTPS Working: {'Yes' if results['https_working'] else 'No'}")
    print(f"Status: {results['status']}")
    if results["status"] == "Partially Connected":
        failed_checks = []
        if not results["dns"]:
            failed_checks.append("DNS resolution")
        if not results["https"]:
            failed_checks.append("HTTPS")
        print(
            "Internet access works, but "
            + " and ".join(failed_checks)
            + " failed."
        )
    print(f"Interface: {results['interface'] or 'Unavailable'}")
    print(f"Default Gateway: {results['default_gateway'] or 'Unavailable'}")
    print(f"MAC Address: {results['mac_address'] or 'Unavailable'}")


# ==============================
# Running Processes
# ==============================

def view_running_processes():
    """Display the top 10 running processes by CPU usage."""
    
    # Displays running processes on the user's system
    print("\n========================================")
    print("           RUNNING PROCESSES")
    print("========================================")

    print(f"{'PID':<10}{'Process Name':<35}{'CPU %':<10}")
    print("-" * 55)

    # Establish a CPU measurement baseline
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            proc.cpu_percent()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # Wait once instead of waiting for every process
    time.sleep(0.5)

    # Store process information before sorting
    processes = []

    for proc in psutil.process_iter(['pid', 'name']):
        try:
            cpu_usage = proc.cpu_percent()

            if cpu_usage != 0.0:
                processes.append(
                    (
                        proc.info['pid'],
                        proc.info['name'],
                        cpu_usage
                    )
                )

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # Sort by CPU usage from highest to lowest
    processes.sort(key=lambda process: process[2], reverse=True)

    # Display the sorted processes
    for pid, name, cpu_usage in processes[:10]:
        print(
            f"{pid:<10}"
            f"{name:<35}"
            f"{cpu_usage:<10.1f}"
        )


# ==============================
# Main Troubleshooting Loop
# ==============================

def user_troubleshooting(user):
    """Read menu choices, run the selected feature, and offer another turn."""
    while True:
        print(
            "\nThank you " + user.name +
            ". Please select an option:\n"
        )

        main_menu()

        choice = input("\nEnter a number (1-6): ").strip()
        if not choice.isdigit() or int(choice) not in range(1, 7):
            print("Invalid choice. Please enter a number from 1 to 6.")
            continue
        option = int(choice)

        # Exit before dispatching a feature; all other numbers map to a menu item.
        if option == 6:
            print(f"\nThank you {user.name} for choosing Byte Wizard. Goodbye!")
            print(ascii_title)
            break

        if option == 1:
            troubleshoot_menu()
            print("\nPlease select a troubleshooting option (1-6):")
            sub_choice = input().strip()

            if not sub_choice.isdigit() or int(sub_choice) not in range(1, 7):
                print("Invalid choice. Please enter a number from 1 to 6.")
                continue

            sub_option = int(sub_choice)

            if sub_option == 6:
                continue
            
            elif sub_option == 1:
                slow_computer(user)
            elif sub_option == 2:
                no_internet(user)
            elif sub_option == 3: 
                no_sound(user)
            elif sub_option == 4:
                computer_wont_turn_on(user)
            elif sub_option == 5:
                other_issues(user)
            

        elif option == 2:
            system_menu()
            print("\nPlease select a system option (1-3):")
            sub_choice = input().strip()

            if not sub_choice.isdigit() or int(sub_choice) not in range(1, 4):
                print("Invalid choice. Please enter a number from 1 to 3.")
                continue

            sub_option = int(sub_choice)

            if sub_option == 3:
                continue
            if sub_option == 1:
                view_system_information()
            elif sub_option == 2:
                system_diagnostic()
        

        elif option == 3:
            network_menu()
            print("\nPlease select a network option (1-3):")
            sub_choice = input().strip()

            if not sub_choice.isdigit() or int(sub_choice) not in range(1, 4):
                print("Invalid choice. Please enter a number from 1 to 3.")
                continue

            sub_option = int(sub_choice)
            
            if sub_option == 3:
                continue            
            if sub_option == 1:
                view_network_information()
            elif sub_option == 2:
                network_diagnostic()
            
        elif option == 4:
            while True:
                security_menu()
                sub_choice = input("\nPlease select a security option (1-3): ").strip()
                if not sub_choice.isdigit() or int(sub_choice) not in range(1, 4):
                    print("Invalid choice. Please enter a number from 1 to 3.")
                    continue

                sub_option = int(sub_choice)
                if sub_option == 1:
                    security_assessment()
                elif sub_option == 2:
                    check_os_updates()
                else:
                    # Return straight to the main menu without an extra prompt.
                    break
            continue

        elif option == 5:
            system_health_menu()
            print("\nPlease select a system health option (1-3):")
            sub_choice = input().strip()

            if not sub_choice.isdigit() or int(sub_choice) not in range(1, 4):
                print("Invalid choice. Please enter a number from 1 to 3.")
                continue

            sub_option = int(sub_choice)

            if sub_option == 3:
                continue
            
            if sub_option == 1:
                quick_scan()
            elif sub_option == 2:
                view_running_processes()

        else:
            print("Invalid option selected.")
            continue

        if not ask_yes_no("\nWould you like to return to the main menu?"):
            print(
                "\nThank you " + user.name +
                " for choosing to use Byte Wizard. Goodbye!"
            )
            print(ascii_title)
            break


# ==============================
# Program Start
# ==============================

text = "Byte Wizard"
ascii_title = pyfiglet.figlet_format(text)

<<<<<<< Updated upstream
print(ascii_title)
print("Welcome to the Byte Wizard!")
print("This tool will help you troubleshoot your computer.\n")
=======
    print(ascii_title)
    print("Welcome to the Byte Wizard!")
    print("This tool will help you troubleshoot your computer.\n")

    try:
        # Ask for a valid name before creating the user record.
        while True:
            user_name = input("Please enter your name:\n")

            if user_name.strip() == "":
                print("Please enter your name.\n")

            elif not user_name.replace(" ", "").isalpha():
                print("Please enter a valid name.\n")

            else:
                break
>>>>>>> Stashed changes

        # Enter the menu loop after setup is complete.
        user_troubleshooting(user=User(name=user_name))
    except (EOFError, KeyboardInterrupt):
        print("\nInput cancelled. Goodbye!")

# Ask for a name containing letters and spaces before creating the user record.
while True:
    user_name = input("Please enter your name:\n")

    if user_name.strip() == "":
        print("Please enter your name.\n")

    elif not user_name.replace(" ", "").isalpha():
        print("Please enter a valid name.\n")

    else:
        break


# Enter the menu loop after setup is complete.
user_troubleshooting(user=User(name=user_name))
