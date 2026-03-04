import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import csv
import sqlite3
from database import db_initialization, add_product, add_price

csv_path = 'data/final_products.csv'

def price_to_float(price_str: str) -> float | None:

    """
    Funkcja do czyszczenia cen z pliku .csv z postaci '89,00 zł' do 89.00
    Zwraca None jeśli w pliku nie ma ceny (?)
    """

    if price_str is None:
        return None
    
    p = str(price_str).strip()

    if p == '' or p.lower() == 'nan':
        return None
    
    p = p.replace('zł', '').strip()
    p = p.replace(' ', '')
    p = p.replace(',', '.')

    try:
        return float(p)
    except ValueError:
        return None
    
def main() -> None:

    db_initialization()

    products_added = 0
    prices_added = 0
    skipped_no_url = 0
    skipped_duplicates = 0

    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            name = row.get('product_title')
            url = row.get('product_url')
            price_raw = row.get('price')

            if not isinstance(url, str) or url.strip() == '':
                skipped_no_url += 1
                continue
    
            #tymczasowo:
            brand = 'Unknown'
            description = None
            target_price = None 

            try:
                product_id = add_product(
                    name = str(name).strip() if name is not None else 'Unknown product',
                    brand = brand, 
                    url = url.strip(),
                    target_price = target_price,
                    description = description
                )
                products_added += 1
            except sqlite3.IntegrityError:
                #pomijamy produkt o tym URL bo juz jest w bazie
                skipped_duplicates += 1
                continue

            price_float = price_to_float(price_raw)
            if price_float is not None:
                add_price(product_id, price_float)
                prices_added += 1

    print(f'Number of products added to the database: {products_added}')
    print(f'Number of prices added to the database: {prices_added}')
    print(f'Number of skipped (missing) URLs: {skipped_no_url}')
    print(f'Number of skipped (duplicate) URLs: {skipped_duplicates}')

if __name__ == '__main__':
    main()

