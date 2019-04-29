import config
import datetime
import random



class Hostel:
    rooms = []
    last_income = 0
    income = 0
    cost_max = 0
    N = -1
    food = ""

    def __init__(self, fund="fund.txt", booking="booking.txt"):
        self.hostel_config = config.hostel_config
        self.fund = open(fund, 'rb')
        self.booking = open(booking, 'rb')

        N = 0
        for line in self.fund:
            room = line.decode('utf_8_sig').split('\n')[0].split(' ')
            self.rooms.append({
                "номер": N,
                "тип": room[1],
                "количество": room[2],
                "комфорт": room[3],
                "занятость": {
                    "даты": []
                }
            })
            N += 1

        # print(self.rooms[23])

    def my_booking(self):
        l = 0
        for line in self.booking:
            b = line.decode('utf_8_sig').split('\n')[0].split(' ')
            if l == 0:
                print(b[0])
                date_booking = datetime.datetime.strptime(b[0], '%d.%m.%Y')
                l += 1

            self.cost_max = 0
            self.N = -1
            self.food = ""
            for i in range(7 - int(b[4])):
                if i == 1 and self.cost_max != 0:
                    break
                for room in self.rooms:
                    if int(room['количество']) < int(b[4]):
                        continue
                    elif int(room['количество']) == int(b[4]) + i:
                        if not room['занятость']['даты']:
                            self.price(room, b, i)
                        else:
                            if not self.equal_dates(room['занятость']['даты'], b):
                                self.price(room, b, i)
                            else:
                                continue

            if date_booking != datetime.datetime.strptime(b[0], '%d.%m.%Y'):
                self.results(date_booking)
                self.last_income = 0
                self.income = 0
                date_booking = datetime.datetime.strptime(b[0], '%d.%m.%Y')

            print('Поступила заявка на бронирование:\n\n' + line.decode('utf_8_sig') + '\n')

            if (self.N != -1):
                if random.random() < 0.25:
                    print('Предложений по данному запросу нет. В бронировании отказано.\n\n')
                    print('--------------------------------------------------------------------\n\n')
                    self.last_income += float(b[7]) * float(b[6]) * float(b[4])
                    continue
                print('Найден:\n\n')
                print('номер %d %s %s рассчитан на %d чел. фактически %d чел. %s стоимость %.2f руб./сутки\n\n' % (
                    self.N + 1, self.rooms[self.N]['тип'], self.rooms[self.N]['комфорт'],
                    int(self.rooms[self.N]['количество']), int(b[4]),
                    self.food, self.cost_max))
                print('Клиент согласен. Номер забронирован.\n\n')
                print('--------------------------------------------------------------------\n\n')
                self.income += self.cost_max * float(b[6])
                self.fill_date(b, self.N)
            else:
                print('Предложений по данному запросу нет. В бронировании отказано.\n\n')
                print('--------------------------------------------------------------------\n\n')
                self.last_income += float(b[7]) * float(b[6]) * float(b[4])

        self.results(date_booking)

    def equal_dates(self, dates, b):
        for date in dates:
            for i in range(int(b[6])):
                if date == datetime.datetime.strptime(b[5], '%d.%m.%Y') + datetime.timedelta(i):
                    return True
        return False

    def fill_date(self, b, N):
        for i in range(int(b[6])):
            self.rooms[N]['занятость']['даты'].append(
                datetime.datetime.strptime(b[5], '%d.%m.%Y') + datetime.timedelta(i))

    def price(self, room, b, i):
        sale = 0
        if i != 0:
            sale = 0.3
        cost = (self.hostel_config['тип'][room['тип']] * self.hostel_config['комфорт'][room['комфорт']]) * (
                1 - sale) * float(room['количество'])
        cost1 = cost + self.hostel_config['питание']['полупансион'] * float(b[4])
        cost2 = cost + self.hostel_config['питание']['завтрак'] * float(b[4])
        cost3 = cost + self.hostel_config['питание']['без питания'] * float(b[4])
        if float(b[7]) * float(b[4]) >= cost1 > self.cost_max:
            self.cost_max = cost1
            self.N = room['номер']
            self.food = "полупансион"
        elif float(b[7]) * float(b[4]) >= cost2 > self.cost_max:
            self.cost_max = cost2
            self.N = room['номер']
            self.food = "завтрак"
        elif float(b[7]) * float(b[4]) >= cost3 > self.cost_max:
            self.cost_max = cost3
            self.N = room['номер']
            self.food = "без питания"

    def results(self, date_booking):
        res_rooms = {
            "одноместный": [0, 0],
            "двухместный": [0, 0],
            "полулюкс": [0, 0],
            "люкс": [0, 0],
            "свободно": 0,
            "занято": 0
        }
        for room in self.rooms:
            flag_room = 0
            if not room['занятость']['даты']:
                res_rooms["свободно"] += 1
                res_rooms[room["тип"]][1] += 1
            else:
                for date in room['занятость']['даты']:
                    if date == date_booking:
                        res_rooms["занято"] += 1
                        res_rooms[room["тип"]][1] += 1
                        res_rooms[room["тип"]][0] += 1
                        flag_room = 1
                if not flag_room:
                    res_rooms["свободно"] += 1
                    res_rooms[room["тип"]][1] += 1

        res = res_rooms
        print('=====================================================================================================\n\n')
        print('Итог за  ' + date_booking.strftime('%d.%m.%Y') + '\n\n')
        print('Количество занятых номеров:  ' + str(res['занято']))
        print('\n\n')
        print('Количество свободных номеров:  ' + str(res['свободно']))
        print('\n\n')
        print('Занятость по категориям:')
        print('\n\n')
        print('Одноместных:  ' + str(res['одноместный'][0]) + ' из ' + str(res['одноместный'][1]))
        print('\n\n')
        print('Двухместных:  ' + str(res['двухместный'][0]) + ' из ' + str(res['двухместный'][1]))
        print('\n\n')
        print('Полулюкс:  ' + str(res['полулюкс'][0]) + ' из ' + str(res['полулюкс'][1]))
        print('\n\n')
        print('Люкс:  ' + str(res['люкс'][0]) + ' из ' + str(res['люкс'][1]))
        print('\n\n')
        print('Процент загруженности гостиницы:  %.2f' % (
                    float(res['занято']) / (float(res['занято']) + float(res['свободно'])) * 100))
        print('\n\n')
        print('Доход за день:  ' + str(self.income))
        print('\n\n')
        print('Упущенный доход:  ' + str(self.last_income))
        print('\n\n')
        print('=====================================================================================================\n\n')



if (__name__ == '__main__'):
    m = Hostel()
    m.my_booking()
