import logging

import SMPCrossPlatform.src.wait as wait
from SMPCrossPlatform.src.smp_time import time_to_int

from src.checks.test_configuration import TestConfiguration
from src.fixtures.test_limits_power_on_schedule_fixture import options_power_limit_zones, options_limp

logger = logging.getLogger(__name__)


def test_limits_power_on_schedule(
        conf: TestConfiguration
) -> None:
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    logger.info("Check test_limits_power_on_schedule")

    relay_block.all_off()
    relay_block.block_on(8)
    wait.wait(wakeup)

    try:
        for tryings in range(11, 23):
            # Включение, авторизация
            tool.auth()
            relay_block.block_on(7)
            wait.wait(wakeup)  # Ждём пока счётчик среагирует
            lamp_power = float(tool.get_value('-ds 14'))

            logger.info(f'Мощность нагрузки: {lamp_power}')
            if lamp_power < 0.075:
                logger.error(
                    f'Слишком слабая нагрузка {lamp_power} : 0.05)'
                )
                logger.warning(f'test {__name__} is Failure')
            relay_block.block_off(7)

            # выключение контроля, сброс всех превышений
            # включение контроля
            tool.auth()

            # загрузка необходимых настроек
            for option in options_power_limit_zones:
                tool.execute(''.join(option))

            for option in options_limp:
                tool.execute(''.join(option))

            # загрузка режима контроля лимитов мощности "по зонам утро-вечер",
            tool.execute('-os 84=[2:1:20:4:1]')
            # tool.set_options([[range(85, 109), percent_of_max_power]])
            # tool.execute_compare('-og 85 86 87', '85={0} 86={0} 87={0}'.format(percent_of_max_power),
            #                          'Настройки лимита  мощности')

            tool.execute(f'-os 89={lamp_power * 0.6}')
            tool.execute(f'-os 101={lamp_power * 0.6}')

            tool.execute("--t=20000 -a 2")  # Скопировать фоновую конфигурацию в рабочую

            # Запись времени
            tool.set_time(time_to_int("9.06.2013 23:59:58"))  # для перехода на день без флага
            wait.wait(2000)
            logger.debug('Проверка флага, не должен быть установлен')
            # чтение флага превышения лимита мощности
            status = int(tool.get_value('-i 23')) & (1 << 0)
            if status == 1:
                logger.error("Флаг превышения лимита установлен, хотя не должен: <start> overLimP != 0")
                logger.warning(f'test {__name__} is Failure')
            else:
                logger.info(
                    'Флаг превышения лимита {}'.format("установлен" if status & (1 << 0) else "не установлен"))
            # контроль номера программы контроля мощности
            if tool.get_value('-i 35') == '12':
                logger.info('Проверка номера действующего расписания контроля мощности')
            else:
                logger.info('Проверка номера действующего расписания контроля мощности')
                logger.error('info 35 не равно 12')
                logger.warning(f'test {__name__} is Failure')

            power_limit_sc = int(tool.get_value('-i 35'))

            logger.info(f'''Лимит мощности для {power_limit_sc}
                        утро: {1000 * float((tool.get_value(f"-og {74 + tryings}")))} Вт,
                        вечером:{1000 * float((tool.get_value(f"-og {86 + tryings}")))} Вт''')
            # включение нагрузки, контроль отсутствия превышения лимита мощности не в зоне

            relay_block.block_on(7)
            wait.wait(5000)

            # фаза включения нагрузки
            wait.wait(1000 * 60 * 3)
            # чтение флага - отсутствие превышения лимита мощности
            logger.debug(r'Проверка флага, не должен быть установлен, как как мы находимся вне зон утро\вечер')
            status = int(tool.get_value('-i 23')) & (1 << 0)
            if status == 1:
                logger.error(
                    "Флаг превышения лимита установлен, хотя не должен: <not zone check> overLimP != 0 ???")
                logger.warning(f'test {__name__} is Failure')
            else:
                logger.info(
                    'Флаг превышения лимита {}'.format("установлен" if status & (1 << 0) else "не установлен"))
            # выключение нагрузки
            relay_block.block_off(7)

            #  контроль превышения лимита мощности в зоне  "утро"
            # перевод времени к зоне включения утро
            tool.set_time(time_to_int(f"{tryings}.01.2013 05:59:58"))  # для прохода к зоне включения утро
            wait.wait(2000)
            logger.debug('Зона утро')
            power_limit_sc = int(tool.get_value('-i 35'))
            logger.info(f'''Лимит мощности для {power_limit_sc}
                        утро: {1000 * float((tool.get_value(f"-og {74 + tryings}")))} Вт,
                        вечером:{1000 * float((tool.get_value(f"-og {86 + tryings}")))} Вт''')
            logger.debug('Включение нагрузки')
            #  включение нагрузки
            relay_block.block_on(7)
            wait.wait(4000)

            # фаза включения нагрузки
            wait.wait(1000 * 3 * 60)  # цикл 3 минуты
            logger.debug('Выключение нагрузки')
            # фаза выключения нагрузки
            relay_block.block_off(7)

            # чтение флага превышения лимита мощности
            logger.debug(r'Проверка флага утром, должен быть установлен, так как прошло 3 минуты')
            status = int(tool.get_value('-i 23')) & (1 << 0)
            if status == 0:
                logger.error("Флаг превышения лимита не установлен, хотя должен: <morning> overLimP != 1 ???")
                logger.warning(f'test {__name__} is Failure')
            else:
                logger.info(
                    'Флаг превышения лимита {}'.format("установлен" if status & (1 << 0) else "не установлен"))

            #  выход из зоны "утро"
            tool.set_time(time_to_int(f"{tryings}.01.2013 08:59:56"))  # для прохода к зоне выключения утро
            wait.wait(5000)
            logger.debug('Конец зоны утро')

            # чтение флага превышения лимита мощности
            logger.debug(r'Проверка флага после зоны утра, не должен быть установлен, так мы вне участка')
            status = int(tool.get_value('-i 23')) & (1 << 0)
            if status == 1:
                logger.error(
                    "Флаг превышения лимита установлен, хотя не должен: <finish morning> overLimP != 0 ???")
                logger.warning(f'test {__name__} is Failure')
            else:
                logger.info(
                    'Флаг превышения лимита {}'.format("установлен" if status & (1 << 0) else "не установлен"))
            # контроль превышения лимита мощности в зоне  "вечер"
            # перевод времени к зоне включения "вечер"
            tool.set_time(time_to_int(f"{tryings}.01.2013 15:59:58"))  # для прохода к зоне включения вечер
            logger.debug('Зона вечер')
            wait.wait(5000)

            #  включение нагрузки
            logger.debug('Включение нагрузки')
            relay_block.block_on(7)
            wait.wait(1000 * 60 * 3)

            # фаза выключения нагрузки
            logger.debug('Выключение нагрузки')
            relay_block.block_off(7)
            wait.wait(4000)
            # чтение флага превышения лимита мощности
            logger.debug(r'Проверка флага вечером, должен быть установлен, так как потребили больше лимита')
            status = int(tool.get_value('-i 23')) & (1 << 0)
            if status == 0:
                logger.error("Флаг превышения лимита не установлен, хотя должен: <evening> overLimP != 1 ???")
                logger.warning(f'test {__name__} is Failure')
            else:
                logger.info(
                    'Флаг превышения лимита {}'.format("установлен" if status & (1 << 0) else "не установлен"))
            #  выход из зоны "вечер"
            tool.set_time(time_to_int(f"{tryings}.06.2013 17:59:58"))
            wait.wait(5000)
            wait.wait(1000 * 3 * 60)  # wait 3 minutes
            logger.debug('Конец зоны вечер')
            # чтение флага превышения лимита мощности
            logger.debug(r'Проверка флага после зоны вечера, не должен быть установлен, так как мы вне зоны')
            status = int(tool.get_value('-i 23')) & (1 << 0)
            if status == 1:
                logger.error("Флаг превышения лимита установлен, хотя не должен: <evening> overLimP != 0 ???")
                logger.warning(f'test {__name__} is Failure')
            else:
                logger.info(
                    f'Флаг превышения лимита {"установлен" if status & (1 << 0) else "не установлен"}')
            logger.warning(f'test {__name__} is OK')

    except Exception as ex:
        logger.warning(f'test {__name__} is Failure')

        logger.error(ex)
