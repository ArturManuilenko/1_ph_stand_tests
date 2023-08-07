import logging

import SMPCrossPlatform.src.wait as wait

from src.checks.test_configuration import TestConfiguration
from datetime import datetime
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)


def test_set_end_period_date(
    conf: TestConfiguration
) -> None:

    """
    Тест проверяет возможность задавать дату окончания месяца (расчётного периода)
     - конкретное число месяца или последний день месяца.
    """

    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    try:
        logger.info('start set end period date')
        logger.warning(f'test {__name__} is Started')
        relay_block.all_off()
        relay_block.block_on(8)
        wait.wait(wakeup)

        tool.auth()
        logger.info('Сброс настроек к заводским, сброс EEPROM')
        tool.execute('--t=30000 -a 5 -a 3')
        tool.execute('--t=30000 -a 25')

        for day in (0, 1, 15, 31, 35):
            logger.info(f'Установка настройки -os 71={day}')
            tool.execute(f'-os 71={day} -a 2')
            next_year_datetime = datetime.now() + relativedelta(month=1, years=1)

            # условие, чтобы при установке начала периода 1 или 0, дата устанавливалась на последний день месяца
            if day == 0 or day == 1:
                day = 32

            for month in range(6):
                next_year_datetime = next_year_datetime + relativedelta(day=day-1, months=1, hour=23, minute=59, second=58)
                datetime_str = next_year_datetime.strftime("%d.%m.%Y %H:%M:%S")
                logger.info(f'Установка времени на конец расчетного периода {datetime_str}')
                tool.set_time(datetime_str)
                wait.wait(10000)

                logger.info('Проверка отсутствия накоплений энергии за расчетный период, до подключения нагрузки')
                if float(tool.get_value('-dm 13')) != 0:
                    logger.error(f'Накопленная энергия за расчетный период {month + 1} не равна 0, '
                                 'при переходе через начало расчетного периода')
                    logger.warning(f'test {__name__} is Failure')
                else:
                    logger.info(f'Накопленная энергия за расчетный период {month + 1} равна 0, '
                                 'при переходе через начало расчетного периода')

                logger.info('Включение нагрузки на 1 минуту')
                relay_block.block_on(7)
                wait.wait(60000)
                relay_block.block_off(7)

                logger.info('Проверка накоплений энергии за расчетный период, после подключения нагрузки')
                if float(tool.get_value('-dm 13')) == 0:
                    logger.error(f'Накопленная энергия за расчетный период {month + 1} равна 0, '
                                 'после включения нагрузки на 1 минуту')
                    logger.warning(f'test {__name__} is Failure')
                else:
                    logger.info(f'Накопленная энергия за расчетный период {month + 1} не равна 0, '
                                 'после включения нагрузки на 1 минуту')
                logger.info('Включение нагрузки на 1 минуту')

        logger.warning(f'test {__name__} is OK')

    except Exception as ex:
        logger.warning(f'test {__name__} is Failure')

        logger.error('', ex)
