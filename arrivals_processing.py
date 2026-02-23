# A module for working with mathematical functions
import math
# A module for generating random values
import random

# Localization
import ru_local as local

# Functions for time processing
from time_processing import *


def get_refill_duration(volume: float) -> int:
    # Дополнительное округление на случай, если объем топлива будет не int
    volume = math.ceil(volume)

    # Скорость заправки 10 литров в минуту
    # Получаем время заправки: делим объем на скорость и прибавляем случайное
    # целое значение: -1, 0, 1
    refill_duration = math.ceil(volume / 10) + random.randint(-1, 1)

    return refill_duration if refill_duration > 0 else 1


def processing_requests(requests: list) -> list[dict]:
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


def assign_requests_to_stations(arrivals: dict, 
                                stations: dict) -> tuple[list[dict], 
                                                         list[dict], 
                                                         int]:
    # Словарь, где для каждого автомата будем хранить список времен окончания текущих заправок
    in_progress = {}
    for station in stations:
        in_progress[station] = []

    # Все прибывшие
    arrivals_all = []
    # Список обслуженных заявок
    served = []

    # Счетчик машин, которые уехали из-за переполненной очереди
    leave_without_refueling = 0

    # Обрабатываем каждую машину по порядку её прибытия
    for arrival in arrivals:

        # Переводим время прибытия из формата 'часы:минуты'
        arrival_t = mints_from_midnight_format_time(arrival[local.TIME])
        # Тип топлива машины
        fuel = arrival[local.TYPE]
        # Длительность заправки в минутах
        duration = arrival[local.REFILL_DURATION]

        # Удаляем из очередей те машины, которые уже закончили заправку
        for station in in_progress:
            new_list = []
            for end_t in in_progress[station]:
                # Оставляем только те заправки,
                # которые заканчиваются позже прибытия новой машины
                if end_t > arrival_t:
                    new_list.append(end_t)
            in_progress[station] = new_list

        # выбираем подходящий автомат:
        # 1) поддерживает марку топлива
        # 2) очередь не переполнена
        # 3) минимальная очередь, при равенстве - меньший номер
        best_station = None
        best_queue = None

        # Перебираем все автоматы
        for station in stations:
            # Максимально допустимая длина очереди
            max_q = stations[station][0]
            # Виды топлива, поддерживаемые автоматом
            fuels = stations[station][1]

            if fuel not in fuels:
                continue

            # Текущая длина очереди
            q_len = len(in_progress[station])

            if q_len >= max_q:
                continue

            # Если это первый подходящий автомат
            if best_station is None:
                best_station = station
                best_queue = q_len
            else:
                # Выбираем автомат: с меньшей очередью, если очередь равна — с меньшим номером
                if q_len < best_queue or (q_len == best_queue and station < best_station):
                    best_station = station
                    best_queue = q_len

        # Если не нашли подходящий автомат - клиент уехал,
        # но событие прибытия добавляем в arrivals_all
        if best_station is None:
            leave_without_refueling += 1

            arrival_2 = arrival.copy()

            arrival_2[local.TIME] = arrival_t
            arrival_2[local.LEAVE] = True

            arrivals_all.append(arrival_2)
            continue

        # Время начала заправки.
        start_t = arrival_t

        # Если на автомате есть машины,
        # то он освободится только когда закончится последняя
        if len(in_progress[best_station]) > 0:
            last_end = in_progress[best_station][-1]
            # Если автомат ещё занят —
            # машина ждёт до его освобождения
            if last_end > start_t:
                start_t = last_end

        # Время окончания заправки
        end_t = start_t + duration

        # Добавляем новую заправку в очередь автомата
        in_progress[best_station].append(end_t)

        # Делаем копию заявки,
        # записываем новое время начала и номер автомата
        arrival_2 = arrival.copy()
        arrival_2[local.TIME] = arrival_t
        arrival_2[local.TIME_START] = start_t
        arrival_2[local.MACHINE] = best_station

        # Добавляем обслуженных в списках
        arrivals_all.append(arrival_2)
        served.append(arrival_2)

    # список всех, список обслуженных, количество уехавших машин
    return arrivals_all, served, leave_without_refueling


def processing_end_refueling(arrivals_served: dict) -> list[dict]:
    # [{время начала заправки (количество минут от полуночи),
    #   количество топлива,
    #   вид топлива,
    #   длительность заправки,
    #   прибыл}, ...]
    finish = []

    for arrival in arrivals_served:
        # Получаем время начала заправки
        start_refill = arrival[local.TIME_START]
        # Длительность заправки
        refill_duration = arrival[local.REFILL_DURATION]
        # Подсчитываем время конца заправки
        end_refill = start_refill + refill_duration
        
        arrival_finish = arrival.copy()

        # Меняем значения словаря
        arrival_finish[local.TIME] = end_refill
        arrival_finish[local.ARRIVAL] = False

        finish.append(arrival_finish)

    return finish


def key_func(e: dict) -> tuple[int, int]:
    t = e[local.TIME]

    prior = 0
    if e[local.ARRIVAL] is True:
        prior = 1

    return (t, prior)
    

def join_lists(arrivals_all: list, arrivals_finishes: list) -> list:
    events = arrivals_all + arrivals_finishes

    # сортировка по времени
    events.sort(key= key_func)

    return events