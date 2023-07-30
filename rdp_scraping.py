"""Scraping sps-holding.ru/rdp data"""
import requests

SHOPS_URL = "https://sps-holding.ru/rdp/?mag"


def get_credentials():
    return []


def scrap_rdp(cred):
    response = requests.get(SHOPS_URL, auth=('legkiy.dmitriy', 'aeP7ohJu'))
    return response.text


if __name__ == '__main__':
    credentials = get_credentials()
    raw_data = scrap_rdp(credentials)
    print(f'^{raw_data}$')
