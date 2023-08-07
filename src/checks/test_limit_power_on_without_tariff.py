import logging
from typing import List

import SMPCrossPlatform.src.wait as wait
from SMPCrossPlatform.src.smp_time import time_to_int, int_to_time

from src.checks.test_configuration import TestConfiguration
from src.fixtures.test_limits_power_on_schedule_fixture import options_limp

logger = logging.getLogger(__name__)


def test_limit_power_on_without_tariff(
        conf: TestConfiguration
) -> None:
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    logger.info("Check limP_zone")

    relay_block.all_off()
    relay_block.block_on(8)
    wait.wait(wakeup)

    def middle_power_value() -> float:
        load_power_list = []
        relay_block.block_on(7)
        logger.debug('Вычисление мощности нагрузки')
        wait.wait(5000)
        for _ in range(10):
            power = float(tool.get_value('-ds 14'))
            load_power_list.append(power)
            wait.wait(1000)
        load_max_power: float = round(sum(load_power_list) / len(load_power_list), 3)
        return load_max_power

    logger.info("Check limP_all")
    relay_block.block_on(8)
    wait.wait(wakeup)
    try:

        # Включение, авторизация
        tool.auth()

        # выключение контроля, сброс всех превышений
        power_threshold = 50 + 0  # +50 потому что разработчик протокола пожадничал биты

        limit_power_list_on: List[float] = []
        limit_power_list_off: List[float] = []

        wait.wait(4000)  # Ждём пока счётчик среагирует
        load_max_power = middle_power_value()
        relay_block.block_off(7)
        logger.info(f'Мощность нагрузки:{load_max_power}')
        percent_of_max_power = round(float(load_max_power) * (power_threshold / 100), 3)
        if load_max_power < 0.075:
            logger.error(f'Слишком слабая средняя нагрузка: {load_max_power}, меньше необходимой 75 Вт')
            logger.warning(f'test {__name__} is Failure')

        tool.execute('-os 84=[0:1:20:4:1]')  # загрузка os 84
        for options in options_limp:
            tool.execute(''.join(options))  # загрузка всех настроек
        # загрузка режима контроля лимитов мощности "включено" "всегда"
        tool.execute(f'-os 84=[0:0:{power_threshold - 50}:4:1]')

        for set_option in range(85, 109):
            tool.execute(f'-os {set_option}={percent_of_max_power}')

        tool.execute("--t=20000 -a 2")  # Скопировать фоновую конфигурацию в рабочую

        for limit_sets in range(85, 88):
            if float(tool.get_value(f'-og {limit_sets}')) != percent_of_max_power:
                logger.error(f'Limit {limit_sets} is not set')
                logger.warning(f'test {__name__} is Failure')
            else:
                logger.info(f'Limit {limit_sets} set is ok')

        # Запись времени
        start_power = float(tool.get_value('-ds 1'))
        wait.wait(9000)
        tool.set_time(time_to_int("31.05.2013 23:59:58"))  # для перехода на следующий месяц
        wait.wait(9000)  # 2000		#  фронт интервала интегрирования мощности

        # Запись времени
        tool.set_time(time_to_int("2.06.2013 23:59:58"))  # для перехода на понедельник
        #  2-й фронт интервала интегрирования мощности, д.б. снят флаг превышения порога мощности
        wait.wait(9000)  # 2000
        # Запись времени
        tool.set_time(time_to_int("30.06.2013 23:59:58"))  # для перехода на следующий месяц
        wait.wait(9000)  # 2000		#  фронт интервала интегрирования мощности

        # Запись времени
        tool.set_time(time_to_int("2.07.2013 23:59:58"))  # для перехода на понедельник
        #  2-й фронт интервала интегрирования мощности, д.б. снят флаг превышения порога мощности
        wait.wait(9000)  # 2000
        end_power = float(tool.get_value('-ds 1')) - start_power
        logger.debug(f'Накоплено с выкл лампой {end_power * 1000}вт')
        # чтение флага превышения лимита мощности
        wait.wait(135000)

        status = int(tool.get_value('-i 23'))
        if status & (1 << 0) != 0:
            logger.error("Флаг превышения лимита установлен, хотя не должен: <start> overLimP != 0")
            logger.warning(f'test {__name__} is Failure')

        # 1) включение нагрузки, контроль превышения лимита мощности
        relay_block.block_on(7)
        logger.debug(f'Время включения нагрузки: {int_to_time(int(tool.get_value("-og 1")))}')
        # wait.wait(3000)

        # фаза включения нагрузки
        for i in range(12):  # цикл 2 минуты.
            current_power = float(tool.get_value("-ds 14"))
            limit_power_list_on.append(current_power)
            logger.debug(f'Текущая мощность: {current_power}')
            logger.debug(f'Текущее время: {int_to_time(int(tool.get_value("-og 1")))}')
            wait.wait(10000)

        average_power_on = sum(limit_power_list_on) / len(limit_power_list_on)

        if average_power_on < load_max_power * 0.2:
            logger.error(
                f"Перегоревшая лампа либо не откалиброванный счётчик, мощность за 90 секунд = {average_power_on}"
            )
            logger.warning(f'test {__name__} is Failure')
        # фаза выключения нагрузки
        relay_block.block_off(7)
        logger.debug(f'Время выключения нагрузки: {int_to_time(int(tool.get_value("-og 1")))}')
        wait.wait(4000)

        # TODO: Сломаный функционал, если ждать 1.4 минуты, то флаг пропадает, но проверка требует его наличие ???
        # TODO: так он и должен пропасть, т.к. средняя за прошлый интревал меньше лимита
        # for i in range(8):  # цикл 1.4 минуты
        #     current_power = float(tool.get_value("-ds 14"))
        #     limit_power_list_off.append(current_power)
        #     logger.debug(f'Текущая мощность: {current_power}')
        #     logger.debug(f'Текущее время: {int_to_time(int(tool.get_value("-og 1")))}')
        #
        #     wait.wait(8500, True)
        # logger.info(limit_power_list_off)
        # logger.info(limit_power_list_off)
        # logger.info(sum(limit_power_list_off))
        # logger.info(len(limit_power_list_off))
        # average_power_off = sum(limit_power_list_off) / len(limit_power_list_off)
        # if average_power_off > load_max_power * 0.01:
        #     logger.error(
        #         f"Самоход, либо неоткалиброванный счётчик, мощность за 90 секунд: {average_power_off}")

        # average_power = sum(limit_power_list_on + limit_power_list_off) / len(
        #     limit_power_list_on + limit_power_list_off
        # )
        # logger.debug(f'Использовано {average_power}Вт, лимит установлен на {percent_of_max_power}Вт')

        logger.debug(f'Время проверки флага: {int_to_time(int(tool.get_value("-og 1")))}')
        # чтение флага превышения лимита мощности
        status = int(tool.get_value("-i 23"))
        if status & (1 << 0) != 1:
            logger.error("Флаг превышения лимита не установлен, хотя должен: overLimP != 1")
            logger.warning(f'test {__name__} is Failure')

        limit_power_list_on.clear()
        limit_power_list_off.clear()

        logger.debug(f'Время включения нагрузки: {int_to_time(int(tool.get_value("-og 1")))}')
        relay_block.block_on(7)

        # фаза включения нагрузки
        for i in range(2):  # цикл 20 сек.
            current_power = float(tool.get_value("-ds 14"))
            limit_power_list_on.append(current_power)
            logger.debug(f'Текущая мощность: {current_power}')
            logger.debug(f'Текущее время: {int_to_time(int(tool.get_value("-og 1")))}')

            wait.wait(10000)
        average_power_on = sum(limit_power_list_on) / len(limit_power_list_on)
        if average_power_on < load_max_power * 0.2:
            logger.error(
                f"Перегоревшая лампа либо не откалиброванный счётчик, мощность за 20 секунд = {average_power_on}"
            )
            logger.warning(f'test {__name__} is Failure')

        # фаза выключения нагрузки
        relay_block.block_off(7)

        logger.debug(f'Время выключения нагрузки: {int_to_time(int(tool.get_value("-og 1")))}')

        wait.wait(4000)
        for i in range(15):  # цикл 160 сек.
            current_power = float(tool.get_value("-ds 14"))
            limit_power_list_off.append(current_power)
            logger.debug(f'Текущая мощность: {current_power}')
            logger.debug(f'Текущее время: {int_to_time(int(tool.get_value("-og 1")))}')
            wait.wait(9734)

        average_power_off = sum(limit_power_list_off) / len(limit_power_list_off)
        if average_power_off > load_max_power * 0.01:
            logger.error(
                f"Самоход либо не откалиброванный счётчик, мощность за 160 секунд = {average_power_off}")
            logger.warning(f'test {__name__} is Failure')

        wait.wait(5000)
        # чтение флага превышения лимита мощности
        average_power = sum(limit_power_list_on + limit_power_list_off) / len(
            limit_power_list_on + limit_power_list_off
        )
        logger.debug(f'Использовано {average_power}Вт, лимит установлен на {percent_of_max_power}Вт')
        logger.debug(f'Время проверки флага: {int_to_time(int(tool.get_value("-og 1")))}')
        status = int(tool.get_value("-i 23"))
        if status & (1 << 0) != 0:
            logger.error("Флаг превышения лимита установлен, хотя не должен: <start> overLimP != 0")
            logger.warning(f'test {__name__} is Failure')
        logger.warning(f'test {__name__} is OK')

    except Exception as ex:
        logger.warning(f'test {__name__} is Failure')

        logger.error(f'{ex}')
