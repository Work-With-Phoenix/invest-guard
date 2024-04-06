import sys
import logo
import user_interaction
import investment_opportunities
from data_fetcher import DataFetcher

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

        # Select an investment opportunity
        selected_opportunity_index = investment_opportunities.InvestmentOpportunities.select_opportunity()
        selected_opportunity = investment_opportunities.InvestmentOpportunities.INVESTMENT_OPPORTUNITIES[selected_opportunity_index]
        print(f"You selected: {selected_opportunity}")

        # Ask the user if they want to continue
        if not continue_or_exit():
            return
        
        # Fetch data for the selected investment opportunity
        data = DataFetcher.fetch_data(selected_opportunity_index)
        print(data)

        # Ask the user if they want to continue
        if not continue_or_exit():
            return

    except KeyboardInterrupt:
        print("\nProcess interrupted. Exiting...")
        sys.exit(0)  # Exit gracefully

if __name__ == "__main__":
    main()
