import datetime
import logging
import time

from SMPCrossPlatform.src import wait

from src.checks.test_configuration import TestConfiguration
from src.fixtures.test_check_tariff_on_timezone_fixture import set_options_commands


logger = logging.getLogger(__name__)


def test_tariff_timezone(
        conf: TestConfiguration
) -> None:
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    logger.info("checking accumulation profiles")
    relay_block.all_off()

    relay_block.block_on(8)
    wait.wait(wakeup)
    try:
        tool.auth()
        tool.execute('--t=20000 -a 5')
        tool.execute('--t=20000 -a 3')
        wait.wait(5000)
        for set_options in set_options_commands:
            tool.execute(''.join(set_options))

        tool.execute('--t=3000 -a 2')
        relay_block.block_on(8)
        wait.wait(wakeup)
        for hour in range(47):
            accumulating_start = []
            accumulating_end = []
            for tariff in range(1, 9):
                vals = str(tool.get_value(f'-ds 1(m{tariff})')[1:-1])
                accumulating_start.append(vals)
            tool.set_time(
                datetime.datetime.now().strftime(
                    "%d.%m.%Y {0}:{1}:00".format(
                        f'0{int(hour // 2)}' if hour < 20 else int(hour // 2), 30 if hour % 2 == 0 else '00'
                    )
                )
            )
            relay_block.block_on(7)
            rate = tool.get_value('-i 7')
            tf_start = float(tool.get_value(f'-ds 1(m{rate})')[1:-1])
            logger.info(f"Начальные накопления на тарифе {rate} = {tf_start}")
            logger.info('Ожидание 2 минуты чтобы накопилась энергия')
            wait.wait(121000)
            tf_end = float(tool.get_value(f'-ds 1(m{rate})')[1:-1])
            logger.info(f"Конечные на тарифе {rate}: {tf_end}")
            if float(tf_end) - float(tf_start) == 0:
                logger.error(f'Ошибка на профиле: {rate} начальные накопления совпали с конечными')
                logger.warning(f'test {__name__} is Failure')
            if (float(tf_end) - float(tf_start)) > 0.0035 or \
                    (float(tf_end) - float(tf_start)) < 0.0025:
                logger.error('Устройство неверно считает энергию\n'
                             f'Подсчитано: {float(tf_end) - float(tf_start)} вместо 0.0025-0.0035')
                logger.warning(f'test {__name__} is Failure')
            else:
                logger.info("{0}:{1}:00 for {2} rate".format
                            (f'0{int(hour // 2)}' if hour < 20 else int(hour // 2),
                             30 if hour % 2 == 0 else '00', rate))
                relay_block.block_off(7)
                time.sleep(3)

            for tariff_rate in range(1, 9):
                vals = str(tool.get_value(f'-ds 1(m{tariff_rate})')[1:-1])
                accumulating_end.append(vals)
            accumulating_start.remove(accumulating_start[int(rate) - 1])
            accumulating_end.remove(accumulating_end[int(rate) - 1])

            if accumulating_start != accumulating_end:
                logger.error(f'На тарифе: {rate} при накоплении энергии, энергия записывается в другие тарифы')
                logger.warning(f'test {__name__} is Failure')
            logger.info(f'Test passed in {datetime.datetime.now()}')
        logger.warning(f'test {__name__} is OK')

    except Exception as e:
        logger.warning(f'test {__name__} is Failure, {e}')
