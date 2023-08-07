import logging

import SMPCrossPlatform.src.wait as wait
from SMPCrossPlatform.src.smp_time import time_to_int

from src.checks.test_configuration import TestConfiguration

from src.fixtures.test_week_tariff_switch_fixture import w_prog, w_day_prog, options_week

logger = logging.getLogger(__name__)


def test_week_tariff(
        conf: TestConfiguration
) -> None:
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    logger.info('CHECK WEEK TARIF PROGRAMS')

    relay_block.all_off()
    relay_block.block_on(8)
    wait.wait(wakeup)

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
        tool.auth()
        # загрузка необходимых настроек
        for options_set in options_week:
            tool.execute(''.join(options_set))

        tool.execute("--t=20000 -a 2")
        tool.set_time('31.12.2012 23:59:45')
        wait.wait(20000)
        # переход через смену сезонных расписаний
        if tool.get_value('-i 10') == '1':
            pass
        else:
            logger.error('info 10 is not match')

        for num, week_program in enumerate(w_prog):
            start_time = time_to_int(f"{week_program[0]:02d}.{week_program[1]:02d}.2013 00:00:00") - 10
            for day in range(7):
                tool.set_time(start_time + day * 24 * 60 * 60)
                wait.wait(15000)
                tar = w_day_prog[week_program[2][day]] + 1
                day = week_program[2][day] + 1
                info_compare(f"{tar} {day} {num + 1} 1")
                logger.debug(f"Check week {week_program}, day {day}")

        logger.warning(f'test {__name__} is OK')

    except Exception as ex:
        logger.warning(f'test {__name__} is Failure')

        logger.error('', ex)
