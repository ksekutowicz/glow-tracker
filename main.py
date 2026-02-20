from database import db_initialization, add_product

def main():
    db_initialization()

    add_product('Abib - Collagen Eye Patch Jericho Rose Jelly', 'Abib', 'https://cosibella.pl/pl/products/abib-17417', target_price = 70.0, description = 'Płatki pod oczy o działaniu nawilżającym marki Abib')

    add_product('Medicube - Collagen Night Wrapping Peel Off Mask', 'Medicube', 'https://cosibella.pl/pl/products/medicube-21829', target_price = 90.0, description = 'Maska ujędrniająca na noc')

    add_product('Dr. Althea - 345 Relief Cream Mist', 'Dr. Althea', 'https://cosibella.pl/pl/products/dr-althea-27504', target_price = 89.99, description = 'Mgiełka do twarzy o kremowej konsystencji')

if __name__ == '__main__':
    main()