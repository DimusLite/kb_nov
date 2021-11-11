import requests, telebot
from datetime import datetime
from os import environ

TOKEN = environ.get('kb_nov_token')

def get_data():
    req = requests.get('https://yobit.net/api/3/ticker/eth_usdt')
    response = req.json()
    sell_price = response['eth_usdt']['sell']
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\nSell ETH price: {sell_price}")


def parse_config_message(text):
    parsed_data = {}
    version_position = text.find('v.')
    parsed_data['version'] = text[version_position + 3:version_position + 8] if version_position > 0 else 'version not found'
    date_position = text.find(' от ')
    parsed_data['date'] = text[date_position + 4:date_position + 12] if date_position > 0 else 'date not found'
    changes_position = text.find('Перечень изменений:')
    changes = text[changes_position + 20:] if changes_position > 0 else 'changes not found'
    changes = '\n'.join([line for line in changes.split('\n') if line.strip() != ''])  # remove empty strings
    parsed_data['changes'] = changes
    return parsed_data

def compose_config_message(data):
    answer = f'\
⚠️📒 Новая версия конфигурации 1с *v{data["version"]}* от *{data["date"]}*\n\
\n\
_Перечень изменений:_\n\
{data["changes"]}\n\
\n\
Обновляемся *вечером после закрытия* или при наличии свободного времени'
    return answer


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
    def start_message(message):
        bot.send_message(message.chat.id, "Hello friend! Type the 'price' to find out the cost of ETH")

    @bot.message_handler(content_types=['text'])
    def send_answer(message):
        msg = message.text
        if msg.lower() == 'price':
            answer = get_ETH_price()
        elif 'новая версия конфигурации' in msg.lower():
            data = parse_config_message(msg)
            print(data)
            answer = compose_config_message(data)
        else:
            answer = 'хз'
        bot.send_message(message.chat.id, answer)
    bot.infinity_polling()

if __name__ == '__main__':
    telegram_bot(TOKEN)