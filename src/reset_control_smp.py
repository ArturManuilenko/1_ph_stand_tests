# import traceback
# from typing import List, Set
#
# from Utils.report import report
# import time
#
# getinfo = list(range(1, 43))  # 36 - ERROR
#
# getoption = list(range(1, 301))  # 148 - ERROR because 'unknown SMP CODE'
#
# getdatas = [13, 14] + [16] + [18] + list(range(22, 43)) + [44] + [49]
# getdatas_m = range(1, 13)
#
# getdatam = list(range(25, 35)) + [55] + [56]
# getdatam_m = list(range(1, 25)) + [35]
#
# getdatam_js = range(1, 98)
#
# getdatam_j = 200
#
# long_requests = 0
#
# journ_CE208_dop = [58, 59, 92, 116, 117, 118, 119, 120]
# journ_CE208 = [46, 58, 59, 92]
#
# journal_decoder = {
#
#     0: 'Nothing',
#     1: 'Successful self-diagnostic',
#     2: 'Switch to winter time',
#     3: 'Switch to summer time',
#     4: 'Internal clock sync',
#     5: 'Flash over interface',
#     6: 'Ручная коррекция времени',
#     7: 'изменение поправки суточного хода часов',
#     8: 'включение разрешения перехода зима\лето',
#     9: 'отключение разрешения перехода зима\лето',
#     10: 'изменение дат и времени перехода зима\лето\зима',
#     11: 'изменение конфигурации',
#     12: 'полная очистка EEPROM',
#     13: 'обнуление тарифных накопителей',
#     14: 'обнуление накоплений за интервалы',
#     15: 'сброс паролей',
#     16: 'сброс счетчика времени отсутствия питания',
#     17: 'сброс счетчика времени возд. магнитом',
#     18: 'сброс счетчика времени пониж. питания',
#     19: 'сброс счетчика времени повыш. питания',
#     20: 'Сброс счетчика времени отклонения частоты сети за порог',
#     21: 'сброс счетчика времени превышения тока по нейтрали',
#     22: 'сброс счетчика времени сверхлимитной мощности',
#     23: 'изменение калибровки линейного канала',
#     24: 'изменение калибровки канала по нейтрали',
#     25: 'изменение разрядности данных на ЖКИ',
#     26: 'изменение способа тарификации',
#     27: 'изменение тарифных расписаний',
#     28: 'смена актуальной группы сезонных расписаний',
#     29: 'изменение профиля контроля мощности',
#     30: 'разрешение контроля мощности',
#     31: 'изменение способа контроля мощности',
#     32: 'изменение расписаний зон максимумов',
#     33: 'изменение лимитов мощности',
#     34: 'изменение лимитов потребления',
#     35: 'изменение нижнего порога напряжения',
#     36: 'изменение верхнего порога напряжения',
#     37: 'Изменение порога частоты сети',
#     38: 'изменение порога дифференциального тока или тока по нейтрали',
#     39: 'Изменение порога малого потребления',
#     40: 'Пополнение оплаты энергии',
#     41: 'разрешение контроля лимита энергии',
#     42: 'изменение нормального состояния реле',
#     43: 'изменение настроек реле нагрузки',
#     44: 'изменение настроек реле сигнализации',
#     45: 'перепрограммирование условий изменения состояния реле нагрузки',
#     46: 'Неудачная самодиагностика',
#     47: 'возврат реле нагрузки в норму кнопкой',
#     48: 'возврат реле сигнализации в норму кнопкой',
#     49: 'изменение настроек звукового сигнала',
#     50: 'перепрограммирование условий изменения состояния реле сигнализации',
#     51: 'изменение условий срабатывания звукового сигнала',
#     53: 'изменение условий сигнализации по интерфейсу',
#     54: 'изменение настроек оптопорта',
#     55: 'изменение настроек оперативного канала',
#     56: 'изменение настроек режимов индикации',
#     57: 'изменение настроек групп индикации',
#     58: 'Неудачная самодиагностика встроенных часов',
#     59: 'Нештатные автостарты счетчика',
#     60: 'пропало внешнее питание',
#     61: 'появилось внешнее питание',
#     62: 'начало провала напряжения',
#     63: 'окончание провала напряжения',
#     64: 'начало превышения лимита напряжения',
#     65: 'окончание превышения лимита напряжения',
#     66: 'начало выхода частоты сети за заданный порог',
#     67: 'окончание выхода частоты сети за заданный порог',
#     68: 'начало превышения лимитов мощности',
#     69: 'окончание превышения лимитов мощности',
#     70: 'превышение лимита энергии 1',
#     71: 'превышение лимита энергии 2',
#     72: 'превышение лимита энергии 3',
#     73: 'блокировка по неверному паролю',
#     74: 'обращение по неверному паролю',
#     75: 'Исчерпание суточного лимита работы от батареи',
#     76: 'начало воздействия магнитом',
#     77: 'окончание воздействия магнитом',
#     78: 'нарушение электронной пломбы клеммной крышки, вскрытие',
#     79: 'восстановление электронной пломбы клеммной крышки',
#     80: 'нарушение электронной пломбы кожуха',
#     81: 'восстановление электронной пломбы кожуха',
#     82: 'начало превышения порога дифтока по нейтрали',
#     83: 'окончание превышения порога дифтока по нейтрали',
#     84: 'превышение лимита рассинхронизации времени',
#     85: 'критическое расхождение времени',
#     86: 'изменение состояния реле нагрузки',
#     87: 'изменение состояния реле сигнализации',
#     88: 'Начало нарушения схемы электроустановки потребителя',
#     89: 'Окончание нарушения схемы электроустановки потребителя',
#     90: 'перегрев счетчика, начало',
#     91: 'перегрев счетчика, окончание',
#     92: 'Неудачная самодиагностика памяти',
#     93: 'Принудительное включение реле нагрузки',
#     94: 'Низкий ресурс батареи',
#     95: 'восстановление рабочего напряжения батареи',
#     96: 'Низкое потребление',
#     97: 'Сброс признака низкого потребления',
#     98: 'Контроль подсоединённой измерительной цепи: кз (начало)',
#     99: 'Контроль подсоединённой измерительной цепи: кз (окончание)',
#     100: 'Контроль подсоединённой измерительной цепи: обрыв (начало)',
#     101: 'Контроль подсоединённой измерительной цепи: обрыв (окончание)',
#     102: 'Обратный поток (начало)',
#     103: 'Обратный поток (окончание)',
#     104: 'Сигнализация 1 (начало)',
#     105: 'Сигнализация 1 (окончание)',
#     106: 'Сигнализация 2 (начало)',
#     107: 'Сигнализация 2 (окончание)',
#     108: 'Смена пароля в сумматоре',
#     109: 'Неудачная самодиагностика',
#     110: 'Сброс сумматора: 0-Power(норма), 1-MCLR, 2-BOR, 3-WDTTO, 4-WDTWU 5-WU, 6-LVD, 7-RI',
#     111: 'Начало воздействия магнитом (сумматор)',
#     112: 'Конец воздействия магнитом (сумматор)',
#     113: 'изменение настроек индикации',
#     114: 'изменение калибровки',
#     115: 'изменение параметров тарификации',
#     116: 'Неудачная самодиагностика измерительного блока',
#     117: 'Неудачная самодиагностика вычислительного блока',
#     118: 'Неудачная самодиагностика блока питания',
#     119: 'Неудачная самодиагностика дисплея',
#     120: 'Неудачная самодиагностика радио',
#     121: 'превышение верхнего лимита тока, начало',
#     122: 'превышение верхнего лимита тока, окончание',
#     123: 'снижение тока ниже нижнего лимита',
#     127: 'Ошибка. Дальше данных нет.',
#     128: 'Превышение % от лимита мощности (только для сигнализации по интерфейсу)',
#     129: 'Превышение лимита прогнозируемой мощности (только для сигнализации по интерфейсу)',
#     131: 'Превышение % от лимита энергии 1 (только для сигнализации по интерфейсу)',
#     132: 'Зона контроля максимума мощности (только для сигнализации по интерфейсу)',
#     133: 'Существенное оперативное событие (только для сигнализации по интерфейсу)',
#     169: 'Воздействие радиополем. Начало.',
#     170: 'Воздействие радиополем. Окончание.',
#     191: 'Воздействие переменным магнитным полем. Начало.',
#     192: 'Воздействие переменным магнитным полем. Окончание.',
#
# }
#
# journ_list_CE208 = [
#     [46, 0, "Bad diagnostic"],  #
#     [58, 0, "Error RTC"],  #
#     [59, 0, "Bad autostart"],  #
#     [92, 0, "Bad memory"],  #
#     [94, 0, "Low Battery"],  #
# ]
#
#
# class Note:
#
#     def __init__(self, note_type, date, par=0):
#         self.note_type = note_type
#         self.date = date
#         self.par = par
#
#     def __repr__(self):
#         if self.par:
#             return '<Journal note at {} "{}" "{}">'.format(self.date,
#                                                            journal_decoder.get(self.note_type, 'UNKNOWN-{}'.format(
#                                                                self.note_type)),
#                                                            self.par)
#         return '<Journal note at {} "{}">'.format(self.date, journal_decoder.get(self.note_type,
#                                                                                  'UNKNOWN-{}'.format(self.note_type)))
#
#     def __hash__(self):
#         return hash((self.note_type, self.date, self.par))
#
#     def __eq__(self, other: 'Note'):
#         return self.note_type == other.note_type and self.date == other.date and self.par == other.par
#
#
# class ResetJournal:
#     def __init__(self, stand_tool, counter_tool, wake_up_time) -> None:
#         self.wakeup = wake_up_time
#         self.relay_block = stand_tool
#         self.tool = counter_tool
#
#     def get_bad_journals(self, bad_list=None):
#         notes = []
#         try:
#             self.tool.deauth()  # деавторизация, чтобы не стирать ошибки
#             if bad_list is not None:
#                 journ_list = bad_list
#             else:
#                 journ_list = journ_list_CE208
#
#             for a in journ_list:
#                 j_bad = self.tool.get_value(
#                     "-dm 201[0..10]({:02d})".format(a[0]))  # считывание журнала, 10 последних записей
#                 for b in j_bad:
#                     b.number = a[0]
#                 notes.extend([n.to_note for n in j_bad])
#
#         except Exception as ex:
#             report.error('', ex)
#
#         return notes
#
#     def get_all_journal_notes(self):
#         # logger.info('Gett all journal notes')
#         notes: List[Note] = []
#         try:
#             self.tool.deauth()
#             i = 0
#             while True:
#                 j_bad = self.tool.get_value("-dm 200[{}..{}]".format(i, i + 9))
#                 if not j_bad:
#                     break
#                 for note in j_bad:
#                     # note = j_bad[0]
#
#                     note = Note(note.number, note.time, note.value)
#                     notes.append(note)
#                     # report.info('NEW NOTE', str(note))
#                 i += 10
#             return notes
#             # for a in range(0, 192):
#             #     j_bad = smp_tool.get_value("-dm 201[0..9]({:02d})".format(a))
#             #
#             #     for note in j_bad:
#             #         note = Note(a, note.time, note.value)
#             #         report.info('NEW NOTE',str(note))
#             #     #     print(note)
#         except Exception as ex:
#             raise
#             # report.failed('Failed to get all journal notes', str(ex))
#
#     def test_smp_reset_control(self):
#         try:
#             def check(prew_errors: Set[Note]):
#                 notes = set()
#                 # jnl=[]
#                 # jnl1=self.tool.get_value('--send=1000 -dm 201=58,0,50')
#                 # jnl2=self.tool.get_value('--send=1000 -dm 201=59,0,50')
#                 # jnl3=self.tool.get_value('--send=1000 -dm 201=92,0,50')
#                 # jnl4=self.tool.get_value('--send=1000 -dm 201=116,0,50')
#                 # jnl5=self.tool.get_value('--send=1000 -dm 201=117,0,50')
#                 # jnl6=self.tool.get_value('--send=1000 -dm 201=118,0,50')
#                 # jnl7=self.tool.get_value('--send=1000 -dm 201=119,0,50')
#                 # jnl8=self.tool.get_value('--send=1000 -dm 201=120,0,50')
#
#                 # journ_list = journ_CE208
#                 # if (CFG_ModelCounter == "CE208_dop"):
#                 #     journ_list = journ_CE208_dop
#                 # ln = 0
#                 # for i in journ_list:
#                 #     jnl = self.tool.get_value('--send=1000 -dm 201[0..50]({:02d})'.format(i))
#                 #     ln = ln + len(jnl)
#                 # if ln > 0:
#                 #     raise SMPException('{} unexpected resets'.format(journal_decoder.get(ln,journal_decoder[0])))
#                 notes = set(self.get_bad_journals())
#                 new = notes - prew_errors
#                 report.debug('AAAAA', str(new))
#                 if len(new) > 0:
#                     for note in new:
#                         report.debug('NEW JOURNAL NOTES', note)
#                     raise ValueError('Unexpected journal notes')
#                 return
#
#             logger.info('CHECK SMP RESET CONTROL')
#
#             # self.tool.auth()
#             # self.tool.execute('--t=45000 -a 25')
#             self.tool.deauth()
#             all_notes = set(self.get_all_journal_notes())
#             # одиночные запуски
#             self.tool.execute(f"--auth='777777' -os 408=[1:0:0:0:0:0:0:0:0:0]")
#             report.debug('CHECK OG 408!', self.tool.get_value('-og 408'))
#             time.sleep(2)
#
#             for i in getinfo:
#                 report.debug('Checking -i {}'.format(i))
#                 # time.sleep(1)
#                 self.tool.execute(f"--auth='777777' --t=40000 -i {i}")
#
#             check(all_notes)
#             report.passed('individual GetInfo')
#
#             for i in getoption:
#                 report.debug('Checking -og {}'.format(i))
#                 self.tool.execute("--auth='777777' --t=40000 -og {}".format(i))
#             check(all_notes)
#             report.passed('individual GetOption')
#
#             for i in getdatas:
#                 report.debug('Checking -ds {}'.format(i))
#                 self.tool.execute("--t=40000 -ds {}".format(i))
#             check(all_notes)
#             report.passed('individual GetDataSingle')
#
#             for i in getdatas_m:
#                 report.debug('Checking -ds {}()'.format(i))
#                 self.tool.execute("--auth='777777' --t=40000 -ds {}(0)".format(i))
#                 self.tool.execute("--auth='777777' --t=40000 -ds {}(11111111)".format(i))
#             check(all_notes)
#             report.passed('individual GetDataSingle masked')
#
#             for i in getdatam:
#                 self.tool.execute("--t=40000 -dm {}[0..10]".format(i))
#                 self.tool.execute("--t=40000 -dm {}[0..100]".format(i))
#                 self.tool.execute("--t=40000 -dm {}[50..100]".format(i))
#                 self.tool.execute("--t=40000 -dm {}[100..200]".format(i))
#                 self.tool.execute("--t=40000 -dm {}[1000..1100]".format(i))
#             check(all_notes)
#             report.passed('individual GetDataMultiple')
#
#             for i in getdatam_m:
#                 self.tool.execute("--send=1000 --t=40000 -dm {}[0..10](0)".format(i))
#                 self.tool.execute("--send=1000 --t=40000 -dm {}[0..100](0)".format(i))
#                 self.tool.execute("--send=1000 --t=40000 -dm {}[50..100](0)".format(i))
#                 self.tool.execute("--send=1000 --t=40000 -dm {}[100..200](0)".format(i))
#                 self.tool.execute("--send=1000 --t=40000 -dm {}[1000..1100](0)".format(i))
#
#                 self.tool.execute("--send=1000 --t=40000 -dm {}[0..10](11111111)".format(i))
#                 self.tool.execute("--send=1000 --t=40000 -dm {}[0..100](11111111)".format(i))
#                 self.tool.execute("--send=1000 --t=40000 -dm {}[50..100](11111111)".format(i))
#                 self.tool.execute("--send=1000 --t=40000 -dm {}[100..200](11111111)".format(i))
#                 self.tool.execute("--send=1000 --t=40000 -dm {}[1000..1100](11111111)".format(i))
#             check(all_notes)
#             report.passed('individual GetDataMultiple masked')
#
#             for i in getdatam_js:
#                 self.tool.execute("--send=1000 --t=40000 -dm 201[0..10]({})".format(i))
#                 self.tool.execute("--send=1000 --t=40000 -dm 201[0..100]({})".format(i))
#                 self.tool.execute("--send=1000 --t=40000 -dm 201[50..100]({})".format(i))
#                 self.tool.execute("--send=1000 --t=40000 -dm 201[100..200]({})".format(i))
#                 self.tool.execute("--send=1000 --t=40000 -dm 201[1000..1100]({})".format(i))
#             check(all_notes)
#             report.passed('individual GetDataMultiple journals')
#
#             self.tool.execute("--send=1000 --t=40000 -dm 200[0..10](0)")
#             self.tool.execute("--send=1000 --t=40000 -dm 200[0..100](0)")
#             self.tool.execute("--send=1000 --t=40000 -dm 200[50..100](0)")
#             self.tool.execute("--send=1000 --t=40000 -dm 200[100..200](0)")
#             self.tool.execute("--send=1000 --t=40000 -dm 200[1000..1100](0)")
#             check(all_notes)
#             report.passed('individual GetDataMultiple common journal')
#             # long_requests=0
#             strlist = []
#             for i in getoption:
#                 strlist.append(str(i))
#             strlist = ' '.join(strlist)
#             self.tool.execute("--send=1000 --t=40000 -og {}".format(strlist))
#             check(all_notes)
#             report.passed('grouped GetOption')
#
#             strlist = []
#             for i in getdatas:
#                 strlist.append(str(i))
#             strlist = ' '.join(strlist)
#             self.tool.execute("--send=1000 --t=40000 -ds {}".format(strlist))
#             check(all_notes)
#             report.passed('grouped GetDataSingle')
#
#             strlist = []
#             for i in getdatas_m:
#                 strlist.append(str(i) + '(0) ' + str(i) + '(11111111)')
#             strlist = ' '.join(strlist)
#             self.tool.execute("--send=1000 --t=40000 -ds {}".format(strlist))
#             check(all_notes)
#             report.passed('grouped GetDataSingle masked')
#
#             for p in ['[0..10]', '[10..20]', '[20..30]', '[50..100]', '[100..200]', '[1000..1100]']:
#                 strlist = []
#                 for i in getdatam:
#                     st = str(i)
#                     strlist.append('{}{}'.format(i, p))
#                 strlist = ' '.join(strlist)
#                 self.tool.execute("--send=1000 --t=40000 -dm {}".format(strlist))
#             check(all_notes)
#             report.passed('grouped GetDataMultiple')
#
#             for p in ['[0..10]', '[10..20]', '[20..30]', '[50..100]', '[100..200]', '[1000..1100]']:
#                 strlist = []
#                 for i in getdatam_m:
#                     st = str(i)
#                     strlist.append('{}{}(0)'.format(i, p))
#                     strlist.append('{}{}(11111111)'.format(i, p))
#                 strlist.append('200{}(0)'.format(p))
#                 strlist = ' '.join(strlist)
#                 self.tool.execute("--send=1000 --t=40000 -dm {}".format(strlist))
#             check(all_notes)
#             report.passed('grouped GetDataMultiple masked and common journal')
#
#             for p in ['[0..10]', '[10..20]', '[20..30]', '[50..100]', '[100..200]', '[1000..1100]']:
#                 strlist = []
#                 for i in getdatam_js:
#                     st = str(i)
#                     strlist.append('201{}({})'.format(p, i))
#                 strlist = ' '.join(strlist)
#                 self.tool.execute("--send=1000 --t=40000 -dm {}".format(strlist))
#             check(all_notes)
#             report.passed('grouped GetDataMultiple journals')
#
#             logger.warning(f'test {__name__} is OK')
#
#         except Exception as ex:
#             report.error('', ex)
