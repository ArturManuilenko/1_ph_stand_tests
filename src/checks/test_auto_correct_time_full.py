import datetime
import logging
from typing import List, Any

import SMPCrossPlatform.src.smp_time as time_smp
from SMPCrossPlatform.src import wait

from src.checks.test_configuration import TestConfiguration

logger = logging.getLogger(__name__)

def test_auto_correct_time_full(
        conf: TestConfiguration
) -> None:
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    logger.info('Start test manual correct time')
    relay_block.all_off()
    relay_block.block_on(8)
    wait.wait(wakeup)
    tool.auth()
    tool.execute('--t=20000 -a 2 -a 80')
    try:

        default_array: List[Any] = []
    
        relay_block.block_on(8)
        wait.wait(wakeup)
        logger.debug('checking arithmetic mouth')

        def prepare_rate(error: int = 3, time: int = 60, sync: int = 9999, monitoring: int = 1) -> None:
            logger.info('start prepare rate')
            try:
                tool.auth()
                tool.execute('--t=20000 -a 5 -a 3')
                wait.wait(1000)
                tool.execute(f'-os 6={time} -os 7={sync} -os 8=[{error}:0:1:{monitoring}]')
                wait.wait(1000)
                tool.execute('--t=20000 -a 80')
                tool.deauth()
                logger.info('prepare rate')

            except Exception as e:
                logger.error(f'error on prepare rate, {e}')
                logger.warning(f'test {__name__} is Failure')

        def relative_logic(month: int, sign: bool = False) -> None:
            de_sync = 0
            for day in range(1, 10):
                tool.auth()
                wait.wait(9000)
                tool.set_time("{:02d}.{:02d}.{} 23:59:57".format(day, month, int(datetime.datetime.now().year) - 1))
                relay_block.block_off(8)
                wait.wait(5000)
                relay_block.block_on(8)
                wait.wait(wakeup)
                tool.auth()

                tool.set_time("{:02d}.{:02d}.{} 05:00:00".format(day + 1, month, int(datetime.datetime.now().year) - 1))
                tool.deauth()

                delta = 5 - (10 + day) * (day % 2)

                tool.execute(
                    f"""-a 42={str(int(tool.get_value('-og 1')) + delta) if sign == False
                    else str(abs(delta) + int(tool.get_value('-og 1')))}""")

                last_divergence = int(tool.get_value('-ds 44') if sign is False else abs(int(tool.get_value('-ds 44'))))
                logger.debug(f'Величина последнего расхождения: {last_divergence}')
                de_sync = de_sync + last_divergence

                if abs(delta - last_divergence) > 2 if sign is False else abs(abs(delta) - last_divergence) > 2:
                    logger.error('delta - ds44 > 2 sec, check correct ')
                    logger.warning(f'test {__name__} is Failure')

                data_single_time_correct = tool.get_value('-ds 42')
                place = data_single_time_correct.find(';')
                r = int(data_single_time_correct[1:place])
                if r != de_sync:
                    logger.error(
                        f'Полученное значение НЕ совпадает с суммой отправленных величин, посчитано: {de_sync}, '
                        f'посчитано счётчиком: {tool.get_value("-ds 42")}'
                    )
                    logger.warning(f'test {__name__} is Failure')

        for options_get in range(6, 9):
            default_array.append(tool.get_value(f'-og {options_get}'))
    
        logger.info(f'Default array: -os 7={default_array[1]}, -os 6={default_array[0]}')
    
        prepare_rate()
    
        for month in range(1, 5):
            tool.auth()
            tool.set_time("01.{:02d}.{} 23:59:57".format((int(datetime.datetime.now().month) + month),
                                                              int(datetime.datetime.now().year) - 1))
            relay_block.block_off(8)
            wait.wait(12000)
    
            relay_block.block_on(8)
            wait.wait(wakeup)
            tool.auth()
            tool.execute('--t=20000 -a 2 -a 80')
            tool.deauth()
            relative_logic(month)
        logger.info('sync arithmetic mouth end')

        prepare_rate(3)

        logger.info('start checking arithmetic year')

        for year in range(1, 5):
            tool.auth()
            tool.set_time(
                f'''{time_smp.int_to_time(
                    time_smp.time_to_int(f"01.01.{int(datetime.datetime.now().year) - year} 00:00:00") - 10)}'''
            )
            wait.wait(15000)

            tool.execute('--t=20000 -a 2 -a 80')
            tool.deauth()
            relative_logic(year)
        logger.info('de sync arithmetic year end')

        prepare_rate(2)
        logger.info('checking absolute error')

        for year in range(1, 5):
            tool.auth()
            tool.set_time(
                f"""{time_smp.int_to_time(
                    time_smp.time_to_int(f"01.01.{int(datetime.datetime.now().year) - year} 00:00:00") - 10)}"""
            )
            wait.wait(15000)

            tool.execute('--t=20000 -a 2 -a 80')
            tool.deauth()
            relative_logic(year, sign=True)
        logger.info('absolute year end')

        prepare_rate(0)
        logger.info('checking absolute error month')

        for month in range(1, 12):
            tool.auth()
            tool.set_time(
                f"""{time_smp.int_to_time(
                    time_smp.time_to_int(f"01.{13 - month}.2020 00:00:00") - 10)}""")
            wait.wait(15000)

            tool.execute('--t=20000 -a 2 -a 80')
            tool.deauth()
            relative_logic(month, sign=True)
        logger.info('absolute month end')

        prepare_rate(time=5, sync=60, monitoring=2)
        tool.auth()

        wait.wait(2000)

        tool.set_time(
            time_smp.int_to_time(
                int(tool.get_value("-og 1")) + 86400
            )
        )
        wait.wait(2000)

        tool.execute(
            f"-a 42={str(int(tool.get_value('-og 1')) + 10)}")

        wait.wait(2000)

        logger.info('Ошибка рассинхронизации зафиксирована и вычитана')

        tool.auth()

        tool.set_time(datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
        tool.execute("-a 2")
        for options_get in range(6, 9):
            if options_get == 8:
                tool.execute(f'-os {options_get}={str(default_array[2]).replace(", ", ":")}')
            else:
                (tool.execute(f'-os {options_get}={default_array[options_get - 6]}'))

        tool.execute('-a 2')
        tool.deauth()
        logger.warning(f'test {__name__} is OK')
        relay_block.all_off()

    except Exception as e:
        logger.error(e)
        logger.warning(f'Test is failure ')
