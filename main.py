import requests
import json
from bs4 import BeautifulSoup
from fake_headers import Headers
from pprint import pprint

HOST = "https://spb.hh.ru/search/vacancy?text=python&area=1&area=2&page="


def get_headers():
    return Headers(browser="firefox", os="win").generate()


# получаем количество страниц
resp = requests.get(url=HOST, headers=get_headers()).text
soup1 = BeautifulSoup(resp, 'lxml')
page_count = soup1.find('div', attrs={'class': 'pager'}).find_all('span', recursive=False)[-1].find('a').find(
    'span').text


def get_text(url):
    return requests.get(url, headers=get_headers()).text


def get_link(page):
    html = get_text(f"{HOST}{page}{'&hhtmFrom=vacancy_search_list'}")
    soup = BeautifulSoup(html, features="lxml")
    tag_lists = soup.find_all("a", class_="serp-item__title")
    links = []
    for tag_list in tag_lists:
        link = tag_list['href'].split('?')[0]
        links.append(link)
    return links


def parse_page():
    links_list = []
    for page in range(int(page_count)):
        print(f'Загрузка {page + 1}/{page_count} страницы')
        links = get_link(page)
        for link in links:
            html = get_text(f"{link}")
            soup = BeautifulSoup(html, features="lxml")
            description = str(soup.find(class_="g-user-content"))
            if 'flask' in description.lower() and 'django' in description.lower():
                links_list.append(link)
    return links_list


def get_info():
    get_info_dict = []
    links = parse_page()
    for link in links:
        html = get_text(f"{link}")
        soup = BeautifulSoup(html, features="lxml")
        salary = soup.find(class_="bloko-header-section-2 bloko-header-section-2_lite").text.replace('\xa0',
                                                                                                     '').replace(
            '\u202f', '')
        if salary is None:
            return
        company = soup.find(attrs={'data-qa': 'bloko-header-2'}).text.replace('\xa0', ' ')
        if company is None:
            return
        city = soup.find(attrs={'data-qa': 'vacancy-view-location'})
        if city is None:
            city = soup.find(attrs={'data-qa': 'vacancy-view-raw-address'})
        job_dict = {
            "Ссылка на вакансию": link,
            "Заработная плата": salary,
            "Наименование организации": company,
            "Город": city.text.split(',')[0]
        }
        get_info_dict.append(job_dict)

    with open('VacancyFromHH.json', 'w', encoding="utf-8") as f:
        json.dump(get_info_dict, f, ensure_ascii=False, indent=4)

    print(f'Загрузка завершена')


if __name__ == "__main__":
    get_info()
