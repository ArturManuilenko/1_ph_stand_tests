import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

from SMPCrossPlatform.src import wait

from src.checks.test_configuration import TestConfiguration

logger = logging.getLogger(__name__)


def test_storage_max_power_without_time_limit(
    conf: TestConfiguration
) -> None:
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    logger.info(f'Test {__name__} start')
    relay_block.all_off()
    relay_block.block_on(8)
    wait.wait(wakeup)

    try:
        logger.info("Авторизация, сброс еепром")
        tool.auth()
        wait.wait(10000)
        tool.execute('-a 3 -a 5')
        tool.execute('-a 25')  # Сброс накоплений
        wait.wait(10000)
        logger.info('Отправка команд -os 84=[0:0:50:0:1] и -os 85=0.001')
        tool.execute('-os 84=[0:0:50:0:1]')
        tool.execute('-os 85=0.001')
        # Установка круглосуточного контроля мощности
        tool.execute('-os 72=[1:1:1:1:1:1] -a 2')
        next_counter_year_datetime = datetime.now() + relativedelta(day=1, years=1)

        for day_month in range(1, 26):
            relay_block.block_on(8)
            wait.wait(wakeup)
            next_counter_year_datetime = next_counter_year_datetime + relativedelta(days=1, months=1)
            datetime_str = next_counter_year_datetime.strftime("%d.%m.%Y %H:%M:%S")
            logger.info(f'Установка даты: {datetime_str}')
            tool.set_time(datetime_str)
            logger.info('Ожидание перехода через минуту')
            wait.wait(3000)
            logger.info("Включение нагрузки")
            relay_block.block_on(7)
            logger.info("Ожидание пока пройдет 60 секунд для интервала")
            wait.wait(61000)
            relay_block.block_off(7)
            logger.info("Выключение нагрузки")

            relay_block.block_off(8)
            logger.info("Выключение устройства на 10 секунд")
            wait.wait(10000)

        relay_block.block_on(8)
        wait.wait(wakeup)
        for period in range(25):
            if float(tool.get_value(f'-dm 35[{period}..{period}]')) < 0.001:
                logger.error(
                    f'Лимит мощности превышен в вечернее воемя, но счётчик его не увидел без ограничения времени'
                )
                logger.warning(f'test {__name__} is Failure')
            else:
                logger.info(f'Превышение лимита мощности записано в периоде {period + 1}')

        logger.warning(f'test {__name__} is OK')

    except Exception as ex:
        logger.warning(f'test {__name__} is Failure')

        logger.error('', ex)
