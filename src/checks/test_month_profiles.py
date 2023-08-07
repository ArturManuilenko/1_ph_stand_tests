import logging
from typing import List

from SMPCrossPlatform.smptool2 import SMPException
from SMPCrossPlatform.src import wait
from SMPCrossPlatform.src.smp_time import time_to_int

from src.checks.test_configuration import TestConfiguration


logger = logging.getLogger(__name__)


def test_month_profiles(
    conf: TestConfiguration
) -> None:
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    logger.info("CHECK MONTH PROFILE")
    relay_block.all_off()
    relay_block.block_on(8)
    wait.wait(wakeup)

    try:
        tool.auth()
        tool.execute("--t=40000 -a 5 -a 3")  # -a 25
        start_sum = float(tool.get_value("-ds 1(0)"))
        day_beg: List[float] = []

        for step in range(1, 13):
            tool.auth()
            logger.info(f"Step-{step}")
            wait.wait(9000)
            tool.set_time(time_to_int('01.{:02d}.2015 00:00:00'.format(step)) - 5)

            if step % 5 == 0:
                relay_block.block_off(8)
                wait.wait(10000)
                relay_block.block_on(8)
                wait.wait(wakeup)
            else:
                wait.wait(10000)

            # сохранить накопление энергии на начало дня
            day_beg.insert(0, tool.get_value("--t=1000 --r=100 -ds 1(0)"))
            relay_block.block_on(8)
            relay_block.block_on(7)
            wait.wait(10000 * step)
            relay_block.block_off(7)

            if step % 3 == 0:
                relay_block.block_off(8)
                wait.wait(10000)
                relay_block.block_on(8)
                wait.wait(wakeup)

            summary = float(tool.get_value("--t=1000 --r=100 -ds 1(0)")) - start_sum

            sut = tool.get_value("-dm 9[0..50](0)")

            rash = tool.get_value("-dm 13[0..50](0)")
            s = float(0)
            for current in range(step):
                s += float(rash[current])
                if abs(float(sut[current]) - float(
                        day_beg[current])) > 0.0011:
                    logger.error(
                        f"Error energy on month begin, {step} iteration {sut[current]} {day_beg[current]}")
                    logger.warning(f'test {__name__} is Failure')
            if abs(float(s) - float(summary)) > 0.00012:
                logger.error(f"Критическое расхождение сумм на итерации-{step}: {s} {summary} ")
                logger.warning(f'test {__name__} is Failure')

            logger.info("Step-{}".format(step))
        logger.warning(f'test {__name__} is OK')

    except Exception as ex:
        logger.warning(f'test {__name__} is Failure')

        logger.error('', ex)
