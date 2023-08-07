import logging
from datetime import datetime

from SMPCrossPlatform.src import wait
from dateutil.relativedelta import relativedelta
from random import choice

from src.checks.test_configuration import TestConfiguration

logger = logging.getLogger(__name__)


def test_storage_depth_public(
    conf: TestConfiguration
) -> None:
    """
    Проверка на глубину хранения энергий расчетных периодов (месяцев)
     - 40 (текущий и 39 предыдущих) расчетных периодов (месяцев)
    Тест записывает накопления в течение 40 месяцев при этом происходят проверки:
    1. Проверка равна ли Текущая накопленная энергия, энергии на начало месяца (до подключения нагрузки)
    2. Сравнение разницы Накоплений энергии на начало текущего и прошлого месяца с энергией за прошлый месяц
    3. Проверка правильности записи энергии за месяц
    4. Разница суммы Накоплений энергии A+ за расчетный период (месяц) с Текущим накоплением счетчика
    5. Глубина и правильность записи накоплений за месяц и накоплений на начало месяца
    6. Запись расчетных периодов без накопления энергии

    При этом в тесте нагрузка подключается на разные периоды времени.
    """
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    start_time = datetime.now()

    logger.info(f'Test {__name__} is Started')
    logger.warning(f'test {__name__} is Started')
    relay_block.all_off()
    relay_block.block_on(8)
    wait.wait(wakeup)

    try:
        tool.auth()
        tool.execute('--t=20000 -a 5 3')
        tool.execute('--t=20000 -a 25')
        tool.execute('--t=20000 -a 26')
        tool.execute('--t=20000 -a 27')
        tool.execute('-os 143=[0]')
        logger.info('Команда -os 143=[0] установлена')
        tool.execute('-os 10=[0:1:0:0:1:0]')
        logger.info('Команда -os 10=[0:1:0:0:1:0] установлена')
        tool.set_current_time()
        wait.wait(2000)  # Ожидание для применения счётчиком времени
        started_accumulation_energy: float = float(tool.get_value('-ds 1'))
        begin_month_energy_list: list = []
        period_accum_energy_list: list = []

        logger.info('Установка даты и времени на начало следующего месяца')
        month_end_time = datetime.now() + relativedelta(day=31, hour=23, minute=59, second=58)
        month_begin_time = month_end_time + relativedelta(seconds=4)
        datetime_str = month_end_time.strftime("%d.%m.%Y %H:%M:%S")
        tool.set_time(datetime_str)
        wait.wait(3000)

        for month in range(40):
            month_begin_time = month_begin_time + relativedelta(months=1)
            datetime_str = month_begin_time.strftime("%d.%m.%Y %H:%M:%S")
            tool.set_time(datetime_str)

            begin_energy_current_month: float = float(tool.get_value('-dm 9[0..0]'))
            begin_energy_prev_month: float = float(tool.get_value('-dm 9[1..1]'))

            logger.info('Проверка равна ли Текущая накопленная энергия, энергии на начало месяца, '
                        'в этом месяце накоплений еще не было')
            if abs(begin_energy_current_month - float(tool.get_value('-ds 1'))) > 0.0001:
                logger.error(f'Энергия на начало месяца {begin_energy_current_month} '
                             f'не равна текущей накопленой энергии {float(tool.get_value("-ds 1"))}')
                logger.warning(f'test {__name__} is Failure')
            else:
                logger.info('Текущая накопленная энергия и энергия на начало месяца равны - ОК')

            # Формирование немного разных накоплений в интервалы для проверки правильности записи в стэк
            wait_time_tuple: tuple = (0, 20, 35, 50)
            wait_time = choice(wait_time_tuple)

            if wait_time:
                relay_block.block_on(7)
                wait.wait(wait_time * 1000)
                estimated_energy: float = float(tool.get_value('-ds 14')) / 3600 * wait_time
                relay_block.block_off(7)
            else:
                estimated_energy = 0

            wait.wait(3000)
            period_accumulation_energy: float = float(tool.get_value("-dm 13[0..0]"))
            # запись накоплений в листы, для последующего сравнения
            period_accum_energy_list.insert(0, period_accumulation_energy)
            begin_month_energy_list.insert(0, begin_energy_current_month)

            logger.info('Сравнение разницы Накоплений энергии на начало текущего и прошлого месяца '
                        'с энергией за прошлый месяц')
            period_accum_energy_prev_month = float(tool.get_value("-dm 13[1..1]"))
            if abs((begin_energy_current_month - begin_energy_prev_month) - period_accum_energy_prev_month) > 0.00015:
                logging.error(f'Разница Накоплений на начало текущего и предыдущего месяца '
                              f'{begin_energy_current_month - begin_energy_prev_month} '
                              f'не равны энергии за месяц {period_accum_energy_prev_month}')
                logger.warning(f'test {__name__} is Failure')
            else:
                logger.info('Накопления энергии на начало текущего и прошлого месяца с энергии за месяц равны - ОК')

            logger.info('Проверка правильности записи энергии за месяц')
            if abs(period_accumulation_energy - estimated_energy) > 0.00015:
                logger.error(f'Устройство неверно подсчитало энергию. '
                             f'Должно быть накоплено за {wait_time} секунд: {estimated_energy}, '
                             f'накоплено на устройстве: {period_accumulation_energy}')
                logger.warning(f'test {__name__} is Failure')
            else:
                logger.info(f'Накопленная энергия счетчика: {period_accumulation_energy}, '
                            f'расчетная энергия: {estimated_energy}, ОК')

            # Разница суммы Накоплений энергии A+ за расчетный период (месяц) с Текущим накоплением счетчика
            started_accumulation_energy = started_accumulation_energy + period_accumulation_energy
            if abs(started_accumulation_energy - float(tool.get_value('-ds 1'))) > 0.0004:
                logger.error('Накопленная + начальная энергия не равны конечной на тест энергии:'
                             f'Энергия, которая должна быть на устройстве: {started_accumulation_energy}, '
                             f'Реальная энергия на устройстве: {float(tool.get_value("-ds 1"))}')
                logger.warning(f'test {__name__} is Failure')
            else:
                logger.info(f'{tool.get_current_time()} Накопленная + начальная энергия равны конечной на тест энергии')

        # проверка глубины и правильности записи
        for accum in range(40):
            # проверки производится с допустимой погрешностью 0,00012 кВт
            if abs(float(tool.get_value(f'-dm 13[{accum}..{accum}]')) - period_accum_energy_list[accum]) > 0.00012:
                logger.error(f'Накопление энергии за расчетный период НЕ правильно записан в -dm 13[{accum}..{accum}]')
                logger.warning(f'test {__name__} is Failure')

            if abs(float(tool.get_value(f'-dm 9[{accum}..{accum}]')) - begin_month_energy_list[accum]) > 0.00012:
                logger.error(f'Накопление энергии на начало расчетного периода '
                             f'НЕ правильно записан в -dm 13[{accum}..{accum}]')
                logger.warning(f'test {__name__} is Failure')

        execution_time = datetime.now() - start_time
        logger.warning(f'test {__name__} is OK, execution time = {execution_time}')

    except Exception as ex:
        logger.warning(f'test {__name__} is Failure')

        logger.error(ex)
