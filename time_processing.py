def mints_from_midnight_format_time(time: str) -> int:
    # 'HH:MM' -> минуты от 00:00

    # Разбиваем строку на часы и минуты
    time_spl = time.split(':')

    hour = int(time_spl[0])
    minute = int(time_spl[1])

    minutes = int(hour) * 60 + int(minute)

    return minutes


def standart_format_time(minutes: int) -> str:
    # минуты от 00:00 -> 'HH:MM'

    hour = minutes // 60
    minute = minutes % 60

    return f'{hour:02d}:{minute:02d}'