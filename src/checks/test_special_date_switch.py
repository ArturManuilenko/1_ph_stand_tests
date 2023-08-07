import logging
from typing import List

import SMPCrossPlatform.src.wait as wait
from SMPCrossPlatform.src.smp_time import time_to_int

from src.checks.test_configuration import TestConfiguration
from src.fixtures.test_special_date_switch_fixture import irreg_date
from src.fixtures.test_special_date_switch_fixture import options_sp_date
from src.fixtures.test_special_date_switch_fixture import reg_date

logger = logging.getLogger(__name__)


def test_special_date_switch(
    conf: TestConfiguration
) -> None:
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    logger.info("CHECK SPECIAL DATE TARIF")
    relay_block.all_off()
    relay_block.block_on(8)
    wait.wait(wakeup)

    def info_compare(compare_list: str) -> None:
        infolist: List = []
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
        # Сброс к заводским настройкам
        tool.execute("-a 5 -a 3")
        # загрузка необходимых настроек
        for options_set in options_sp_date:
            tool.execute(''.join(options_set))

        tool.execute("--t=20000 -a 2")
        # активация 0 группы сменой года
        tool.set_time('31.12.2022 23:59:55')
        wait.wait(10000)
        # Плавающие (не регулярные) особые даты
        for dt in irreg_date:
            start_time = time_to_int("{:02d}.{:02d}.{} 00:00:00".format(dt[0], dt[1], dt[2]))
            tool.set_time(start_time - 5)
            wait.wait(10000)
            # проверка тариф график недельная программа группа
            info_compare(f'2 {dt[3] + 1} 1 1')
            logger.debug(f'Check switch on {dt[0], dt[1], dt[2]}')

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

            # проверка при выходе из дня
            tool.set_time(start_time + 24 * 3600 - 5)
            wait.wait(10000)
            info_compare('1 1 1 1')
            logger.debug(f'Check switch on {dt[0], dt[1], dt[2]}')

        # Регулярные особые даты
        for dt in reg_date:
            start_time = time_to_int("{:02d}.{:02d}.2022 00:00:00".format(dt[0], dt[1]))
            tool.set_time(start_time - 5)
            wait.wait(10000)
            # проверка тариф график недельная программа группа
            info_compare(f'2 {dt[2] + 1} 1 1')
            logger.debug(f'Check switch on {dt[0], dt[1]}')

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

            # проверка при выходе из дня
            tool.set_time(start_time + 24 * 3600 - 5)
            wait.wait(10000)
            info_compare(f'1 1 1 1')
            logger.info(f'Check switch on {dt[0], dt[1]}')

        logger.warning(f'test {__name__} is OK')

    except Exception as ex:
        logger.warning(f'test {__name__} is Failure')

        logger.error('', ex)
