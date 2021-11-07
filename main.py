import requests, telebot
from datetime import datetime
from os import environ

TOKEN = environ.get('kb_nov_token')

def get_data():
    req = requests.get('https://yobit.net/api/3/ticker/eth_usdt')
    response = req.json()
    sell_price = response['eth_usdt']['sell']
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\nSell ETH price: {sell_price}")


def telegram_bot(TOKEN):
    bot = telebot.TeleBot(TOKEN)

    @bot.message_handler(commands=['start'])
    def start_message(message):
        bot.send_message(message.chat.id, "Hello friend! Type the 'price' to find out the cost of ETH")

    @bot.message_handler(content_types=['text'])
    def send_text(message):
        msg = message.text
        if msg.lower() == 'price':
            try:
                req = requests.get('https://yobit.net/api/3/ticker/eth_usdt')
                response = req.json()
                sell_price = response['eth_usdt']['sell']
                answer = f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\nSell ETH price: {sell_price}"
            except Exception as ex:
                print(ex)
                answer = "ошибка"
        elif 'новая версия конфигурации' in message.text.lower():
            version_position = msg.find('v.')
            version = msg[version_position+3:version_position + 8] if version_position>0 else 'version not found'
            date_position = msg.find(' от ')
            date = msg[date_position+4:date_position+12] if date_position>0 else 'date not found'
            changes_position = msg.find('Перечень изменений:')
            changes = msg[changes_position+20:] if changes_position>0 else 'changes not found'
            changes = '\n'.join([line for line in changes.split('\n') if line.strip() != '']) #remove empty strings
            answer =  f'⚠️📒 Новая версия конфигурации 1с *v{version}* от *{date}*\n'
            answer += '\n'
            answer += '_Перечень изменений:_\n'
            answer += f'{changes}\n'
            answer += '\n'
            answer += 'Обновляемся *вечером после закрытия* или при наличии свободного времени'
        else:
            answer = 'хз'
        bot.send_message(message.chat.id, answer)

    bot.infinity_polling()

if __name__ == '__main__':
    telegram_bot(TOKEN)