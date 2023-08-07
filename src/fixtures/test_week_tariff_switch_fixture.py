from typing import List, Union, Tuple

options_week: List[Union[str, List[str]]] = [
    # Загрузка режима тарификации AP только «по расписаниям».
    '-os 10=[0:0:1:0:0:0]',
    # перейти на группу ноль 1 января
    '-os 70=[1:1:1:0]',
    # Загрузка сезонных программ все отключены
    [f" -os {_}=[0:0:0:0:0:0:0:0:0:0]" for _ in range(44, 67)],  # 1-24
    # Загрузка дневных программ - все отключены.
    [f" -os {_}=[0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0]"
     for _ in range(11, 43)],  # 1-19
    # Загрузка особых дат - все отключены.
    '-os 67=[0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0]',
    [f" -os {_}=[0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0"
     f":0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0"
     f":0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0"
     f":0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0]"
     for _ in range(68, 69)],
    '-os 11=[1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1]',
    '-os 12=[2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2]',
    '-os 13=[3:3:3:3:3:3:3:3:3:3:3:3:3:3:3:3:3:3:3:3:3:3:3:3:3:3:3:3:3:3:3:3:3:3:3:3:3:3:3:3:3:3:3:3:3:3:3:3]',
    '-os 14=[4:4:4:4:4:4:4:4:4:4:4:4:4:4:4:4:4:4:4:4:4:4:4:4:4:4:4:4:4:4:4:4:4:4:4:4:4:4:4:4:4:4:4:4:4:4:4:4]',
    '-os 15=[5:5:5:5:5:5:5:5:5:5:5:5:5:5:5:5:5:5:5:5:5:5:5:5:5:5:5:5:5:5:5:5:5:5:5:5:5:5:5:5:5:5:5:5:5:5:5:5]',
    '-os 16=[6:6:6:6:6:6:6:6:6:6:6:6:6:6:6:6:6:6:6:6:6:6:6:6:6:6:6:6:6:6:6:6:6:6:6:6:6:6:6:6:6:6:6:6:6:6:6:6]',
    '-os 17=[7:7:7:7:7:7:7:7:7:7:7:7:7:7:7:7:7:7:7:7:7:7:7:7:7:7:7:7:7:7:7:7:7:7:7:7:7:7:7:7:7:7:7:7:7:7:7:7]',
    '-os 43=[7:1:0:0:1:2:3:4:5:6]',
    '-os 44=[14:1:0:2:2:2:2:2:2:2]',
    '-os 45=[4:3:0:4:4:4:4:4:4:4]',
    '-os 46=[11:3:0:6:5:4:3:2:1:0]'
]

w_day_prog: List[int] = [1, 2, 3, 4, 5, 6, 7]
# List[Sequence[Union[int, int, List[int]]]]
# List[Union[List[Union[Union[List[int]], int]]]]

w_prog: List[Tuple[int, int, List[int]]] = [
    (7, 1, [0, 1, 2, 3, 4, 5, 6]),
    (14, 1, [2, 2, 2, 2, 2, 2, 2]),
    (4, 3, [4, 4, 4, 4, 4, 4, 4]),
    (11, 3, [6, 5, 4, 3, 2, 1, 0]),
]