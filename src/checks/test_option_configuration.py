'''
Счетчик должен вести два варианта конфигурации - рабочую и фоновую - и обеспечивать выполнение следующих операций с конфигурациями:
- запись фоновой конфигурации в рабочую,
- запись рабочей конфигурации в фоновую,
- запись рабочей конфигурации в фоновую, а фоновой в рабочую,
- запись заводской конфигурации в рабочую.
Все изменения настроек (кроме технологических) ведутся в фоновой конфигурации.
Счетчик должен вести две контрольные суммы конфигураций
'''

import logging

from typing import NamedTuple, Dict, Callable, List, Any

import SMPCrossPlatform.src.smp_exception
from SMPCrossPlatform.src import wait

from src.checks.test_configuration import TestConfiguration
from src.fixtures.test_option_configuration_fixture import dict_of_options, \
    dict_of_change_options, dict_of_options_tech, dict_of_change_options_tech

logger = logging.getLogger(__name__)

def test_option_configuration(
    conf: TestConfiguration
) -> None:

    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    logger.info('Test option configuration')
    relay_block.all_off()
    relay_block.block_on(8)
    relay_block.block_off(7)
    wait.wait(wakeup)

    try:
        # TODO подготовка, приведение настроек к исходным
        logger.info('подготовка, приведение настроек к исходным')
        tool.auth()
        comand: str
        for index in dict_of_options:
            comand = dict_of_options[index]
            logger.info(f'Устанавливаю -os {index}={comand}')
            tool.execute(f'-os {index}={comand}')
        tool.execute('-a 2 --t=10000')

        logger.info('Проверяю что контрольные суммы рабочей и фоновой конфигураций не отличаются')
        if tool.get_value(f'-i 26') != tool.get_value(f'-i 28'):
            logger.error('Контрольные суммы рабочей и фоновой конфигураций отличаются')
            raise Exception

        # TODO запись технологических настроек в рабочую конфигурацию
        logger.info('Проверка записи технологических настроек в рабочую')
        tool.auth()

        logger.info('Устанавливаю исходные технологические настройки')
        for index in dict_of_options_tech:
            comand = dict_of_options_tech[index]
            logger.info(f'Устанавливаю -os {index}={comand}')
            tool.execute(f'-os {index}={comand}')
        tool.execute('-a 2 --t=10000')
        wait.wait(2000)

        logger.info('Устанавливаю измененные технологические настройки')
        for index in dict_of_options_tech:
            comand = dict_of_change_options_tech[index]
            logger.info(f'Устанавливаю -os {index}={comand}')
            tool.execute(f'-os {index}={comand}')

        logger.info('Поверяю что рабочая установилась (технологические)')
        for index in dict_of_options_tech:
            if tool.get_value(f'-og1 {index}') != dict_of_change_options_tech[index]:
                logger.error('Технологические настройки не записались в рабочую конфигурацию, '
                             f'og1 {index}= {tool.get_value(f"-og1 {index}")} '
                             f'должно быть {dict_of_change_options_tech[index]}')
                raise Exception

        logger.info('Проверяю что контрольные суммы рабочей и фоновой конфигураций не отличаются')
        if tool.get_value(f'-i 26') != tool.get_value(f'-i 28'):
            logger.error('Контрольные суммы рабочей и фоновой конфигураций отличаются')
            raise Exception

        # TODO запись фоновой конфигурации в рабочую
        logger.info('Проверка записи фоновой конфигурации в рабочую')
        tool.auth()

        logger.info('Устанавливаю измененные настройки')
        for index in dict_of_options:
            comand = dict_of_change_options[index]
            logger.info(f'Устанавливаю -os {index}={comand}')
            tool.execute(f'-os {index}={comand}')

        logger.info('Проверяю что контрольные суммы рабочей и фоновой конфигураций отличаются')
        if tool.get_value(f'-i 26') == tool.get_value(f'-i 28'):
            logger.error('Контрольные суммы рабочей и фоновой конфигураций не отличаются')
            raise Exception

        logger.info('Поверяю что фоновая установилась')
        for index in dict_of_options:
            if tool.get_value(f'-og {index}') != dict_of_change_options[index]:
                logger.error('Настройки не записались в фоновую конфигурацию, '
                             f'og {index}={tool.get_value(f"-og {index}")} '
                             f'должно быть {dict_of_change_options[index]}')
                raise Exception

        logger.info('Поверяю что рабочая не изменилась')
        for index in dict_of_options:
            if tool.get_value(f'-og1 {index}') != dict_of_options[index]:
                logger.error('Изменилась рабочая конфигурация, '
                             f'og1 {index}= {tool.get_value(f"-og1 {index}")} '
                             f'должно быть {dict_of_options[index]}')
                raise Exception

        logger.info('Копирую фоновую в рабочую -a 2')
        tool.execute('-a 2')

        logger.info('Поверяю что фоновая скопировалась в рабочую')
        for index in dict_of_options:
            if tool.get_value(f'-og1 {index}') != dict_of_change_options[index]:
                logger.error('Фоновая не скопировалась в рабочую, '
                             f'og1 {index}= {tool.get_value(f"-og1 {index}")} '
                             f'должно быть {dict_of_change_options[index]}')
                raise Exception

        # TODO запись рабочей конфигурации в фоновую
        logger.info('Проверка записи рабочей конфигурации в фоновую')
        tool.auth()

        logger.info('Подготовка, приведение настроек к исходным')
        tool.auth()
        comand: str
        for index in dict_of_options:
            comand = dict_of_options[index]
            logger.info(f'Устанавливаю -os {index}={comand}')
            tool.execute(f'-os {index}={comand}')
        tool.execute('-a 2 --t=10000')

        logger.info('Устанавливаю измененные настройки')
        for index in dict_of_options:
            comand = dict_of_change_options[index]
            logger.info(f'Устанавливаю -os {index}={comand}')
            tool.execute(f'-os {index}={comand}')

        logger.info('Поверяю что фоновая установилась')
        for index in dict_of_options:
            if tool.get_value(f'-og {index}') != dict_of_change_options[index]:
                logger.error('Настройки не записались в фоновую конфигурацию, '
                             f'og {index}={tool.get_value(f"-og {index}")} '
                             f'должно быть {dict_of_change_options[index]}')
                raise Exception

        logger.info('Отменяю настройки -a 3')
        tool.execute('-a 3')

        logger.info('Поверяю что рабочая не изменилась')
        for index in dict_of_options:
            if tool.get_value(f'-og1 {index}') != dict_of_options[index]:
                logger.error('Изменилась рабочая конфигурация, '
                             f'og1 {index}= {tool.get_value(f"-og1 {index}")} '
                             f'должно быть {dict_of_options[index]}')
                raise Exception

        logger.info('Поверяю что фоновая вернулась к исходной')
        for index in dict_of_options:
            if tool.get_value(f'-og {index}') != dict_of_options[index]:
                logger.error('Фоновая конфигурация не вернулась к исходной , '
                             f'og {index}= {tool.get_value(f"-og {index}")} '
                             f'должно быть {dict_of_options[index]}')
                raise Exception

        # TODO запись рабочей конфигурации в фоновую, а фоновой в рабочую
        logger.info('Проверка рабочей конфигурации в фоновую, а фоновой в рабочую')
        tool.auth()

        logger.info('Устанавливаю измененные настройки')
        for index in dict_of_options:
            comand = dict_of_change_options[index]
            logger.info(f'Устанавливаю -os {index}={comand}')
            tool.execute(f'-os {index}={comand}')

        logger.info('Поверяю что фоновая установилась')
        for index in dict_of_options:
            if tool.get_value(f'-og {index}') != dict_of_change_options[index]:
                logger.error('Настройки не записались в фоновую конфигурацию, '
                             f'og {index}={tool.get_value(f"-og {index}")} '
                             f'должно быть {dict_of_change_options[index]}')
                raise Exception

        logger.info('Поверяю что рабочая не изменилась')
        for index in dict_of_options:
            if tool.get_value(f'-og1 {index}') != dict_of_options[index]:
                logger.error('Изменилась рабочая конфигурация, '
                             f'og1 {index}= {tool.get_value(f"-og1 {index}")} '
                             f'должно быть {dict_of_options[index]}')
                raise Exception

        logger.info('Меняю рабочую конфигурацию с фоновой -a 4')
        tool.execute('-a 4')

        logger.info('Поверяю что фоновая установилась = рабочей')
        for index in dict_of_options:
            if tool.get_value(f'-og {index}') != dict_of_options[index]:
                logger.error('Настройки не записались в фоновую конфигурацию, '
                             f'og {index}={tool.get_value(f"-og {index}")} '
                             f'должно быть {dict_of_options[index]}')
                raise Exception

        logger.info('Поверяю что рабочая установилась = фоновой')
        for index in dict_of_options:
            if tool.get_value(f'-og1 {index}') != dict_of_change_options[index]:
                logger.error('Изменилась рабочая конфигурация, '
                             f'og1 {index}= {tool.get_value(f"-og1 {index}")} '
                             f'должно быть {dict_of_change_options[index]}')
                raise Exception

        # TODO запись заводской конфигурации в рабочую
        logger.info('Проверка записи заводской конфигурации в рабочую')
        tool.execute(f'-os 1={int(tool.get_value("-og 1")) + 86400}')
        tool.auth()
        wait.wait(2000)

        logger.info("Формирую список настроек заводской конфигурации")
        logger.info("Первичная инициализация счетчика -a 44")
        tool.execute('-a 44 --t=10000')
        wait.wait(2000)
        dict_of_defolt_options = {}
        for index in dict_of_options:
            dict_of_defolt_options[index] = tool.get_value(f'-og {index}')
        logger.info(f'Настройки по дефолту {dict_of_defolt_options}')

        logger.info('Устанавливаю измененные настройки')
        for index in dict_of_options:
            comand = dict_of_change_options[index]
            logger.info(f'Устанавливаю -os {index}={comand}')
            tool.execute(f'-os {index}={comand}')

        logger.info('Копирую фоновую в рабочую -a 2')
        tool.execute('-a 2')

        logger.info('Поверяю что рабочая установилась')
        for index in dict_of_options:
            if tool.get_value(f'-og1 {index}') != dict_of_change_options[index]:
                logger.error('Настройки не записались в фоновую конфигурацию, '
                             f'og1 {index}={tool.get_value(f"-og1 {index}")} '
                             f'должно быть {dict_of_change_options[index]}')
                raise Exception

        logger.info('Установливаю заводскую конфигурацию -a 5')
        tool.execute('-a 5')

        logger.info('Поверяю что рабочая установилась = заводской')
        for index in dict_of_options:
            if tool.get_value(f'-og1 {index}') != dict_of_defolt_options[index]:
                logger.error('Рабочая конфигурация не равна заводской, '
                             f'og1 {index}= {tool.get_value(f"-og1 {index}")} '
                             f'должно быть {dict_of_defolt_options[index]}')
                raise Exception

        relay_block.block_off(8)
        relay_block.block_off(7)
        logger.warning(f'test {__name__} is \t OK')

    except Exception as ex:
        logger.warning(f'test {__name__} is \t Failure')
        logger.error(ex)
