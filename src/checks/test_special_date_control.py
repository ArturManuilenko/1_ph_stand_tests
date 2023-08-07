import logging
import time
from random import randint
from typing import List

from SMPCrossPlatform.src import wait

from src.checks.test_configuration import TestConfiguration
from src.fixtures.test_special_date_control_fixture import set_options_setup

logger = logging.getLogger(__name__)


def test_special_date_control(
        conf: TestConfiguration
) -> None:
    logger.info('test_special_date_control')
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    # write default counter setts
    ready_array: List = []
    default_array: List = []
    relay_block.all_off()
    relay_block.block_on(8)
    wait.wait(wakeup)
    tool.auth()
    try:
        for set_options in range(11, 44):

            if set_options == 43:
                default_array.append(str(tool.get_value('-og 67')).replace(", ", ":"))

            else:
                default_array.append(str(tool.get_value(f'-og {set_options}')).replace(", ", ":"))

        for set_options in range(11, 44):

            if set_options == 43:
                logger.info(f'execute command: {set_options_setup}')

                tool.execute(f'-os 67={set_options_setup}')

                get_command: str = str(tool.get_value('-og 67')).replace(", ", ":")
                ready_array.append(get_command)
                logger.info(f'Range: {set_options}, val: {get_command}')

            else:
                rv: int = randint(0, 7)
                calculate_command = f"[{rv}:{f'{rv}:{rv}:'* 23}{rv}]"
                setup_command = f"-os {set_options}={calculate_command}"
                logger.info(f'random value = {rv}, send command: {setup_command}')
                tool.execute(setup_command)
                command_get_value = str(tool.get_value(f'-og {set_options}')).replace(", ", ":")
                ready_array.append(command_get_value)
                logger.info(
                    f'Range: {set_options}, val: {command_get_value}'
                )
                if calculate_command not in tool.get_value(f"-og {set_options}"):
                    logger.error(f'Значение команды со счётчика -og {command_get_value},'
                                 f' отправленное: -os {set_options} = {calculate_command}')
                    logger.warning(f'test {__name__} is Failure')
                wait.wait(500)

        logger.info(f"Final array: {ready_array}")
        time.sleep(2)
        tool.auth()

        for set_options in range(33):
            if set_options == 32:
                logger.info(f'{default_array[set_options]}')
                set_command = f"-os 67={(str(default_array[set_options]))}"
                logger.info(f'send command: {set_command}')
                tool.execute(set_command)
            else:
                logger.info(default_array[set_options])
                set_other_options = f"-os {set_options + 11}={(str(default_array[set_options]))}"
                logger.info(f'send command: {set_other_options}')
                tool.execute(set_other_options)
                current_get_option: str = tool.get_value(f'-og {set_options + 11}')
                if current_get_option != default_array[set_options]:
                    logger.error(f'Значение команды со счётчика -og {current_get_option} '
                                 f'отправленное: {default_array[set_options]}')
                    logger.warning(f'test {__name__} is Failure')

        tool.execute('-a 2')
        logger.info('test special date control')
        logger.warning(f'test {__name__} is OK')

    except Exception as e:
        logger.warning(f'test {__name__} is Failure')

        logger.error('', e)
