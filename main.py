# A module with a dictionary with prices for fuel brands
import fuel_prices

# Functions for time processing
from time_processing import *

# Functions for reading files: input.txt and gas_station.txt
from reading_files import *

# Functions for processing and creating a list with dictionaries that 
# store arrivals data
from arrivals_processing import *

# Functions: calculation of the amount of fuel sold and income,
# information output
from results_and_conclusion import *


def main():
    # Получаем список со всеми заявками на заправку
    requests = reading_requests()
    # Получаем словарь с информацией о бензоколонках
    gas_stations = reading_gas_stations()
    # Получаем словарь с данными о ценах на бензин
    gas_prices = fuel_prices.get_fuel_prices()

    # Получаем список прибытий на заправку:
    # [{время прибытия (HH:MM формат),
    #   количество топлива,
    #   вид топлива,
    #   длительность заправки,
    #   прибыл}, ...]
    arrivals_not_served = processing_requests(requests)
    
    # Назначаем прибывших на автоматы и получаем список начала заправки:
    # [{время начала заправки (количество минут от полуночи),
    #   количество топлива,
    #   вид топлива,
    #   длительность заправки,
    #   прибыл}, ...]
    # Получаем 2 списка: всех клиентов, обслуженных клиентов,
    # количество клиентов, которые покинули АЗС не заправив автомобиль
    arrivals_all, arrivals_served, leave_count = assign_requests_to_stations(
                                                        arrivals_not_served,
                                                        gas_stations)

    # Получаем список окончания заправки:
    # [{время конца заправки (количество минут от полуночи),
    #   количество топлива,
    #   вид топлива,
    #   длительность заправки,
    #   прибыл}, ...]
    arrivals_finishes = processing_end_refueling(arrivals_served)

    # Общий список (прибывшие, заправившиеся и не дождавшиеся заправки)
    general_list = join_lists(arrivals_all, arrivals_finishes)

    # Подсчитываем итоги
    volumes_fuel_day, income = calculating_results(gas_prices, arrivals_served)

    report = create_output_text(general_list,
                                arrivals_all,
                                volumes_fuel_day,
                                income,
                                leave_count,
                                gas_stations)


    with open('output.txt', 'w', encoding= 'utf-8') as f:
        f.write(report)


if __name__ == '__main__':
    main()