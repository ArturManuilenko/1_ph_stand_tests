import logging

import SMPCrossPlatform.src.wait as wait

from src.checks.test_configuration import TestConfiguration
from src.fixtures.test_event_schedule_tariff_fixture import options_tariff_both

logger = logging.getLogger(__name__)


def test_event_schedule_tariff(
    conf: TestConfiguration
) -> None:
    '''
    Тест проверяет приоритет тарификации по расписанию и по событию.
    '''
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    logger.info('start external and schedule tariff')
    logger.warning(f'test {__name__} is Started')
    relay_block.all_off()
    relay_block.block_on(8)
    wait.wait(wakeup)

    def info_compare(compare_list: str) -> None:
        infolist: list = []
        compare_list_format = list(compare_list.split(" "))

        for info_get in range(7, 11):
            infolist.append(tool.get_value(f"-i {info_get}"))

        if infolist == compare_list_format:
            logger.info(f'list compare -i 7 8 9 10 == {infolist} is Ok')
        else:
            logger.error(f'list compare list compare -i 7 8 9 10: expected [{compare_list}] '
                         f'!= actual {infolist} is not match')
            logger.warning(f'test {__name__} is Failure')

    try:
        tool.auth()
        # set nessesary settings
        tool.execute('-a 5 -a 3')

        for option in options_tariff_both:
            tool.execute(''.join(option))
            logger.info(f'Установка настроек: {option}')
        tool.execute('--t=20000 -a 2')

        # check schedule tarification
        logger.info('Установка времени 31.12.2022 23:59:59, ожидание перехода на тарификацию по расписанию')
        tool.set_time('31.12.2022 23:59:59')
        wait.wait(3000)
        info_compare('1 1 1 1')
        # initiate event
        logger.info('Включение нагрузки для инициализации события')
        relay_block.block_on(7)
        wait.wait(60000)
        # check switch tarif to 8
        info_compare('8 0 0 0')
        # turn off event
        logger.info('Отключение нагрузки и ожидание возврата на тарификацию по расписанию')
        relay_block.block_off(7)
        wait.wait(120000)
        # check schedule tarification
        info_compare('1 1 1 1')

        logger.warning(f'test {__name__} is OK')

    except Exception as ex:
        logger.warning(f'test {__name__} is Failure')

        logger.error('', ex)
