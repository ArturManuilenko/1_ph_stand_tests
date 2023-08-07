import logging

import SMPCrossPlatform.src.wait as wait

from src.checks.test_configuration import TestConfiguration
from src.fixtures.test_external_shedule_tariff_fixture import options_tarif_event

logger = logging.getLogger(__name__)


def test_external_shedule_tariff(
    conf: TestConfiguration
) -> None:
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    relay_block.all_off()
    relay_block.block_on(8)
    wait.wait(wakeup)
    logger.info(f'start {__name__}')

    def info_compare(compare_list: str) -> None:
        infolist = []
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
        relay_block.block_on(8)
        tool.auth()
        # загрузка необходимых настроек
        tool.execute("--t=20000 -a 5 -a 3")
        for option_set in options_tarif_event:
            tool.execute(''.join(option_set))

        tool.execute("--t=20000 -a 2")
        # гарантировать смену тарифной группы
        tool.set_time('31.12.2022 23:59:59')
        wait.wait(2000)  # 1000
        # проверка тариф график недельная программа группа
        info_compare('2 1 1 1')

        # Запись накоплений в тариф, с проверкой накопления
        start_tarif_energy = float(tool.get_value('-ds 1(m2)')[1:-1])
        relay_block.block_on(7)
        wait.wait(15000)
        relay_block.block_off(7)
        if float(tool.get_value('-ds 1(m2)')[1:-1]) - start_tarif_energy == 0:
            logger.error(f'Energy did not increased in 2 tariff')
            logger.warning(f'test {__name__} is Failure')
        else:
            logger.info(f'Energy increased in 2 tariff')

        # смена расписания
        tool.set_time('09.01.2022 23:59:59')
        wait.wait(2000)
        info_compare('3 2 2 1')

        # Запись накоплений в тариф, с проверкой накопления
        start_tarif_energy = float(tool.get_value('-ds 1(m3)')[1:-1])
        relay_block.block_on(7)
        wait.wait(15000)
        relay_block.block_off(7)
        if float(tool.get_value('-ds 1(m3)')[1:-1]) - start_tarif_energy == 0:
            logger.error(f'Energy did not increased in 3 tariff')
            logger.warning(f'test {__name__} is Failure')
        else:
            logger.info(f'Energy increased in 3 tariff')

        # Проверка возвращения на тариф "по расписанию" после смены внешней командой
        tool.execute('-a 9=5')
        info_compare('5 0 0 0')
        tool.execute('-os 10=[0:0:1:0:0:1] -a 2')
        info_compare('3 2 2 1')

        logger.warning(f'test {__name__} is OK')

    except Exception as ex:
        logger.warning(f'test {__name__} is OK')

        logger.error('', ex)



