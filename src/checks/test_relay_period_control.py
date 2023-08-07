"""
Проверка возможности настройки промежутка времени (от 30 сек до 3600 сек) после срабатывания реле,
в течение которого счетчик не контролирует реле (только на возврат).

В тетсте реле размыкается по событию "Неправильный пароль",
после чего контролируется время до возврата реле в нормальное состояние.

Контроль для точек 30, 60 и 3600 сек
"""

import logging

import SMPCrossPlatform.src.smp_exception
from SMPCrossPlatform.src import wait
from time import time
from src.checks.test_configuration import TestConfiguration

logger = logging.getLogger(__name__)


def test_relay_period_control(
    conf: TestConfiguration
) -> None:
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    logger.info('Test relay period control')
    relay_block.all_off()
    relay_block.block_on(8)
    wait.wait(wakeup)

    # счетчик времени включения реле/нагрузки
    def wait_on_relay(timeout: int = 3700) -> int:
        print('Ожидание включения нагрузки...')
        start_time = time()
        while time() - start_time <= timeout:
            if float(tool.get_value('-ds 22')) >= 0.008:
                return int(time() - start_time)
        logger.error(f'Реле не замкнулось за : {timeout} секунд')
        logger.warning(f'test {__name__} is Failure')

    try:
        tool.auth()
        tool.execute("--t=40000 -a 5 -a 3")
        # дейстивя по событию - реле по неправильному паролю
        logger.info('Отправляю команды -os 125=[1:0:30] -os 168=[1:0:0:0:0:0:0] -a 2 -a 10=0')
        tool.execute('-os 125=[1:0:30] -os 168=[1:0:0:0:0:0:0] -a 2 -a 10=0 --t=12000')
        logger.info(f"-og 125={tool.get_value('-og 125')}")

        # проверка наличия нагрузки
        relay_block.block_on(7)
        wait.wait(2000)
        if float(tool.get_value('-ds 22')) < 0.008:
            logger.info('Проверка наличия нагрузки - fail')
            logger.error('Нагрузка не подключена/реле неисправно')
            logger.warning(f'test {__name__} is Failure')
        else:
            logger.info('Проверка наличия нагрузки - оk')

        logger.info('Старт цикла проверки')
        for pause_until_repeat in (30, 60, 3600):
            tool.auth()
            logger.info(f'Проверка для паузы до повторной проверки {pause_until_repeat}')
            logger.info(f'Отправляю команды -os 125=[1:0:{pause_until_repeat}] -a 2')
            tool.execute(f'-os 125=[1:0:{pause_until_repeat}] -a 2 --t=12000')
            logger.info(f"-og 125={tool.get_value('-og 125')}")

            # на сутки вперед чтобы избежать блокировки по паролю
            tool.set_time(int(tool.get_value('-og 1')) + 86400)

            # вызываю событие по неправильному паролю
            try:
                tool.auth('888888')
            except SMPCrossPlatform.src.smp_exception.SMPException as f:
                logger.info(f"Успешная ошибка авторизации {f} - ok")

            wait.wait(4000)  # минимальная задержка для реакции счетчика на событие

            time_on_relay: int = wait_on_relay(pause_until_repeat + 10)
            if abs(time_on_relay - pause_until_repeat) >= 5:
                logger.error(
                    f'Время возврата реле в нормальное состояние не соответствует заданному: {pause_until_repeat}, '
                    f'фактическое: {time_on_relay}'
                )
                logger.warning(f'test {__name__} is Failure')
            logger.info(f'Реле вернулось в нормальное состояние за {time_on_relay} - ok')
            logger.info(f'Проверка для паузы до повторной проверки {pause_until_repeat} - ok')

        relay_block.block_off(8)
        relay_block.block_off(7)
        logger.warning(f'test {__name__} is OK')

    except Exception as ex:
        logger.warning(f'test {__name__} is Failure')    #
        logger.error('', ex)
