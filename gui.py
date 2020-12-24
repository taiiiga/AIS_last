# -*- coding: utf-8 -*-
import requests
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QTableWidget, QLabel, QComboBox, QApplication, QTableWidgetItem, QPushButton
from bs4 import BeautifulSoup
import re
import os
import sys

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

def clear(arr):
    array = []
    word = arr[0]
    array.append(word)
    for i in range(len(arr)):
        if word == arr[i]:
            pass
        else:
            word = arr[i]
            array.append(word)
    return array

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


# Функции для второго уровня
def get_list(soup):
    ths = soup.find_all('th')
    head = []
    for th in ths:
        spans = th.find_all('span')
        for span in spans:
            p = span.find_all('p')
            if len(p) != 0 and p[0].get_text() != '':
                head.append(p[0].get_text())
    head = clear(head)
    print('head after set', head)
    new_head = []
    for item in head:
        new_item = separate_capital_words(item)
        if len(new_item) > 1:
            txt = ''
            for i in new_item:
                txt += i + ' '
        else:
            txt = new_item[0]
        new_head.append(txt)
    print(new_head)
    lots = []
    items = soup.find_all('tr', {"class": "datarow"})
    for item in items:
        tds = item.find_all('td', {"class": "datacell"})
        buffer = []
        for td in tds:
            if td.find('span').find('a') is not None:
                buffer.append(td.find('span').find('a', title='Просмотр').get('href'))
                print('url:', td.find('span').find('a', title='Просмотр').get('href'))
            elif td.find('span').find('span') is not None:
                buffer.append(td.find('span').find('span').get_text())
                print('1:', td.find('span').find('span').get_text())
            elif td.find('span') is not None:
                buffer.append(td.find('span').get_text())
                print('2:', td.find('span').get_text())
        print("БУФЕР РАЗМЕР:", len(buffer))
        slot = {}
        slot.update({'url': buffer[0]})
        for i in range(len(new_head)):
            print(new_head[i] + ' - ' + buffer[i + 1])
            slot.update({new_head[i]: buffer[i + 1]})
        lots.append(slot)
    print('ИТОГ:', len(lots))
    return lots


# Функции для третьего уровня
def get_deal(soup):
    text = {}
    titles = soup.find_all('div', id='tabsLot-tab-0')[0].find_all('tr')
    for i in range(len(titles)):
        try:
            check1 = titles[i].find_all('td')[0].find('label')
            check2 = titles[i].find_all('td')[1].find('span')
            if check1 is not None and check2 is not None:
                word = check1.get_text().strip().upper()
                status = check2.get_text().strip()
                try:
                    text.update({word: status})
                    print(word + ' ' + status)
                except:
                    text.update({'ПЛОЩАДЬ:': status})
                    print('ПЛОЩАДЬ: ' + status)
        except:
            pass
    return text


def parse(url, level):
    html = get_html(url)
    if html.status_code == 200:
        if level == 1:
            return get_main(get_content(html.text))
        elif level == 2:
            return get_list(get_content(html.text))
        elif level == 3:
            return get_deal(get_content(html.text))
    else:
        print("Ошибка")


class Menu(QMainWindow):
    dict = {}
    buttons = []
    sections = []
    lots = []
    deals = {}
    table_columns = 0
    table_rows = 0
    url = ''

    def __init__(self):
        super(Menu, self).__init__()
        self.table = QTableWidget(self)
        self.torgi = QLabel(self)
        self.comboBox = QComboBox(self)
        self.initUI()

    def initUI(self):
        self.setGeometry(200, 200, 800, 470)
        self.setFixedSize(800, 470)
        self.setWindowTitle("Хисамов Искандер")
        self.setWindowIcon(QIcon('favicon.png'))

        self.sections = parse(URL, 1)  # Парсим список разделов
        self.sections.pop(len(self.sections) - 1)

        self.torgi.setText("Торги")
        self.torgi.setGeometry(390, 10, 460, 30)

        for i in range(len(self.sections)):
            self.comboBox.addItem(self.sections[i].get('title'))
        self.comboBox.setGeometry(20, 40, 760, 30)
        self.comboBox.currentTextChanged.connect(self.to_section)

        for i in range(len(self.sections)):
            self.dict.update({self.sections[i].get('title'): i})

        self.table.setGeometry(80, 80, 700, 340)

        for i in range(10):
            button = QPushButton(self)
            button.setText('Открыть')
            button.setGeometry(20, 105 + i * 30, 60, 25)
            button.setEnabled(False)
            button.setVisible(False)
            button.clicked.connect(self.to_deal)
            self.buttons.append(button)

        prev_button = QPushButton(self)
        prev_button.setText('Предыдущая страница')
        prev_button.setGeometry(80, 430, 200, 25)
        prev_button.setEnabled(False)

        next_button = QPushButton(self)
        next_button.setText('Следующая страница')
        next_button.setGeometry(580, 430, 200, 25)
        next_button.setEnabled(False)

        self.to_section()

    # Парсим список лотов
    def to_section(self):
        self.lots = parse(URL + self.sections[self.dict.get(self.comboBox.currentText())].get('url'), 2)

        keys = []
        if len(self.lots) != 0:
            for item in self.lots[0].keys():
                keys.append(item)
            keys = keys[1:]

        self.table_columns = 8
        self.table_rows = len(self.lots)
        self.table.setColumnCount(self.table_columns)
        self.table.setRowCount(self.table_rows)
        self.table.setHorizontalHeaderLabels(keys)

        for i in range(self.table_rows):
            self.buttons[i].setEnabled(True)
            self.buttons[i].setVisible(True)

        for i in range(self.table_rows, 10):
            self.buttons[i].setEnabled(False)
            self.buttons[i].setVisible(False)

        for row in range(self.table_rows):
            col = 0
            for column in keys:
                self.table.setItem(row, col, QTableWidgetItem(self.lots[row].get(column)))
                col += 1
        self.table.setWordWrap(True)

    def to_deal(self):
        for button in self.buttons:
            if button == self.sender():
                index = self.buttons.index(button)
        self.show_deal(URL + self.lots[index].get('url'))

    def show_deal(self, url):
        self.w = Deal(url)
        self.w.show()


class Deal(QMainWindow):
    url = ''

    def __init__(self, url):
        super(Deal, self).__init__()
        self.setGeometry(200, 200, 600, 800)
        self.setFixedSize(600, 800)
        self.setWindowTitle("Хисамов Искандер")
        self.setWindowIcon(QIcon('favicon.png'))
        self.table = QTableWidget(self)
        self.table.setGeometry(20, 20, 560, 760)
        self.url = url
        self.info = parse(self.url, 3)
        key = self.info.keys()
        keys = []
        for item in key:
            keys.append(item)
        value = self.info.values()
        values = []
        for item in value:
            values.append(item)
        all_items = []
        for i in range(len(keys)):
            all_items.append(keys[i])
            all_items.append(values[i])
        self.table_columns = 2
        self.table_rows = len(self.info)
        self.table.setColumnCount(self.table_columns)
        self.table.setRowCount(self.table_rows)
        self.table.setHorizontalHeaderLabels(('Характеристика', 'Значение'))
        count = 0
        for i in range(self.table_rows):
            for column in range(2):
                self.table.setItem(i, column, QTableWidgetItem(all_items[count]))
                count += 1
        self.table.setWordWrap(True)

def menu():
    app = QApplication(sys.argv)
    m = Menu()
    m.show()
    sys.exit(app.exec_())


menu()
