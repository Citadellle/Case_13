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
    # Get list of all refueling requests
    requests = reading_requests()
    # Get dictionary with gas station information
    gas_stations = reading_gas_stations()
    # Get dictionary with fuel price data
    gas_prices = fuel_prices.get_fuel_prices()

    # Get list of arrivals at the gas station:
    # [{arrival time (HH:MM format),
    #   amount of fuel,
    #   fuel type,
    #   refueling duration,
    #   arrival flag}, ...]
    arrivals_not_served = processing_requests(requests)
    
    # Assign arrivals to stations and get list of refueling starts:
    # [{start time of refueling (minutes from midnight),
    #   amount of fuel,
    #   fuel type,
    #   refueling duration,
    #   arrival flag}, ...]
    # Get: list of all clients, list of served clients,
    # Get number of clients who leave the station without refueling
    arrivals_all, arrivals_served, leave_count = assign_requests_to_stations(
                                                        arrivals_not_served,
                                                        gas_stations)

    # Get list of the end of refueling:
    # [{end time of refueling (minutes from midnight),
    #   amount of fuel,
    #   fuel type,
    #   refueling duration,
    #   arrival flag}, ...]
    arrivals_finishes = processing_end_refueling(arrivals_served)

    # Combined list (arrivals, completed refuelings, and not refueling)
    general_list = join_lists(arrivals_all, arrivals_finishes)

    # Calculate results for the day
    volumes_fuel_day, income = calculating_results(gas_prices, arrivals_served)

    report = create_output_text(general_list,
                                arrivals_all,
                                volumes_fuel_day,
                                income,
                                leave_count,
                                gas_stations)

    # Recording the report to a output.txt file
    with open('output.txt', 'w', encoding= 'utf-8') as f:
        f.write(report)


if __name__ == '__main__':
    main()
