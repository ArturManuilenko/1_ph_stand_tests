import logging

import SMPCrossPlatform.src.wait as wait
from SMPCrossPlatform.src.smp_time import time_to_int, int_to_time

from src.checks.test_configuration import TestConfiguration

from src.fixtures.test_power_limit_schedule_fixture import set_option_power_zone, options_power_limit_list, \
    options_setLimP_off, options_setLimP_on_all, options_setLimP_on_tarif, options_setLimP_on_zone, datechk

logger = logging.getLogger(__name__)


def test_power_limit_schedule(
        conf: TestConfiguration
) -> None:
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    logger.info("Check limit schedule power")

    relay_block.all_off()
    relay_block.block_on(8)
    wait.wait(wakeup)

    try:
        # Включение, авторизация
        tool.auth()

        # загрузка необходимых настроек
        for options in set_option_power_zone:  # формирование массива зон контроля
            logger.debug(f'send commands: {options}')
            tool.execute(options)

        for options in options_power_limit_list:
            logger.debug(f'send commands: {options}')
            tool.execute(options)

        # режим "контроль выключен"
        for options in options_setLimP_off:
            logger.debug(f'send commands: {options}')
            tool.execute(options)

        tool.execute("--t=20000 -a 2")  # Скопировать фоновую конфигурацию в рабочую

        if not tool.get_value('-i 35') == '0':
            logger.error('info 35 is not match')
            logger.error(f'Info 35 needed to be 0, current value: {tool.get_value("-i 35")}')
            logger.warning(f'test {__name__} is Failure')
        # режим «Контроль включен» , режим контроля «всегда»
        for options in options_setLimP_on_all:
            logger.debug(f'send commands: {options}')
            tool.execute(options)

        tool.execute("--t=20000 -a 2")  # Скопировать фоновую конфигурацию в рабочую
        if not tool.get_value('-i 35') == '0':
            logger.error('info 35 is not match')
            logger.error(f'Info 35 needed to be 0, current value: {tool.get_value("-i 35")}')
            logger.warning(f'test {__name__} is Failure')
        # режим контроля «по назначенному тарифу»
        for options in options_setLimP_on_tarif:
            logger.debug(f'send commands: {options}')
            tool.execute(options)

        tool.execute("--t=20000 -a 2")  # Скопировать фоновую конфигурацию в рабочую
        if tool.get_value('-i 35') == '0':
            pass
        else:
            logger.error('info 35 is not match')
            logger.error(f'Info 35 needed to be 0, current value: {tool.get_value("-i 35")}')
            logger.warning(f'test {__name__} is Failure')
        # режим контроля «по расписанию зон контроля»

        for options in options_setLimP_on_zone:
            logger.debug(f'send commands: {options}')
            tool.execute(options)

        tool.execute("--t=20000 -a 2")  # Скопировать фоновую конфигурацию в рабочую

        for num, schedule_day in enumerate(datechk):
            wait.wait(9000)
            tool.set_time(time_to_int(f"{schedule_day[0]}.{schedule_day[1]}.2013 00:00:15"))
            wait.wait(2000)
            if tool.get_value('-i 35') != f'{num + 1}':
                logger.info(f'Info matched for {int_to_time(int(tool.get_value("-og 1")))}')
            else:
                logger.error(f'Info 35 needed to be 0, current value: {tool.get_value("-i 35")}')
                logger.warning(f'test {__name__} is Failure')

        logger.info('test_power_limits_schedule')
        logger.warning(f'test {__name__} is OK')

    except Exception as ex:
        logger.warning(f'test {__name__} is Failure')

        logger.error('test_power_limits_schedule: ', ex)
