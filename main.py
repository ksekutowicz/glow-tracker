from pathlib import Path
from datetime import datetime
import json
import pandas as pd

from config import DATA_DIR, VERBOSE

PRODUCTS_FILE = Path("products.json")
COMBINED_HISTORY_FILE = DATA_DIR / "combined_price_history.csv"


def load_tracked_products() -> dict:
    """
    Wczytuje products.json
    """

    if not PRODUCTS_FILE.exists():
        print("brak pliku products.json")
        return {}

    with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_latest_csv_files() -> list[Path]:
    """
    Zwraca listę plików final_products_*.csv posortowaną malejąco po czasie modyfikacji
    """
    files = sorted(
        DATA_DIR.glob("final_products_*.csv"),
        key=lambda path: path.stat().st_mtime,
        reverse=True
    )
    return files


def normalize_price(price):
    """
    Zamienia np.:
    '129,99 zł' -> 129.99
    '89.00' -> 89.0
    None / NaN -> None
    """
    if pd.isna(price):
        return None

    price_str = str(price).strip().lower()
    price_str = price_str.replace("zł", "")
    price_str = price_str.replace("\xa0", "")
    price_str = price_str.replace(" ", "")
    price_str = price_str.replace(",", ".")

    try:
        return float(price_str)
    except ValueError:
        return None


def load_price_dataframe(csv_path: Path) -> pd.DataFrame:
    """
    Wczytuje CSV i normalizuje kolumnę price
    """
    df = pd.read_csv(csv_path)

    required_columns = {"product_url", "price"}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Brak wymaganych kolumn w {csv_path.name}: {missing}")

    df["product_url"] = df["product_url"].astype(str).str.strip()
    df["normalized_price"] = df["price"].apply(normalize_price)

    if "product_title" not in df.columns:
        df["product_title"] = None

    # gdyby były duplikaty URL, zostawiamy ostatni wpis
    df = df.drop_duplicates(subset="product_url", keep="last").reset_index(drop=True)

    return df


def extract_snapshot_datetime(csv_path: Path):
    """
    final_products_22_03_08_00.csv -> datetime(rok_biezacy, 3, 22, 8, 0)
    """
    try:
        raw = csv_path.stem.replace("final_products_", "")
        dt = datetime.strptime(raw, "%d_%m_%H_%M")
        dt = dt.replace(year=datetime.now().year)
        return dt
    except ValueError:
        return None


def make_price_column_name(snapshot_dt: datetime) -> str:
    return f"price_{snapshot_dt.strftime('%Y_%m_%d_%H_%M')}"


def build_combined_price_dataframe(csv_files: list[Path]) -> pd.DataFrame:
    """
    Tworzy jeden zbiorczy dataframe z final_products_*.csv.
    Każdy snapshot dodaje nową kolumnę ceny, np.:
    price_2026_03_22_08_00
    """
    history_df = None

    # chcemy iść od najstarszego do najnowszego
    files_ascending = sorted(csv_files, key=lambda path: path.stat().st_mtime)

    for csv_path in files_ascending:
        snapshot_dt = extract_snapshot_datetime(csv_path)
        if snapshot_dt is None:
            if VERBOSE:
                print(f"Pomijam plik o niepoprawnej nazwie: {csv_path.name}")
            continue

        price_col = make_price_column_name(snapshot_dt)

        df = load_price_dataframe(csv_path)

        current_df = df[["product_url", "product_title", "normalized_price"]].copy()
        current_df = current_df.rename(columns={"normalized_price": price_col})

        if history_df is None:
            history_df = current_df
        else:
            # merge po URL, bo tytuł może się czasem zmienić
            history_df = history_df.merge(
                current_df[["product_url", price_col]],
                on="product_url",
                how="outer"
            )

            # uzupełnienie product_title dla nowych rekordów
            titles_df = current_df[["product_url", "product_title"]].drop_duplicates(subset="product_url")
            history_df = history_df.merge(
                titles_df,
                on="product_url",
                how="left",
                suffixes=("", "_new")
            )

            if "product_title_new" in history_df.columns:
                history_df["product_title"] = history_df["product_title"].fillna(history_df["product_title_new"])
                history_df = history_df.drop(columns=["product_title_new"])

    if history_df is None:
        return pd.DataFrame(columns=["product_url", "product_title"])

    
    price_columns = sorted(
        [col for col in history_df.columns if col.startswith("price_")]
    )
    ordered_columns = ["product_url", "product_title"] + price_columns
    history_df = history_df[ordered_columns]

    return history_df


def save_combined_price_dataframe(df: pd.DataFrame):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(COMBINED_HISTORY_FILE, index=False)


def get_price_columns_with_dates(df: pd.DataFrame):
    """
    Zwraca listę krotek:
    [
        ("price_2026_03_22_08_00", datetime(...)),
        ...
    ]
    posortowaną rosnąco po dacie.
    """
    price_columns = []

    for col in df.columns:
        if not col.startswith("price_"):
            continue

        try:
            raw = col.replace("price_", "")
            dt = datetime.strptime(raw, "%Y_%m_%d_%H_%M")
            price_columns.append((col, dt))
        except ValueError:
            continue

    price_columns.sort(key=lambda x: x[1])
    return price_columns


def get_start_and_current_price(row: pd.Series, date_added_str: str, price_columns_with_dates):
    """
    Dla pojedynczego produktu:
    - start_price = pierwsza cena z kolumny, której data >= date_added
    - current_price = ostatnia niepusta cena z dostępnych kolumn
    """
    try:
        date_added = datetime.strptime(date_added_str, "%Y-%m-%d %H:%M")
    except ValueError:
        return None, None

    start_price = None
    current_price = None

    # start_price
    for col, dt in price_columns_with_dates:
        value = row.get(col)
        if dt >= date_added and pd.notna(value):
            start_price = value
            break

    # current_price = ostatnia dostępna niepusta cena
    for col, _dt in reversed(price_columns_with_dates):
        value = row.get(col)
        if pd.notna(value):
            current_price = value
            break

    return start_price, current_price


def send_notification(email: str, product_url: str, old_price: float, new_price: float):
    condition = True if new_price < old_price else False

    if condition:
        print("\n==============================")
        print("POWIADOMIENIE")
        print(f"Użytkownik: {email}")
        print(f"Produkt: {product_url}")
        print(f"Cena spadła: {old_price:.2f} -> {new_price:.2f} PLN")
        print("==============================")


if __name__ == "__main__":
    tracked_products = load_tracked_products()

    if not tracked_products:
        print("Brak użytkowników lub brak śledzonych produktów")
        raise SystemExit(0)

    csv_files = get_latest_csv_files()

    if len(csv_files) < 1:
        print("Nie znaleziono żadnych plików final_products_*.csv")
        raise SystemExit(0)

    combined_df = build_combined_price_dataframe(csv_files)
    save_combined_price_dataframe(combined_df)

    if combined_df.empty:
        print("Nie udało się zbudować zbiorczego dataframe'a")
        raise SystemExit(0)

    price_columns_with_dates = get_price_columns_with_dates(combined_df)

    if not price_columns_with_dates:
        print("Brak kolumn cenowych w zbiorczym dataframe")
        raise SystemExit(0)

    notifications_count, checked_count, missing_count = 0, 0, 0

    for email, products in tracked_products.items():
        for item in products:
            checked_count += 1

            # zgodność wsteczna: stary format jako zwykły string URL
            if isinstance(item, str):
                url = item.strip()
                date_added = None
            else:
                url = str(item.get("url", "")).strip()
                date_added = item.get("date_added")

            if not url:
                missing_count += 1
                if VERBOSE:
                    print("Pusty URL - pomijam wpis")
                continue

            if not date_added:
                missing_count += 1
                if VERBOSE:
                    print(f"Brak date_added dla produktu: {url}")
                continue

            product_row = combined_df[combined_df["product_url"] == url]

            if product_row.empty:
                missing_count += 1
                if VERBOSE:
                    print(f"Nie znaleziono produktu w zbiorczym pliku: {url}")
                continue

            row = product_row.iloc[0]

            old_price, new_price = get_start_and_current_price(
                row=row,
                date_added_str=date_added,
                price_columns_with_dates=price_columns_with_dates
            )

            if old_price is None or new_price is None:
                missing_count += 1
                if VERBOSE:
                    print(f"Brak ceny startowej lub aktualnej dla produktu: {url}")
                continue

            if old_price != new_price:
                send_notification(email, url, old_price, new_price)
                if new_price < old_price:
                    notifications_count += 1

    if VERBOSE:
        print("\n===== PODSUMOWANIE =====")
        print(f"Sprawdzonych produktów: {checked_count}")
        print(f"Brakujących w CSV: {missing_count}")
        print(f"Wysłanych powiadomień: {notifications_count}")
        print(f"Zbiorczy plik zapisano do: {COMBINED_HISTORY_FILE}")
        print("========================")