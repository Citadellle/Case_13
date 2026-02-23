# A module for generating random values
import random

# Localisation
import ru_local as local

# Functions for time processing
from time_processing import *


def calculating_results(gas_prices: dict, arrivals_served: dict) -> tuple:
    #Задаем словарь с пока что пустыми значениями проданного топлива
    volumes_day = {}
    for t in gas_prices:
        volumes_day[t] = 0

    # Доход
    income = 0.0
    # Проходимся по посещениям
    for arrival in arrivals_served:
        type_fuel = arrival[local.TYPE]
        volume_fuel = int(arrival[local.VOLUME])

        # Если есть нужное топливо, то заправляем
        if type_fuel in volumes_day:
            # Сохраняем в словаре, сколько литров топлива заправили
            volumes_day[type_fuel] += volume_fuel
            # Добавляем к доходу вырочку от заправки
            income += (volume_fuel * float(gas_prices[type_fuel]))
    

    return volumes_day, income


def create_output_text(general_list, arrivals_all, volumes_day, income, left_count, stations) -> str:
    lines = []

    queues = {}
    for station in stations:
        queues[station] = []

    for e in general_list:
        time_str = standart_format_time(e[local.TIME])
        fuel = e[local.TYPE]
        liters = int(e[local.VOLUME])
        duration = e[local.REFILL_DURATION]
        station = e.get(local.MACHINE)

        if e[local.ARRIVAL]:
            # клиент не встал в очередь и уехал
            if e.get(local.LEAVE) is True:
                lines.append(
                    f"В {time_str} новый клиент: "
                    f"{time_str} {fuel} {liters} {duration} "
                    f"не смог заправить автомобиль и покинул АЗС.")
            else:
                lines.append(
                    f"В {time_str} новый клиент: "
                    f"{time_str} {fuel} {liters} {duration} "
                    f"встал в очередь к автомату №{station}")
                queues[station].append(duration)

        else:
            lines.append(
                f"В {time_str} клиент "
                f"{time_str} {fuel} {liters} {duration} заправил свой автомобиль и покинул АЗС.")
            if queues[station]:
                queues[station].pop(0)


        for station_id in sorted(stations.keys()):
            max_q = stations[station_id][0]
            fuels = " ".join(stations[station_id][1])
            stars = "*" * len(queues[station_id])

            lines.append(
                f"Автомат №{station_id} "
                f"максимальная очередь: {max_q} "
                f"Марки бензина: {fuels} ->{stars}"
            )

        lines.append("")

    lines.append("")
    lines.append("Итог за сутки:")

    for fuel in volumes_day:
        lines.append(f"{fuel}: {volumes_day[fuel]} л")
    
    lines.append(f"Заехало на заправку: {len(arrivals_all)}")

    lines.append(f"Уехало из-за очереди: {left_count}")

    lines.append(f"Доход за день: {int(income)} руб")

    # Постоянные расходы: Зарплата и страховка + Налоги с дохода + 
    #                     Аренда земли + Прочие расходы
    expenses_permanent = random.randint(150000, 180000) + int(income * 30 * 0.06) + \
                         random.randint(50000, 80000) + random.randint(20000, 30000)
    # Закупка топлива + Банковская комиссия
    expenses_variables = (income * 0.8 + income * 0.018) * 30
    # Общие ежемесячные расходы
    expenses_month = expenses_permanent + expenses_variables

    income_month = income * 30

    lines.append(f"Привиденные затраты за день: {expenses_month // 30} руб")

    lines.append(f"Средний доход за месяц: {int(income_month)} руб")
    lines.append(f"Средние затраты за месяц: {int(expenses_month)} руб")
    

    lines.append(f"Время окупаемости заправки: {round(10000000 / (income_month - expenses_month), 1)} года.")



    return "\n".join(lines)
