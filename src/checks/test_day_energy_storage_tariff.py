import logging
import random
from datetime import date, datetime
from typing import List

from SMPCrossPlatform.src import wait
from SMPCrossPlatform.src.smp_exception import SMPException
from dateutil.relativedelta import relativedelta

from src.checks.test_configuration import TestConfiguration

logger = logging.getLogger(__name__)


def test_day_energy_storage_tariff(
    conf: TestConfiguration
) -> None:
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    logger.info('Test day energy tariff storage ')
    relay_block.all_off()
    relay_block.block_on(8)
    wait.wait(wakeup)

    try:
        logger.info("Авторизация, сброс еепром")
        tool.auth()
        tool.execute('-a 25')
        wait.wait(10000)
        logger.info("Установка 2013 года")
        tool.set_time('01.01.2013 00:00:00')
        wait.wait(9000)
        tool.execute('-os 10=[0:1:0:0:1:0] -a 2 --t=2000')
        logger.info("Установка внешней тарификации")
        wait.wait(5000)
        start_energy: List[str] = tool.get_value('-dm 5[0..10]')
        if start_energy != ['0'] * 11:
            logger.error(
                f'Полученные значения со счётчика о накоплениях за день должны быть 0, так как время было переведено '
                f'назад, значения: {tool.get_value("-dm 5[0..10]")}'
            )
            logger.warning(f'test {__name__} is Failure')
        for days in range(0, 128):
            random_tariff = random.randint(1, 7)
            tool.execute(f'-a 9={random_tariff}')
            logger.info(f'Установлен тариф {random_tariff}')
            calculated_date = ((datetime(2013, 1, 1, 00, 00, 00)) +
                               relativedelta(days=days + 1)).strftime("%d.%m.%Y %H:%M:%S")
            logger.info(f'Установка даты: {calculated_date}')
            tool.set_time(calculated_date)
            relay_block.block_on(7)
            logger.info('Ожидание 10 секунд для достаточного накопления')
            wait.wait(15000)
            if float(tool.get_value(f'-dm 5[0..0](m{random_tariff})')) == 0:
                logger.error(f'Счётчик не накопил дневную энергию на дате: {tool.get_current_time()}')
                logger.warning(f'test {__name__} is Failure')

        for tariff_list in range(1, 8):
            last_energy = tool.get_value(f'-dm 5[0..1](m{tariff_list})')

            logger.info("Поиск нулевых накоплений в ежедневных накоплениях")
            if ['0'] in last_energy:
                logger.error(
                    f'Счётчик неверно записал накопленные значения. Cписок с устройства: {tool.get_value(f"-dm 5[0..1](m{tariff_list})")}'
                )
                logger.warning(f'test {__name__} is Failure')

        for continue_days in range(128, 150):
            calculated_date = ((datetime(2013, 1, 1, 00, 00, 00)) +
                               relativedelta(days=continue_days + 1)).strftime("%d.%m.%Y %H:%M:%S")
            logger.info(f'Установка даты: {calculated_date}')
            tool.set_time(calculated_date)
            wait.wait(10000)
            if float(tool.get_value(f'-dm 5[{continue_days}..{continue_days}]')) != 0:
                logger.error(
                    f'Счётчик неверно записал накопленные значения. Cписок с устройства: '
                    f'{tool.get_value(f"-dm 5[{continue_days}..{continue_days}]")} должно быть 0'
                )
                logger.warning(f'test {__name__} is Failure')
            logger.warning(f'test {__name__} is OK')

    except Exception as ex:
        logger.warning(f'test {__name__} is Failure')

        logger.error('', ex)
