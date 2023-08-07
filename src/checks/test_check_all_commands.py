import logging

from SMPCrossPlatform.src import wait

from src.checks.test_configuration import TestConfiguration

logger = logging.getLogger(__name__)


def test_check_all_commands(
    conf: TestConfiguration
) -> None:

    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    logger.info('Test check all commands')
    relay_block.all_off()
    relay_block.block_on(8)
    wait.wait(wakeup)

    try:
        tool.auth()
        logger.info('Check info')
        with open('command_file_with_commands.txt', 'w') as file_with_commands:
            for info in range(1, 84):
                try:
                    answer = tool.get_value(f'-i {info}')
                    file_with_commands.write(f"info: {info}, {answer}\n")
                    logging.info(f'info {info}, {answer}')
                except Exception as ex:
                    logging.error(f"ERROR {ex} on INFO {info}")
                    continue

            logger.info('Check get option')
            for get_option in range(1, 550):
                try:
                    answer = tool.get_value(f'-og {get_option}')

                    file_with_commands.write(f"og: {get_option}, {answer}\n")
                    logging.info(f"og: {get_option}, {answer}\n")
                except Exception as ex:
                    logging.error(f"ERROR {ex} on GET_OPTION {get_option}")
                    continue

            logger.info('Check dm')
            for data_multiple in range(1, 260):
                try:
                    answer = tool.get_value(f'-dm {data_multiple}')

                    file_with_commands.write(f"dm: {data_multiple}, {answer}\n")
                    logging.info(f"dm: {data_multiple}, {answer}\n")
                except Exception as ex:
                    logging.error(f"ERROR {ex} on DATA_MULTIPLE {data_multiple}")
                    continue

            logger.info('Check dm with 0 mask')
            for data_multiple_general in range(1, 260):
                try:
                    answer = tool.get_value(f'-dm {data_multiple_general}(m0)')

                    file_with_commands.write(f"dm: {data_multiple_general}(m0), {answer}\n")
                    logging.info(f"dm: {data_multiple_general}, {answer}\n")
                except Exception as ex:
                    logging.error(f"ERROR {ex} on DATA_MULTIPLE_EX (dm1) {data_multiple_general}")
                    continue

            logger.info('Check dm mask 10')
            for data_multiple_on_tariff in range(1, 260):
                try:
                    answer = tool.get_value(f'-dm {data_multiple_on_tariff}(m10)')

                    file_with_commands.write(f"dm: {data_multiple_on_tariff}(m10), {answer}\n")
                    logging.info(f"dm: {data_multiple_on_tariff}, {answer}\n")
                except Exception as ex:
                    logging.error(f"ERROR {ex} on DATA_MULTIPLE_EX (-dm1 (10)) {data_multiple_on_tariff}")
                    continue

            logger.info('Check ds')
            for data_single in range(1, 112):
                try:
                    answer = tool.get_value(f'-ds {data_single}')
                    file_with_commands.write(f"ds: {data_single}, {answer}\n")
                    logging.info(f"ds: {data_single}, {answer}\n")

                except Exception as ex:
                    logging.error(f"ERROR {ex} on DATA_SINGLE {data_single}")
                    continue
                    
            logger.info('Check ds1')
            for data_single_extended in range(1, 110):
                try:
                    answer = tool.get_value(f'-ds1 {data_single_extended}')

                    file_with_commands.write(f"ds1: {data_single_extended}, {answer}\n")
                    logging.info(f"ds1: {data_single_extended}, {answer}\n")
                except Exception as ex:
                    logging.error(f"ERROR {ex} on DATA_SINGLE_EX {data_single_extended}")
                    continue

        logger.info('Check dm1')
        for data_multiple_extended in range(1, 350):
            try:
                answer = tool.get_value(f'-dm1 {data_multiple_extended}')

                file_with_commands.write(f"dm1: {data_multiple_extended}, {answer}\n")
                logging.info(f"dm1: {data_multiple_extended}, {answer}\n")

            except Exception as ex:
                logging.error(f"ERROR {ex} on DATA_MULTIPLE_EX {data_multiple_extended}")
                continue

    except Exception as ex:
        logger.warning(f'test {__name__} is Failure')

        logger.error(ex)
