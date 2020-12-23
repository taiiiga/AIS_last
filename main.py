# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import re
import os

os.system('chcp 65001')

URL = 'https://torgi.gov.ru/'
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/87.0.4280.88 Mobile Safari/537.36',
    'accept': '*/*'
}


# Общие функции
def get_html(url, params=None):
    response = requests.get(url, headers=HEADERS, params=params)
    response.encoding = 'utf-8'
    return response


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def separate_capital_words(words):
    new_words = re.findall('[А-Я][^А-Я]*', words)
    return new_words


def separate_numbers(words, h):
    new_words = words.split('Л')
    string = str(new_words[h])
    return string


# Функции для первого уровня
def get_main(soup):
    items = soup.find_all('span', id='auctions_menu')[0].find_all('li')
    torgi = []
    id = 0
    for item in items:
        torgi.append({
            'id': id,
            'title': item.find('a').get_text(),
            'url': item.find('a').get('href')
        })
        id += 1
    return torgi


def parse_main(url):
    html = get_html(url)
    if html.status_code == 200:
        return get_main(get_content(html.text))
    else:
        print("Ошибка")


# Функции для второго уровня
def get_list(soup):
    lots = []
    number = 2
    items = soup.find_all('tr', {"class": "datarow"})
    for item in items:
        tds = item.find_all('td', {"class": "datacell"})
        buffer = []
        if tds[0].find('span').find('a') is not None:
            buffer.append(tds[0].find('span').find('a', title='Просмотр').get('href'))
            buffer.append(tds[1].find('span').get_text())
            try:
                buffer.append(tds[2].find('span').find('span').find('span').get_text())
            except:
                buffer.append(tds[2].find('span').find('span').get_text())
            buffer.append('Лот 1')
        if len(lots) > 0:
            if lots[len(lots) - 1].get('Номер извещения') == buffer[2]:
                buffer[3] = 'Лот ' + str(number)
                number += 1
        lots.append({
            'url': buffer[0],
            'Организатор торгов': buffer[1],
            'Номер извещения': separate_numbers(buffer[2], 0),
            'Номер лота': buffer[3]
        })
    return lots


def parse_list(url):
    html = get_html(url)
    if html.status_code == 200:
        return get_list(get_content(html.text))
    else:
        print("Ошибка")


# Функции для третьего уровня
def get_deal(soup):
    titles = soup.find_all('div', id='tabsLot-tab-0')[0].find_all('tr')
    for i in range(len(titles)):
        try:
            check1 = titles[i].find_all('td')[0].find('label')
            check2 = titles[i].find_all('td')[1].find('span')
            if check1 is not None and check2 is not None:
                word = check1.get_text().strip().upper()
                status = check2.get_text().strip()
                try:
                    print(word + ' ' + status)
                except:
                    print('ПЛОЩАДЬ: ' + status)
        except:
            pass


def parse_deal(url):
    html = get_html(url)
    if html.status_code == 200:
        get_deal(get_content(html.text))
    else:
        print("Ошибка")


sections = parse_main(URL + 'index.html')
sections.pop(len(sections) - 1)
for section in sections:
    print(section.get('id'), '-', section.get('title'))
section = int(input("Выберите раздел: "))

print()
lots = parse_list(URL + sections[section].get('url'))

j = 0
print('')
if len(lots) != 0:
    print("Торги:")
    for lot in lots:
        print(j, ':', lot.get('Организатор торгов'), '-', lot.get('Номер извещения'), '-', lot.get('Номер лота'))
        j += 1
    lot = int(input("Выберите лот: "))

    print()
    parse_deal(URL + lots[lot].get('url'))
else:
    print("Торгов нет")
