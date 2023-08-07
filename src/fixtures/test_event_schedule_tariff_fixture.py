options_tariff_both = [
    # Загрузка режима тарификации AP «по событиям, по расписанию».
    '-os 10=[1:0:1:0:0:0]',
    # Программа 1 с 01.01, в Программе 1 все тарифы 1
    '-os 43=[1:1:0:0:0:0:0:0:0:0]',
    '-os 11=[0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0]',
    # с 1 января контроль мощности 0,001 кВт, действие по событию - переход на 8 тариф
    '-os 72=[1:1:0:48:0:0]',
    '-os 84=[0:0:0:1:1]',
    '-os 85=0.001',
    '-os 152=[0:0:0:0:0:0:8]',
]
