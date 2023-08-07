import logging
from typing import List

from SMPCrossPlatform.smptool2 import SMPException
from SMPCrossPlatform.src import wait

from src.checks.test_configuration import TestConfiguration

logger = logging.getLogger(__name__)


def test_accumulation_day_energy(
    conf: TestConfiguration
) -> None:
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    logger.warning('Test accumulation day energy')
    relay_block.all_off()
    relay_block.block_on(8)
    wait.wait(wakeup)
    try:

        tool.auth()
        tool.execute("--t=40000 -a 5 -a 3")  # -a 25
        wait.wait(wakeup)
        start_time: int = 31708790
        start_sum: float = float(tool.get_value("-ds 1(0)"))
        day_beg: List[float] = []
        for step in range(1, 20):

            step_time = start_time + 24 * 3600 * step
            logger.info(f"Step-{step}")
            tool.set_time(step_time)

            if step % 5 == 0:
                relay_block.block_off(8)
                wait.wait(10000)
                relay_block.block_on(8)
                wait.wait(wakeup)
            else:
                wait.wait(10000)

            # сохранить накопление энергии на начало дня

            day_beg.insert(0, float(tool.get_value("-ds 1(0)")))
            relay_block.block_on(7)
            wait.wait(10000 * step)
            relay_block.block_off(7)

            if step % 3 == 0:
                relay_block.all_off()
                wait.wait(10000)
                relay_block.block_on(8)
                wait.wait(wakeup)

            sum_energy = float(tool.get_value("-ds 1(0)")) - start_sum

            sut: str = tool.get_value("-dm 1[0..50](0)")

            rash = tool.get_value("-dm 5[0..50](0)")
            s: int = 0
            for current_step in range(step):

                s += float(rash[current_step])
                if round(abs(float(sut[current_step]) - float(day_beg[current_step])), 4) > 0.0003:
                    logger.error(SMPException(
                        f"Error energy on day begin: {sut[current_step]} must be {day_beg[current_step]};"
                        f" {step} iteration"))
                    logger.warning(f'test {__name__} is Failure')

            if round(abs(s - sum_energy), 4) > 0.0001:
                logger.error(f"Error summary energy: {s} must be {sum_energy}; after {step} iteration")
                logger.warning(f'test {__name__} is Failure')
            logger.info(f"Step-{step}")
        logger.warning(f'test {__name__} is OK')

    except Exception as ex:
        logger.warning(f'test {__name__} is failure')
        logger.error('', ex)
