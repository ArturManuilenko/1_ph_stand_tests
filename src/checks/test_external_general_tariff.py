import logging

import SMPCrossPlatform.src.wait as wait

from src.checks.test_configuration import TestConfiguration
from src.fixtures.test_external_general_tariff_fixture import options_tariff_both

logger = logging.getLogger(__name__)


def test_external_general_tariff(
        conf: TestConfiguration
) -> None:
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    relay_block.all_off()
    logger.info('test_tarif_event_external')
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
        # Включение, авторизация
        tool.auth()
        # загрузка необходимых настроек
        tool.execute("--t=20000 -a 5 -a 3")
        logger.info("установить заводские настройки -->> OK")
        for step in options_tariff_both:
            tool.execute(''.join(step))

        logger.info("установка настроек -->> OK")
        tool.execute("--t=20000 -a 2")
        logger.info("скопировать фоновую конфигурацию в рабочую -->> OK")

        # Проверка отсутствия тарификации
        info_compare('0 0 0 0')
        # Инициация события и проверка перехода на тариф по событию
        relay_block.block_on(7)
        wait.wait(61000)
        info_compare('7 0 0 0')

        # Проверка возврата на прошлый тариф по окончанию события
        relay_block.block_off(7)
        wait.wait(121000)
        info_compare('0 0 0 0')

        # Проверка отсутствия перехода на другой тариф при отключенном режиме тарификации "по событиям"
        tool.auth()
        tool.execute('-os 152=[0:0:0:0:0:0:6]')
        tool.execute('-os 10=[0:0:0:0:0:0]')
        tool.execute('-a 2')
        relay_block.block_on(7)
        wait.wait(61000)
        info_compare('0 0 0 0')
        relay_block.block_off(7)

        logger.warning(f'test {__name__} is OK')

    except Exception as ex:
        logger.warning(f'test {__name__} is Failure')

        logger.error('', ex)
