import logging
from typing import List, Union

import SMPCrossPlatform.src.smp_time as smp_time
from SMPCrossPlatform.src import wait

from src.checks.test_configuration import TestConfiguration

logger = logging.getLogger(__name__)


def test_intervals_profiles(
        conf: TestConfiguration
) -> None:
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool
    try:
        logger.info('CHECK INTERVAL PROFILE')
        relay_block.block_on(8)
        wait.wait(wakeup)

        tool.auth()
        tool.execute("--t=40000 -a 5 -a 3")  # -a 25
        # перевод часов вперед

        # контроль параметров сети (напряжение ток)
        tool.execute('-os 144=[1] -os 143=[6] -os 288=1')
        tool.execute("--t=40000 -a 2")

        # проверка минутного интервала
        tool.set_time("01.01.2020 00:00:00")
        tool.execute("-os 143=[0]")

        tool.execute("--t=40000 -a 2")
        relay_block.block_on(7)
        wait.wait(120000)
        relay_block.block_off(7)

        res: float = float(tool.get_value("-dm 25"))
        if 0.0016 < res or res < 0.0012:
            logger.warning(f'test {__name__} is Failure')
            logger.error(f"Неверные накопления на минутном интервале: {res}")

        voltage: float = float(tool.get_value('-dm 33'))
        if 260 < voltage or voltage < 190:
            logger.warning(f'test {__name__} is Failure')
            logger.error(f"Неверный срез по напряжению на минутном интервале: {voltage}")

        current: float = float(tool.get_value('-dm 57'))
        if 0.5 < current or current < 0.3:
            logger.warning(f'test {__name__} is Failure')
            logger.error(f"Неверный срез по току на минутном интервале: {current}")

        logger.info('1-min interval')
        # проверка 3-минутного интервала
        logger.info("check 3-min interval")
        wait.wait(1500)

        tool.set_time("01.02.2020 00:00:00")
        logger.debug("set time 01.02.2020 00:00:00")
        tool.execute('-os 143=[1]')
        tool.execute("--t=40000 -a 2")

        logger.debug('power ON')
        relay_block.block_on(7)
        wait.wait(190000)
        logger.debug('power OFF')
        relay_block.block_off(7)

        res = float(tool.get_value("-dm 25"))
        if 0.0036 > res or res > 0.0046:
            logger.warning(f'test {__name__} is Failure')
            logger.error(f"Неверные накопления на 3-х минутном интервале: {res}")

        voltage: float = float(tool.get_value('-dm 33'))
        if 260 < voltage or voltage < 190:
            logger.warning(f'test {__name__} is Failure')
            logger.error(f"Неверный срез по напряжению на 3-х минутном интервале: {voltage}")

        current: float = float(tool.get_value('-dm 57'))
        if 0.5 < current or current < 0.3:
            logger.warning(f'test {__name__} is Failure')
            logger.error(f"Неверный срез по току на 3-х минутном интервале: {current}")

        logger.info('3-min interval')
        # проверка 5-минутного интервала
        logger.info("check 5-min interval")
        wait.wait(1500)

        tool.set_time("01.03.2020 00:00:00")
        logger.debug("set time 01.03.2020 00:00:00")

        tool.execute('-os 143=[2]')
        tool.execute("--t=40000 -a 2")

        relay_block.block_on(7)
        logger.debug('power ON')
        wait.wait(310000)
        logger.debug('power OFF')
        relay_block.block_off(7)

        res = float(tool.get_value("-dm 25"))
        if 0.0077 < res or res < 0.0062:
            logger.warning(f'test {__name__} is Failure')
            logger.error(f"Неверные накопления на 5-и минутном интервале: {res}")

        voltage: float = float(tool.get_value('-dm 33'))
        if 260 < voltage or voltage < 190:
            logger.warning(f'test {__name__} is Failure')
            logger.error(f"Неверный срез по напряжению на 5-и минутном интервале: {voltage}")

        current: float = float(tool.get_value('-dm 57'))
        if 0.5 < current or current < 0.3:
            logger.warning(f'test {__name__} is Failure')
            logger.error(f"Неверный срез по току на 5-и минутном интервале: {current}")
        logger.info('5-min interval')

        tool.auth()
        # контроль параметров сети (напряжение частота)
        tool.execute('-os 288=0')
        tool.execute("--t=40000 -a 2")

        # проверка 10-минутного интервала
        logger.info("check 10-min interval:")
        wait.wait(1500)

        tool.set_time("01.04.2020 00:00:00")
        logger.debug("set time 01.04.2020 00:00:00")

        tool.execute('-os 143=[3]')
        tool.execute("--t=40000 -a 2")

        relay_block.block_on(7)
        logger.debug('power ON')
        wait.wait(610000)
        logger.debug('power OFF')
        relay_block.block_off(7)

        res = tool.get_value("-dm 25")
        if 0.0133 > float(res) or float(res) < 0.0124:
            logger.warning(f'test {__name__} is Failure')
            logger.error("Неверные накопления на 10-и минутном интервале:" + str(res))
        logger.info('10-min interval')

        # проверка заполнения интервала
        relay_block.block_on(8)
        wait.wait(150)
        logger.info("check count energy on interval:")
        start_time = smp_time.time_to_int("01.05.2020 00:00:00")

        res_array: List[Union[int, float]] = [_ for _ in range(10)]

        for array_iterator in range(0, 10):
            res_array[array_iterator] = float(tool.get_value("-ds 1(0)"))
            relay_block.block_on(7)
            wait.wait(array_iterator * 10000)
            relay_block.block_off(7)
            wait.wait(1000)
            res_array[array_iterator] = round(float(tool.get_value("-ds 1(0)")) - res_array[array_iterator], 4)

            tool.set_time(start_time - 4 + (array_iterator + 1) * 30 * 60)
            wait.wait(5000)
        wait.wait(150)
        tool.execute('-os 143=[0]')
        tool.execute("--t=40000 -a 2")
        res_intervals: str = tool.get_value("-dm 25[0..20]")
        for flags in range(0, 10):
            if round(int(res_intervals[flags]) - (res_array[9 - flags]), 4) > 0.0001:
                logger.warning(f'test {__name__} is Failure')
                logger.error(f"5Wrong values & flags with interval: {res_intervals}")

        # проверить перевод часов вперед
        logger.info("check forward time correction:")
        tool.set_time(start_time + 15 * 30 * 60)
        wait.wait(15000)
        res_intervals = tool.get_value("-dm 25[0..20]")

        for i in range(0, 5):
            if int(res_intervals[i]) != 0:
                logger.warning(f'test {__name__} is Failure')
                logger.error(f"6Wrong values & flags with interval: {res_intervals}")

        # проверить перевод часов назад и сохранение суммированной энергии
        logger.info("check backward time correction:")
        wait.wait(5 * 10000)

        start_time = smp_time.time_to_int("01.01.2020 00:00:00")

        relay_block.block_on(7)
        wait.wait(5 * 10000)
        relay_block.block_off(7)
        tool.set_time(start_time + 16 * 30 * 60 - 4)
        wait.wait(5000)
        relay_block.block_on(7)
        wait.wait(15 * 10000)
        relay_block.block_off(7)
        wait.wait(1000)

        res2 = tool.get_value("-dm 25[0..20]")
        tool.set_time(start_time + 3 * 30 * 60 - 4)
        wait.wait(1500)

        wait.wait(1500)

        r_sum = sum(map(float, res2))

        sum_values = float(tool.get_value("-ds 9(0)"))

        if abs(r_sum - sum_values) > 0.0000003:
            logger.error(f"Wrong time back sum: must be {r_sum}, is {sum_values}")
        logger.warning(f'test {__name__} is OK')

        logger.info("check paramms power line:")
        for i in range(5):
            tool.set_time(1000 + i * 60 - 30)
            relay_block.block_on(7)
            wait.wait(10 * 1000)
            relay_block.block_off(7)

        tool.set_time(1000 + 5 * 60)
        res_voltage: str = tool.get_value("-dm 33[0..4]")
        res_freq: str = tool.get_value("-dm 34[0..4]")
        for i in range(0, 5):
            if abs(float(res_voltage[i])) - 230 >= 30:
                logger.warning(f'test {__name__} is Failure')
                logger.error(f"Wrong values & flags with interval of voltage: {res_voltage}")
            if abs(float(res_freq[i])) - 50 >= 2:
                logger.warning(f'test {__name__} is Failure')
                logger.error(f"Wrong values & flags with interval of freq: {res_freq}")

    except Exception as e:
        logger.warning(f'test {__name__} is Failure')

        logger.error('', e)
