options_tariff_both = [
    # Загрузка режима тарификации AP «по событиям».
    '-os 10=[1:0:0:0:0:0]',
    # Расписение контроля мощности 1
    '-os 72=[1:1:0:48:0:0]',
    # Настройки контроля лимитов активной мощности: -без ограничения, 1 мин, 50%, 1 тариф, контроль включен
    '-os 84=[0:0:0:1:1]',
    # Лимиты активной мощности утренний и вечерний
    '-os 85=0.001',
    '-os 97=0.001',
    # Установка действия по ограничению лимита мощности на 7 тариф
    '-os 152=[0:0:0:0:0:0:7]',
]
