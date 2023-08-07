import logging

import SMPCrossPlatform.src.wait as wait
from SMPCrossPlatform.smptool2 import SMPException

from src.checks.test_configuration import TestConfiguration

logger = logging.getLogger(__name__)


def almost_equals(a: float, b: float, epsilon: float = 0.00012) -> float:
    return abs(a - b) <= epsilon


def test_time_correction_wo_command(
    conf: TestConfiguration
) -> None:
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    logger.info('CHECK PROFILE TIME CORRECTION')
    relay_block.all_off()
    relay_block.block_on(8)
    wait.wait(wakeup)
    try:
        tool.auth()
        tool.execute("--t=40000 -a 5 -a 3")  # -a 25
        logger.debug('Sending commands -a 5, -a 3')

        tool.set_time("31.12.2012 23:59:55")
        wait.wait(10000)

        accumulation_start = tool.get_value("-ds 1(0)")

        relay_block.block_on(7)
        wait.wait(20000)
        relay_block.block_off(7)
        accumulation_end = tool.get_value("-ds 1(0)")

        tool.set_time("01.01.2013 23:59:55")
        wait.wait(9000)

        tool.set_time("05.01.2013 00:30:00")
        sut1 = tool.get_value("-dm 1[0..10](0)")
        on_sut1 = tool.get_value("-dm 5[0..10](0)")

        for day_interval in range(0, 4):
            if not almost_equals(float(sut1[day_interval]), float(accumulation_end)) \
                or float(on_sut1[day_interval]) != 0:
                logger.error(
                    f"Wrong time forward day interval value:{sut1[day_interval]}!={accumulation_end}")
                logger.warning(f'test {__name__} is Failure')

        if float(sut1[4]) != float(accumulation_start):
            logger.error("Wrong time forward day interval last value")
            logger.warning(f'test {__name__} is Failure')

        tool.set_time("01.05.2013 00:30:00")
        mon1 = tool.get_value("--t=40000 -dm 9[0..10](0)")
        on_mon1 = tool.get_value("--t=40000 -dm 13[0..10](0)")

        for time_forward in range(0, 4):
            if abs(float(sut1[time_forward]) - float(accumulation_end)) > 0.002 or float(on_mon1[time_forward]) != 0:
                logger.error("Wrong time forward month interval value")
                logger.warning(f'test {__name__} is Failure')

        if not almost_equals(float(mon1[4]), float(accumulation_start)):
            logger.error(
                f"Wrong time forward month interval last value {mon1[4]} {accumulation_start}")
            logger.warning(f'test {__name__} is Failure')
        wait.wait(9000)
        tool.set_time("01.01.2017 00:30:00")
        year1 = tool.get_value("-dm 17[0..10](0)")
        on_year1 = tool.get_value("-dm 21[0..10](0)")

        for time_forward_year in range(0, 4):
            if not almost_equals(float(year1[time_forward_year]), float(accumulation_end)) \
                or float(on_year1[time_forward_year]) != 0:
                logger.error(f"Wrong time forward day interval value {year1[time_forward_year]}!={accumulation_end}")
                logger.warning(f'test {__name__} is Failure')

        if float(year1[4]) != float(accumulation_start):
            logger.error("Wrong time forward day interval last value")
            logger.warning(f'test {__name__} is Failure')
        relay_block.block_on(7)
        wait.wait(20000)
        relay_block.block_off(7)

        end1: float = float(tool.get_value("-ds 1(0)"))

        tool.set_time("31.12.2013 23:59:55")
        wait.wait(10000)
        year2 = tool.get_value("-dm 17[0..10](0)")
        mon2 = tool.get_value("-dm 9[0..10](0)")
        sut2 = tool.get_value("-dm 1[0..10](0)")
        if not any((almost_equals(float(sut2[0]), end1), almost_equals(float(mon2[0]), float(end1)),
                    almost_equals(float(year2[0]), float(end1)))):
            logger.error(f"Wrong last interval after time back "
                         f"Y {year2[0]}!={end1}, "
                         f"M {mon2[0]}!={end1}, "
                         f"D {sut2[0]}!={end1}")
            logger.warning(f'test {__name__} is Failure')

        logger.warning(f'test {__name__} is OK')

    except Exception as ex:
        logger.warning(f'test {__name__} is Failure')

        logger.error('', ex)
