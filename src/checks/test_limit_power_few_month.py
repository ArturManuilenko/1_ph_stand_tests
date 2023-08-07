import logging

import SMPCrossPlatform.src.wait as wait
from src.checks.test_configuration import TestConfiguration
from src.fixtures.test_limit_power_month_fixture import options_zone, t_mon, t_morn_start, t_evn_start

logger = logging.getLogger(__name__)

""" Основной смысл теста- это проверка накопления и сохранения лимитов мощности за несколько месяцев.
    Как при переходе через месяц во включенном состоянии,так и при выключенном.
"""


def test_limit_power_few_month(
    conf: TestConfiguration
) -> None:
    wakeup = conf.wake_up
    relay_block = conf.relay_block
    tool = conf.tool

    logger.info('CHECK LIMIT POWER IN A FEW MONTH')
    relay_block.all_off()
    relay_block.ave_on()
    wait.wait(wakeup)
    try:
        tool.auth()
        wait.wait(wakeup)
        tool.execute("-a 28")  # Обнуление максимумов мощности за расчетные периоды
        tool.execute("-os 84=[2:0:0:0:1] -a 2")  # ограничения активной потребляемой мощности
        for settings in options_zone:
            tool.execute(settings)
        wait.wait(2000)
        for day_step in range(9):
            tool.set_time(t_morn_start[day_step])
            wait.wait(65000)   # c 8:00 до 8:01 счетчик будет фиксировать превышение мощности
            tool.set_time(t_evn_start[day_step])
            wait.wait(65000)
            tool.set_time(t_mon[day_step])
            logger.info(f'Ретроспектива {day_step + 1}, {tool.get_value("-dm 35[0..11](0)")}')
        tool.set_time(t_morn_start[9])
        wait.wait(65000)
        tool.set_time(t_mon[10])  # в режиме сна #10
        relay_block.all_off()
        wait.wait(120000)
        relay_block.ave_on()
        wait.wait(wakeup)
        tool.set_time(t_morn_start[10])
        wait.wait(90000)
        tool.set_time(t_morn_start[11])
        wait.wait(90000)
        retro = tool.get_value("-dm 35[0..11](0)")
        logger.info(f'Последняя ретроспектива", {[float(i) for i in retro]}')
        if 0 in [float(i) for i in retro]:
            logger.error("накопления не сохраняются")
        else:
            logger.info("накопления сохраняются")
    except Exception as ex:
        logger.warning(f'test {__name__} is Failure')
        logger.error(ex)
