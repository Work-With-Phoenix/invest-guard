import sys
import logo
import user_interaction
import cli
import logging


# Configure logging
logging.basicConfig(level=logging.INFO)

def continue_or_exit():
    """Asks the user if they want to continue or exit."""
    if not user_interaction.ask_to_continue():
        print("Exiting...")
        sys.exit(0)  # Exit gracefully
    return True

def main():
    try:
        # Display the logo and welcome message
        logo.display_logo_and_intro()
        user_interaction.welcome_user()

        # Ask the user if they want to continue
        if not continue_or_exit():
            return
        
        
        # Call the CLI run function
        cli.run()
           
        
        
    except KeyboardInterrupt:
        print("\nProcess interrupted. Exiting...")
        sys.exit(0)  # Exit gracefully

if __name__ == "__main__":
    main()
