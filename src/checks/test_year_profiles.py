import logging
from typing import List

from SMPCrossPlatform.src import wait
from SMPCrossPlatform.src.smp_time import time_to_int

from src.checks.test_configuration import TestConfiguration

logger = logging.getLogger(__name__)


def almost_equals(a: float, b: float, epsilon: float = 0.00012) -> float:
    return abs(a - b) <= epsilon


def test_year_profiles(
    conf: TestConfiguration
) -> None:
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    logger.info('CHECK YEAR PROFILE')
    relay_block.all_off()
    relay_block.block_on(8)
    wait.wait(wakeup)
    try:
        tool.auth()
        tool.execute("--t=40000 -a 5 -a 3")  # -a 25
        tool.execute('-a 25')
        wait.wait(10000)

        day_beg: List = []

        for step in range(1, 11):
            logger.info(f"Step-{step}")
            tool.auth()
            tool.set_time(time_to_int(f'01.01.{2015 + step} 00:00:00') - 20)  # -20 sec.
            wait.wait(5000)
            if step % 5 == 0:
                relay_block.block_off(8)
                wait.wait(20000)
                relay_block.block_on(8)
            else:
                wait.wait(20000)
            # сохранить накопление энергии на начало дня
            day_beg.append(float(tool.get_value("--t=1000 --r=100 -ds 1(0)")))
            relay_block.block_on(7)
            wait.wait(10000 * step)  # 10000 * i
            relay_block.block_off(7)
            logger.info(f'Энергия на начало дня в новом году: {day_beg[step - 1]}')
            if step % 3 == 0:
                relay_block.block_off(8)
                wait.wait(10000)
                relay_block.block_on(8)
                wait.wait(wakeup)
            else:
                wait.wait(10000)
            energy_start_of_year: str = tool.get_value("-dm 17[0..9](0)")  # энергия на начало года
            energy_per_year: str = tool.get_value("-dm 21[0..9](0)")  # энергия за год
            logger.info(f'Энергия на начало года: {energy_start_of_year}, энергия за год: {energy_per_year}')
            if not almost_equals(float(energy_start_of_year[0]), float(day_beg[step - 1])):
                logger.error(
                    f"Error energy on year begin, {step} iteration: {energy_start_of_year[step]} {day_beg[step]}")
                logger.warning(f'test {__name__} is Failure')

            if step >= 2:
                for i in range(step - 1):
                    if not float(energy_start_of_year[i]) - float(energy_start_of_year[i + 1]) - \
                           float(energy_per_year[i + 1]) <= 0.0001:
                        logger.error(
                            f'Накопления за год и на начало {i}-го года не сходятся. Накопления с устройства: '
                            f'Энергии на начало года:  {energy_start_of_year} '
                            f'Энергии за год:  {energy_per_year} '
                        )
                        logger.warning(f'test {__name__} is Failure')
            logger.info(f"Step-{step}")
        logger.warning(f'test {__name__} is OK')

    except Exception as ex:
        logger.warning(f'test {__name__} is Failure')

        logger.error('', ex)
