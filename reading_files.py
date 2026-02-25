from typing import List, Dict, Tuple

def reading_requests() -> List[str]:
    '''
    The function reads data from the 'input.txt' file and returns
    a list of strings, each representing a line from the file.

    Returns:
        list[str]: List of strings read from the input file
    '''

    with open('input.txt', encoding = 'utf-8') as file:
        requests  = [i.strip() for i in file.readlines()]
    
    return requests


def reading_gas_stations() -> Dict[int, Tuple]:
    '''
    The function reads gas station data from the 'gas_stations.txt' file.

    File format: each line contains gas station number, maximum queue length,
    and available fuel types separated by spaces.

    Returns:
        dict[int: tuple]: Dictionary where key is gas station number and
                         value is a tuple containing:
                         - maximum possible queue length (int)
                         - list of available fuel types (list[str])
    '''
    
    gas_stations = {}

    with open('gas_stations.txt', encoding = 'utf-8') as file:
        for line in file.readlines():
            line_elements = line.split()
            # Dictionary with gas station data:
            # {number gas station : (max possible queue length,
            #                        [fuel types])}
            gas_stations[int(line_elements[0])] = (int(line_elements[1]),
                                                   line_elements[2:])

    return gas_stations
