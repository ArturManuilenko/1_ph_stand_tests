import logging
from typing import Union, Any

from SMPCrossPlatform.src import wait
from SMPCrossPlatform.src.smp_time import int_to_time, time_to_int

from src.checks.test_configuration import TestConfiguration
from src.fixtures.test_autocorrect_arifm_month_fixture import options_time_mode

logger = logging.getLogger(__name__)


def test_time_limits(
        conf: TestConfiguration
) -> None:
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool
    relay_block.all_off()

    logger.info('CHECK TIME LIMITS')
    relay_block.block_on(8)
    wait.wait(wakeup)

    try:
        # Включение, авторизация
        tool.auth()
        # загрузка необходимых настроек
        tool.execute("--t=20000 -a 5 -a 3")
        tool.execute('--t=20000 -a 25')
        tool.auth()

        tool.execute(options_time_mode)
        tool.execute(f"--t=20000 -a 2")  # -a 80")
        tool.set_time('31.12.2012 20:59:58')

        wait.wait(5000)
        rass: Any = 0
        for day in range(1, 10):
            tool.set_time("{:02d}.01.2012 20:59:58".format(day))
            t0: Union[str, int] = int(tool.get_value("-og 1"))
            logger.info(f"t0 = {t0}")  # test output

            wait.wait(4000)  # 2000 - мало
            logger.info("Delay 4 sec")  # test output
            tool.deauth()
            # tool.execute(f'-a 42={t0 + 8}')  # 8 секунд, чтобы на 4 было больше текущего времени
            current_time: int = int(tool.get_value("-og 1"))
            logger.info(f"t = {current_time}")  # test output

            current_time = current_time + 10
            logger.info(f"go_sync = {current_time}")  # test output
            tool.execute(f'-a 42={current_time}')
            delta: int = int(tool.get_value("-ds 44"))
            logger.info(f"delta ={delta}")  # test output

            rass = rass + delta
            logger.info(f"de-sync = {rass}")  # test output

            status: int = int(tool.get_value("-i 23"))
            logger.info(f"status ={status & (1 << 10)}")  # test output
            if status & (1 << 10) == 0 and rass > 50 or status & (1 << 10 != 0 and rass <= 50):
                logger.error("Invalid status flag with month limit")
                logger.warning(f'test {__name__} is Failure')
            logger.info(f"step-1-{day}")

        logger.info("step-1")
        tool.auth()
        # загрузка необходимых настроек
        tool.execute("--t=20000 -a 5 -a 3")
        tool.execute(options_time_mode)
        tool.execute('-os 8=[2:0:1:0]')
        wait.wait(9000)

        tool.auth()

        tool.execute(f"--t=20000 -a 2 ")  # -a 80")
        tool.set_time('31.12.2012 20:59:58')

        wait.wait(9000)
        sum_rass: int = 0
        rass = list(range(1, 13))
        for month in range(1, 13):
            tool.auth()
            nt_str: str = int_to_time(time_to_int("01.{:02d}.2013 00:00:00".format(month)) - 1)
            logger.info(f"nt_str = {nt_str}")  # test output
            wait.wait(9000)
            tool.set_time(nt_str)
            t0 = int(tool.get_value("-og 1"))
            logger.info(f"t0 = {t0}")  # test output

            tool.deauth()
            wait.wait(2000)  # было 1000
            logger.info("Delay 2 sec")  # test output

            current_time = int(tool.get_value("-og 1"))
            logger.info(f"t = {current_time}")  # test output

            current_time = current_time + 10

            logger.info(f"go_sync = {current_time}")  # test output
            tool.execute(f'-a 42={current_time}')
            delta = int(tool.get_value("-ds 44"))
            logger.info(f"delta ={delta}")  # test output
            sum_rass = sum_rass + delta
            logger.info(f"sum_rass = {sum_rass}")  # test output
            wait.wait(1000)

            rass[month - 1] = delta
            status = int(tool.get_value("-i 23"))
            logger.info(f"status = {status & (1 << 10)}")  # test output
            if status & (1 << 10 == 0 and sum_rass > 50) or (status & (1 << 10) != 0 and sum_rass <= 50):
                logger.error("Invalid status flag with month limit")
                logger.warning(f'test {__name__} is Failure')
            logger.info(f"step-2-{month}")

        logger.info("step-3")
        sum_rass = sum_rass - 10

        for month_second_func in range(1, 13):
            tool.auth()
            nt_str = int_to_time(time_to_int("01.{:02d}.2013 00:00:00".format(month_second_func)) + 10)
            logger.info(f"nt_str = {nt_str}")  # test output
            wait.wait(9000)
            tool.set_time(nt_str)
            t0 = (tool.get_value("-og 1"))
            logger.info(f"t0 = {t0}")  # test output

            tool.deauth()
            wait.wait(2000)  # было 1000
            logger.info("Delay 2 sec")  # test output

            current_time = tool.get_value("-og 1")
            tool.execute(f'-a 42={int(current_time) - 10}')
            sum_rass = sum_rass - 10
            logger.info(f"sum_rass = {sum_rass}")  # test output
            logger.info(f"t = {current_time}")  # test output
            status = int(tool.get_value("-i 23"))
            logger.info(f"status = {status & (1 << 10)}")  # test output

            if (status & (1 << 10) == 0 and sum_rass > 50) or (status & (1 << 10) != 0 and sum_rass <= 50):
                logger.error("Invalid status flag with month limit")
                logger.warning(f'test {__name__} is Failure')
            logger.info(f"step-3-{month_second_func}")

        logger.info("step-3")
        logger.warning(f'test {__name__} is OK')

    except Exception as ex:
        logger.warning(f'test {__name__} is Failure')

        logger.error('', ex)
