from typing import NamedTuple

from SMPCrossPlatform.smptool2 import SMPTool2
from one_ph_owen_stand.CapTool import CAPTool


class TestConfiguration(NamedTuple):
    wake_up: int
    tool: SMPTool2
    relay_block: CAPTool
    counter_com: str
