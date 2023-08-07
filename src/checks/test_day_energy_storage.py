'''
Тест проверяет глубину хранения накоплений по дням (128 дней)

Случайным образом формируются накополения по 2му и по 3му тарифу (по расписанию) для 128 дней,
проверяется правильность записей накоплений на начало дня и за день на всю глубину хранения.

https://kiwi.qa.unic-lab.by/case/1081/
'''

import logging
from datetime import datetime
from typing import List
from random import randint

from SMPCrossPlatform.src import wait
from dateutil.relativedelta import relativedelta

from src.checks.test_configuration import TestConfiguration

logger = logging.getLogger(__name__)

def test_day_energy_storage(
    conf: TestConfiguration
) -> None:
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    logger.info('Test day energy tariff storage ')
    relay_block.all_off()
    relay_block.block_on(8)
    wait.wait(wakeup)

    try:
        tool.auth()
        wait.wait(wakeup)
        logger.info("Установка тарификации по временным зонам, расписание 1")
        tool.execute('-os 10=[0:0:1:0:0:1] 43=[1:1:0:0:0:0:0:0:0:0] 46=[0:0:0:0:0:0:0:0:0:0] 47=[0:0:0:0:0:0:0:0:0:0]')
        logger.info("Расписание 1 00.00-00.30 T2, 00.30-01.00 T3")
        tool.execute(f'-os 11=[1:2:{"0:" * 45}0]')
        wait.wait(1000)
        tool.execute('--t=2000 -a 2')
        tool.execute('--t=20000 -a 25')
        wait.wait(2000)
        tool.set_time('01.02.2025 00:05:00')
        wait.wait(3000)

        if tool.get_value('--t=2000 -dm 5[0..10]') != ['0'] * 11:
            logger.error(
                f'Полученные значения со счётчика о накоплениях за день должны быть 0, так как время было переведено '
                f'назад, значения: {tool.get_value("-dm 5[0..10]")}'
            )
            raise Exception

        logger.info('Проверка правильности фиксации накоплений за сутки')
        start_energy: float = float(tool.get_value('-ds 1'))
        sum_energy_per_day: float = 0
        logger.info(f'Текущее накопление энергии A+ = {start_energy}')
        energy_per_day_calc: list = []
        energy_per_day_calc_t2: list = []
        energy_per_day_calc_t3: list = []
        for days in range(0, 128):
            logger.info(f'проверка для : {days} дня                      ---Старт---')
            start_day_energy_temp = float(tool.get_value('-ds 1'))

            # накопление во 2й Тариф
            logger.info('Накопление во 2й Тариф')
            if days % 5 == 0:
                calculated_date = ((datetime(2025, 1, 1, 00, 5, 00)) +
                               relativedelta(days=days + 1, seconds=-305)).strftime("%d.%m.%Y %H:%M:%S")
                logger.info(f'Установка даты: {calculated_date}')
                logger.info(f'Переход через границу суток в выключенном состоянии')
                tool.set_time(calculated_date)
                relay_block.block_off(8)
                wait.wait(10000)
                relay_block.block_on(8)
                wait.wait(wakeup)
            else:
                calculated_date = ((datetime(2025, 1, 1, 00, 5, 00)) +
                                   relativedelta(days=days + 1)).strftime("%d.%m.%Y %H:%M:%S")
                logger.info(f'Установка даты: {calculated_date}')
                tool.set_time(calculated_date)
                wait.wait(wakeup)

            if tool.get_value('-i 7') != '2':
                logger.error(f"Не установился 2й тариф")
                raise Exception
            relay_block.block_on(7)
            logger.info('накопление во 2й Тариф')
            wait.wait(7000 + randint(0, 10000)) #случайные накопления день ото дня
            relay_block.block_off(7)
            wait.wait(5000)
            energy_per_day_calc_t2 = [tool.get_value(f'-dm 5[](m2)')] + energy_per_day_calc_t2

            # накопление в 3й Тариф
            logger.info('Накопление в 3й Тариф')
            calculated_date = ((datetime(2025, 1, 1, 00, 5, 00)) +
                               relativedelta(days=days + 1, minutes=30)).strftime("%d.%m.%Y %H:%M:%S")
            logger.info(f'Установка даты: {calculated_date}')
            tool.set_time(calculated_date)
            wait.wait(1000)
            if tool.get_value('-i 7') != '3':
                logger.error(f"Не установился 3й тариф")
                raise Exception
            relay_block.block_on(7)
            logger.info('накопление в 3й Тариф')
            wait.wait(7000 + randint(0, 10000))  # случайные накопления день ото дня
            relay_block.block_off(7)
            wait.wait(2000)
            energy_per_day_calc_t3 = [tool.get_value(f'-dm 5[](m3)')] + energy_per_day_calc_t3

            if float(tool.get_value('-ds 1')) - start_day_energy_temp == 0:
                logger.error(f"Нет накоплений за сутки, "
                             f"накопления до включения нагрузки {start_day_energy_temp} "
                             f"накопления после выключения нагрузки {float(tool.get_value('-ds 1'))} "
                             f"накопления за текущие сутки {tool.get_value(f'-dm 5[]')} ")
                logger.info(tool.get_current_time())
                raise Exception

            if float(tool.get_value(f'-dm 5[]')) - float(tool.get_value('-ds 1')) - start_day_energy_temp <= 0.00011:
                energy_per_day_calc = [tool.get_value(f'-dm 5[]')] + energy_per_day_calc
            else:
                logger.error(f"Накопления за сутки и разница текущих не совпадают: "
                             f"накопления до включения нагрузки {start_day_energy_temp} "
                             f"накопления после выключения нагрузки {float(tool.get_value('-ds 1'))} "
                             f"накопления за текущие сутки {tool.get_value(f'-dm 5[]')} ")
                logger.info(tool.get_current_time())
                raise Exception

            # проверка на всю сформированную глубину
            if days > 0:
                # общая
                sum_energy_per_day = 0
                for index, value in enumerate(tool.get_value(f'-dm 5[0..{days}]')):
                    if abs(float(value) - float(energy_per_day_calc[index])) > 0.00011:
                        logger.error(f"Накопления расчетные и со счетчика не совпадают, "
                                     f"расчетные {energy_per_day_calc[index]} "
                                     f"со счетчика {value} "
                                     f"разница {float(value) - float(energy_per_day_calc[index])} ")
                        logger.info(f'Энергии за день расчетные   {energy_per_day_calc}')
                        logger.info(f"Энергии за день со счетчика {tool.get_value(f'-dm 5[0..{days}]')}")
                        raise Exception
                    sum_energy_per_day += float(value)

                # тариф 2
                sum_energy_per_day_t2: float = 0
                for index, value in enumerate(tool.get_value(f'-dm 5[0..{days}](m2)')):
                    if abs(float(value) - float(energy_per_day_calc_t2[index])) > 0.00011:
                        logger.error(f"Накопления расчетные и со счетчика для t2 не совпадают, "
                                     f"расчетные {energy_per_day_calc_t2[index]} "
                                     f"со счетчика {value} "
                                     f"разница {float(value) - float(energy_per_day_calc_t2[index])} ")
                        logger.info(f'Энергии за день расчетные   {energy_per_day_calc_t2}')
                        logger.info(f"Энергии за день со счетчика {tool.get_value(f'-dm 5[0..{days}](m2)')}")
                        raise Exception
                    sum_energy_per_day_t2 += float(value)

                # тариф 3
                sum_energy_per_day_t3: float = 0
                for index, value in enumerate(tool.get_value(f'-dm 5[0..{days}](m3)')):
                    if abs(float(value) - float(energy_per_day_calc_t3[index])) > 0.00011:
                        logger.error(f"Накопления расчетные и со счетчика для t2 не совпадают, "
                                     f"расчетные {energy_per_day_calc_t3[index]} "
                                     f"со счетчика {value} "
                                     f"разница {float(value) - float(energy_per_day_calc_t3[index])} ")
                        logger.info(f'Энергии за день расчетные   {energy_per_day_calc_t3}')
                        logger.info(f"Энергии за день со счетчика {tool.get_value(f'-dm 5[0..{days}](m3)')}")
                        raise Exception
                    sum_energy_per_day_t3 += float(value)

                if abs(sum_energy_per_day - sum_energy_per_day_t2 - sum_energy_per_day_t3) > 0.00021:
                    logger.error(f"Сумма энергий за день общая и по тарифам не сходятся "
                                 f"на {days} дне, "
                                 f"сумма общей {sum_energy_per_day} "
                                 f"сумма по т2 {sum_energy_per_day_t2} "
                                 f"сумма по т3 {sum_energy_per_day_t3}")
                    raise Exception

        # Проверка соответствия сумм
        full_energy_test: float = float(tool.get_value('-ds 1')) - start_energy
        logger.info(f'Накопление энергии A+ за тест {full_energy_test}')
        if abs(full_energy_test - sum_energy_per_day) > 0.00021:
            logger.error(f"Энергия за тест и сумма накjплений за сутки не сходятся "
                         f"Энергия за тест {full_energy_test} "
                         f"сумма накjплений за сутки {sum_energy_per_day} ")
            raise Exception

        logger.info(f'Проверка соответствий энегрий на начало дня и за день')
        energy_per_day_meter: List[float] = list(map(float, tool.get_value(f'-dm 5[0..127]')))
        # энергия на начало дня, пришлось разбить на 3 запроса из-за специфики SMP
        energy_start_day: list = list(map(float, tool.get_value('-dm 1[0..50]')))
        energy_start_day += list(map(float, tool.get_value('-dm 1[51..100]')))
        energy_start_day += list(map(float, tool.get_value('-dm 1[101..127]')))

        for i in range(len(energy_start_day) - 1):
            if not energy_start_day[i] - energy_start_day[i + 1] - energy_per_day_meter[i + 1] <= 0.00011:
                logger.error(
                    f'Накопления за день и на начало {i}-го дня не сходятся. Накопления с устройства: '
                    f'Энергии на начало дня:  {energy_per_day_meter} '
                    f'Энергии за день:  {energy_start_day} '
                )
                raise Exception

        logger.info(f'Энергии за день расчетные   {energy_per_day_calc}')
        logger.info(f"Энергии за день со счетчика {tool.get_value(f'-dm 5[0..127]')}")
        # энергия на начало дня, пришлось разбить на 3 запроса из-за специфики SMP
        energy_start_day = list(map(float, tool.get_value('-dm 1[0..50]')))
        energy_start_day += list(map(float, tool.get_value('-dm 1[51..100]')))
        energy_start_day += list(map(float, tool.get_value('-dm 1[101..127]')))
        logger.info(f"Энергии на начало дня {energy_start_day}")

        logger.info(f'Формирование дней без потребления')
        for continue_days in range(128, 150):
            calculated_date = ((datetime(2025, 1, 1, 00, 00, 00)) +
                               relativedelta(days=continue_days + 1)).strftime("%d.%m.%Y %H:%M:%S")
            logger.info(f'Установка даты: {calculated_date}')
            tool.set_time(calculated_date)
            wait.wait(10000)
            energy_per_day_calc = ['0.0'] + energy_per_day_calc
            if float(tool.get_value(f'-dm 5[{continue_days}..{continue_days}]')) != 0:
                logger.error(
                    f'Счётчик неверно записал накопленные значения. Cписок с устройства: '
                    f'{tool.get_value(f"-dm 5[{continue_days}..{continue_days}]")} должно быть 0'
                )
                raise Exception

        logger.info(f'Проверка соответствий энегрий на начало дня и за день (повторно)')
        energy_per_day_meter = list(map(float, tool.get_value(f'-dm 5[0..127]')))
        # энергия на начало дня, пришлось разбить на 3 запроса из-за специфики SMP
        energy_start_day: list = list(map(float, tool.get_value('-dm 1[0..50]')))
        energy_start_day += list(map(float, tool.get_value('-dm 1[51..100]')))
        energy_start_day += list(map(float, tool.get_value('-dm 1[101..127]')))

        for i in range(len(energy_start_day) - 1):
            if not energy_start_day[i] - energy_start_day[i + 1] - energy_per_day_meter[i + 1] <= 0.00011:
                logger.error(
                    f'Накопления за день и на начало {i}-го дня не сходятся. Накопления с устройства: '
                    f'Энергии на начало дня:  {energy_per_day_meter} '
                    f'Энергии за день:  {energy_start_day} '
                )
                raise Exception

        logger.warning(f'test {__name__} is \t OK')

    except Exception as ex:
        logger.warning(f'test {__name__} is \t Failure')
        logger.error(ex)
