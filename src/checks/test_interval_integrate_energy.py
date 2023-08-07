"""
Логика теста подходит для NEROS

Тест работает с прошивкой Ю. Кобы под ГЛ-1. Интервалы начинают отсчитывать с чётных значений, т.е.:
1 минута - каждую минуту
3 минуты - каждые 3 минуты, то есть если время 08:28, то интервал закончится в 08:30 и следующий уже нормальный,
в 08:33 будет полный интервал
интервалы в таком случае: 00:03, 00:06, 00:09, 00:12, 00:15, 00:18, 00:21, 00:24, 00:27, 00:30, 00:33, 00:36, 00:39,
00:42, 00:45, 00:48, 00:51, 00:54, 00:57, 01:00

5 минут - каждые 5 минут, то есть при времени в 08:18, досчитает до 08:20, далее каждые 5 минут, 08:25 - полный интервал
интервалы в таком случае: 00:05, 00:10, 00:15, 00:20, 00:25, 00:30, 00:35, 00:40, 00:45, 00:50, 00:55, 01:00
10 минут - каждые 10 минут, при времени в 08:18, досчитает до 08:20, далее каждые 10 минут, 08:30 - полный интервал
интервалы в таком случае: 00:10, 00:20, 00:30, 00:30, 00:40, 00:50, 01:00...
15 минут - каждые 15 минут, при времени в 08:18, досчитает до 08:30, далее каждые 15 минут, 08:40 - полный интервал
интервалы в таком случае: 00:15, 00:30, 00:45, 01:00
30 минут - каждые 30 минут, при времени в 08:18, досчитает до 08:30, далее каждые 30 минут, 08:40 - полный интервал
интервалы в таком случае: 00:30, 01:00
60 минут - каждые 60 минут, при времени в 08:18, досчитает до 09:00, далее каждые 60 минут, 08:40 - полный интервал
интервалы в таком случае: 01:00
"""

import logging

from SMPCrossPlatform.src import wait
from SMPCrossPlatform.src.smp_exception import SMPException

from src.checks.test_configuration import TestConfiguration
from src.fixtures.test_interval_integrate_energy_fixture import *

logger = logging.getLogger(__name__)


def test_interval_integrate_energy(
    conf: TestConfiguration
) -> None:
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    logger.info('Test interval integrate energy')
    relay_block.all_off()
    relay_block.block_on(8)
    wait.wait(wakeup)

    try:
        tool.auth()
        logger.info('Отправляю команды -os 144=[1] -os 288=0 -os 143=[7]')
        tool.execute('-os 144=[1] -os 288=0 -os 143=[7] -a 2 --t=12000')
        wait.wait(10000)
        for interval in range(7):
            logger.info(f'Авторизация, отправка команды -os 143=[{interval}]')
            tool.auth()
            tool.execute(f'-os 143=[{interval}]')
            tool.execute("-a 2")
            wait.wait(10000)
            #if 0 in [float(_) for _ in tool.get_value('-dm 25[0..10]')]:
            for i in tool.get_value('-dm 25[0..10]'):
                if i != '0':
                    logger.error(
                        f'Накопления, вычитанные командой -dm 25 не пустые после смены интервала  командой -os '
                        f'143 на {interval}'
                    )
                    logger.warning(f'test {__name__} is Failure')
                    break

            while not tool.get_current_time()[14:19] in time_border[interval]:
                ...

            relay_block.block_on(7)

            wait.wait(profiles_list[interval])
            logger.info(tool.get_value('-dm 25[0..10]'))
            power_load = float(tool.get_value('-ds 14')) / 3600 * (profiles_list[interval] / 1000)

            counter_energy = float(tool.get_value('-dm 25[0..0]'))

            if abs(power_load - counter_energy) > 0.0005:
                logger.error(
                    f'Посчитанная и записанная в устройство энергии не совпадают, подсчитанная: {power_load}, '
                    f'на устройстве: {counter_energy}'
                )
                logger.warning(f'test {__name__} is Failure')

            relay_block.block_off(7)
            wait.wait(1200)
        logger.warning(f'test {__name__} is OK')

    except Exception as ex:
        logger.warning(f'test {__name__} is Failure')

        logger.error('', ex)
