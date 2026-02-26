# A module for generating random values
import random

# Localisation
import ru_local as local

# Functions for time processing
from time_processing import *


def calculating_results(gas_prices: dict, arrivals_served: dict) -> tuple:
    """
    The function calculates daily fuel volumes sold and total income
    based on served refueling requests and current fuel prices.

    Args:
        gas_prices (dict): Dictionary with fuel types as keys and
                           their prices as values
        arrivals_served (dict): Dictionary containing served arrivals with:
                               - TYPE: fuel type
                               - VOLUME: amount of fuel refueled

    Returns:
        tuple: A tuple containing:
            - volumes_day (dict): Dictionary with fuel types and
                                  total liters sold
            - income (float): Total daily income from all refueling operations
    """
    # Set up a dictionary with initial zero values for fuel sold
    volumes_day = {}
    for t in gas_prices:
        volumes_day[t] = 0

    # Income
    income = 0.0
    # Iterate over all served arrivals
    for arrival in arrivals_served:
        type_fuel = arrival[local.TYPE]
        volume_fuel = int(arrival[local.VOLUME])

        # If the required fuel type is available, serve the customer
        if type_fuel in volumes_day:
            # Store the amount of fuel dispensed for this type
            volumes_day[type_fuel] += volume_fuel
            # Add the revenue from this refueling to total income
            income += (volume_fuel * float(gas_prices[type_fuel]))

    return volumes_day, income


def create_output_text(general_list: list, arrivals_all: list,
                       volumes_day: dict, income: float,
                       left_count: int, stations: dict) -> str:
    """
    Generates a complete simulation report:
    - step‑by‑step events with queue states;
    - final results;
    - extended statistics (by fuel type, by pump, waiting times);
    - economic analysis.

    Args:
        general_list (list): List of all events (arrivals and departures)
                             in chronological order.
        arrivals_all (list): List of all arrival events
                             (including those refused).
        volumes_day (dict): Dictionary with fuel types and total liters sold
                            per type.
        income (float): Total daily income from served refuelings.
        left_count (int): Number of customers who left without service.
        stations (dict): Dictionary describing each fuel pump:
                         key – pump id,
                         value – tuple (max_queue, [fuel_types]).

    Returns:
        str: Formatted multi‑line report string.
    """
    lines = []

    # Current queues at each pump (for display during event handling)
    queues = {station: [] for station in stations}

    # Statistics by fuel type
    fuel_stats = {
        fuel: {'served': 0, 'volume': 0.0, 'refused': 0}
        for fuel in volumes_day.keys()
    }

    # Statistics by pump
    station_stats = {
        station: {
            'served': 0,
            'volume': 0.0,
            'total_wait': 0,
            'total_duration': 0,
            'max_queue': 0,
            'wait_list': []
        }
        for station in stations
    }

    # Overall waiting time indicators
    total_wait_all = 0
    total_served_all = 0
    max_wait_all = 0

    for event in general_list:
        # Event time (arrival or departure) in minutes from midnight
        event_time = event[local.TIME]
        event_time_str = standart_format_time(event_time)

        fuel = event[local.TYPE]
        liters = event[local.VOLUME]
        duration = event[local.REFILL_DURATION]
        station = event.get(local.MACHINE)


        if event[local.ARRIVAL]:
            if event.get(local.LEAVE) is True:  # Customer left without joining queue
                lines.append(
                    f"{local.IN} {event_time_str} {local.NEW_CLIENT}"
                    f"{event_time_str} {fuel} {int(liters)} {duration} "
                    f"{local.COULD_NOT}"
                )
                if fuel in fuel_stats:
                    fuel_stats[fuel]['refused'] += 1
            else:                            # Customer joined the queue
                lines.append(
                    f"{local.IN} {event_time_str} {local.NEW_CLIENT}"
                    f"{event_time_str} {fuel} {int(liters)} {duration} "
                    f"{local.QUEUE} {station}"
                )
                queues[station].append(duration)
                # Update maximum queue length for this pump
                current_q = len(queues[station])
                if current_q > station_stats[station]['max_queue']:
                    station_stats[station]['max_queue'] = current_q

        else:
            # Customer's arrival time (when they first came)
            arrival_time = event.get(local.TIME_ARRIVAL)
            if arrival_time is None:
                arrival_time = event_time - duration
            arrival_time_str = standart_format_time(arrival_time)

            lines.append(
                f"{local.IN} {event_time_str} {local.CLIENT}"
                f"{arrival_time_str} {fuel} {int(liters)} {duration} "
                f"{local.REFUELED}"
            )

            # Start time of refueling
            start_time = event_time - duration
            wait = start_time - arrival_time   # waiting time in queue

            if station is not None:
                # Update pump statistics
                st = station_stats[station]
                st['served'] += 1
                st['volume'] += liters
                st['total_duration'] += duration
                st['total_wait'] += wait
                st['wait_list'].append(wait)

                # Update overall waiting statistics
                total_served_all += 1
                total_wait_all += wait
                if wait > max_wait_all:
                    max_wait_all = wait

                # Update fuel type statistics
                if fuel in fuel_stats:
                    fuel_stats[fuel]['served'] += 1
                    fuel_stats[fuel]['volume'] += liters

            # Remove the customer from the queue
            if queues[station]:
                queues[station].pop(0)

        # Display queue states for all pumps after this event
        for sid in sorted(stations.keys()):
            max_q = stations[sid][0]
            fuels = " ".join(stations[sid][1])
            stars = "*" * len(queues[sid])
            lines.append(
                f"{local.AUTOMATIC_CONTROL_NUMBER} {sid} "
                f"{local.MAX} {max_q} "
                f"{local.STAMP_GASOLINE} {fuels} ->{stars}"
            )
        lines.append("")

    lines.append("")
    lines.append(local.RESULT)
    for fuel in volumes_day:
        lines.append(f"{fuel}: {volumes_day[fuel]} {local.LITERS}")
    lines.append(f"{local.COME} {len(arrivals_all)}")
    lines.append(f"{local.AWAY} {left_count}")
    lines.append(f"{local.INCOME} {int(income)} {local.RUBLES}")

    # Additional statistics
    lines.append("")
    lines.append(local.ADDITIONAL_STATISTICS)
    lines.append(local.STAMP)
    for fuel in sorted(fuel_stats.keys()):
        s = fuel_stats[fuel]
        lines.append(
            f"  {fuel}: {local.SERVICED_1} {s['served']}, "
            f"{local.AMOUNT} {s['volume']} {local.LITERS}, "
            f"{local.REJECTION} {s['refused']}"
        )


    lines.append("")
    lines.append(local.MACHINES)
    for sid in sorted(stations.keys()):
        st = station_stats[sid]
        avg_wait = (st['total_wait'] / st['served']
                    if st['served'] > 0 else 0)
        load_percent = (st['total_duration'] / (24 * 60)) * 100
        lines.append(f"  {local.AUTOMATIC_CONTROL_NUMBER}{sid}:")
        lines.append(f"    {local.SERVICED_2} {st['served']}")
        lines.append(f"    {local.MARKET_LITERS} {st['volume']}")
        lines.append(f"    {local.AVERAGE_TIME} {avg_wait} "
                     f"{local.MINUTES}")
        lines.append(f"    {local.MAX_LINE} {st['max_queue']}")
        lines.append(f"    {local.LOADING} {load_percent}%")

    lines.append("")
    if total_served_all > 0:
        avg_wait_all = total_wait_all / total_served_all
        lines.append(f"{local.GENERAL_AVERAGE} {avg_wait_all} "
                     f"{local.MINUTES}")
        lines.append(f"{local.MAX_TIME} {max_wait_all} {local.MINUTES}")
    lines.append(
        f"{local.PERCENT} {left_count / len(arrivals_all) * 100}% "
        f"({left_count} {local.FROM} {len(arrivals_all)})"
    )

    # Economic analysis
    lines.append("")
    lines.append(local.ECONOMIC_ANALYSIS)
    expenses_permanent = (
        random.randint(150000, 180000)
        + int(income * 30 * 0.06)
        + random.randint(50000, 80000)
        + random.randint(20000, 30000)
    )
    expenses_variables = (income * 0.8 + income * 0.018) * 30
    expenses_month = expenses_permanent + expenses_variables
    income_month = income * 30

    lines.append(f"{local.QUOTED_CONSUMMENTS} {expenses_month // 30} "
                 f"{local.RUBLES}")
    lines.append(f"{local.AVERAGE_PASSAGE} {int(income_month)} "
                 f"{local.RUBLES}")
    lines.append(f"{local.AVERAGE_COSTS} {int(expenses_month)} "
                 f"{local.RUBLES}")
    lines.append(
        f"{local.PAYBACK_TIME}"
        f"{round(10000000 / (income_month - expenses_month), 1)} "
        f"{local.YEAR}"
    )

    return "\n".join(lines)
