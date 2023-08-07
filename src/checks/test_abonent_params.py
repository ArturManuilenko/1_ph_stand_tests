import logging

import SMPCrossPlatform.src.wait as wait

from src.checks.test_configuration import TestConfiguration
from src.fixtures.test_abonent_params_fixture import abonent_addr_options, abonent_number, \
    message_for_abonent, tariff_plan

logger = logging.getLogger(__name__)


def test_abonent_params(
    conf: TestConfiguration
) -> None:

    """
    Тест проверяет реализацию возможности задавать данные абонента:
        - абонентский номер (8 байт),
        - тарифный план (1-ый символ буква: A, B, C или D; 2-ой, 3-ий, 4-ый символы – цифры от 0 до 9),
        - адреса абонента (128 символов),
        - сообщение для абонента (128 символов)
    """

    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    # Проверка позитивных сценариев
    def check_positive_cases(os_command: int, set_options: str) -> None:
        logger.info(f'Установка параметров абонента: -os {os_command}={set_options}')
        tool.execute(f'-os {os_command}={set_options} -a 2')

        if tool.get_value(f'-og {os_command}') == set_options:
            logger.info(f'Команда -os {os_command}={set_options} выполнена успешно!')
        else:
            logger.error(f'Команда -og {os_command} не соответствует ожидаемому результату!')
            logger.error(f'{tool.get_value(f"-og {os_command}")}')
            logger.warning(f'test {__name__} is Failure')


    try:
        logger.info('start set abonent params')
        logger.warning(f'test {__name__} is Started')
        relay_block.all_off()
        relay_block.block_on(8)
        wait.wait(wakeup)

        tool.auth()
        logger.info('Сброс настроек к заводским, очистка EEPROM')
        tool.execute('--t=30000 -a 5 -a 3')
        tool.execute('--t=30000 -a 25')

        # Установка и проверка Адреса абонента
        for set_options in abonent_addr_options:
            check_positive_cases(os_command=176, set_options=set_options)
            wait.wait(1000)

        # Установка и проверка Номера абонента
        for set_options in abonent_number:
            check_positive_cases(os_command=177, set_options=set_options)
            wait.wait(1000)

        # Установка и проверка Сообщения для абонента
        for set_options in message_for_abonent:
            check_positive_cases(os_command=178, set_options=set_options)
            wait.wait(1000)

        # Установка и проверка Названия тарифного плана
        for set_options in tariff_plan:
            check_positive_cases(os_command=179, set_options=set_options)
            wait.wait(1000)


        logger.warning(f'test {__name__} is OK')

    except Exception as ex:
        logger.warning(f'test {__name__} is Failure')

        logger.error('', ex)
