# A module for generating random values
import random

# Localisation
import ru_local as local

# Functions for time processing
from time_processing import *


def calculating_results(gas_prices: dict, arrivals_served: dict) -> tuple:
    '''
    The function calculates daily fuel volumes sold and total income
    based on served refueling requests and current fuel prices.

    Args:
        gas_prices (dict): Dictionary with fuel types as keys and their prices as values
        arrivals_served (dict): Dictionary containing served arrivals with:
                               - TYPE: fuel type
                               - VOLUME: amount of fuel refueled

    Returns:
        tuple: A tuple containing:
            - volumes_day (dict): Dictionary with fuel types and total liters sold
            - income (float): Total daily income from all refueling operations
    '''

    # Initialize dictionary with zero values for each fuel type
    volumes_day = {}
    for t in gas_prices:
        volumes_day[t] = 0

    # Total income
    income = 0
    # Iterate through all served requests
    for arrival in arrivals_served:
        type_fuel = arrival[local.TYPE]
        volume_fuel = int(arrival[local.VOLUME])

        # If fuel type is available, process the refueling
        if type_fuel in volumes_day:
            # Store total liters refueled for this fuel type
            volumes_day[type_fuel] += volume_fuel
            # Add to total income from this refueling
            income += (volume_fuel * float(gas_prices[type_fuel]))
    

    return volumes_day, income


def create_output_text(general_list,
                       arrivals_all,
                       volumes_day,
                       income,
                       left_count,
                       stations) -> str:
    output = []

    # Queue tracking dictionary
    queues = {station: [] for station in stations}

    for event in general_list:
        # Converting time from the format: minutes from midnight to
        # the HH:MM format
        
        # Arrival time
        arrival_time_str = standart_format_time(event[local.TIME])
        # Start refill time
        event_time_str = standart_format_time(event.get(local.TIME_START,
                                                    event[local.TIME]))

        type_fuel = event[local.TYPE]
        volume_fuel = int(event[local.VOLUME])
        duration = event[local.REFILL_DURATION]
        station = event.get(local.MACHINE)

        # Event processing
        if event[local.ARRIVAL]:

            # Сlient has leave
            if event.get(local.LEAVE):
                output.append(local.NEW_CLIENT_LEAVE.format(arrival_time_str, 
                                                            event_time_str, 
                                                            type_fuel, 
                                                            volume_fuel, 
                                                            duration))
                
            else:
                output.append(local.NEW_CLIENT_QUEUE.format(event_time_str,
                                                            arrival_time_str,
                                                            type_fuel,
                                                            volume_fuel,
                                                            duration, 
                                                            station))
                
                queues[station].append(duration)

        else:
            arrival_time_str = standart_format_time(event.get(
                local.TIME_ARRIVAL,event.get(local.TIME_START,
                                             event[local.TIME])))
            
            time_str = standart_format_time(event[local.TIME])

            output.append(local.CLIENT_DEPART.format(time_str,
                                                     arrival_time_str,
                                                     type_fuel,
                                                     volume_fuel,
                                                     duration))
            
            # Removing the first item from the queue for the gas station
            del queues[station][0]


        for station in stations.keys():
            max_q, type_fuels = stations[station]
            # Visual representation of queue length
            stars = "*" * len(queues[station])

            output.append(local.MACHINE_STATUS.format(station, max_q, 
                                                      type_fuels, stars))

        # Adding an empty line for indentation in the future display of lines
        output.append("")


    output.append("")
    output.append(local.RESULT)

    for fuel in volumes_day:
        output.append(local.FUELS_VOLUME.format(fuel, volumes_day[fuel]))
    
    output.append(local.ARRIVALS_COUNT.format(len(arrivals_all)))

    output.append(local.LEAVE_COUNT.format(left_count))

    output.append(local.DAY_INCOME.format(int(income)))


    # Financial indicators
    # Fixed expenses: Salary and insurance + Taxes on income + 
    #                 Land lease + Other expenses
    expenses_permanent = random.randint(150000, 180000) + \
                         int(income * 30 * 0.06) + \
                         random.randint(50000, 80000) + \
                         random.randint(20000, 30000)
    
    # Variables expenses: (Fuel purchase + Bank commission) * num days in month
    expenses_variables = (income * 0.8 + income * 0.018) * 30

    # Total monthly expenses
    expenses_month = expenses_permanent + expenses_variables

    income_month = income * 30

    output.append(local.DAY_EXPENSES.format(expenses_month // 30))

    output.append(local.MONTH_INCOME.format(int(income_month)))
    output.append(local.MONTH_EXPENSES.format(int(expenses_month)))
    

    output.append(local.PAYBACK_TIME.format(
        round(10000000 / (income_month - expenses_month), 1)))


    return "\n".join(output)
