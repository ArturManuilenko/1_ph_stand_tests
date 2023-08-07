import logging

import SMPCrossPlatform.src.wait as wait

from src.checks.test_configuration import TestConfiguration
from src.fixtures.test_event_general_tariff_fixture import options_tariff_both

logger = logging.getLogger(__name__)


def test_event_general_tariff(
    conf: TestConfiguration
) -> None:
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    logger.info('start external and general tariff')
    relay_block.all_off()
    relay_block.block_on(8)
    wait.wait(wakeup)

    def info_compare(compare_list: str) -> None:
        infolist: list = []
        compare_list_format = list(compare_list.split(" "))

        for info_get in range(7, 11):
            infolist.append(tool.get_value(f"-i {info_get}"))

        if infolist == compare_list_format:
            logger.info('list compare is Ok')
        else:
            logger.error('list compare is not match')
            logger.warning(f'test {__name__} is Failure')

    try:
        relay_block.block_on(8)
        # Включение, авторизация
        tool.auth()
        # загрузка необходимых настроек
        tool.execute("--t=20000 -a 5 -a 3")
        for option_set in options_tariff_both:
            tool.execute(''.join(option_set))

        tool.execute("--t=20000 -a 2")
        # проверка отсутствия тарификации
        info_compare('0 0 0 0')
        relay_block.block_on(7)
        wait.wait(120000)
        # проверка установки тарифа по событию
        info_compare('8 0 0 0')
        relay_block.block_off(7)
        wait.wait(120000)
        tool.auth()

        # проверка отсутствия тарификации
        info_compare('0 0 0 0')
        # установить тарификацию по событиям и внешней
        tool.execute('-os 10=[1:1:0:0:0:0]')
        tool.execute("--t=20000 -a 2")
        # проверка тарификации внешней командой
        tool.execute('-a 9=4')
        info_compare('4 0 0 0')


        relay_block.block_on(7)
        wait.wait(120000)
        # проверка установки тарифа по событию
        info_compare('8 0 0 0')

        relay_block.block_off(7)
        wait.wait(120000)

        # проверка возврата к тарифу установленному по команде
        info_compare('4 0 0 0')

        relay_block.block_off(7)

        logger.warning(f'test {__name__} is OK')

    except Exception as ex:
        logger.warning(f'test {__name__} is Failure')

        logger.error('', ex)
