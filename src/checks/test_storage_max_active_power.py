import logging
from datetime import date

from SMPCrossPlatform.src import wait

from src.checks.test_configuration import TestConfiguration

logger = logging.getLogger(__name__)


def test_storage_max_active_power(
    conf: TestConfiguration
) -> None:
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    logger.info('Test storage depth on tariffs ')
    relay_block.all_off()
    relay_block.block_on(8)
    wait.wait(wakeup)

    try:
        logger.info("Авторизация, сброс еепром")
        tool.auth()
        wait.wait(10000)
        tool.execute('-a 25')  # Сброс накоплений
        wait.wait(10000)  # Wait for counter
        tool.execute('-os 84=[2:0:50:0:1]')
        logger.info('Отправка команды set option 84=[2:0:50:0:1]')
        for set_limits in range(85, 109):
            tool.execute(f'-dm {set_limits}=0.001')
        logger.info('Отправка команды set option 72-83=[2:0:50:0:1], 100% достижения лимита, интервал 1 минута')
        for set_options in range(72, 84):
            tool.execute(f'-os {set_options}=[1:1:16:20:26:28]')

        for day_command in range(12):
            tool.execute(f'-os {71 + day_command}=[{day_command + 1}:{day_command + 1}:16:20:26:28]')

        logger.info("Применяю настройки")
        tool.execute('-a 2')
        next_counter_year = int(date.today().year) + 1

        for check_day in range(1, 13):
            relay_block.block_on(8)
            wait.wait(wakeup)
            logger.info(f'Установка даты: {check_day:02}.{check_day:02}.{next_counter_year} 07:59:55')
            tool.set_time(f'{check_day:02}.{check_day:02}.{next_counter_year} 07:59:55')
            logger.info('Ожидание перехода через минуту')
            wait.wait(6000)
            logger.info("Включение нагрузки")
            relay_block.block_on(7)
            logger.info("Ожидание пока пройдет 60 секунд для интервала")
            wait.wait(60000)
            relay_block.block_off(7)
            logger.info("Выключение нагрузки")

            logger.info(f'Установка даты: {check_day:02}.{check_day:02}.{next_counter_year} 12:59:55')
            tool.set_time(f'{check_day:02}.{check_day:02}.{next_counter_year} 12:59:55')
            logger.info('Ожидание перехода через минуту')
            wait.wait(6000)
            logger.info("Включение нагрузки")
            relay_block.block_on(7)
            logger.info("Ожидание пока пройдет 60 секунд для интервала")
            wait.wait(60000)
            relay_block.block_off(7)
            logger.info("Выключение нагрузки")

            relay_block.block_off(8)
            logger.info("Выключение устройства на 10 секунд")
            wait.wait(10000)

        relay_block.block_on(8)
        wait.wait(wakeup)
        for check_energy_day in range(0, 12):
            if float(tool.get_value(f'-dm 35[{check_energy_day}..{check_energy_day}](m1)')) < 0.001:
                logger.error(
                    f'Лимит мощности превышен в утреннее время, но счётчик его не увидел на отрезке {check_energy_day}'
                )
                logger.warning(f'test {__name__} is Failure')
                logger.error(
                    f'Лимит мощности превышен в утреннее время, но счётчик его не увидел на отрезке {check_energy_day}'
                )

            if float(tool.get_value(f'-dm 35[{check_energy_day}..{check_energy_day}](m2)')) < 0.001:
                logger.error(
                    f'Лимит мощности превышен в вечернее время, но счётчик его не увидел на отрезке {check_energy_day}'
                )
                logger.warning(f'test {__name__} is Failure')
                logger.error(
                    f'Лимит мощности превышен в вечернее время, но счётчик его не увидел на отрезке {check_energy_day}'
                )

        logger.warning(f'test {__name__} is OK')

    except Exception as ex:
        logger.warning(f'test {__name__} is Failure')

        logger.error('', ex)


'''
-os 84=[2:0:50:0:1] - вкл контроль мощности, по расписанию зон контроля, процент достижения = 100
-os 72=[1:1:16:20:26:28] 85=1 97=1 - начало 01.01 утро время: 08:00 конец 10:00 лимит 1квт, день начало 13:00 конец 14:00 лимит 5квт
'''
