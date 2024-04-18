"""Цей файл використовується для заповнення БД словами та знаходження для них синонімів"""

import requests
import bs4
import sqlite3
from DataBase import Words, IrregularVerbs
def fill_words():
    """This function fills DB(Words) with words from https://hadiach.city web-site"""
    # заповнення таблиці словами та перекладом
    session_1 = requests.session()
    resp_1 = session_1.get('https://hadiach.city/articles/58204/400-sliv-anglijskoyu-yaki-dopomozhut-zrozumiti-75-tekstiv')

    if resp_1.status_code == 200:
        print('Success')
    else:
        print('bad result')

    soup_1 = bs4.BeautifulSoup(resp_1.text, 'html.parser')

    list_words = []
    for el in soup_1.find_all('div', class_ = 'content'):
        word = el.text.strip().split()
        list_words.append((word[1], word[-1]))


    for el in list_words:
        ob = Words(Word = el[0], Word_Translation = el[1])
        ob.save()

def fill_synonyms():
    """This function fills DB(Words) with word's synonyms from www.thesaurus.com web-site"""
    # заповнення таблиці синонімами
    Words_list = list = Words.select(Words.Word, Words.ID, Words.Word_Translation).execute()
    for word in Words_list:
        session_2 = requests.session()
        resp_2 = session_2.get(f'https://www.thesaurus.com/browse/{word.Word.lower()}')
        soup_2 = bs4.BeautifulSoup(resp_2.text, 'html.parser')

        synonyms_list = []
        for el in soup_2.find_all('section', class_='q7ELwPUtygkuxUXXOE9t ULFYcLlui2SL1DTZuWLn'):
            ul = el.find('ul')
            for li in ul:
                if len(synonyms_list) < 6:
                    synonyms_list.append(li.text)
                else:
                    break

        Words.update(Synonyms='/'.join(synonyms_list)).where(Words.ID == word.ID).execute()

def fill_irregullar():
    """This function fills DB(Irregular Words) with 3 forms of irregullar words and thems translations from www.thesaurus.com web-site"""

    # Заповнення таблиці з неправильними дієсловами
    session_3 = requests.session()
    resp_3 = session_3.get('http://easy-english.com.ua/irregular-verbs/')
    soup_3 = bs4.BeautifulSoup(resp_3.text, 'html.parser')

    table = soup_3.find('div', class_ = 'su-table')
    tbody = table.find('tbody')
    rows = tbody.find_all('tr')

    global_list = []
    for el in rows:
        list = []
        for word in el.find_all('td'):
            list.append(word.text)
        global_list.append(list)

    global_list = [el for el in global_list if len(el) == 4]

    for el in global_list[1:]:
        ob = IrregularVerbs(form_1 = el[0], form_2 = el[1], form_3 = el[2], Translation = el[3])
        ob.save()
