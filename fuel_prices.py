import requests
from bs4 import BeautifulSoup


def get_fuel_prices() -> dict:
    url = 'https://driff.ru/fuel-dynamics/'

    try:
        # Отправляем запрос к серверу и получаем содержимое страницы
        r = requests.get(url)
        # Преобразуем из формата str к формату BeautifulSoup,
        # с которым удобнее работать
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Ищем по тегам
        # Берем только первые 4 элемента
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