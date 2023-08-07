import logging

import SMPCrossPlatform.src.wait as wait
from SMPCrossPlatform.src.smp_time import time_to_int

from src.checks.test_configuration import TestConfiguration

logger = logging.getLogger(__name__)

""" Проверка перехода на зимнее/летнее время по дате и времени.
    После перехода на зимнее время в рамках 25 часа есть оссобенности счетчика (нельзя поменять время)
    Также в этом тесте проверяем сохраняет ли счетчик накопления за 25 час
"""


def test_change_winter_summer_date_time(
    conf: TestConfiguration
) -> None:
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    logger.info('Проверка перехода на зимнее/летнее время по дате и времени')
    relay_block.all_off()
    relay_block.ave_on()
    wait.wait(wakeup)
    try:
        tool.auth()
        started_accumulation_energy = float(tool.get_value("-ds 1"))
        logger.info(f'Начальная энергия (-ds 1){started_accumulation_energy}')
        wait.wait(wakeup)
        tool.execute("-os 3=[1] -a 2")  # по дате и времени [1]
        tool.execute("--t=8000 -a 27 -a 2")  # Обнуление накоплений за интервалы
        tool.set_time("28.10.2018 02:59:40")
        tool.execute("-os 143=[4] -a 2")   # интервал 15 мин
        time_before_winter: int = time_to_int(tool.get_current_time())

        relay_block.ave_off()
        # проверяем переход в выключенном состоянии
        wait.wait(30000)
        relay_block.ave_on()
        wait.wait(wakeup)

        # при корректном переходе время будет 2:00
        winter_time: int = time_to_int(tool.get_current_time())
        if winter_time < time_before_winter:
            logger.info("Переход на зимнее осуществляется корректно")
        else:
            logger.error("Переход на зимнее не осуществляется")

        # примерно в 2:10 выключаем счетчик из сети ждем 5 минут и включаем, время не должно быть больше 3:00
        wait.wait(600000)
        relay_block.ave_off()
        wait.wait(300000)
        relay_block.ave_on()
        current_time: int = time_to_int(tool.get_current_time())
        if current_time < time_before_winter:
            logger.info("Переход в выключенном состоянии осуществляется корректно")
        else:
            logger.error("Переход в выключенном состоянии не осуществляется")

        # особенности счетчика ждем конца 25 часа для проверки перехода на летнее время
        wait.wait(2677500)
        slice_energy = tool.get_value("--t=20000 -dm 29[0..4]")
        logger.info(f'Интервал накоплений за 25 час (-dm 29){slice_energy}')

        end_energy_storage = float(tool.get_value("-ds 1"))
        logger.info(f'Конечная энергия (-ds 1){end_energy_storage}')

        summary_energy_intervals = sum([float(x) for x in slice_energy])  # cумма накоплений за интервал
        summary_energy_interval_started = started_accumulation_energy + summary_energy_intervals
        if (end_energy_storage - summary_energy_interval_started) > 0.002:
            logger.error(
                'Подсчитанная энергия - (ds1 - начальная) расходится больше, чем на 0.002 (погрешность), '
                f'полученное знаение: {(end_energy_storage - summary_energy_interval_started)}'
            )
        else:
            logger.info('Подсчитанная энергия - (ds1 - начальная) не расходится больше, чем на 0.002 (погрешность), '
                f'полученное знаение: {(end_energy_storage - summary_energy_interval_started)}')

        tool.set_time("31.03.2019 02:59:40")
        logger.info('Проверка перехода на летнее')
        time_before_summer: int = time_to_int(tool.get_current_time())
        relay_block.ave_off()
        wait.wait(30000)
        relay_block.ave_on()
        wait.wait(wakeup)
        summer_time: int = time_to_int(tool.get_current_time())
        if summer_time > time_before_summer:
            logger.info("Переход на летнее осуществляется корректно")
        else:
            logger.error("Переход на летнее не осуществляется")
    except Exception as ex:
        logger.warning(f'test {__name__} is Failure')

        logger.error(ex)
