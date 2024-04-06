import sys

def welcome_user():
    """
    Welcomes the user to the Investment Opportunity Analysis Tool.
    """
    print("Welcome to the Investment Opportunity Analysis Tool!")

def ask_to_continue():
    """
    Asks the user if they want to continue using the tool.
    
    Returns:
        bool: True if the user wants to continue, False otherwise.
    """
    while True:
        choice = input("\nDo you want to continue? (yes/no): ").strip().lower()
        if choice == "yes":
            return True
        elif choice == "no":
            print("Exiting...")
            sys.exit(0)
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

