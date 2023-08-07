import logging

from SMPCrossPlatform.smptool2 import SMPException
from SMPCrossPlatform.src import wait

from src.checks.test_configuration import TestConfiguration

logger = logging.getLogger(__name__)


def test_absolute_special_date(
    conf: TestConfiguration
) -> None:
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    logger.info('Test absolute special date ')
    relay_block.all_off()
    relay_block.block_on(8)
    wait.wait(wakeup)
    try:
        tool.auth()
        tool.execute('-os 43=[1:1:0:0:1:2:3:4:5:6] -os 10=[0:0:1:0:1:0] -a 2 -t=2000')
        logger.info('Checking 96 special dates w/o reboot')

        '''недельное расписание задействовано + по временным зонам'''
        '''добавить тариф -i 7'''
        '''Группа расписаний -i 9'''
        for program in range(1, 31):  # TODO: tariff program (32) in 96 special dates
            tool.auth()
            mass_value = f'[{":".join(f"{program}:1:{program}:{program}" for _ in range(1, 49))}]'
            tool.execute(f"-os 68={mass_value}")
            logger.info(f'accept 1-48 special dates: {program}')
            wait.wait(3000)

            tool.execute(f"-os 69={mass_value}")
            logger.info(f'accept 49-96 special dates: {program}')
            tool.execute('-a 2')

            wait.wait(3000)
            if tool.get_value('-og 68') != mass_value:
                logger.error(f'Special date (1-48) is not match, tariff program: {program}'
                             f'Counter value: {tool.get_value("-og 68")}, needed value: {mass_value}')
                logger.warning(f'test {__name__} is Failure')
                continue
            if tool.get_value('-og 69') != mass_value:
                logger.error(f'Special date (49-96) is not match, tariff program: {program}'
                             f'Counter value: {tool.get_value("-og 69")}, needed value: {mass_value}')
                logger.warning(f'test {__name__} is Failure')
                SMPException(f'Special date (49-96) is not match, tariff program: {program}')
                continue
        logger.info('1-96 special dates checking w/o reboot device is over')

        for program in range(1, 31):  # TODO: tariff program (32) in 96 special dates
            logger.info('Checking 96 special dates')

            wait.wait(wakeup)
            tool.auth()

            mass_value = f'[{":".join(f"{program}:1:{program}:{program}" for _ in range(1, 49))}]'
            logger.info(mass_value)
            logger.info(program)
            tool.execute(f"-os 68={mass_value}")
            wait.wait(3000)

            tool.execute(f"-os 69={mass_value}")
            tool.execute('-a 2')
            wait.wait(3000)

            tool.set_time(f'{program:02}.01.{2012 + program} 01:00:00')
            logger.info(tool.get_value('-i 8'))
            relay_block.block_off(8)
            wait.wait(5000)
            relay_block.block_on(8)

            if tool.get_value('-i 8') != f"{program + 1}":
                logger.error(f'Special date is not ON, tariff program: {program}, needed value: {program + 1} '
                             f'current value: {tool.get_value("-i 8")}')
                logger.warning(f'test {__name__} is Failure')
                continue

            if tool.get_value('-og 68') != mass_value:
                logger.error(f'Special date (1-48) is not match, tariff program: {program}'
                             f'Counter value: {tool.get_value("-og 68")}, needed value: {mass_value}')
                logger.warning(f'test {__name__} is Failure')
                continue
            if tool.get_value('-og 69') != mass_value:
                logger.error(f'Special date (48-96) is not match, tariff program: {program}'
                             f'Counter value: {tool.get_value("-og 69")}, needed value: {mass_value}')
                logger.warning(f'test {__name__} is Failure')
                continue

        logger.warning(f'test {__name__} is OK')

    except Exception as ex:
        logger.warning(f'test {__name__} is Failure')

        logger.error('', ex)

