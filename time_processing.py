def mints_from_midnight_format_time(time: str) -> int:
    '''
    The function converts time from 'HH:MM' format to minutes since midnight.

    Args:
        time (str): Time string in 'HH:MM' format

    Returns:
        int: Number of minutes since midnight
    '''

    # Split string into hours and minutes
    time_spl = time.split(':')

    hour = int(time_spl[0])
    minute = int(time_spl[1])

    minutes = int(hour) * 60 + int(minute)

    return minutes


def standart_format_time(minutes: int) -> str:
    '''
    The function converts minutes since midnight to standard 'HH:MM' time format.

    Args:
        minutes (int): Number of minutes since midnight

    Returns:
        str: Time string in 'HH:MM' format
    '''

    hour = minutes // 60
    minute = minutes % 60

    # Formatting the output
    return f'{hour:02d}:{minute:02d}'
