# A module for working with mathematical functions
import math
# A module for generating random values
import random

# Localization
import ru_local as local

# Functions for time processing
from time_processing import *


def get_refill_duration(volume: float) -> int:
    '''
    The function calculates the time needed to refuel a given volume of fuel.
    Refueling speed is 10 liters per minute plus a random variation 
    of -1, 0, or 1 minute.

    Args:
        volume (float): Volume of fuel to refuel in liters

    Returns:
        int: Refueling duration in minutes (minimum 1 minute)
    '''

    # Additional rounding in case fuel volume is not an integer
    volume = math.ceil(volume)

    # Refueling speed is 10 liters per minute
    # Get refueling time: divide volume by speed and add random 
    # integer value: -1, 0, 1
    refill_duration = math.ceil(volume / 10) + random.randint(-1, 1)

    return refill_duration if refill_duration > 0 else 1


# Creating a list of arrivals
def processing_requests(requests: list) -> list:
    '''
    The function processes raw request data and converts it into a structured
    list of dictionaries containing information about each refueling request.

    Args:
        requests (list): List of raw request strings, each containing:
                        - arrival time
                        - fuel volume
                        - fuel type

    Returns:
        list[dict]: List of dictionaries with processed request data:
                   - TIME: arrival time
                   - VOLUME: fuel volume
                   - TYPE: fuel type  
                   - REFILL_DURATION: calculated refueling time
                   - ARRIVAL: flag (True for initial requests)
    '''

    data = []

    for request in requests:
        request_spl = request.split()

        time_arrival = request_spl[0]
        volume_fuel = float(request_spl[1])
        type_fuel = request_spl[2]
        refill_duration = get_refill_duration(volume_fuel)

        data.append({local.TIME: time_arrival,
                     local.VOLUME: volume_fuel,
                     local.TYPE: type_fuel,
                     local.REFILL_DURATION: refill_duration,
                     local.ARRIVAL: True})

    return data


# Processing the arrival list
def assign_requests_to_stations(arrivals: dict, 
                                stations: dict) -> tuple:
    '''
    The function assigns incoming refueling requests to appropriate gas stations
    based on fuel type compatibility, queue lengths, and station availability.

    Args:
        arrivals (dict): Dictionary containing information about incoming vehicles
                        including arrival time, fuel type, and refueling duration
        stations (dict): Dictionary with gas station data including:
                        - maximum queue length
                        - available fuel types

    Returns:
        tuple[list[dict], list[dict], int]: A tuple containing:
            - list of all processed arrivals with assignment details
            - list of successfully served requests
            - number of vehicles that left without refueling
    '''

    # Dictionary storing end times of current refueling for each station
    in_progress = {}
    for station in stations:
        in_progress[station] = []

    # All arrivals
    arrivals_all = []
    # List of served requests
    served = []

    # Counter for vehicles that left due to full queues
    leave_without_refueling = 0

    # Process each vehicle in order of arrival
    for arrival in arrivals:

        # Convert arrival time from 'hours:minutes' format
        arrival_t = mints_from_midnight_format_time(arrival[local.TIME])
        # Vehicle's fuel type
        fuel = arrival[local.TYPE]
        # Refueling duration in minutes
        duration = arrival[local.REFILL_DURATION]

        # Remove completed refuelings from queues
        for station in in_progress:
            new_list = []
            for end_t in in_progress[station]:
                # Keep only refuelings that end after new vehicle's arrival
                if end_t > arrival_t:
                    new_list.append(end_t)
            in_progress[station] = new_list

        # Select appropriate station:
        # 1) supports the fuel type
        # 2) queue is not full
        # 3) minimal queue length, equal queues - smaller number
        best_station = None
        best_queue = None

        # Iterate through all stations
        for station in stations:
            # Maximum allowed queue length
            max_q = stations[station][0]
            # Fuel types supported by the station
            fuels = stations[station][1]

            if fuel not in fuels:
                continue

            # Current queue length
            q_len = len(in_progress[station])

            if q_len >= max_q:
                continue

            # If this is the first suitable station
            if best_station is None:
                best_station = station
                best_queue = q_len
            else:
                # Choose station: with smaller queue, if equal - with smaller number
                if q_len < best_queue or (q_len == best_queue and station < best_station):
                    best_station = station
                    best_queue = q_len

        # If no suitable station found - client leaves,
        # but add arrival event to arrivals_all
        if best_station is None:
            # increasing the number of those who leave without refueling
            leave_without_refueling += 1

            arrival_2 = arrival.copy()

            arrival_2[local.TIME] = arrival_t
            arrival_2[local.LEAVE] = True

            arrivals_all.append(arrival_2)
            continue

        # Start time of refueling
        start_t = arrival_t

        # If there are vehicles at the station,
        # it will be free only when the last one finishes
        if len(in_progress[best_station]) > 0:
            last_end = in_progress[best_station][-1]
            # If station is still busy -
            # vehicle waits until it's free
            if last_end > start_t:
                start_t = last_end

        # End time of refueling
        end_t = start_t + duration

        # Add new refueling to station queue
        in_progress[best_station].append(end_t)

        # Create copy of request,
        # record new start time and station number
        arrival_2 = arrival.copy()
        arrival_2[local.TIME] = arrival_t
        arrival_2[local.TIME_START] = start_t
        arrival_2[local.MACHINE] = best_station

        # Add to served lists
        arrivals_all.append(arrival_2)
        served.append(arrival_2)

    # all arrivals, served requests, number of clients that leave
    return arrivals_all, served, leave_without_refueling


# Creating a refueling list
def processing_end_refueling(arrivals_served: dict) -> list:
    '''
    The function processes served refueling requests and creates
    finish refueling events.

    Args:
        arrivals_served (dict): Dictionary containing served requests with:
                               - TIME_START: start time of refueling 
                                             (minutes from midnight)
                               - REFILL_DURATION: duration of refueling
                               - VOLUME: amount of fuel
                               - TYPE: fuel type
                               - ARRIVAL: arrival flag

    Returns:
        list[dict]: List of finish events for each served request
    '''

    # [{start time of refueling (minutes from midnight),
    #   amount of fuel,
    #   fuel type,
    #   refueling duration,
    #   arrival flag}, ...]
    finish = []

    for arrival in arrivals_served:
        # Get start time of refueling
        start_refill = arrival[local.TIME_START]
        # Refueling duration
        refill_duration = arrival[local.REFILL_DURATION]
        # Calculate end time of refueling
        end_refill = start_refill + refill_duration
        
        arrival_finish = arrival.copy()

        # Save the arrival time, because then TIME will become the end time
        arrival_finish[local.TIME_ARRIVAL] = arrival[local.TIME]

        # Changing dictionary values
        arrival_finish[local.TIME] = end_refill
        arrival_finish[local.ARRIVAL] = False

        finish.append(arrival_finish)

    return finish


def key_func(e: dict) -> tuple:
    '''
    The sorting key for the list of events.

        Sorting:
            1) by time e[local.TIME] (minutes from midnight)
            2) if the time is equal, by priority:
               priority=1 for arrival events (ARRIVAL=True),
               priority=0 for completion events (ARRIVAL=False)

        This means that if the time is the same, the completion event will occur earlier.,
        and arrival is later (since (t,0) < (t,1)).

        Args:
            e (dict): An event (dictionary) with the keys local.TIME and local.ARRIVAL.

        Returns:
            tuple[int, int]: (time, priority) for sorting.
    '''

    # Get value by TIME key
    t = e[local.TIME]

    prior = 0
    # Get and check value by ARRIVAL key
    # Dictionaries with True value have higher priority
    if e[local.ARRIVAL] is True:
        prior = 1

    return (t, prior)
    

def join_lists(arrivals_all: list, arrivals_finishes: list) -> list:
    '''
    Combines arrival and completion events into one list and sorts by time.

        Args:
            arrivals_all (list): Arrival events (including those who left).
            arrivals_finishes (list): Refueling completion events.

        Returns:
            list: A general sorted list of events (general_list).
    '''

    events = arrivals_all + arrivals_finishes

    # sort by time
    events.sort(key= key_func)

    return events
