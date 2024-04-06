class InvestmentOpportunities:
    """Class to manage investment opportunities."""

    # Define placeholder investment opportunities
    INVESTMENT_OPPORTUNITIES = [
        "Stocks",
        "Bonds",
        "Mutual Funds",
        "Cryptocurrency",
        "Real Estate",
        "Commodities",
        "Options",
        "ETFs",
        "Forex",
        "Precious Metals",
        "Savings Accounts",
        "Retirement Accounts",
        "Peer-to-Peer Lending",
        "Startup Investments",
        # Add more investment opportunities as needed
    ]

    @staticmethod
    def select_opportunity():
        """Prompt the user to select an investment opportunity."""
        print("Select an investment opportunity:")
        for i, option in enumerate(InvestmentOpportunities.INVESTMENT_OPPORTUNITIES, start=1):
            print(f"{i}. {option}")
        
        while True:
            choice = input("Enter the number corresponding to your choice: ")
            if choice.isdigit():
                choice = int(choice)
                if 1 <= choice <= len(InvestmentOpportunities.INVESTMENT_OPPORTUNITIES):
                    return choice - 1  # Return the index of the selected opportunity
                else:
                    print("Invalid choice. Please enter a number within the range.")
            else:
                print("Invalid input. Please enter a number.")
