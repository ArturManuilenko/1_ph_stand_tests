import logging
import sys

import SMPCrossPlatform.smptool2
from SMPCrossPlatform.src.wait import wait

from src.checks.test_configuration import TestConfiguration

logger = logging.getLogger(__name__)


def test_counter_connect(
        conf: TestConfiguration
) -> None:
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    logger.warning('Test counter connect and check system started')
    logger.info("Check counter")
    relay_block.all_off()
    relay_block.block_on(8)
    wait(wakeup)

    try:
        try:
            tryings = 0
            while tryings < 10:
                logger.info('send command -i 5')
                try:
                    tryings = tryings + 1
                    if 'Error: no answer' in tool.get_value('-i 5'):
                        continue
                    else:
                        break

                except Exception:
                    continue

            if 3 < tryings < 10:
                logger.error('Низкое качество соединения с устройством')
                raise SMPCrossPlatform.smptool2.SMPException(
                    'Низкое качество соединения с устройством', f'Попытки соединиться: {tryings}. Завершение проверок')
            if tryings == 10:
                logger.error('Соединиться с устройством не удалось')
                raise SMPCrossPlatform.smptool2.SMPException(
                    f'Устройство не отвечает', f'Попыток соединиться: {tryings}. Завершение проверок')
            else:
                logger.info('Устройство установлено, отвечает корректно')
        except Exception as e:
            logger.error(f'Ошибка проверки устройства: {e}')
            sys.exit()

        logger.info('Checking lamp')

        try:
            relay_block.block_on(7)
            wait(wakeup)
            current_power = float(tool.get_value("-ds 14"))
            voltage = float(tool.get_value("-ds 24"))
            battery_voltage = float(tool.get_value('-ds 32'))

            if battery_voltage < 2.9:
                logger.error(f"Низкий заряд батареи устройства {battery_voltage}")
                raise ValueError(f"Низкий заряд батареи устройства {battery_voltage}")
            if current_power < 0.075:
                logger.error(
                    f"Перегоревшая лампа либо не откалиброванный счётчик, мощность лампы: {current_power}"
                )
                raise ValueError(f"Перегоревшая лампа либо не откалиброванный счётчик, мощность лампы: {current_power}")
            if voltage > 240:
                logger.error(
                    f"Слишком высокое напряжение сети: {voltage}")
                raise ValueError(f"Слишком высокое напряжение сети: {voltage}")
            logger.info(f'Лампа работает, счётчик откалиброван, мощность {current_power * 1000}Вт')

            relay_block.block_off(7)
        except Exception as ex:
            logger.error(f'Ошибка проверки ламп либо счётчика: {ex}')
            relay_block.all_off()
            sys.exit()
        logger.warning(f'test {__name__} is OK')
    except Exception as e:
        logger.warning(f'test {__name__} is failure, {e}')
