# Used to create ASCII art for the Byte Wizard title
import pyfiglet

# Used to get Platform information for the user's computer
import platform

# Used to get Network information for the user's computer
import socket

# Used on MacOS to get route process for defauly gateway
import subprocess

# Used to get check HTTPS connectivity
import urllib.request

# Used to gather system information
import psutil

# Used to get date/time information
import datetime

# Used to wait
import time


# ==============================
# Gets User's Operating System
# ==============================

def get_operating_system():
    """Return the operating system name in a user-friendly format."""
    operating_system = platform.system()

    if operating_system == "Darwin":
        return "macOS"

    return operating_system


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

    disk_usage = psutil.disk_usage("/")
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

    # macOS reports the gateway in the output of `route`.
    if operating_system == "Darwin":
        result = subprocess.run(
            ["route", "-n", "get", "default"],
            capture_output=True,
            text=True
        )

        for line in result.stdout.splitlines():
            if "gateway:" in line:
                return line.split()[1]
            
    # Windows reports gateway addresses in `ipconfig` output.
    elif operating_system == "Windows":
        result = subprocess.run(
            ["ipconfig"],
            capture_output=True,
            text=True
        )

        for line in result.stdout.splitlines():
            if "Default Gateway" in line:
                parts = line.split(":")
                if len(parts) > 1:
                    gateway = parts[1].strip()
                    if gateway:
                        return gateway
                    
    # Linux includes the gateway after "default via" in `ip route` output.
    elif operating_system == "Linux":
        result = subprocess.run(
            ["ip", "route"],
            capture_output=True,
            text=True
        )

        for line in result.stdout.splitlines():
            if line.startswith("default via"):
                return line.split()[2]

    return None


# ==============================
# Network User's Network Information
# ==============================

def get_network_information():
    """Collect network details and connection checks for reuse by the program."""
    hostname = socket.gethostname()
    gateway = get_default_gateway()

    # Ask the operating system which local address it would use for internet
    # traffic, then match that address to the corresponding network interface.
    ip_address = None
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as route_socket:
            route_socket.connect(("8.8.8.8", 53))
            ip_address = route_socket.getsockname()[0]
    except OSError:
        pass

    # psutil provides the IP, subnet mask, MAC address, and up/down state
    # for each named network interface.
    interfaces = psutil.net_if_addrs()
    interface_stats = psutil.net_if_stats()
    interface = None
    subnet_mask = None
    mac_address = None
    for name, addresses in interfaces.items():
        ipv4 = next((address for address in addresses
                     if address.family == socket.AF_INET
                     and address.address == ip_address), None)
        if ipv4:
            interface = name
            subnet_mask = ipv4.netmask
            link_family = getattr(psutil, "AF_LINK", None)
            mac = next((address.address for address in addresses
                        if address.family == link_family), None)
            if mac and mac not in ("00:00:00:00:00:00", "00-00-00-00-00-00"):
                mac_address = mac
            break

    if not ip_address:
        try:
            ip_address = socket.gethostbyname(hostname)
        except socket.gaierror:
            ip_address = None

    # Test a direct connection by IP so this check does not depend on DNS.
    try:
        with socket.create_connection(("8.8.8.8", 53), timeout=3):
            internet_status = True
    except OSError:
        internet_status = False

    # A successful name lookup confirms that DNS resolution is available.
    try:
        socket.gethostbyname("google.com")
        dns_status = True
    except socket.gaierror:
        dns_status = False

    # Request a secure web page to check end-to-end HTTPS access.
    try:
        with urllib.request.urlopen("https://google.com", timeout=5):
            https_status = True
    except Exception:
        https_status = False

    interface_up = bool(interface and interface_stats.get(interface)
                        and interface_stats[interface].isup)
    gateway_status = bool(gateway)
    # Keep short compatibility keys for the diagnostic and descriptive keys
    # for the network information screen and any other callers.
    return {
        "hostname": hostname,
        "ip_address": ip_address,
        "subnet_mask": subnet_mask,
        "dns": dns_status,
        "dns_working": dns_status,
        "https": https_status,
        "https_working": https_status,
        "internet": internet_status,
        "status": "Connected" if interface_up and gateway_status and internet_status else "Disconnected",
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
# Quick System & Network Scan
# ==============================

def qucik_scan():
    """Run a quck system and network health check that returns results as a .txt file"""
    print("\n========================================\nBYTE WIZARD SCAN\n========================================")


    system = get_system_information()
    network = get_network_information()

    print("\nSYSTEM\n")

    # CPU
    if system["CPU Usage"] < 70:
        cpu_result = "[PASS]"
    elif system["CPU Usage"] <= 90:
        cpu_result = "[FAIL]"

    print(f"{'CPU Usage':<25} {system['CPU Usage']:>6.5f}%     {cpu_result}")

    # Memory
    if system["Memory Usage"] < 80:
        memory_result = "[PASS]"
    elif system["Memory Usage"] <= 90:
        memory_result = "[WARNING]"
    else:
        memory_result = "[FAIL]"

    print(f"{'Memory Usage':<25} {system['Memory Usage']:>6.4f}%     {memory_result}")

    # Disk
    if system['Disk Usage'] < 80:
        disk_result = "[PASS]"
    elif system['Disk Usage'] <= 90:
        disk_result = "[WARNING]"
    else:
        disk_result = "[FAIL]"

    print(f"{'Storage Usage':<25} {system['Disk Usage']:>6.4f}%     {disk_result}")

    print("\nNETWORK\n")

    # Internet
    internet_result = "[PASS]" if network["internet"] else "[FAIL]"
    print(f"{'Internet Connection':<25} {('Connected' if network['internet'] else 'Not Connected'):<12} {internet_result}")

    # DNS
    dns_result = "[PASS]" if network["dns"] else "[FAIL]"
    print(f"{'DNS Resolution':<25} {('Working' if network['dns'] else 'Not Working'):<12} {dns_result}")

    # Gateway
    gateway_result = "[PASS]" if network["gateway_status"] else "[FAIL]"
    print(f"{'Default Gateway':<25} {('Found' if network['gateway_status'] else 'Not Found'):<12} {gateway_result}")

    # HTTPS
    https_result = "[PASS]" if network["https"] else "[FAIL]"
    print(f"{'HTTPS Connectivity':<25} {('Working' if network['https'] else 'Not Working'):<12} {https_result}")

    # Overall results
    all_results = (
        cpu_result,
        memory_result,
        disk_result,
        internet_result,
        dns_result,
        gateway_result,
        https_result
    )

    if "[FAIL]" in all_results:
        overall_result = "[FAIL]"
    elif "[WARNING]" in all_results:
        overall_result = "[WARNING]"
    else:
        overall_result = "[PASS]"

    print("\n========================================")
    print(f"{'Overall Status:':<25} {overall_result}")
    print("========================================")

    if ask_yes_no("\nWould you like to save this scan as a .txt report?"):
        save_quick_scan_report(system, network)


# ==============================
# Quick System & Network Scan Save
# ==============================

def save_quick_scan_report(system, network):
    """Save Quick Scan results to a text file."""

    # Saves the report to system using a timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_name = "byte_wizard_quick_scan_{timestap}.txt"

    with open(report_name, "w") as report:
        report.write("========================================\n")
        report.write("           BYTE WIZARD SCAN\n")
        report.write("========================================\n\n")

        report.write("SYSTEM\n")
        report.write("----------------------------------------\n")
        report.write(f"CPU Usage:      {system['CPU Usage']:.1f}%\n")
        report.write(f"Memory Usage:   {system['Memory Usage']:.1f}%\n")
        report.write(f"Storage Usage:  {system['Disk Usage']:.1f}%\n\n")

        report.write("NETWORK\n")
        report.write("----------------------------------------\n")
        report.write(
            f"Internet:       "
            f"{'Connected' if network['internet'] else 'Not Connected'}\n"
        )
        report.write(
            f"DNS:            "
            f"{'Working' if network['dns'] else 'Not Working'}\n"
        )
        report.write(
            f"Gateway:        "
            f"{'Found' if network['gateway_status'] else 'Not Found'}\n"
        )
        report.write(
            f"HTTPS:          "
            f"{'Working' if network['https'] else 'Not Working'}\n"
        )

    print(f"\nReport saved as: {report_name}")

        
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
    if results['CPU Usage'] < 70:
        cpu_result = "[PASS]"
    elif results['CPU Usage'] <= 90:
        cpu_result = "[WARNING]"
    else:
        cpu_result = "[FAIL]"


    print(f"{'Memory Usage:':<25}  {psutil.virtual_memory().percent}%")

    if psutil.virtual_memory().percent < 80:
        memory_result = "[PASS]"
    elif psutil.virtual_memory().percent <= 90:
        memory_result = "[WARNING]"
    else:
        memory_result = "[FAIL]"


    print(f"{'Storage Usage:':<25}   {results['Disk Usage']}% used")

    if results['Disk Usage'] < 80:
        disk_result = "[PASS]"
    elif results['Disk Usage'] <= 90:
        disk_result = "[WARNING]"
    else:
        disk_result = "[FAIL]"

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

    print(f"{'\nOverall Diagnostic:\n':<25} {overall_result}")

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
    """Store the user's name and email, with a masked email for display."""
    def __init__(self, name, email):
        self.name = name
        self._email = email

    # Returns a masked version of the email address
    def get_email(self):
        if self._email == "Not provided":
            return self._email
        return self._email[0] + "****" + self._email[self._email.index("@"):]

    # Returns the actual email for internal comparison
    def get_actual_email(self):
        return self._email


# ==============================
# Main Menu
# ==============================

def main_menu():
    """Print the numbered choices handled by user_troubleshooting()."""
    print("\n========================================\nMAIN MENU\n========================================")

    print("\nTROUBLESHOOTING")
    print("1. Slow Computer")
    print("2. No Internet")
    print("3. No Sound")
    print("4. Computer Won't Turn On")
    print("5. Other Issue")

    print("\nDIAGNOSTICS")
    print("6. Run System Diagnostic")
    print("7. Run Network Diagnostic")
    print("8. Run Quick Scan")

    print("\nSYSTEM INFORMATION")
    print("9. View System Information")
    print("10. View Network Information")
    print("11. View Running Processes")
   
    print("\n12. Exit")


# ==============================
# Email Functions
# ==============================

def change_email(user):
    """Ask for and confirm a new email before saving it to the user."""
    while True:
        new_email = input("Please enter your new email address: ")

        if new_email == user.get_actual_email():
            print(
                "The new email address cannot be the same as "
                "the current email address. Please try again.\n"
            )
            continue

        if "@" not in new_email or "." not in new_email:
            print("Invalid email format. Please try again.\n")
            continue

        confirm_new_email = input(
            "Please re-enter your new email address for confirmation: "
        )

        if new_email == confirm_new_email:
            user._email = new_email

            print(
                "Thank you " + user.name +
                ", your email address has been updated to: " +
                user.get_email() + "\n"
            )
            break

        else:
            print(
                "The email addresses do not match. "
                "Please try again.\n"
            )


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
    """Let the user summarize another issue and optionally update their email."""
    print("\n========================================\nOTHER ISSUE\n========================================")
    print("Describe the problem in a sentence or two. Avoid including passwords or other private information.\n")
    detailed_issue = input("> ").strip()
    while not detailed_issue:
        print("Please enter a short description so you can review it.")
        detailed_issue = input("> ").strip()

    print(f"\nThanks, {user.name}. Your issue summary is:\n\"{detailed_issue}\"\n")
    print("Byte Wizard does not send or save support requests, so keep this summary to share with a technician if needed.")
    print(f"Contact email on file: {user.get_email()}")

    if ask_yes_no("Would you like to update your contact email?"):
        print(
            "\nHm... no worries, even a wizard misplaces his owl sometimes. "
            "Let's update that for you " + user.name + ".\n"
        )

        change_email(user)


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
    print(f"{'Total Memory:':<25}  {results['Memory Total']:2f} GB")
    print(f"{'Total Storage:':<25}  {results['Disk Total']:2f} GB")


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
    print(f"Interface: {results['interface'] or 'Unavailable'}")
    print(f"Default Gateway: {results['default_gateway'] or 'Unavailable'}")
    print(f"MAC Address: {results['mac_address'] or 'Unavailable'}")


# ==============================
# Running Processes
# ==============================

def view_running_processes():

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

        choice = input("\nEnter a number (1-12): ").strip()
        if not choice.isdigit() or int(choice) not in range(1, 13):
            print("Invalid choice. Please enter a number from 1 to 12.")
            continue
        option = int(choice)

        # Exit before dispatching a feature; all other numbers map to a menu item.
        if option == 12:
            print(f"\nThank you {user.name} for choosing Byte Wizard. Goodbye!")
            print(ascii_title)
            break

        if option == 1:
            slow_computer(user)

        elif option == 2:
            no_internet(user)

        elif option == 3:
            no_sound(user)

        elif option == 4:
            computer_wont_turn_on(user)

        elif option == 5:
            other_issues(user)

        elif option == 6:
            system_diagnostic()

        elif option == 7:
            network_diagnostic()

        elif option == 8:
            qucik_scan()

        elif option == 9:
            view_system_information()

        elif option == 10:
            view_network_information()

        elif option == 11:
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

print(ascii_title)
print("Welcome to the Byte Wizard!")
print("This tool will help you troubleshoot your computer.\n")


# Ask for a name containing letters and spaces before creating the user record.
while True:
    user_name = input("Please enter your name:\n")

    if user_name.strip() == "":
        print("Please enter your name.\n")

    elif not user_name.replace(" ", "").isalpha():
        print("Please enter a valid name.\n")

    else:
        break


# Email is optional; when supplied, ask twice to catch typing mistakes.
email_choice = ask_yes_no("\nWould you like to provide your email address for your own reference?")
if email_choice:
    while True:
        email_address = input(
            "\nEnter your email address for further assistance: "
        )

        email_address = email_address.strip()
        if "@" not in email_address or "." not in email_address.split("@")[-1] or " " in email_address:
            print("Invalid email format. Please try again.\n")
            continue

        confirm_email_address = input(
        "\nPlease re-enter your email address for confirmation: "
     )

        if email_address == confirm_email_address:
            break

        else:

            print("The email addresses do not match. Please try again.\n")

else:
    email_address = "Not provided"



# Create the user record consumed by the troubleshooting features.
user = User(user_name, email_address)

# Enter the menu loop after setup is complete.
user_troubleshooting(user)
