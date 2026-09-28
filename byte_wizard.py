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


# ==============================
# Uptime Information
# ==============================
def get_uptime():
    boot_time = psutil.boot_time()
    current_time = datetime.datetime.now().timestamp()
    uptime_seconds = current_time - boot_time
    return datetime.timedelta(seconds=int(uptime_seconds))


# ==============================
# Default Gateway Information
# ==============================

def get_default_gateway():
    operating_system = platform.system()

# Funtion for macOS
    if operating_system == "Darwin":
        result = subprocess.run(
            ["route", "-n", "get", "default"],
            capture_output=True,
            text=True
        )

        for line in result.stdout.splitlines():
            if "gateway:" in line:
                return line.split()[1]
            
# Function for WindowsOS
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
                    
# Function for LinuxOS
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
# User Network Information/Diagnostic
# ==============================

def network_diagnostic():
    # Prints out a summary of the network tests ran
    print(
            "========================================"
                        "NETWORK SUMMARY"
            "========================================"
            )
    

    hostname = socket.gethostname()
    try:
        ip_address = socket.gethostbyname(hostname)
    except socket.gaierror:
        ip_address = "Unavailable"

    print("\nHostname: " + hostname)
    print("IP Address: " + ip_address + "\n")

    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        internet_status = True
        print("Internet Connection: Connected")
    except OSError:
        internet_status = False
        print("Internet Connection: Not Connected")

    try:
        dns_resolution = socket.gethostbyname("google.com")
        dns_status = True
        print("DNS Resolution: Working")
        print(f"Resolved IP: {dns_resolution}")
    except socket.gaierror:
        dns_status = False
        print("DNS Resolution: Not working")

    gateway = get_default_gateway()
    if gateway:
        gateway_status = True
        print(f"Default Gateway: {gateway}")
    else:
        gateway_status = False
        print("Default Gateway: Not Found")

    try:
        urllib.request.urlopen("https://google.com", timeout=5)
        https_status = True
        print("HTTPS Connection: Working")
    except Exception:
        https_status = False
        print("HTTPS Connection: Not Working")


# Runs a diagnostic
    print("\nRunning diagnostic....\n")

    if internet_status:
        internet_result = "[PASS]"
    else:
        internet_result = "[FAIL]"

    if dns_status:
        dns_result = "[PASS]"
    else:
        dns_result = "[FAIL]"

    if gateway_status:
        gateway_result = "[PASS]"
    else:
        gateway_result = "[FAIL]"

    if https_status:
        https_result = "[PASS]"
    else:
        https_result = "[FAIL]"

    print(f"{'Internet Connection':<25} {internet_result}")
    print(f"{'DNS Resolution':<25} {dns_result}")
    print(f"{'Default Gateway':<25} {gateway_result}")
    print(f"{'HTTPS Connectivity':<25} {https_result}")

# Tells the user of potential issues if anything has failed
    print("\nPotential Issue(s)\n")
    if internet_result == "[FAIL]":
        print("An Internet connection could not be established. Check your network connection, router, or Internet Service Provider.")
    if dns_result == "[FAIL]":
        print("DNS resolution appears to be failing. Your computer may be unable to translate domain names into IP addresses.")
    if gateway_result == "[FAIL]":
        print("Your default gateway could not be detected. Your computer may be having trouble communicating with the local network or router.")
    if https_result == "[FAIL]":
        print("HTTPS connectivity failed. Your computer may be experiencing a problem connecting to a secure website.")
    if (
        internet_result == "[PASS]"
        and dns_result == "[PASS]"
        and gateway_result == "[PASS]"
        and https_result == "[PASS]"
    ):
        print("No network issues were detected.")
        

# ==============================
# User System Information/Diagnostic
# ==============================

def system_diagnostic():
    # Prints out a summary of the system tests ran
    print(
    "========================================"
                "SYSTEM SUMMARY"
    "========================================"
    )

    if platform.system() == "Darwin":
        operating_system = "macOS"
    else:
        operating_system = platform.system()

    print(f"\nOperating System:   {operating_system}")
    print(f"OS Version:   {platform.release()}")
    print(f"Machine Type:   {platform.machine()}")
    print(f"Hostname:   {platform.node()}")
    print(f"Python Version:  {platform.python_version()}\n")

    cpu_usage = psutil.cpu_percent(interval=1)
    print(f"CPU Usage:  {cpu_usage}%")

    if cpu_usage < 70:
        cpu_result = "[PASS]"
    elif cpu_usage <= 90:
        cpu_result = "[WARNING]"
    else:
        cpu_result = "[FAIL]"


    print(f"Memory Usage:  {psutil.virtual_memory().percent}%")

    if psutil.virtual_memory().percent < 80:
        memory_result = "[PASS]"
    elif psutil.virtual_memory().percent <= 90:
        memory_result = "[WARNING]"
    else:
        memory_result = "[FAIL]"


    disk_usage = psutil.disk_usage("/")
    disk_free = disk_usage.free / (1024 ** 3)
    disk_percent = disk_usage.percent
    print(f"Storage Usage:   {disk_percent}% used")

    if disk_percent < 80:
        disk_result = "[PASS]"
    elif disk_percent <= 90:
        disk_result = "[WARNING]"
    else:
        disk_result = "[FAIL]"

    print(f"Disk Free:  {disk_free:.2f} GB\n")
    

    uptime = get_uptime()
    print(f"System Uptime:  {uptime}")

    if uptime < datetime.timedelta(days=14):
        uptime_result = "[PASS]"
    elif uptime <= datetime.timedelta(days=30):
        uptime_result = "[WARNING]"
    else:
        uptime_result = "[FAIL]"


    if all(result == "[PASS]" for result in (
        cpu_result,
        memory_result,
        disk_result,
        uptime_result
    )):
        overall_result = "[PASS]"

    elif any(result == "[WARNING]" for result in (
        cpu_result,
        memory_result,
        disk_result,
        uptime_result
    )):
        overall_result = "[WARNING]"

    else:
        overall_result = "[FAIL]"
    
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

    print(f"{'Overall Diagnostic:':<25} {overall_result}")


# ==============================
# User Class
# ==============================

class User:
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
    print("1. Slow Computer")
    print("2. No Internet")
    print("3. No Sound")
    print("4. Computer Won't Turn On")
    print("5. System Diagnostic")
    print("6. Network Diagnostic")
    print("7. Other Issue")


# ==============================
# Email Functions
# ==============================

def change_email(user):
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

def slow_computer(user):
    while True:
        print(
            "========================================"
                        "SLOW COMPUTER"
            "========================================"
            )
        print("Is your computer slow all the time?")
        print("1. Yes")
        print("2. No")

        slow_computer_answer = input("\n")

        if slow_computer_answer.lower() == "yes":
            print(
                "\nPlease follow these steps to troubleshoot "
                "your slow computer:\n"
            )
            print("1. Close any unnecessary programs and browser tabs.")
            print("2. Run a virus scan to check for malware.")
            print("3. Check for software updates and install them.")
            print("4. Consider upgrading your hardware if your computer is old.")
            break

        elif slow_computer_answer.lower() == "no":
            print(
                "\nOk, please follow these steps to troubleshoot "
                "your slow computer:\n"
            )
            print("1. Check if any specific programs are causing the computer to run slowly.")
            print("2. Run a virus scan to check for malware.")
            print("3. Check for software updates and install them.")
            print("4. Consider upgrading your hardware or deleting unnecessary files.")
            break

        else:
            print("Invalid input. Please enter 'yes' or 'no.'")


def no_internet(user):
    while True:
        print(
                "========================================"
                            "NO INTERNET"
                "========================================"
                )
        print("Are you on a wired or wireless connection?")
        print("1. Wired")
        print("2. Wireless")

        connection_type = input("\n")

        if connection_type.lower() == "wired":
            print(
                "\nHm, ok. Please follow these steps to troubleshoot "
                "your wired internet connection:\n"
            )
            print("1. Check if your Ethernet cable is securely connected.")
            print("2. Restart your router and modem.")
            print("3. Check if other devices can connect to the internet.")
            print("4. Contact your internet service provider if the issue persists.")
            break

        elif connection_type.lower() == "wireless":
            print(
                "\nI see. Please follow these steps to troubleshoot "
                "your wireless internet connection:\n"
            )
            print("1. Check if your Wi-Fi is turned on and connected.")
            print("2. Restart your router and modem.")
            print("3. Check if other devices can connect to the internet.")
            print("4. Contact your internet service provider if the issue persists.")
            break

        else:
            print("Invalid input. Please enter 'wired' or 'wireless.'")


def no_sound(user):
    print(
            "========================================"
                            "NO SOUND"
            "========================================"
            )
    print("Please follow these steps to troubleshoot your sound issues:\n")
    print("1. Check if your speakers or headphones are properly connected.")
    print("2. Verify that the volume is not muted or too low.")
    print("3. Update your audio drivers.")
    print("4. Check if the issue is with a specific application.")


def computer_wont_turn_on(user):
    print(
            "========================================"
                    "COMPUTER WONT TURN ON"
            "========================================"
            )
    print(
        "Alright " + user.name +
        ", please follow these steps to troubleshoot your computer:\n"
    )
    print("1. Check if the power cable is securely connected.")
    print("2. Ensure the power outlet is working.")
    print("3. Try pressing the power button for a few seconds.")
    print("4. If the issue persists, consider seeking professional help.")


def other_issues(user):
    print(
            "========================================"
                        "OTHER ISSUES"
            "========================================"
            )
    print("Please describe the issue you are experiencing:\n")

    detailed_issue = input()

    print(
        "\nThank you " + user.name +
        ", the following has been provided for troubleshooting: " +
        detailed_issue + "\n"
    )

    print(
        "We will contact you with further assistance. "
        "Please check if the email address you provided is correct: " +
        user.get_email() + "\n"
    )

    if input("Is this email address correct? (yes/no): ").lower() == "no":
        print(
            "\nHm... no worries, even a wizard misplaces his owl sometimes. "
            "Let's update that for you " + user.name + ".\n"
        )

        change_email(user)


# ==============================
# Main Troubleshooting Loop
# ==============================

def user_troubleshooting():
    while True:
        print(
            "\nThank you " + user.name +
            ". Please select an option:\n"
        )

        main_menu()

        try:
            option = int(input("\n"))

        except ValueError:
            print("Invalid input. Please enter a number.")
            continue

        if option == 1:
            slow_computer(user)

        elif option == 2:
            no_internet(user)

        elif option == 3:
            no_sound(user)

        elif option == 4:
            computer_wont_turn_on(user)

        elif option == 5:
            system_diagnostic()

        elif option == 6:
            network_diagnostic()

        elif option == 7:
            other_issues(user)

        else:
            print("Invalid option selected.")
            continue

        finished = input(
            "\nDo you want to troubleshoot another issue? (yes/no): "
        )

        if finished.lower() == "no":
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


# Get and validate user's name
while True:
    user_name = input("Please enter your name:\n")

    if user_name.strip() == "":
        print("Please enter your name.\n")

    elif not user_name.replace(" ", "").isalpha():
        print("Please enter a valid name.\n")

    else:
        break


# Get and validate user's email address / or if theyd rather not enter it

email_choice = input(
    "\nWould you like to provide your email address for further assistance? (yes/no): "
)
if email_choice.lower() == "yes":
    while True:
        email_address = input(
            "\nEnter your email address for further assistance: "
        )

        if "@" not in email_address or "." not in email_address:
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




# Create User object
user = User(user_name, email_address)

# Start the program
user_troubleshooting()
