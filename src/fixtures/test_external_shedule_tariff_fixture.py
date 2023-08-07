options_tarif_event = [
    # Загрузка режима тарификации A «внешняя, по временным зонам».
    '-os 10=[0:1:1:0:0:0]',
    '-os 70=[1:1:0:0]',
    '-os 43=[1:1:0:0:0:0:0:0:0:0]',
    '-os 44=[10:1:0:1:1:1:1:1:1:1]',
    [f" -os {_}=[0:0:0:0:0:0:0:0:0:0]" for _ in range(45, 67)],
    # Установить лимит мощности 1, остальные выключить
    '-os 72=[1:1:0:48:0:0]',
    [f' -os {_}=[0:0:0:0:0:0]' for _ in range(73, 84)],
    '-os 11=[1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1:1]',
    '-os 12=[2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2:2]',
    [f" -os {_}=[0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0]"
     for _ in range(13, 43)],
    '-os 67=[0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0]',
    [f" -os {_}=[0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0"
     f":0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0"
     f":0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0"
     f":0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0]"
     for _ in range(68, 70)]
]
