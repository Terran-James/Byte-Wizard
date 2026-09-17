# Used to create ASCII art for the Byte Wizard title
import pyfiglet


# ==============================
# User Class
# ==============================

class User:
    def __init__(self, name, email):
        self.name = name
        self._email = email

    # Returns a masked version of the email address
    def get_email(self):
        return self._email[0] + "****" + self._email[self._email.index("@"):]

    # Returns the actual email for internal comparison
    def get_actual_email(self):
        return self._email


# ==============================
# Main Menu
# ==============================

def main_menu():
    print("1. Slow computer")
    print("2. No internet")
    print("3. No sound")
    print("4. Computer won't turn on")
    print("5. Other issues")


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
        print("\nYou selected: Slow computer\n")
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
        print("\nYou selected: No internet\n")
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
    print("\nYou selected: No sound\n")
    print("Please follow these steps to troubleshoot your sound issues:\n")
    print("1. Check if your speakers or headphones are properly connected.")
    print("2. Verify that the volume is not muted or too low.")
    print("3. Update your audio drivers.")
    print("4. Check if the issue is with a specific application.")


def computer_wont_turn_on(user):
    print("\nYou selected: Computer won't turn on\n")
    print(
        "Alright " + user.name +
        ", please follow these steps to troubleshoot your computer:\n"
    )
    print("1. Check if the power cable is securely connected.")
    print("2. Ensure the power outlet is working.")
    print("3. Try pressing the power button for a few seconds.")
    print("4. If the issue persists, consider seeking professional help.")


def other_issues(user):
    print("\nYou selected: Other issues\n")
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
            print(ascii_art)
            break


# ==============================
# Program Start
# ==============================

text = "Byte Wizard"
ascii_art = pyfiglet.figlet_format(text)

print(ascii_art)
print("Welcome to the Byte Wizard!\n")
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


# Get and validate user's email
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


# Create User object
user = User(user_name, email_address)

# Start the program
user_troubleshooting()