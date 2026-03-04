'''import requests
from bs4 import BeautifulSoup

r = requests.get('https://cosibella.pl/pl/products/skintra-17721')
#print(r.status_code)
#print(r.text[:1000]) 

soup = BeautifulSoup(r.text, 'html.parser')
scripts = soup.find_all('script')


'''