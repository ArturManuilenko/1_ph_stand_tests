import argparse
import logging
import os
import platform
import sys
from datetime import date
from typing import NamedTuple, Dict, Callable, List, Any

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.checks.test_configuration import TestConfiguration
from src.checks.test_check_system import test_counter_connect
from src.checks.test_accumulation_day_energy import test_accumulation_day_energy
from src.checks.test_time_limits import test_time_limits
from src.checks.test_event_general_tariff import test_event_general_tariff
from src.checks.test_external_general_tariff import test_external_general_tariff
from src.checks.test_external_shedule_tariff import test_external_shedule_tariff
from src.checks.test_external_tarification import test_external_tarification
from src.checks.test_intervals_profiles import test_intervals_profiles
from src.checks.test_month_profiles import test_month_profiles
from src.checks.test_special_date_switch import test_special_date_switch
from src.checks.test_tariff_a_a_plus import test_tariff_a_a_plus
from src.checks.test_tariff_group import test_tariff_group
from src.checks.test_check_tariff_on_timezone import test_tariff_timezone
from src.checks.test_time_correction_wo_command import test_time_correction_wo_command
from src.checks.test_year_profiles import test_year_profiles
from src.checks.test_special_date_switch_tariff import test_special_date_switch_tariff
from src.checks.test_week_tariff_switch import test_week_tariff_switch
from src.checks.test_week_tariff import test_week_tariff
from src.checks.test_power_limit_schedule import test_power_limit_schedule
from src.checks.test_max_power_month import test_max_power_month
from src.checks.test_limits_power_on_schedule import test_limits_power_on_schedule
from src.checks.test_limit_power_on_without_tariff import test_limit_power_on_without_tariff
from src.checks.test_limit_power_on_tariff import test_limit_power_on_tariff
from src.checks.test_special_date_control import test_special_date_control
from src.checks.test_absolute_special_date import test_absolute_special_date
from src.checks.test_ten_years_summary_energy import test_ten_years_summary_energy
from src.checks.test_ten_years_profiles import test_ten_years_profiles
from src.checks.test_storage_depth_tariff import test_storage_depth_tariff
from src.checks.test_storage_depth_public import test_storage_depth_public
from src.checks.test_interval_integrate_energy import test_interval_integrate_energy
from src.checks.test_storage_max_active_power import test_storage_max_active_power
from src.checks.test_day_energy_storage import test_day_energy_storage
from src.checks.test_day_energy_storage_tariff import test_day_energy_storage_tariff
from src.checks.test_updating_readings import test_updating_readings
from src.checks.test_check_all_commands import test_check_all_commands
from src.checks.test_storage_max_power_without_time_limit import test_storage_max_power_without_time_limit
from src.checks.test_storage_max_power_tariff import test_storage_max_power_tariff
from src.checks.test_event_schedule_tariff import test_event_schedule_tariff
from src.checks.test_set_end_period_date import test_set_end_period_date
from src.checks.test_abonent_params import test_abonent_params

from src.checks.test_auto_correct_time_full import test_auto_correct_time_full
from src.checks.test_relay_period_control import test_relay_period_control
from src.checks.test_change_winter_summer_auto import test_change_winter_summer_auto
from src.checks.test_change_winter_summer_date_time import test_change_winter_summer_date_time
from src.checks.test_option_configuration import test_option_configuration

from SMPCrossPlatform.smptool2 import SMPTool2
from one_ph_owen_stand.CapTool import CAPTool
CWD = os.getcwd()
sys.path.append(CWD)

LOGGING_DIR = os.path.join(CWD, '.var', 'logging')

logger = logging.getLogger(__name__)

DEBUG_FILEHANDLER = logging.FileHandler(f"LOGGING_DIR/{date.today()}-SMP_DEBUG.txt")
INFO_FILEHANDLER = logging.FileHandler(f"LOGGING_DIR/{date.today()}-SMP_INFO.txt")
WARNING_FILEHANDLER = logging.FileHandler(f"LOGGING_DIR/{date.today()}-SMP_TESTS.txt")
ERROR_FILEHANDLER = logging.FileHandler(f"LOGGING_DIR/{date.today()}-SMP_ERRORS.txt")

DEVICE_NAME__GL_1 = 'GL1'
DEVICE_NAME__L_1 = 'L1'
DEVICE_NAME__L_2 = 'L2'
DEVICE_NAME__CL_1 = 'CL1'
DEVICE_NAME__CL_1_485 = 'CL1-485'
DEVICE_NAME__CL_2 = 'CL2'
DEVICE_NAME__GL_2 = 'GL2'

DEVICE_NAME_SET = {
    DEVICE_NAME__GL_1,
    DEVICE_NAME__L_1,
    DEVICE_NAME__L_2,
    DEVICE_NAME__CL_1,
    DEVICE_NAME__CL_1_485,
    DEVICE_NAME__CL_2,
    DEVICE_NAME__GL_2
}


class LevelFilter(logging.Filter):
    def __init__(self, level: int) -> None:
        super().__init__()
        self.level = level

    def filter(self, record: Any) -> bool:
        return record.levelno == self.level


class CmdTestConfigure(NamedTuple):
    device: str
    wake_up: int
    stand_port: str
    counter_port: str
    counter_mac: str
    test_repeats: int
    timeout: str
    repeats: int
    nolog: str
    channel: str
    ip: str
    method: str
    password: str
    tests: List[str]

    @property
    def checks(self) -> List[str]:
        checks = set()
        for t in self.tests:
            if t == '*':
                return list(TESTS_MAP.keys())
            checks.add(t)
        return list(checks)

    @staticmethod
    def add_parser_args(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--wakeup', dest="wake_up", type=int, default=5, required=True,
                            help='Time to counter started: from 1 to 5 second')
        parser.add_argument('--device', dest="device", choices=tuple(DEVICE_NAME_SET), type=str, required=True,
                            help='Device name')
        parser.add_argument('--stand_comport', dest="stand_port", type=str, required=True, help='1ph stand port')
        parser.add_argument('--test_repeats', dest="test_repeats", type=str, required=True, help='repeat times tests')
        parser.add_argument('--counter_comport', dest="counter_port", type=str, required=True, help='counter port')
        parser.add_argument('--counter_mac', dest="counter_mac", default='0', type=str, required=False, help='mac')
        parser.add_argument('--timeout', dest="timeout", default='150', type=str, required=False,
                            help='repeats timeout')
        parser.add_argument('--repeats', dest="repeats", default='1', type=str, required=False, help='repeats times')
        parser.add_argument('--nolog', dest="nolog", default='nolog', type=str, required=False,
                            help='SMP log (nolog or log)')
        parser.add_argument('--ip', dest="ip", default='', type=str, required=False, help='ip address - for TCP/IP')
        parser.add_argument('--method', dest="method", type=str, required=True,
                            help='Connect method: direct = opto, plc - for radio/plc, tcp/ip - ethernet')
        parser.add_argument('--password', dest="password", type=str, required=False, default='777777',
                            help='Counter password')
        parser.add_argument('--tests', dest='tests', type=str, nargs='?', choices=('*', *TESTS_MAP.keys()), default='*',
                            required=False,
                            help='test list')
        parser.add_argument('--channel', dest="channel", type=str, required=False, help='Counter channel', default='')

    def run(self) -> None:
        print(f'TESTS: {",".join(self.checks)}')
        logger.debug('Autotests beginning')
        if platform.system() == "Windows":
            relay_block = CAPTool(port=f'COM{self.stand_port}')
            counter_com = f'COM{self.counter_port}'
        else:
            relay_block = CAPTool(port=f'/dev/ttyUSB{self.stand_port}')
            counter_com = f'ttyUSB{self.counter_port}'

        tool_params = dict(
            com=counter_com,
            mac=self.counter_mac,
            timeout=self.timeout,
            repeats=int(self.repeats),
            nolog=self.nolog,
            channel=self.channel,
            ip=self.ip,
            method=self.method,
            password=self.password
        )

        tool = SMPTool2(**tool_params)

        conf = TestConfiguration(
            wake_up=self.wake_up * 1000,
            tool=tool,
            relay_block=relay_block,
            counter_com=counter_com,
        )
        for test_repeats in range(int(self.test_repeats)):
            for test_id in self.checks:
                try:
                    TESTS_MAP[test_id](conf)
                except Exception as e:
                    logger.error(f'Error test: {test_id} repeat: {test_repeats}, error: {e}')
                    logger.warning(f'Test {test_id} is Failure')


TESTS_MAP: Dict[str, Callable[[TestConfiguration], None]] = {
        'test_counter_connect': test_counter_connect,
        'test_accumulation_day_energy': test_accumulation_day_energy,
        'test_tariff_timezone': test_tariff_timezone,
        'test_absolute_special_date': test_absolute_special_date,
        'test_time_limits': test_time_limits,
        'test_event_general_tariff': test_event_general_tariff,
        'test_external_general_tariff': test_external_general_tariff,
        'test_external_schedule_tariff': test_external_shedule_tariff,
        'test_external_tarification': test_external_tarification,
        'test_intervals_profiles': test_intervals_profiles,
        'test_month_profiles': test_month_profiles,
        'test_special_date_switch': test_special_date_switch,
        'test_tariff_a_a_plus': test_tariff_a_a_plus,
        'test_tariff_group': test_tariff_group,
        "test_special_date_control": test_special_date_control,
        'test_time_correction_wo_command': test_time_correction_wo_command,
        'test_year_profiles': test_year_profiles,
        'test_special_date_switch_tariff': test_special_date_switch_tariff,
        'test_week_tariff_switch': test_week_tariff_switch,
        'test_week_tariff': test_week_tariff,
        'test_power_limit_schedule': test_power_limit_schedule,
        'test_max_power_month': test_max_power_month,
        'test_limits_power_on_schedule': test_limits_power_on_schedule,
        'test_limit_power_on_without_tariff': test_limit_power_on_without_tariff,
        'test_limit_power_on_tariff': test_limit_power_on_tariff,
        'test_ten_years_summary_energy': test_ten_years_summary_energy,
        'test_ten_years_profiles': test_ten_years_profiles,
        'test_storage_depth_tariff': test_storage_depth_tariff,
        'test_storage_depth_public': test_storage_depth_public,
        'test_interval_integrate_energy': test_interval_integrate_energy,
        'test_storage_max_active_power': test_storage_max_active_power,
        'test_day_energy_storage': test_day_energy_storage,
        'test_day_energy_storage_tariff': test_day_energy_storage_tariff,
        'test_updating_readings': test_updating_readings,
        'test_check_all_commands': test_check_all_commands,
        'test_storage_max_power_without_time_limit': test_storage_max_power_without_time_limit,
        'test_storage_max_power_tariff': test_storage_max_power_tariff,
        'test_event_schedule_tariff': test_event_schedule_tariff,
        'test_set_end_period_date': test_set_end_period_date,
        'test_abonent_params': test_abonent_params,
        'test_auto_correct_time_full': test_auto_correct_time_full,
        'test_relay_period_control': test_relay_period_control,
        'test_change_winter_summer_date_time': test_change_winter_summer_date_time,
        'test_change_winter_summer_auto': test_change_winter_summer_auto,
        'test_option_configuration': test_option_configuration,
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--log', type=str, default='DEBUG', required=False, help='Added logging info by default')
    cmd_parser = parser.add_subparsers(required=True, dest='cmd')

    CmdTestConfigure.add_parser_args(cmd_parser.add_parser('test_configure'))

    args = dict(vars(parser.parse_args()))

    cmd = str(args.pop('cmd'))
    log = str(args.pop('log'))

    DEBUG_FILEHANDLER.addFilter(LevelFilter(logging.DEBUG))
    INFO_FILEHANDLER.addFilter(LevelFilter(logging.INFO))
    WARNING_FILEHANDLER.addFilter(LevelFilter(logging.WARNING))
    ERROR_FILEHANDLER.addFilter(LevelFilter(logging.ERROR))

    logging.basicConfig(
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        handlers=[DEBUG_FILEHANDLER, INFO_FILEHANDLER, WARNING_FILEHANDLER, ERROR_FILEHANDLER],
        level=log
    )

    if cmd == 'test_configure':
        CmdTestConfigure(**args).run()


if __name__ == "__main__":
    main()
