import requests
from bs4 import BeautifulSoup
import csv

# url = 'https://auto.ria.com/uk/newauto/marka-jeep/'
# url = 'https://auto.ria.com/uk/newauto/marka-bentley/'
# url = 'https://auto.ria.com/uk/newauto/marka-audi/'
HEADERS = {
           'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
           }
HOST = 'https://auto.ria.com'
FILE = 'cars.csv'


def save_result(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Марка', 'Посилання', 'Ціна в долларах', 'Ціна в гривнях', 'Місто', 'Салон'])
        for item in items:
            writer.writerow([item['title'], item['link'], item['USD'], item['UAH'], item['city'], item['showroom']])


def get_html(url, params=None):
    r = requests.get(url=url, headers=HEADERS, params=params)
    return r


def get_pages_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find_all('span', class_='mhide')
    if pagination:
        return int(pagination[-1].get_text())
    return 1


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='proposition')
    cars = []
    for item in items:
        price = item.find('div', class_='proposition_price').get_text().split('•')
        usd_price = price[0].strip()
        if price[1].strip():
            uah_price = price[1].strip()
        else:
            uah_price = 'no information'

        location = item.find('div', class_='proposition_region').get_text().split('•')
        if location[1].strip():
            showroom = location[1].strip()
        else:
            showroom = 'car dealership is not specified'

        cars.append(
            {
                'title': item.find('h3', class_='proposition_name').get_text(strip=True),
                'link': HOST + item.find('a').get('href'),
                'USD': usd_price,
                'UAH': uah_price,
                'city': location[0].strip(),
                'showroom': showroom
            }
        )
    return cars


def parse(url):
    html = get_html(url)
    if html.status_code == 200:
        cars = []
        pages_num = get_pages_count(html.text)
        for page in range(1, pages_num + 1):
            print(f'Parsing page {page} of {pages_num}...')
            html = get_html(url, params={'page': page})
            cars.extend(get_content(html.text))
        save_result(cars, FILE)
        print(f"Parsing done.\n\n"
              f"received {len(cars)} cars")
    else:
        print(f'Error: {html.status_code}')


if __name__ == '__main__':
    url = input("Enter URL: ")
    url = url.strip()
    parse(url)

