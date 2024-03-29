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


def query_the_db(db, query, param=None):
    sqlite_connection = None
    try:
        print("Open SQLite connection")
        sqlite_connection = sqlite3.connect(db)
        cursor = sqlite_connection.cursor()
        if param:
            cursor.execute(query, param)
        else:
            cursor.execute(query)
        return cursor.fetchall()
    except sqlite3.Error as error:
        print("SQLite connection error", error)
    finally:
        if sqlite_connection:
            sqlite_connection.commit()
            sqlite_connection.close()
            print("SQLite connection closed")
    return False


def init_db_shop():
    query = '''\
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
);'''
    return query_the_db(SHOPS_DB, query)


def upsert_db_shops(data):
    init_db_shop()
    for shop in data:
        query = f'''
INSERT INTO shops (code, ip, city, address, email, tel, sa, bigboss, 
                   hugeboss, astronomicboss)
VALUES {tuple(shop.values())}
ON CONFLICT(code) DO UPDATE SET
    code = ?, ip = ?, city = ?, address = ?, email = ?, tel = ?, sa = ?, 
    bigboss = ?, hugeboss = ?, astronomicboss = ?
'''
        query_the_db(SHOPS_DB, query, list(shop.values()))
    return get_db_shops('Lite')


def get_db_shops(param):
    if param.isdigit():
        code_shop = int(param)
        query = f'''\
SELECT *
FROM shops
WHERE code = {code_shop}
'''
        return query_the_db(SHOPS_DB, query)
    else:
        query = f'''\
SELECT *
FROM users
WHERE name = "{param}" OR nick = "{param}"
'''
        result = query_the_db(SHOPS_DB, query)
        if result:
            user_name = result[0][1]
            query = f'''\
SELECT *
FROM shops
WHERE sa = "{user_name}"
'''
            return query_the_db(SHOPS_DB, query)


def update_db_shops():
    shops = []
    users = get_db_users()
    for user in users:
        remote_page = get_remote_page(
            URL_RDP + user[3],
            {'User-Agent': USER_AGENT},
            (RDP_ACCOUNT['login'], RDP_ACCOUNT['password'])
        )
        user_shops = convert_page_to_shops(remote_page)
        shops.extend(user_shops)

    return upsert_db_shops(shops)


def init_db_user():
    query = '''
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    nick TEXT NOT NULL UNIQUE,
    url_key TEXT NOT NULL,
    cookie TEXT NOT NULL
);
        '''
    return query_the_db(SHOPS_DB, query)


def get_db_users():
    query = '''
SELECT *
FROM users
            '''
    return query_the_db(SHOPS_DB, query)


def upsert_db_users(users):
    """Add users to database users table
    Input: users list of tuples
    Call example: upsert_db_users([('id', 'name', 'nick', '', ''), ...])
    """
    for user in users:
        query = f'''
INSERT INTO users (id, name, nick, url_key, cookie)
VALUES {user}
ON CONFLICT(id) DO UPDATE SET
    id = ?, name = ?, nick = ?, url_key = ?, cookie = ?
        '''
        query_the_db(SHOPS_DB, query, user)
    return get_db_users()


if __name__ == '__main__':
    # print(upsert_db_users(users))
    # print(get_db_users())
    print(update_db_shops())

    # print(get_shops_data(5421))

    # remote_page = get_remote_page(
    #     URL_R,
    #     {'User-Agent': USER_AGENT, 'Cookie': USER_COOKIES['Lite']},
    #     (R_ACCOUNT['login'], R_ACCOUNT['password'])
    # )


