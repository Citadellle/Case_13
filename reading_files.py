def reading_requests() -> list[str]:
    with open('input.txt', encoding = 'utf-8') as file:
        requests  = [i.strip() for i in file.readlines()]
    
    return requests


def reading_gas_stations() -> dict[int: tuple]:
    gas_stations = {}

    with open('gas_stations.txt', encoding = 'utf-8') as file:
        for line in file.readlines():
            line_elements = line.split()
            # Словарь с данными о бензоколонках:
            # {number gas station : (max possible queue length,
            #                        [petrol brands])}
            gas_stations[int(line_elements[0])] = (int(line_elements[1]),
                                                   line_elements[2:])

    return gas_stations