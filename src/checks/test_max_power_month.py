import logging

import SMPCrossPlatform.src.wait as wait
from SMPCrossPlatform.src.smp_time import time_to_int, int_to_time

from src.checks.test_configuration import TestConfiguration
from src.fixtures.test_max_power_month_fixture import options_Pmax_zone, options_limp, t_mon, t_evn_start, t_morn_start

logger = logging.getLogger(__name__)


def test_max_power_month(
        conf: TestConfiguration
) -> None:
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    logger.info("Check Pmax")

    relay_block.all_off()
    relay_block.block_on(8)
    wait.wait(wakeup)
    dt0 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    dt1 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    try:
        # Включение, авторизация
        tool.auth()

        # выключение контроля, сброс всех превышений

        # включение контроля лимитов мощности, Pmax
        # загрузка всех настроек
        for settings in options_Pmax_zone:
            tool.execute(settings)

        for settings in options_limp:
            tool.execute(''.join(settings))  # загрузка зон контроля

        tool.execute('-os 84=[2:1:20:4:0]')  # загрузка режима контроля лимитов мощности "по зонам утро-вечер",
        tool.execute("--t=20000 -a 2")  # Скопировать фоновую конфигурацию в рабочую

        for day_step in range(12):
            logger.debug(f"Check Pmax, step = {day_step}")  # вывод в rep-файл

            # start: считывание массива Pmax
            pmax = tool.get_value("-dm 35[0..12](0110)")  # учитывает ответ NEED_WAIT

            logger.debug(f"Pmax[0] = {pmax[day_step]}")  # вывод в rep-файл

            #  переход к началу месяца
            tool.set_time(time_to_int(t_mon[day_step]))
            logger.debug(f'morning step = {day_step}')

            wait.wait(5000)

            #  Проход к зоне "утро"
            tool.set_time(time_to_int(t_mon[day_step]))
            logger.debug('morning start')
            wait.wait(2000)

            #  включение нагрузки
            relay_block.block_on(7)
            t_on = int(tool.get_value("-og 1"))  # время включения нагрузки утром
            logger.debug(f't_on={int_to_time(t_on)}')
            wait.wait(4000)  # ждём пока он учует что нагрузка есть

            summary_power = float(0)
            average_power = 13 - day_step
            # фаза включения нагрузки
            for _ in range(18 - 5 - day_step):  # чтобы была разница суммарной энергии
                current_power = float(tool.get_value("-ds 14"))
                logger.debug(f'Текущая мощность{current_power}')
                summary_power += current_power
                if current_power <= 0.02:
                    logger.error("Invalid_morn current Pmean >= 20W", current_power)
                    logger.warning(f'test {__name__} is Failure')

                wait.wait(10000)

            # фаза выключения нагрузки
            relay_block.block_off(7)
            t_off = int(tool.get_value("-og 1"))  # время выключения нагрузки утром
            logger.debug(f't_off={int_to_time(t_off)}')
            dt0[day_step] = t_off - t_on
            # длительность зоны вкл. нагрузки  утром
            logger.debug(f'dt0: [{day_step}]={dt0[day_step]}')

            summary_power /= average_power  # средняя мощность за время включения нагрузки
            summary_power *= dt0[day_step] / (3 * 60)  # усредненная мощность на 3-мин. интервале
            logger.debug(f'Morning power[{day_step}]={summary_power}')

            # TODO: started power is absent
            # relay_block.block_on(6)
            # wait.wait(4000)  # ждём пока он учует что нагрузка есть
            #
            # for _ in range(5 + day_step):
            #     current_power = float(tool.get_value("-ds 14"))
            #     logger.debug('Текущая мощность', current_power)
            #     if current_power < 0.004:
            #         logger.error("Invalid_morn current Pmean < 4W", current_power)
            #     wait.wait(10000)
            #
            # relay_block.block_off(6)

            #  выход из зоны "утро"
            tool.set_time(time_to_int(t_morn_start[day_step]) + 60 * 60 * 3)
            # длительность зоны - 3 часа
            logger.debug('morning finish')
            wait.wait(3000)  # было 2000

            # перевод времени к зоне включения "вечер"
            tool.set_time(time_to_int(t_evn_start[day_step]))  # для прохода к зоне включения вечер
            logger.debug('evening start')
            wait.wait(2000)

            #  включение нагрузки

            t_on = int(tool.get_value("-og 1"))  # время выключения нагрузки вечером
            logger.debug(f'Time On lamp: {int_to_time(t_on)}')
            relay_block.block_on(7)
            wait.wait(5000)  # ждём пока он учует что нагрузка есть
            summary_power = 0
            average_power: int = 0

            # фаза включения нагрузки
            for _ in range(18 - 3 - day_step):  # чтобы была разница суммарной энергии
                current_power = float(tool.get_value("-ds 14"))
                logger.debug(f'Текущая мощность {current_power}')
                summary_power += current_power
                average_power += 1
                if current_power <= 0.020:
                    logger.error("Invalid_evn current Pmean >= 20W", current_power)
                    logger.warning(f'test {__name__} is Failure')
                wait.wait(10000)

            # фаза выключения нагрузки
            relay_block.block_off(7)

            t_off = int(tool.get_value("-og 1"))  # время выключения нагрузки вечером
            logger.debug(f'Time off lamp evening {int_to_time(t_off)}')
            dt1[day_step] = t_off - t_on
            # длительность зоны вкл. нагрузки  вечером
            logger.debug(f'dt1[{day_step}]={dt1[day_step]}')

            summary_power /= average_power
            summary_power = summary_power * dt1[day_step] / (3 * 60)
            relay_block.block_on(7)
            # включение нагрузки для вечернего интервала
            # усредненная мощность на 3-мин. интервале
            logger.debug(f'Pave_evn[{day_step}]={summary_power}')
            wait.wait(4000)  # ждём пока он увидит что нагрузка есть
            for _ in range(3 + day_step):
                current_power = float(tool.get_value("-ds 14"))
                logger.debug(f'Текущая мощность = {current_power}')
                if current_power < 0.004:
                    logger.error("Invalid_evn current Pmean < 4W", current_power)
                    logger.warning(f'test {__name__} is Failure')
                wait.wait(10000)

            #  выход из зоны "вечер"
            current_time = int(tool.get_value("-og 1"))
            logger.debug(f'evning go_end={current_time}')
            tool.set_time(time_to_int(t_evn_start[day_step]) + 60 * 60 * 2)
            # длительность зоны - 2 часа
            wait.wait(3000)  # было 2000
            current_time = int(tool.get_value("-og 1"))
            logger.debug(f'evning finish={current_time}')

            #  считывание массива Pmax
            pmax = tool.get_value("-dm 35[0..12](0110)")  # учитывает ответ NEED_WAIT
            logger.debug(f"{pmax[0]=}")  # вывод в rep-файл

            #  завершение последнего месяца
        tool.set_time(time_to_int(t_mon[1]))
        wait.wait(5000)  # было 2000

        # чтение Pmax
        pmax = tool.get_value("-dm 35[0..12](0110)")  # учитывает ответ NEED_WAIT

        logger.debug(f'Check Pmax value : {pmax}')

        for i in range(2):
            logger.debug('Pmax_morning={}'.format(pmax[0]))
            logger.debug('Pmax_evening={}'.format(pmax[1]))

            if pmax[0] == 0.0:  # за   утро
                logger.error("Invalid Pmax_morning value (=0)")
                logger.warning(f'test {__name__} is Failure')
            if pmax[1] == 0.0:  # за  вечер
                logger.error("Invalid Pmax_evening value (=0)")
                logger.warning(f'test {__name__} is Failure')
            if pmax[0] < pmax[i - 1]:  # за   утро
                logger.error("Invalid compare Pmax_morning value")
                logger.warning(f'test {__name__} is Failure')
            if pmax[1] < pmax[i - 1]:  # за   вечер
                logger.error("Invalid compare Pmax_evening value")
                logger.warning(f'test {__name__} is Failure')

        logger.warning(f'test {__name__} is OK')

    except Exception as e:
        logger.warning(f'test {__name__} is Failure')

        logger.error('Check Pmax', e)
