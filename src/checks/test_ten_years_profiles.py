import logging
from datetime import datetime
from random import randint

from SMPCrossPlatform.src import wait
from dateutil.relativedelta import relativedelta

from src.checks.test_configuration import TestConfiguration

logger = logging.getLogger(__name__)


def test_ten_years_profiles(
    conf: TestConfiguration
) -> None:
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    logger.info('Test ten years summary calculate energy')
    relay_block.all_off()
    relay_block.block_on(8)
    wait.wait(wakeup)

    try:
        tool.auth()
        tool.execute('-os 143=[0]')
        logger.info('Команда -os 143=[0] установлена')
        tool.execute('-os 10=[0:1:0:0:1:0] -a 2')
        logger.info('Команда -os 10=[0:1:0:0:1:0] установлена')

        for month in range(0, 120):  # TODO: 120 месяцев
            tool.auth()
            active_tariff = randint(1, 8)
            tool.execute(f'-a 9={active_tariff}')
            wait.wait(1500)
            logger.info(f'Включаю тариф {active_tariff}')
            logger.error(f'тариф {active_tariff} не включен') if int(tool.get_value('-i 7')) != active_tariff \
                else logger.info(f'тариф {active_tariff} включен')

            started_energy_on_tariff: float = float(tool.get_value(f'-ds 1(m{active_tariff})')[1:-1])
            started_energy_summary: float = float(tool.get_value('-ds 1'))
            logger.info(
                f'Начальная энергия до подсчётов на тарифе {active_tariff}: {tool.get_value(f"-ds 1(m{active_tariff})")[1:-1]}')
            data_start_plus_change = (datetime(2012, 12, 31, 23, 59, 55) +
                                      relativedelta(months=month)).strftime('%d.%m.%Y %H:%M:%S')
            logger.info(f"Корректирую дату в {data_start_plus_change}")
            logger.info(f'Накопления для {month} месяца')
            tool.set_time(data_start_plus_change)

            if month // 2:
                pass
            else:
                logger.info('Переход в выключенном состоянии')
                relay_block.block_off(8)
                wait.wait(35000)
                relay_block.block_on(8)
                wait.wait(wakeup)

            while not tool.get_current_time()[17:19].startswith('59'):
                ...

            logger.info('Счётчик перешел через минуту, нагрузка включена')
            relay_block.block_on(7)

            for waiting in range(8):
                wait.wait(3750)  # TODO: Время для того чтобы устройство увидело нагрузку
                power = float(tool.get_value('-ds 14'))
                if power < 0.060:
                    logger.error(f'Низкая нагрузка/перегоревшая лампа, текущая нагрузка: {power}')
                    logger.warning(f'test {__name__} is Failure')

            power_interval_calculated = float(tool.get_value('-ds 14')) / 3600 * int(tool.get_current_time()[17:19])
            relay_block.block_off(7)
            logger.info('30 секунд прошло, нагрузка выключена')
            logger.info('Ожидание 60 секунд без нагрузки')
            wait.wait(60000)

            relay_block.block_on(7)
            time_on_power_lamp = int(tool.get_current_time()[17:19])
            logger.info('Нагрузка включена, жду пока счётчик её увидит')
            wait.wait(3750)

            while not tool.get_current_time()[17:19].startswith('59'):
                if float(tool.get_value('-ds 14')) < 0.060:
                    logger.error(f'Низкая нагрузка/перегоревшая лампа, текущая нагрузка: {tool.get_value("-ds 14")}')
                    logger.warning(f'test {__name__} is Failure')

            power_interval_calculated = power_interval_calculated + float(tool.get_value('-ds 14')) / 3600 * (
                60 - time_on_power_lamp)

            relay_block.block_off(7)
            logger.info('Счётчик перешел через второй интервал, вычитываю -dm 25[0..2]')
            wait.wait(3000)
            ended_energy_on_tariff = sum([float(tool.get_value(f'-dm 25[{_}..{_}]')) for _ in range(3)])
            logger.info(
                f'Подсчитанная энергия: {power_interval_calculated}, подсчитана с начальной: '
                f'{power_interval_calculated + started_energy_on_tariff} - она должна совпадать с конечной,'
                f' начальная на прогон: {started_energy_on_tariff}, вычитанная через ds 1: '
                f'{float(tool.get_value(f"-ds 1(m{active_tariff})")[1:-1])}, ds 1 текущего тарифа - конечная = '
                f'{float(tool.get_value(f"-ds 1(m{active_tariff})")[1:-1]) + ended_energy_on_tariff}'
            )
            accumulated_energy = float(tool.get_value(f"-ds 1(m{active_tariff})")[1:-1])
            summary_energy_interval_started = power_interval_calculated + started_energy_on_tariff
            summary_energy_tariff_intervals = float(accumulated_energy + ended_energy_on_tariff)

            if abs(summary_energy_interval_started - summary_energy_tariff_intervals) > 0.002:
                logger.error(
                    'Подсчитанная энергия - (ds1 - начальная) расходятся больше, чем на 0.002 (погрешность), '
                    f'полученное знаение: '
                    f'{abs(summary_energy_interval_started - summary_energy_tariff_intervals)} '
                )
                logger.warning(f'test {__name__} is Failure')
            if abs((started_energy_summary + ended_energy_on_tariff) -
                   (started_energy_summary + power_interval_calculated)) > 0.0003:
                logger.error(
                    'Массив энергий, вычитанных через dm25 не совпадает с суммой ds1 на текущей итерации и начальной '
                    'энергией, записанной в тарифы, полученное значение: '
                    f'{abs(power_interval_calculated - (float(tool.get_value("-ds 1")) - started_energy_on_tariff))} '
                )

        logger.warning(f'test {__name__} is OK')

    except Exception as ex:
        logger.warning(f'test {__name__} is Failure')

        logger.error('', ex)
