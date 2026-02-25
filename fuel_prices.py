import requests
from bs4 import BeautifulSoup

def get_fuel_prices() -> dict:
    '''
    The function take current fuel prices from the website driff.ru.
    If the website is unavailable or an error occurs, returns default prices.

    Returns:
        dict: Dictionary containing fuel types as keys and 
              their prices as values.
    '''
    url = 'https://driff.ru/fuel-dynamics/'

    try:
        # Send a request to the server and get the page content
        r = requests.get(url)
        # Convert from string format to BeautifulSoup format for 
        # easier parsing
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Search by tags
        # Take only the first 4 elements
        fuels_data = soup.find('tbody').find_all('tr')[:4]

        prices = [fuel.find_all('td')[1].text for fuel in fuels_data]

        fuel_prices = {'АИ-92' : prices[0],
                       'АИ-95' : prices[1],
                       'АИ-98' : prices[2],
                       'ДТ' : prices[3]}

    except:
        fuel_prices = {'АИ-92' : 63.04,
                       'АИ-95' : 67.32,
                       'АИ-98' : 83.25,
                       'ДТ' : 77.02}
    
    
    return fuel_prices
