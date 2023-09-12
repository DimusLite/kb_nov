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
        cursor.execute(f'''\
SELECT * 
FROM users
WHERE name = "{param}" OR nick = "{param}"
''')
        user = cursor.fetchone()
        if not user:
            print('user wasnt finded')
            try:
                code_shop = int(param)
                cursor.execute(f'''\
SELECT *
FROM shops
WHERE code = {code_shop}
            ''')
                result = []
                for res in cursor:
                    result.append(res)
                return result
            except ValueError:
                return None
        user_name = user[1]
        cursor.execute(f'''\
SELECT *
FROM shops
WHERE sa = "{user_name}"
    ''')
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
    try:
        sqlite_connection = sqlite3.connect(SHOPS_DB)
        cursor = sqlite_connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                nick TEXT NOT NULL UNIQUE,
                url_key TEXT NOT NULL,
                cookie TEXT NOT NULL
            );
        ''')
        return True
    except sqlite3.Error as error:
        print("SQLite connection error", error)
    finally:
        if (sqlite_connection):
            sqlite_connection.commit()
            sqlite_connection.close()
            print("SQLite connection closed")
    return False


def get_db_users():
    try:
        sqlite_connection = sqlite3.connect(SHOPS_DB)
        cursor = sqlite_connection.cursor()
        cursor.execute('''
SELECT *
FROM users
            ''')
        users = []
        for res in cursor:
            users.append(res)
        return users
    except sqlite3.Error as error:
        print("SQLite connection error", error)
    finally:
        if (sqlite_connection):
            sqlite_connection.commit()
            sqlite_connection.close()
            print("SQLite connection closed")
    return False


def upsert_db_users(users):
    """Add users to database users table
    Input: users list of tuples
    Call example: upsert_db_users([('id', 'name', 'nick', '', ''), ...])
    """
    try:
        sqlite_connection = sqlite3.connect(SHOPS_DB)
        cursor = sqlite_connection.cursor()
        for user in users:
            sql_query = f'''
            INSERT INTO users (id, name, nick, url_key, cookie)
            VALUES {user}
            ON CONFLICT(id) DO UPDATE SET
                id = ?, name = ?, nick = ?, url_key = ?, cookie = ?
        '''
            cursor.execute(sql_query, user)
        return True
    except sqlite3.Error as error:
        print("SQLite connection error", error)
    finally:
        if (sqlite_connection):
            sqlite_connection.commit()
            sqlite_connection.close()
            print("SQLite connection closed")
    return False


if __name__ == '__main__':
    # print(upsert_db_users(users))
    print(get_db_users())
    # print(update_db_shops())

    # print(get_shops_data(5421))

    # remote_page = get_remote_page(
    #     URL_R,
    #     {'User-Agent': USER_AGENT, 'Cookie': USER_COOKIES['Lite']},
    #     (R_ACCOUNT['login'], R_ACCOUNT['password'])
    # )


