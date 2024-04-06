from investment_opportunities import InvestmentOpportunities
from data_fetch_methods import fetch_stock_data, fetch_bonds_data, fetch_mutual_funds_data

class DataFetcher:
    @staticmethod
    def fetch_data(selected_opportunity_index):
        try:
            selected_opportunity = InvestmentOpportunities.INVESTMENT_OPPORTUNITIES[selected_opportunity_index]
        except IndexError:
            return "Invalid opportunity index."
        
        data_fetcher_method = getattr(DataFetcher, f'fetch_{selected_opportunity.lower().replace(" ", "_")}_data', None)
        if data_fetcher_method:
            return data_fetcher_method()
        else:
            return "No data available for the selected opportunity."
