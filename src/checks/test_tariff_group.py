import logging

import SMPCrossPlatform.src.wait as wait

from src.checks.test_configuration import TestConfiguration
from src.fixtures.test_tariff_group_fixture import options_tariff_to_second_group, options_tariff_to_first_group

logger = logging.getLogger(__name__)


def test_tariff_group(
        conf: TestConfiguration
) -> None:
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    logger.info('start change group tariff')
    relay_block.all_off()
    relay_block.block_on(8)
    wait.wait(wakeup)

    def info_compare(compare_list: str) -> None:
        infolist: list = []
        compare_list_format: list = list(compare_list.split(" "))

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
        for option in options_tariff_to_second_group:
            tool.execute(''.join(option))

        tool.execute("--t=20000 -a 2")
        # гарантировать смену тарифной группы
        logger.info(f'Усатновка времени: 31.12.2022 23:59:59')
        tool.set_time('31.12.2022 23:59:59')
        wait.wait(2000)  # было 1000
        # проверка тариф график недельная программа группа
        info_compare('1 1 1 1')

        wait.wait(9000)
        logger.info(f'Усатновка времени 29.10.2023 23:59:59 и ожидание перехода на 2 группу')
        tool.set_time('29.10.2023 23:59:59')
        wait.wait(2000)
        info_compare('2 2 13 2')

        # проверка перехода на 1 группу сезонных расписаний
        tool.execute(options_tariff_to_first_group[0])
        logger.info(f'Усатновка времени: 31.12.2024 23:59:59 и ожидание перехода на 1 группу')
        tool.set_time('31.12.2024 23:59:59')
        wait.wait(2000)
        info_compare('1 1 1 1')


        logger.warning(f'test {__name__} is OK')

    except Exception as ex:
        logger.warning(f'test {__name__} is Failure')

        logger.error('', ex)
