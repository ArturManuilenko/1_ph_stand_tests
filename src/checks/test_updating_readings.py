import logging
from datetime import datetime

from SMPCrossPlatform.src import wait

from src.checks.test_configuration import TestConfiguration

logger = logging.getLogger(__name__)


def test_updating_readings(
    conf: TestConfiguration
) -> None:
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    logger.info('Test updating readings from counter')
    relay_block.all_off()
    relay_block.block_on(8)
    wait.wait(wakeup)

    try:
        for checks in range(15):
            start_time: int = int(datetime.utcnow().timestamp())
            print(start_time)
            relay_block.block_on(7)
            while float(tool.get_value('-ds 14')) == 0:
                ...
            end_time: int = int(datetime.utcnow().timestamp())
            if end_time - start_time > 3:
                logger.error(f'Счетчик увидел нагрузку больше, чем за 3 секунды, время составило: '
                             f'{end_time - start_time}')
                logger.warning(f'test {__name__} is Failure')

            relay_block.block_off(7)
            wait.wait(10000)

        logger.warning(f'test {__name__} is OK')

    except Exception as ex:
        logger.warning(f'test {__name__} is Failure')

        logger.error('', ex)

