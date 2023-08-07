import logging
from datetime import datetime
from random import choice

from SMPCrossPlatform.src import wait
from dateutil.relativedelta import relativedelta
from typing import List

from src.checks.test_configuration import TestConfiguration

logger = logging.getLogger(__name__)


def test_storage_depth_tariff(
    conf: TestConfiguration
) -> None:
    """
    Проверка на глубину хранения энергий расчетных периодов (месяцев) по тарифам
    Тест записывает накопления в течение 40 месяцев при этом происходят проверки:
    1. Проверка равна ли Текущая накопленная энергия в тарифе, энергии на начало месяца в тарифе (до подключения нагрузки)
    2. Сравнение разницы Накоплений энергии на начало текущего и прошлого месяца с энергией за прошлый месяц по тарифам
    3. Проверка правильности записи энергии за месяц по тарифам
    4. Разница суммы Накоплений энергии A+ за расчетный период (месяц) по тарифам с Текущим накоплением счетчика по тарифам
    5. Глубина и правильность записи накоплений за месяц по тарифам и накоплений на начало месяца по тарифам

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
        tool.execute('--t=20000 -a 25')
        tool.execute('--t=20000 -a 26')
        tool.execute('--t=20000 -a 27')
        wait.wait(10000)
        tool.execute('--t=20000 -a 5 3')
        tool.execute('-os 143=[0]')
        logger.info('Команда -os 143=[0] установлена')
        tool.execute('-os 10=[0:1:0:0:1:0]')
        tool.execute('--t=20000 -a 2')
        logger.info('Команда -os 10=[0:1:0:0:1:0] установлена')
        tool.set_current_time()
        wait.wait(2000)  # Ожидание для применения счётчиком времени
        started_accumulation_energy: float = float(tool.get_value('-ds 1(m0)')[1:-1])

        # Список номеров 8 тарифов для записи накоплений по месяцам
        tariff_energy_list: List = []
        [tariff_energy_list.append([]) for i in range(8)]
        begin_month_energy_list: List = []
        [begin_month_energy_list.append([]) for i in range(8)]

        logger.info('Установка даты и времени на начало следующего месяца')
        month_end_time = datetime.now() + relativedelta(day=31, hour=23, minute=59, second=58)
        month_begin_time = month_end_time + relativedelta(seconds=4)
        tool.set_time(month_end_time.strftime("%d.%m.%Y %H:%M:%S"))
        wait.wait(3000)

        for month in range(40):
            month_begin_time = month_begin_time + relativedelta(months=1)
            tool.set_time(month_begin_time.strftime("%d.%m.%Y %H:%M:%S"))

            for active_tariff in range(1, 9):
                tool.auth()

                begin_energy_current_month: float = float(tool.get_value(f'-dm 9[0..0](m{active_tariff})'))
                begin_energy_prev_month: float = float(tool.get_value(f'-dm 9[1..1](m{active_tariff})'))

                # Проверка равна ли Текущая накопленная энергия, энергии на начало месяца
                # в тарифе {active_tariff} в этом месяце накоплений еще не было
                current_tariff_energy = float(tool.get_value(f'-ds 1(m{active_tariff})')[1:-1])
                if abs(begin_energy_current_month - current_tariff_energy) > 0.0001:
                    logger.error(f'Энергия на начало месяца {begin_energy_current_month} '
                                 f'не равна текущей накопленой энергии '
                                 f'-ds 1(m{active_tariff})={current_tariff_energy}')
                    logger.warning(f'test {__name__} is Failure')
                else:
                    logger.info(f'Текущая накопленная энергия и энергия на начало месяца '
                                f'в тарифе {active_tariff} равны - ОК')

                # Сравнение разницы Накоплений энергии на начало текущего и прошлого месяца с энергией за прошлый месяц
                period_accum_energy_prev_month = float(tool.get_value(f"-dm 13[1..1](m{active_tariff})"))
                if abs((begin_energy_current_month - begin_energy_prev_month)
                       - period_accum_energy_prev_month) > 0.00015:
                    logging.error(f'Разница Накоплений на начало текущего и предыдущего месяца '
                                  f'{begin_energy_current_month - begin_energy_prev_month} '
                                  f'не равны энергии за месяц {period_accum_energy_prev_month}')
                    logger.warning(f'test {__name__} is Failure')
                else:
                    logger.info('Накопления энергии на начало текущего и прошлого месяца с энергии за месяц равны - ОК')

                logger.info(f'Включаю тариф {active_tariff}')
                tool.execute(f'--t=2000 -a 9={active_tariff}')

                if int(tool.get_value('-i 7')) != active_tariff:
                    logger.error(f'тариф {active_tariff} не включен')
                    logger.warning(f'test {__name__} is Failure')
                else:
                    logger.info(f'тариф {active_tariff} включен')

                # Формирование немного разных накоплений в интервалы для проверки правильности записи в стэк
                wait_time_tuple: tuple = (0, 20, 35)
                wait_time = choice(wait_time_tuple)

                if wait_time:
                    relay_block.block_on(7)
                    wait.wait(wait_time * 1000)
                    estimated_energy: float = float(tool.get_value('-ds 14')) / 3600 * wait_time
                    relay_block.block_off(7)
                else:
                    estimated_energy = 0

                wait.wait(3000)
                period_accumulation_energy = float(tool.get_value(f"-dm 13[0..0](m{active_tariff})"))
                tariff_energy_list[active_tariff - 1].insert(0, period_accumulation_energy)
                begin_month_energy_list[active_tariff - 1].insert(0, begin_energy_current_month)

                logger.info('Проверка правильности записи энергии за месяц')
                if abs(period_accumulation_energy - estimated_energy) > 0.00015:
                    logger.error(f'Для тарифа {active_tariff} устройство неверно подсчитало энергию. '
                                 f'Должно быть накоплено за {wait_time} секунд: {estimated_energy}, '
                                 f'накоплено на устройстве: {period_accumulation_energy}')
                    logger.error(f'Для тарифа {active_tariff} устройство неверно подсчитало энергию.')
                    logger.warning(f'test {__name__} is Failure')
                else:
                    logger.info(f'Накопленная энергия счетчика: {period_accumulation_energy}, '
                                f'расчетная энергия: {estimated_energy}, ОК')

                # Разница суммы Накоплений энергии A+ за расчетный период (месяц) по тарифам
                # с Текущим накоплением счетчика суммы по тарифам
                started_accumulation_energy = started_accumulation_energy + period_accumulation_energy
                current_tariff_sum = float(tool.get_value('-ds 1(m0)')[1:-1])
                if abs(started_accumulation_energy - current_tariff_sum) > 0.0006:
                    logger.error('Накопленная + начальная энергия не равны конечной на тест энергии:'
                                 f'Энергия, которая должна быть на устройстве: {started_accumulation_energy}, '
                                 f'Реальная энергия на устройстве: {current_tariff_sum}')
                    logger.error(f'period_accumulation_energy  {period_accumulation_energy}')
                    logger.error(f'Время счетчика: {tool.get_current_time()}')
                    logger.warning(f'test {__name__} is Failure')

        # Проверка глубины накоплений за 40 месяцев по тарифам
        for accum in range(40):
            for tariff in range(1, 9):
                tariff_energy_in_meter = abs(float(tool.get_value(f'-dm 13[{accum}..{accum}](m{tariff})')))
                if tariff_energy_in_meter - tariff_energy_list[tariff - 1][accum] > 0.00012:
                    logger.error(f'Накопление энергии за расчетный период '
                                 f'не правильно записан в -dm 13[{accum}..{accum}](m{tariff})={tariff_energy_in_meter},'
                                 f'должен был записать {tariff_energy_list[tariff - 1][accum]}')
                    logger.warning(f'test {__name__} is Failure')

                tariff_energy_in_meter = abs(float(tool.get_value(f'-dm 9[{accum}..{accum}](m{tariff})')))
                if tariff_energy_in_meter - begin_month_energy_list[tariff - 1][accum] > 0.00012:
                    logger.error(f'Накопление энергии на начало расчетного периода по тарифам '
                                 f'не правильно записан в -dm 9[{accum}..{accum}](m{tariff})={tariff_energy_in_meter},'
                                 f'должен был записать {begin_month_energy_list[tariff - 1][accum]}')
                    logger.warning(f'test {__name__} is Failure')

        execution_time = datetime.now() - start_time
        logger.warning(f'test {__name__} is OK, execution time = {execution_time}')

    except Exception as ex:
        logger.warning(f'test {__name__} is Failure')

        logger.error(ex)
