import logging

import SMPCrossPlatform.src.wait as wait
from SMPCrossPlatform.src.smp_time import time_to_int

from src.checks.test_configuration import TestConfiguration
from src.fixtures.test_limits_power_on_schedule_fixture import options_limp

logger = logging.getLogger(__name__)


def test_limit_power_on_tariff(
        conf: TestConfiguration
) -> None:
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    logger.info("Check test_limit_power_on_tariff")

    relay_block.all_off()
    relay_block.block_on(8)
    wait.wait(wakeup)

    try:

        # Включение, авторизация
        tool.auth()

        # выключение контроля, сброс всех превышений
        for options in options_limp:
            tool.execute(''.join(options)) # загрузка всех настроек
        # первая группа
        tool.execute(' -os 46=[23:3:0:31:30:29:28:27:26:25]')
        tool.execute(' -os 47=[14:4:0:10:11:12:13:14:15:16]')
        # загрузка режима контроля лимитов мощности "выключено", тип "по назначенному тарифу"
        tool.execute("--t=20000 -a 2")  # Скопировать фоновую конфигурацию в рабочую

        # Запись времени
        tool.set_time(time_to_int("03.06.2013 23:59:58"))  # для перехода на понедельник
        wait.wait(2000)

        # чтение флага превышения лимита мощности
        status = int(tool.get_value("-i 23"))
        if status & (1 << 0) != 0:
            logger.error(f"Invalid status flag No_overLimP: {tool.get_value('-i 23')}")
            raise Exception

        # включение контроля
        # загрузка режима контроля лимитов мощности "по назначенному тарифу Т5"
        tool.execute('-os 84=[1:1:20:4:1]')
        tool.execute("--t=20000 -a 2")  # Скопировать фоновую конфигурацию в рабочую

        # контроль номера тек. дневной тарифной программы

        if int(tool.get_value('-i 8')) != 12 or int(tool.get_value('-i 9')) != 5:
            logger.error(f'info 8/9 is not matched. i 8 = {tool.get_value("-i 8")}, i9 = {tool.get_value("-i 9")}')
            raise Exception
        else:
            logger.info(f'info 8/9 match is ok: {tool.get_value("-i 8 9")}')

        # включение нагрузки, контроль отсутствия превышения лимита мощности при несовпадении тарифа
        relay_block.block_on(7)
        wait.wait(4000)

        # Pcurr = tool.get_value("-ds 14")
        # cnt_overLimP = tool.get_value("-ds 37")

        # фаза включения нагрузки
        # цикл 3 минуты
        wait.wait(60 * 3 * 1000)

        # чтение флага - отсутствие превышения лимита мощности
        status = int(tool.get_value("-i 23"))
        if status & (1 << 0) != 0:
            logger.error(f"Invalid status flag overLimP: {tool.get_value('-i 23')}")
            raise Exception

        # выключение нагрузки
        relay_block.block_off(7)

        # перевод времени к зоне действия тарифа Т5
        # tool.set_options([[1, "'3.06.2013 00:29:58'"]])	#
        tool.set_time(time_to_int("04.06.2013 00:29:58"))  # для прохода к зоне действия Т5
        wait.wait(2000)

        #  включение нагрузки
        relay_block.block_on(7)
        wait.wait(4000)

        # current_power = tool.get_value("-ds 14")
        # cnt_overLimP = tool.get_value("-ds 37")

        # фаза включения нагрузки
        for i in range(9):  # цикл 1.5 минуты
            current_power = float(tool.get_value("-ds 14"))
            if current_power < 0.020:
                logger.error("Invalid current Pmean")
                raise Exception
            wait.wait(9550)

        # фаза выключения нагрузки
        relay_block.block_off(7)
        wait.wait(4000)
        for i in range(9):  # цикл 1.5 минуты
            current_power = float(tool.get_value("-ds 14"))
            if current_power > 0.004:
                logger.error("Invalid current Pmean")
                raise Exception
            wait.wait(9550)

        # чтение флага превышения лимита мощности
        status = int(tool.get_value("-i 23"))
        if status & (1 << 0) == 0:
            logger.error(f"Invalid status flag overLimP: {tool.get_value('-i 23')}")
            raise Exception

        logger.warning(f'test {__name__} is \t OK')

    except Exception as ex:
        logger.warning(f'test {__name__} is \t Failure')

        logger.error(ex)
