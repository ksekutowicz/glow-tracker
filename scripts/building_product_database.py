import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import time
import random
import os

# ==============================
# KONFIGURACJA
# ==============================

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0 Safari/537.36'}

base_url = 'https://cosibella.pl'
filename = 'data/final_products.csv'

# ==============================
# PRZYGOTOWANIE PLIKU
# ==============================

if not os.path.exists(filename):
    pd.DataFrame(columns=[
        'product_id',
        'product_title',
        'product_url',
        'price'
    ]).to_csv(filename, index=False)

#wczytanie już zapisanych ID (żeby nie duplikować)
existing_ids = set(pd.read_csv(filename)['product_id'].astype(str))

# ==============================
# SESJA
# ==============================

session = requests.Session()
session.headers.update(headers)

# ==============================
# POBRANIE MENU
# ==============================

r = session.get(base_url, timeout=30)
r.raise_for_status()

soup = BeautifulSoup(r.text, 'html.parser')
nav_items = soup.find_all('li', class_='navbar__item')

links = []

for item in nav_items:
    link = item.find('a')
    if link:
        href = link.get('href')
        full_url = urljoin(base_url, href)
        links.append(full_url)

l = pd.DataFrame({'link': links})
l = l.drop_duplicates(subset='link').reset_index(drop=True)

exclude_patterns = [
    '/blog',
    '/promotions/',
    '/bestsellers/',
    '/newproducts/',
    '#',
    'cosibellacorner.pl',
    '/links/',
    '/about/',
    'producers.php'
]

for pattern in exclude_patterns:
    l = l[~l['link'].str.contains(pattern, regex=False, na=False)]

l = l.reset_index(drop=True)
l2 = l.link.tolist()

# ==============================
# SCRAPOWANIE PRODUKTÓW
# ==============================

for i, category_url in enumerate(l2):
    print(f'\nKategoria: {i}/{len(l2)}')

    for j in range(20):

        if j == 0:
            final_link = category_url
        else:
            final_link = f'{category_url}?counter={j}'

        print(f'Strona: {final_link}')

        try:
            r = session.get(final_link, timeout=30)
            r.raise_for_status()
        except requests.RequestException as e:
            print('Błąd requestu:', e)
            break

        soup = BeautifulSoup(r.text, 'html.parser')
        products = soup.find_all('a', class_='product__icon')

        if not products:
            print('Brak produktów – koniec paginacji')
            break

        for product in products:
            product_id = product.get('data-product-id')

            #pomijamy już zapisane
            if not product_id or product_id in existing_ids:
                continue

            product_url = product.get('href')
            product_title = product.get('title')

            container = product.find_parent()

            price = None
            if container:
                price_tag = container.find('strong', class_='price')
                if price_tag:
                    price = price_tag.get_text(strip=True)

            #zapis jednej linijki od razu do pliku
            row = pd.DataFrame([{
                'product_id': product_id,
                'product_title': product_title,
                'product_url': product_url,
                'price': price
            }])

            row.to_csv(filename, mode='a', header=False, index=False)

            existing_ids.add(product_id)

        time.sleep(random.uniform(1, 4))

print('\nSCRAPOWANIE ZAKOŃCZONE')