import logging

import SMPCrossPlatform.smptool2
from SMPCrossPlatform.src import smp_time
from SMPCrossPlatform.src.wait import wait

from src.checks.test_configuration import TestConfiguration

from src.fixtures.test_tariff_A_A_plus_fixture import Prepare_smp_command

logger = logging.getLogger(__name__)


def test_tariff_a_a_plus(
        conf: TestConfiguration
) -> None:
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    logger.info("CHECK SPECIAL DATE TARIF")
    relay_block.all_off()
    relay_block.block_on(8)
    wait(wakeup)

    try:
        logger.info('CHECK TARIF CONSUMPTED & GENERATED')
        # Включение, авторизация
        tool.auth()
        # загрузка необходимых настроек
        tool.execute("--t=20000 -a 5 -a 3")
        for set_option in Prepare_smp_command:
            tool.execute(''.join(set_option))

        tool.execute("--t=20000 -a 2")

        change_date = smp_time.time_to_int('31.12.2020 23:59:58')
        tool.set_time("31.12.2020 23:59:58")
        SMPCrossPlatform.src.wait.wait(10000)
        # естественный переход
        for times in range(1, 20):
            infolist_ten = []
            infolist_four = []
            tool.set_time(change_date + times * 24 * 3600)
            SMPCrossPlatform.src.wait.wait(5000)
            for get_option in range(7, 11):
                infolist_ten.append(tool.get_value(f"-i {get_option}"))

            for get_option in range(38, 42):
                infolist_four.append(tool.get_value(f"-i {get_option}"))

            if infolist_ten.sort() == infolist_four.sort():
                logger.info(f'Ok for {times} iteration')
            else:
                logger.error(f'{infolist_ten} is not match {infolist_four}, test filed on {times} iteration')
                logger.warning(f'test {__name__} is Failure')

        # перевод часов
        for times in range(20, 40):
            infolist_ten = []
            infolist_four = []
            tool.set_time(change_date + 2 + times * 24 * 3600)
            SMPCrossPlatform.src.wait.wait(5000)
            for get_option in range(7, 11):
                infolist_ten.append(tool.get_value(f"-i {get_option}"))

            for get_option in range(38, 42):
                infolist_four.append(tool.get_value(f"-i {get_option}"))

            if infolist_ten.sort() == infolist_four.sort():
                logger.info(f'Ok for {times}')
            else:
                logger.error(f'{infolist_ten} is not match {infolist_four}, test filed on {times} iteration')
                logger.warning(f'test {__name__} is Failure')
        logger.warning(f'test {__name__} is OK')

    except Exception as ex:
        logger.warning(f'test {__name__} is Failure')

        logger.error('', ex)
