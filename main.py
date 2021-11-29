import requests, telebot, re, json
from datetime import datetime
from os import environ

TOKEN = environ.get('kb_nov_token')
SHIFTS_FILE = 'shifts.json'

def parse_cfg_msg(text):
    match = re.search(r'v\.?\s{1,3}(\d{1,2}\.\d{1,4})', text)  # v. 9.123
    version = match.group(1) if match else "Not found"

    match = re.search(r'\d{2}\.\d{2}\.\d{2,4}', text)  # xx.xx.xx
    date = match.group(0) if match else "Not found"

    CHANGES_TITLE = 'Перечень изменений:'
    titles_position = text.find(CHANGES_TITLE)
    changes = text[titles_position + len(CHANGES_TITLE):].strip() if titles_position > 0 else "Not found"

    data = {
        'version': version,
        'date': date,
        'changes': changes
    }
    return data


def compose_cfg_msg(data):
    answer = f'\
⚠️📒 Новая версия конфигурации 1с *v{data["version"]}* от *{data["date"]}*\n\
\n\
_Перечень изменений:_\n\
{data["changes"]}\n\
\n\
Обновляемся *вечером после закрытия* или при наличии свободного времени'
    return answer


def get_shifts_data(file):
    with open(file, 'r') as json_file: # read data from file
        data = json.load(json_file)

    for day in data: # convert str to data
        day['date'] = datetime.strptime(day['date'], "%d.%m.%Y")
    return data


def put_shifts_data(data):
    for day in data:
        day['date'] = datetime.strftime(day['date'], "%d.%m.%Y")
    with open('shifts.json', 'w') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)


def get_nearest_shifts(data, date):
    NEAREST = range(-7, 14)
    nearest_shifts = ""
    for day in data:
        delta_now = day['date'] - datetime.now()
        delta_date = day['date'] - date
        if delta_date.days in NEAREST:
            if delta_now.days < 0:
                mark = 'del'
            elif delta_now.days < 7:
                mark = 'strong'
            else:
                mark = 'a'
        else:
            continue  # exclude all days passed or future more 1 week

        nearest_shifts += f"<{mark}>{day['date']:%d.%m %a}  {day['watcher']}</{mark}>\n"

    return nearest_shifts


def swap_shifts(data, date1, date2):
    watcher1, watcher2 = 'error', 'error'
    for day in data:
        if day['date'] == date1:
            watcher1 = day['watcher']
            print(day)
        if day['date'] == date2:
            watcher2 = day['watcher']
            print(day)
    if watcher1 != 'error' and watcher2 != 'error':
        for day in data:
            if day['date'] == date1:
                day['watcher'] = watcher2
                print(day)
            if day['date'] == date2:
                day['watcher'] = watcher1
                print(day)
    return data


def get_ETH_price():
    try:
        req = requests.get('https://yobit.net/api/3/ticker/eth_usdt')
        response = req.json()
        sell_price = response['eth_usdt']['sell']
        return f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\nSell ETH price: {sell_price}"
    except Exception as ex:
        print(ex)
        return "ошибка"


def telegram_bot(TOKEN):
    bot = telebot.TeleBot(TOKEN)

    @bot.message_handler(commands=['start'])
    def send_start_msg(msg):
        start_msg = "Hello friend! Just paste the text to convert it to config message or type /help for more options"
        bot.send_message(msg.chat.id, start_msg)


    @bot.message_handler(commands=['help'])
    def send_help_msg(msg):
        help_msg = "/cfg - blank config message\n\
/shifts - nearest shifts schedule\n\
/shifts dd.mm.yy - nearest to dd.mm.yy shifts\n\
"
        bot.send_message(msg.chat.id, help_msg)


    @bot.message_handler(commands=['cfg'])
    def send_cfg_template(msg):
        default_cfg_data = {
            'version': '9.xxx',
            'date': datetime.now().strftime('%d.%m.%Y'),
            'changes': '- технические доработки'
        }
        bot.send_message(msg.chat.id, compose_cfg_msg(default_cfg_data))


    @bot.message_handler(commands=['shifts'])
    def send_shifts_schedule(msg):
        data = get_shifts_data(SHIFTS_FILE)
        data.sort(key=lambda x: x['date'])
        date = datetime.now()
        params = msg.text.split()[1:]
        if len(params) == 1:
            try:
                date = datetime.strptime(params[0], "%d.%m.%y")
            except:
                bot.send_message(msg.chat.id,'Wrong date, try dd.mm.yy format')
        nearest_shifts = get_nearest_shifts(data, date)
        if nearest_shifts == "":
            nearest_shifts = "There are no data in the date you specified"
        bot.send_message(msg.chat.id, nearest_shifts, parse_mode="HTML")


    @bot.message_handler(commands=['swap'])
    def swap(msg):
        data = get_shifts_data(SHIFTS_FILE)
        data1, data2 = None, None
        params = msg.text.split()[1:]
        if len(params) == 2:
            try:
                date1 = datetime.strptime(params[0], "%d.%m.%y")
                date2 = datetime.strptime(params[1], "%d.%m.%y")
                print(date1, date2)
            except:
                bot.send_message(msg.chat.id, 'Wrong date, try dd.mm.yy format')
        else:
            bot.send_message(msg.chat.id, 'Two dates must be specified: /swap_shifts dd.mm.yy dd.mm.yy')
        if date1 and date2:
            data = swap_shifts(data, date1, date2)
            shifts_to_output = get_nearest_shifts(data, date1)
            put_shifts_data(data)
            bot.send_message(msg.chat.id, shifts_to_output, parse_mode="HTML")


    @bot.message_handler(content_types=['text'])
    def send_answer(msg):
        answer = ''
        if msg.text.lower() == 'price':
            answer = get_ETH_price()
        elif 'новая версия конфигурации' in msg.text.lower():
            data = parse_cfg_msg(msg.text)
            answer = compose_cfg_msg(data)
        if answer:
            bot.send_message(msg.chat.id, answer)


    bot.infinity_polling()


if __name__ == '__main__':
    telegram_bot(TOKEN)