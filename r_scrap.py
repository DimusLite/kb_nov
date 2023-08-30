"""Scraping sps-holding.ru/r/ and sps-holding.ru/rdp/ data"""
import requests

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


def get_remote_page(url, headers=None, auth=None):
    response = requests.get(url=url,
                            headers=headers,
                            auth=auth)
    if response.ok:
        return response.text
    else:
        print('Requests error', response.status_code)
    return None


if __name__ == '__main__':
    # remote_page = get_remote_page(
    #     URL_RDP+USER_KEYS['Galasha'],
    #     {'User-Agent': USER_AGENT},
    #     (RDP_ACCOUNT['login'], RDP_ACCOUNT['password'])
    # )

    remote_page = get_remote_page(
        URL_R,
        {'User-Agent': USER_AGENT, 'Cookie': USER_COOKIES['Lite']},
        (R_ACCOUNT['login'], R_ACCOUNT['password'])
    )

    print(remote_page)
