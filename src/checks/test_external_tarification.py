import logging

from SMPCrossPlatform.src import wait

from src.checks.test_configuration import TestConfiguration

from src.fixtures.test_external_tarification_fixure import options_ex_shed_tarif

logger = logging.getLogger(__name__)


def test_external_tarification(
        conf: TestConfiguration
) -> None:
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    relay_block.all_off()
    relay_block.block_on(8)
    wait.wait(wakeup)
    logger.info('start checking external tariff')

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
        relay_block.block_on(8)
        # Включение, авторизация
        tool.auth()
        # загрузка необходимых настроек
        tool.execute("--t=20000 -a 5 -a 3")
        for options_set in options_ex_shed_tarif:
            tool.execute(''.join(options_set))
        tool.execute("--t=20000 -a 2")
        tool.set_time('31.12.2022 23:59:58')
        wait.wait(5000)
        # проверка тариф график недельная программа группа
        # "Check off all tarif parameters"
        for tariff in (1, 3, 6, 2, 8, 7):
            tool.execute(f"--t=20000 -a 9={tariff}")
            info_compare(f'{tariff} 0 0 0')

            # Запись накоплений в тариф, с проверкой накопления
            start_tarif_energy = float(tool.get_value(f'-ds 1(m{tariff})')[1:-1])
            relay_block.block_on(7)
            wait.wait(15000)
            relay_block.block_off(7)
            if float(tool.get_value(f'-ds 1(m{tariff})')[1:-1]) - start_tarif_energy == 0:
                logger.error(f'Energy did not increased in {tariff} tariff')
                logger.warning(f'test {__name__} is Failure')
            else:
                logger.info(f'Energy increased in {tariff} tariff')
        tool.execute(f"--t=5000 -a 9=0")
        info_compare(f'1 1 1 1')

        logger.warning(f'test {__name__} is OK')

    except Exception as ex:
        logger.warning(f'test {__name__} is Failure')

        logger.error('', ex)
