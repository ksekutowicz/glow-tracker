from pathlib import Path
import time

__all__ = ['BASE_URL', 'HEADERS', 'DATA_DIR', 'DB_PATH']

BASE_URL = 'https://cosibella.pl'
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / 'data'
DB_PATH = DATA_DIR / 'price_tracker.db'
#FINAL_PRODUCTS_CSV = DATA_DIR / f"final_products_{time.strftime('%d_%m_%H_%M')}.csv"

HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0 Safari/537.36'}
