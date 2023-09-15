import json
import logging
import re
import sys
import time
from datetime import datetime
from os import environ
from threading import Thread

import requests
import telebot
from dotenv import load_dotenv

import r_scrap

load_dotenv()
logger = logging.getLogger(__name__)

BOT_TOKEN = environ.get('BOT_TOKEN', None)
AUTHOR_CHAT_ID = environ.get('AUTHOR_CHAT_ID', None)
SHIFTS_FILE = 'shifts.json'
SHOPS_FILE = 'shops.json'
LOG_FILE = 'main.log'


def set_logging_config():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
        handlers=[
            logging.FileHandler(str(__file__).split('.')[0] + '.log'),
            logging.StreamHandler(stream=sys.stdout)
        ]
    )


def parse_cfg_msg(text):
    _CHANGES_TITLE = 'Перечень изменений:'
    _NOT_FOUND_MSG = 'Not found'
    _COMPLETE_LOG_MSG ='ZWSP cleared'

    text = text.replace('​', '') #clear message from ZWSP
    add_to_log(text, _COMPLETE_LOG_MSG)
    match = re.search(r'v\.?\s{1,3}(\d{1,2}\.?\d{1,4})', text)  # v. 9.123
    version = match.group(1) if match else _NOT_FOUND_MSG

    match = re.search(r'\d{2}\.\d{2}\.\d{2,4}', text)  # xx.xx.xx
    date = match.group(0) if match else _NOT_FOUND_MSG

    titles_position = text.find(_CHANGES_TITLE)
    changes = text[titles_position + len(_CHANGES_TITLE):].strip() if titles_position > 0 else _NOT_FOUND_MSG

    data = {
        'version': version,
        'date': date,
        'changes': changes
    }
    return data


def parse_outdated_msg(text):
    shops_nums = re.findall(r'№(\d{4,5})', text)
    return shops_nums


def compose_cfg_msg(data):
    answer = f"""\
⚠️📒 Новая версия конфигурации 1с *v{data['version']}* от *{data['date']}*

_Перечень изменений:_
{data['changes']}

Обновляемся *вечером после закрытия* или при наличии свободного времени
"""

    return answer


def compose_outdated_msg(codes, shops):
    _OUTDATED_MSG = "Магазины с необновленной конфигурацией:\n"

    msg = _OUTDATED_MSG
    for code in codes:
        for shop in shops:
            if shop['Code'] == code:
                msg += f"""\
{code} {shop['City']} {shop['Address']} +{shop['Tel']}
"""
    return msg


def compose_shops_msg(shops):
    if not shops:
        return 'Нет магазинов с таким номером или СА'
    msg = ''
    if len(shops) > 1:
        msg += f'СТ {shops[0][6]}:\n'
        for shop in shops:
            msg += f'''\
{shop[0]} {shop[2]} {shop[3]}
'''
    else:
        shop = shops[0]
        msg += f'''\
Магазин {shop[0]} {shop[2]} {shop[3]}:
{shop[5]}
{shop[4]}
{shop[6]}
'''

    return msg


def get_shifts_data(file):
    _DATE_FORMAT = "%d.%m.%Y"

    with open(file, 'r') as json_file: # read data from file
        data = json.load(json_file)

    for day in data: # convert str to data
        day['date'] = datetime.strptime(day['date'], _DATE_FORMAT)
    return data


def put_shifts_data(data):
    _DATE_FORMAT = "%d.%m.%Y"

    for day in data:
        day['date'] = datetime.strftime(day['date'], _DATE_FORMAT)
    with open('shifts.json', 'w') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)


def get_shops(file):
    with open(file, 'r') as json_file:
        data = json.load(json_file)
    return data


def get_nearest_shifts(data, date):
    _NEAREST = range(-7, 14)
    nearest_shifts = ""
    for day in data:
        delta_now = day['date'] - datetime.now()
        delta_date = day['date'] - date
        if delta_date.days in _NEAREST:
            if delta_now.days < 0:
                mark = 'del'
            elif delta_now.days < 7:
                mark = 'strong'
            else:
                mark = 'a'
        else:
            continue  # exclude all days passed or future more 1 week

        nearest_shifts += f"""\
<{mark}>{day['date']:%d.%m %a}  {day['watcher']}</{mark}>
"""

    return nearest_shifts


def swap_shifts(data, date1, date2):
    watcher1, watcher2 = 'error', 'error'
    for day in data:
        if day['date'] == date1:
            watcher1 = day['watcher']
        if day['date'] == date2:
            watcher2 = day['watcher']
    if watcher1 != 'error' and watcher2 != 'error':
        for day in data:
            if day['date'] == date1:
                day['watcher'] = watcher2
            if day['date'] == date2:
                day['watcher'] = watcher1
    return data


def get_ETH_price():
    _URL = 'https://yobit.net/api/3/ticker/eth_usdt'
    _CONNECTION_ERROR_MSG = 'Cannot connect to ETH prices server'
    _SERVER_ERROR_MSG = 'ETH price server error'
    _SELL_PRICE_MSG = 'Sell ETH price:'

    try:
        response = requests.get(_URL)
    except requests.ConnectionError as ex:
        logger.error(_CONNECTION_ERROR_MSG, _URL, ex)
    if response.status_code == 200:
        json_response = response.json()
        sell_price = json_response['eth_usdt']['sell']
        return f"""\
{datetime.now().strftime('%Y-%m-%d %H:%M')}
{_SELL_PRICE_MSG} {sell_price}
        """
    else:
        logger.error(_SERVER_ERROR_MSG)
    return None


def get_weather(city=None):
    """
    Request weather data on the wttr.in
    More params: https://wttr.in/:help
    """

    _DEFAULT_CITY = 'Великий Новгород'
    _CONNECTION_ERROR_MSG = 'Cannot connect to weather server'
    _SERVER_ERROR_MSG = 'Weather server error'
    _CITIES = {
        'новгород': 'Великий Новгород',
        'спб': 'Санкт-Петербург',
        'питер': 'Санкт-Петербург',
        'санкт-петербург': 'Санкт-Петербург',
        'мск': 'Москва',
        'москва': 'Москва'
    }

    _WEATHER_PARAMS = {
        #'0': '',
        #'T': '',
        'format': 2,
        'M': '',
        'lang': 'ru',
    }

    if city in _CITIES:
        city = _CITIES[city]
    else:
        city = _DEFAULT_CITY

    url = f'https://wttr.in/{city}'
    try:
        response = requests.get(url, params=_WEATHER_PARAMS)
    except requests.ConnectionError as ex:
        logger.error(_CONNECTION_ERROR_MSG, url, ex)
    if response.status_code == 200:
        return f'{city} {response.text}'
    else:
        logger.error(_SERVER_ERROR_MSG)
    return None


def add_to_log(msg, event):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"""\
{current_time} - {event}: {msg}
"""
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(log_msg)


def run_handlers(bot):
    _WELCOME_MSG = """\
Hello friend! Just paste the text to convert it to config message or type /help for more options
"""
    _HELP_MSG = """\
/cfg - blank config message
/shifts - nearest shifts schedule
/shifts dd.mm.yy - nearest to dd.mm.yy shifts
/swap dd.mm.yy dd.mm.yy - swap shifts
"""
    _DEFAULT_CHANGES_MSG = "- технические доработки"
    _WRONG_INPUT_MSG = "Wrong date, try dd.mm.yy format"
    _DATES_MISSING_MSG = "Two dates must be specified: /swap dd.mm.yy dd.mm.yy"
    _NO_SHIFTS_DATA = "There are no data on the days you specified"
    _WRONG_ADD_INPUT_MSG = 'One date must be specified: /add dd.mm.yy first_name last_name'
    _SEARCH_PATTERN = 'новая версия конфигурации'
    _NEW_CFG_LOG_MSG = 'New config notify arrived'
    _UNUPDATED_PATTERN = 'Неактуальная версия конф. 1С!'
    _CMD_WEATHER = 'погода'
    _CMD_PRICE = 'price'

    @bot.message_handler(commands=['start'])
    def send_start_msg(msg):
        bot.send_message(msg.chat.id, _WELCOME_MSG)

    @bot.message_handler(commands=['help'])
    def send_help_msg(msg):
        bot.send_message(msg.chat.id, _HELP_MSG)

    @bot.message_handler(commands=['cfg'])
    def send_cfg_template(msg):
        default_cfg_data = {
            'version': '9.xxx',
            'date': datetime.now().strftime('%d.%m.%Y'),
            'changes': _DEFAULT_CHANGES_MSG
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
                bot.send_message(msg.chat.id, _WRONG_INPUT_MSG)
        nearest_shifts = get_nearest_shifts(data, date)
        if nearest_shifts == "":
            nearest_shifts = _NO_SHIFTS_DATA
        bot.send_message(msg.chat.id, nearest_shifts, parse_mode="HTML")

    @bot.message_handler(commands=['swap'])
    def swap(msg):
        data = get_shifts_data(SHIFTS_FILE)
        date1, date2 = None, None
        params = msg.text.split()[1:]
        if len(params) == 2:
            try:
                date1 = datetime.strptime(params[0], "%d.%m.%y")
                date2 = datetime.strptime(params[1], "%d.%m.%y")
            except:
                bot.send_message(msg.chat.id, _WRONG_INPUT_MSG)
        else:
            bot.send_message(msg.chat.id, _DATES_MISSING_MSG)
        if date1 and date2:
            data = swap_shifts(data, date1, date2)
            shifts_to_output = get_nearest_shifts(data, date1)
            put_shifts_data(data)
            bot.send_message(msg.chat.id, shifts_to_output, parse_mode="HTML")

    @bot.message_handler(commands=['add'])
    def add_shifts(msg):
        data = get_shifts_data(SHIFTS_FILE)
        params = msg.text.split()[1:]
        if len(params) == 3:
            try:
                date = datetime.strptime(params[0], "%d.%m.%y")
            except:
                bot.send_message(msg.chat.id, _WRONG_INPUT_MSG)
            record = {}
            record['date'] = date
            record['watcher'] = params[1] + ' ' + params[2]
            data.append(record)
            shifts_to_output = get_nearest_shifts(data, date)
            put_shifts_data(data)
            bot.send_message(msg.chat.id, shifts_to_output, parse_mode="HTML")
        else:
            bot.send_message(msg.chat.id, _WRONG_ADD_INPUT_MSG)

    @bot.message_handler(commands=['get'])
    def send_shops(msg):
        param = msg.text.split()[1]
        if param:
            shops = r_scrap.get_db_shops(param)
            shops_msg = compose_shops_msg(shops)
            bot.send_message(msg.chat.id, shops_msg)

    @bot.message_handler(commands=['upd'])
    def upd_shops(msg):
        if r_scrap.update_db_shops():
            bot.send_message(msg.chat.id, 'Shops data updated')

    @bot.message_handler(commands=['eth'])
    def get_eth(msg):
        answer = get_ETH_price()
        if answer:
            bot.send_message(msg.chat.id, answer)    \

    @bot.message_handler(commands=['weather'])
    def get_eth(msg):
        try:
            param = msg.text.split()[1]
        except IndexError:
            param = None
        answer = get_weather(param)
        if answer:
            bot.send_message(msg.chat.id, answer)



    @bot.message_handler(content_types=['text'])
    def process_text(msg):
        answer = None
        if _SEARCH_PATTERN in msg.text.lower():
            add_to_log(msg.text, _NEW_CFG_LOG_MSG)
            new_cfg_msg_data = parse_cfg_msg(msg.text)
            answer = compose_cfg_msg(new_cfg_msg_data)
        elif _UNUPDATED_PATTERN in msg.text:
            outdated_shops = parse_outdated_msg(msg.text)
            shops = get_shops(SHOPS_FILE)
            answer = compose_outdated_msg(outdated_shops, shops)
        if answer:
            bot.send_message(msg.chat.id, answer)

    bot.infinity_polling()


class MissingEnvVar(Exception):
    """Missing environment variables"""
    pass


def check_tokens():
    """Check if env variables loaded"""
    env_vars = [BOT_TOKEN, AUTHOR_CHAT_ID]
    vars_availability = [False if not var else True for var in env_vars]
    logger.debug(vars_availability)
    if not all(vars_availability):
        return False
    return True


def scheduled_check(bot):
    _START_LOG_MSG = 'Start monitoring'
    _NO_UPDATES_LOG_MSG = 'Resource checked, there is no updates'

    # now = datetime.datetime.now()
    # hour = now.hour
    # print('hour:', hour)
    logger.info(_START_LOG_MSG)

    while True:
        # if hour in [22, 24]:
        msg = _NO_UPDATES_LOG_MSG
        logger.info(msg)
        # bot.send_message(AUTHOR_CHAT_ID, msg)

        time.sleep(30)


def main():
    """Main bot logic."""
    _MISSING_VARS_LOG_MSG = 'Missing environment variables'

    set_logging_config()
    if not check_tokens():
        logger.critical(_MISSING_VARS_LOG_MSG)
        raise MissingEnvVar(_MISSING_VARS_LOG_MSG)
    logger.debug(BOT_TOKEN)
    bot = telebot.TeleBot(BOT_TOKEN)
    Thread(target=scheduled_check, args=(bot,)).start()
    run_handlers(bot)


if __name__ == '__main__':
    main()
