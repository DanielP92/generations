import os
import time
import random
from requests import get
from bs4 import BeautifulSoup as soup

alphabet = 'abcdefghijklmnopqrstuvwxyz'

female_names_url = 'https://www.verywellfamily.com/top-1000-baby-girl-names-2757832'
male_names_url = 'https://www.verywellfamily.com/top-1000-baby-boy-names-2757618'
last_name_url = 'https://surnames.behindthename.com/names/'

first_names_urls = [female_names_url, male_names_url]
surname_urls = [last_name_url + f'letter/{letter}/0' for letter in alphabet]

class AllNames:
    first_names = {'boy': [], 'girl': []}
    surnames = []
    
    def __init__(cls):
        if os.path.exists('surnames.txt'):
            print('surnames.txt exists')
        else:
            cls.write_all_surnames()

        print('getting first names...')
        for url in first_names_urls:
            cls.get_first_names(url)
            
        print('getting surnames')
        cls.get_surnames()


    def write_all_surnames(cls):
        for url in surname_urls:
            try:
                cls.write_surnames_to_file(url)
                time.sleep(1)
            except AttributeError:
                pass

    def get_first_names(cls, url):
        names = soup(get(url).content, 'html.parser').ol
        name_list = names.find_all('li')
        name_list = [li.text.strip() for li in name_list]
        for name in name_list:
            for key in cls.first_names.keys():
                if str(key) in str(url):
                    cls.first_names[key].append(name)

    def get_surnames(cls):
        with open('surnames.txt','r', encoding='utf-8') as text_file:
            for name in text_file:
                cls.surnames.append(name.strip())

    def write_surnames_to_file(cls, url):
        pg_no = 1
        last_pg = pg_no
        url = url.replace(url[len(url) - 1], str(pg_no))

        page_soup = soup(get(url).content, 'html.parser')

        pages = page_soup.find('div', class_='pgblurb').text.strip()
        if 'page' in pages:
            last_pg = int(pages[-1]) + 1

        with open('surnames.txt', 'a') as text_file:
            if last_pg == 1:
                url = url
                print(url)
                page_soup = page_soup
                name_info = page_soup.find_all('span', class_='listname')
                for name in name_info:
                    text_file.write(name.a.text.capitalize() + '\n')
                print('names written to file')
            else:
                for i in range(1, last_pg):
                    url = url.replace(url[len(url) - 1], str(i))
                    print(url)
                    page_soup = soup(get(url).content, 'html.parser')
                    name_info = page_soup.find_all('span', class_='listname')
                    for name in name_info:
                        text_file.write(name.a.text.capitalize() + '\n')
                    print('names written to file')
