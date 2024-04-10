import requests
from bs4 import BeautifulSoup

class DataFetcher:
    def fetch_company_names(self, query):
        url = f"https://finance.yahoo.com/lookup?s={query}"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract company names from the lookup page
            company_names = [link.text for link in soup.find_all("a", class_="Fw(b)")]
            return company_names
        except Exception as e:
            print(f"Failed to fetch company names: {e}")
            return []

# Example usage:
fetcher = DataFetcher()
company_names = fetcher.fetch_company_names("apple")
print("Company names:", company_names)
