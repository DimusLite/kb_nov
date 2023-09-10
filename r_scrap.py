"""Scraping sps-holding.ru/r/ and sps-holding.ru/rdp/ data"""
from bs4 import BeautifulSoup
import requests
import sqlite3

RDP_ACCOUNT = {
    'login': 'legkiy.dmitriy',
    'password': 'aeP7ohJu'
}
R_ACCOUNT = {
    'login': 'zzz',
    'password': 'zzz'
}
URL_R = 'https://sps-holding.ru/r/?m=summary&json&i'
URL_RDP = 'https://sps-holding.ru/rdp/?mag'
USER_AGENT = 'PostmanRuntime/7.32.3'
USER_COOKIES = {
    'Lite': ('u=%D0%93%D0%B0%D0%BB%D0%BA%D0%B8%D0%BD%20%D0%98%D0%BB%D1%8C%D1'
             '%8F%20%D0%92%D0%B0%D0%B4%D0%B8%D0%BC%D0%BE%D0%B2%D0%B8%D1%87'
             '%7C%D0%93%D0%B0%D0%BB%D0%BA%D0%B8%D0%BD%20%D0%98%D0%BB%D1%8C'
             '%D1%8F%20%D0%92%D0%B0%D0%B4%D0%B8%D0%BC%D0%BE%D0%B2%D0%B8%D1%'
             '87%7C%D0%9F%D0%BE%D0%BF%D0%BE%D0%B2%20%D0%95%D0%B2%D0%B3%D0%B5'
             '%D0%BD%D0%B8%D0%B9%20%D0%9D%D0%B8%D0%BA%D0%BE%D0%BB%D0%B0%D0'
             '%B5%D0%B2%D0%B8%D1%87%7C%D0%9B%D1%91%D0%B3%D0%BA%D0%B8%D0%B9'
             '%20%D0%94%D0%BC%D0%B8%D1%82%D1%80%D0%B8%D0%B9%20%D0%A1%D0%B5'
             '%D1%80%D0%B3%D0%B5%D0%B5%D0%B2%D0%B8%D1%87; r_modul=summary;'),
}
USER_KEYS = {
    'Galasha': '&user=36c5b421216cd156fd18f7b866354a16',
    'Grigoriev': '&user=040d1a1362f3ff3a6746340d578b4672',
    'Lite': '',
    'Pinchuk': '&user=ce1835257ace0ad250d33b41cf0190eb'
}
USERS = {
    'Galasha': 'Галаша Александр Александрович',
    'Grigoriev': 'Григорьев Александр Владимирович',
    'Lite': 'Лёгкий Дмитрий Сергеевич',
    'Pinchuk': 'Пинчук Алексей Анатольевич'
}
SHOPS_DB = 'shops.sqlite'


def get_remote_page(url, headers=None, auth=None):
    response = requests.get(url=url,
                            headers=headers,
                            auth=auth)
    if response.ok:
        return response.content
    else:
        print('Requests error', response.status_code)
    return None


def convert_page_to_shops(source):
    soup = BeautifulSoup(source, 'html.parser')
    table = soup.find('table', class_='livefilter')
    rows = table.find_all('tr')
    shops = []
    for row in rows:
        cols = row.find_all('td')
        href = row.find('a')['href']
        email = href.split(':')[1]  # remove mailto:
        shop = {
            'Code': cols[0].text,
            'IP': cols[1].text,
            'City': cols[4].text,
            'Address': cols[3].text,
            'email': email,
            'Tel': cols[6].text,
            'SA': cols[10].text,
            'BigBoss': cols[11].text,
            'HugeBoss': cols[12].text,
            'AstronomicBoss': cols[13].text
        }
        shops.append(shop)
    return shops


def upsert_db_shops(data):
    try:
        sqlite_connection = sqlite3.connect(SHOPS_DB)
        cursor = sqlite_connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shops(
                code INTEGER PRIMARY KEY,
                ip text NOT NULL,
                city text NOT NULL,
                address text NOT NULL,
                email text NOT NULL,
                tel INTEGER NOT NULL,
                sa text NOT NULL,
                bigboss text,
                hugeboss text,
                astronomicboss text
            );
        ''')

        for shop in data:
            sql_query = f'''
    INSERT INTO shops (code, ip, city, address, email, tel, sa, bigboss, 
                       hugeboss, astronomicboss)
    VALUES {tuple(shop.values())}
    ON CONFLICT(code) DO UPDATE SET
        code = ?, ip = ?, city = ?, address = ?, email = ?, tel = ?, sa = ?, 
        bigboss = ?, hugeboss = ?, astronomicboss = ?
'''
            cursor.execute(sql_query, list(shop.values()))
        return True

    except sqlite3.Error as error:
        print("SQLite connection error", error)
    finally:
        if (sqlite_connection):
            sqlite_connection.commit()
            sqlite_connection.close()
            print("SQLite connection closed")
    return False


def get_db_shops(param):
    try:
        sqlite_connection = sqlite3.connect(SHOPS_DB)
        cursor = sqlite_connection.cursor()
        if param in USERS.keys():
            user = USERS[param]
            cursor.execute(f'''\
SELECT * 
FROM shops
WHERE sa = "{user}"
''')
        else:
            try:
                code_shop = int(param)
                cursor.execute(f'''\
SELECT *
FROM shops
WHERE code = {code_shop}
''')
            except ValueError:
                return None
        result = []
        for res in cursor:
            result.append(res)
        return result
    except sqlite3.Error as error:
        print("SQLite connection error", error)
    finally:
        if (sqlite_connection):
            sqlite_connection.commit()
            sqlite_connection.close()
            print("SQLite connection closed")

    return '[Shops list]'


def update_db_shops():
    shops = []
    for user in USER_KEYS.values():
        remote_page = get_remote_page(
            URL_RDP + user,
            {'User-Agent': USER_AGENT},
            (RDP_ACCOUNT['login'], RDP_ACCOUNT['password'])
        )
        user_shops = convert_page_to_shops(remote_page)
        shops.extend(user_shops)

    return upsert_db_shops(shops)


if __name__ == '__main__':
    # print()
    print(update_db_shops())

    # print(get_shops_data(5421))

    # remote_page = get_remote_page(
    #     URL_R,
    #     {'User-Agent': USER_AGENT, 'Cookie': USER_COOKIES['Lite']},
    #     (R_ACCOUNT['login'], R_ACCOUNT['password'])
    # )


