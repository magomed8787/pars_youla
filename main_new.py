import requests
import re
import csv
from bs4 import BeautifulSoup
from datetime import datetime


with open(f"demo_file.csv", "w", encoding="utf-8") as file:
    writer = csv.writer(file)

    writer.writerow(
        (
            "Имя пользователя",
            "Заголовок",
            "Цена",
            "Ссылка на объявление",
            "Дата объявления",
            "Просмотры",
            "Продавец. Ссылка",
            "Продавец. Год регистрации",
            "Продавец. Активные объявления",
            "Продавец. Проданные объявления",
            "Продавец. Рейтинг",
            "Продавец. Количество отказов",
            "Количество отзывов",
        )
    )

def graphql_request(attributes_, search=''):
    products = []
    cursor = ''
    while True:
        headers = {
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Origin': 'https://youla.ru',
            'Referer': 'https://youla.ru/mahachkala/auto',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'accept': '*/*',
            'appId': 'web/3',
            'authorization': '',
            'content-type': 'application/json',
            'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'uid': '653502fe9f9b6',
            'x-app-id': 'web/3',
            'x-offset-utc': '+04:00',
            'x-uid': '653502fe9f9b6',
            'x-youla-splits': '8a=7|8b=7|8c=0|8m=0|8v=0|8z=0|16a=0|16b=0|64a=4|64b=0|100a=14|100b=83|100c=0|100d=0|100m=0',
        }

        json_data = {
            'operationName': 'catalogProductsBoard',
            'variables': {
                'sort': 'DEFAULT',
                'attributes': attributes_,
                'datePublished': None,
                'location': {
                    'latitude': None,
                    'longitude': None,
                    'city': '576d0614d53f3d80945f8dfe',
                    'distanceMax': None,
                },
                'search': search,
                'cursor': cursor,
            },
            'extensions': {
                'persistedQuery': {
                    'version': 1,
                    'sha256Hash': '6e7275a709ca5eb1df17abfb9d5d68212ad910dd711d55446ed6fa59557e2602',
                },
            },
        }

        res = requests.post('https://api-gw.youla.io/graphql', headers=headers, json=json_data).json()
        # print(res)  #Словарь джейсон
        for item in res['data']['feed']['items']:
            if 'product' in item:
                products.append(item['product']['url'])
        has_next_page = res['data']['feed']['pageInfo']['hasNextPage']
        if not has_next_page:
            break
        cursor = res['data']['feed']['pageInfo']['cursor']


    return products


def parse_input_link_to_attributes(link_: str):
    # TODO: пофиксить косяки на примерах
    attributes = []
    params: str = link_.split('?')[1]
    splitted_params = params.split('&')
    slug_dict = {}
    for p in splitted_params:
        tmp = re.search(r'attributes\[(\w+)]\[(\w+)]=(\w+)', p)
        slug, key, value = tmp.group(1), tmp.group(2), tmp.group(3)
        if key.isdigit():
            slug_dict = {'slug': slug, 'value': [value], 'to': None, 'from': None}
            attributes.append(slug_dict)
            slug_dict = {}
        else:
            if slug_dict:
                slug_dict[key] = int(value) if value.isdigit() else value
                attributes.append(slug_dict)
                slug_dict = {}
            else:
                slug_dict = {'slug': slug, 'value': None, key: int(value) if value.isdigit() else value}
    return attributes


def parse_product(product_url_):
    ans = {}
    res = requests.get(product_url_)
    tmp = re.search(f'"productId":"(.+?)"', res.text)
    if tmp:
        product_id = tmp.group(1)
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.6',
            'Connection': 'keep-alive',
            'Origin': 'https://youla.ru',
            'Referer': 'https://youla.ru/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-GPC': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'X-Offset-UTC': '+04:00',
            'X-Youla-Json': '{}',
            'X-Youla-Splits': '8a=3|8b=3|8c=0|8m=0|8v=0|8z=0|16a=0|16b=0|64a=4|64b=0|100a=69|100b=51|100c=0|100d=0|100m=0',
            'sec-ch-ua': '"Chromium";v="118", "Brave";v="118", "Not=A?Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        params = {
            'app_id': 'web/3'
        }

        ans = requests.get(f'https://api.youla.io/api/v1/product/{product_id}', params=params,
                           headers=headers).json()
    return ans['data']

input_links = open('input_data.txt', 'r').read().split()

def collect_all_products():
    products = []

    for link in input_links:
        attribs = parse_input_link_to_attributes(link)
        products.extend(graphql_request(attribs))

    return products



#
#

if __name__ == '__main__':


    all_products_data = collect_all_products()

    products_urls_list = []

    for item in all_products_data:
        product_url = "https://youla.ru" + item
        products_urls_list.append(product_url)




    for url in products_urls_list:
        # print(url)
        a = parse_product(url)

        # print(a['price'])
        # print(a['name'])

        name = a['owner']['name'] #Имя
        head = a['name'] #Заголовок
        price = a['price'] #Цена
        product_url = url #Ссылка на объявление
        date_add = datetime.fromtimestamp(a['date_created']) #Дата объявления
        views = a['views'] #Просмотры

        user_url = 'https://youla.ru/user/' + a['owner']['id'] + '/active' #Продавец ссылка
        store = 'нет' #Продавец магазин
        date_registered = datetime.fromtimestamp(a['owner']['date_registered']) #Продавец. Год регистрации
        prods_active = a['owner']['prods_active_cnt'] #Продавец. Активные объявления
        prods_sold = a['owner']['prods_sold_cnt'] #Продавец. Проданные объявления
        prods_rating = a['owner']['rating_mark'] #Продавец. Рейтинг
        reviews = a['owner']['rating_mark_cnt'] #Продавец. Количество отзывов
        # print(a)
        # print(date_add)





    #

        with open(f"demo_file.csv.", "a", encoding="utf-8") as file:
            writer = csv.writer(file)

            writer.writerow(
                (
                    name,
                    head,
                    price,
                    product_url,
                    date_add,
                    views,
                    user_url,
                    store,
                    date_registered,
                    prods_active,
                    prods_sold,
                    prods_rating,
                    reviews
                )
            )














