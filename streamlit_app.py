import streamlit as st
import json
from pathlib import Path
from datetime import datetime

# ==============================
# STYLE
# ==============================

st.markdown("""
<style>

/* --- TŁO --- */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #ffe6f2, #ffd6eb);
}

/* --- GŁÓWNY CONTAINER --- */
.main-box {
    background: white;
    padding: 2rem;
    border-radius: 20px;
    box-shadow: 0px 10px 30px rgba(0,0,0,0.1);
    max-width: 700px;
    margin: auto;
}

/* --- TYTUŁ --- */
h1 {
    text-align: center;
    color: #cc0066;
}

/* --- OPIS --- */
.description {
    text-align: center;
    color: #666;
    margin-bottom: 20px;
}

/* --- INPUTY --- */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background-color: #fff0f7 !important;
    color: #4d0026 !important;
    border: 1px solid #ffb3d9;
    border-radius: 12px;
    padding: 10px;
}

/* --- BUTTON --- */
[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(90deg, #ff66b2, #ff3385);
    color: white;
    border-radius: 12px;
    border: none;
    padding: 10px 20px;
    font-weight: bold;
    transition: 0.3s;
}

[data-testid="stFormSubmitButton"] button:hover {
    transform: scale(1.05);
}

</style>
""", unsafe_allow_html=True)

# ==============================
# PLIKI
# ==============================

DATA_FILE = Path("products.json")

# ==============================
# FUNKCJE
# ==============================

def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ==============================
# APP
# ==============================

data = load_data()

st.markdown('<div class="main-box">', unsafe_allow_html=True)

st.title("Glow Tracker ✨")
st.markdown(
    '<p class="description">Śledź ceny swoich ulubionych kosmetyków 💄</p>',
    unsafe_allow_html=True
)

email = st.text_input("Podaj swój adres e-mail")

if email:
    user_products = data.get(email, [])

    if email in data:
        st.success("Znaleziono Twoją istniejącą listę produktów ✨")
    else:
        st.info("To wygląda na Twoją pierwszą wizytę. Dodaj produkty do śledzenia 💖")

    # ==============================
    # LISTA ISTNIEJĄCYCH PRODUKTÓW
    # ==============================
    st.subheader("Twoje zapisane produkty")

    if user_products:
        for i, item in enumerate(user_products):
            # zgodność wsteczna ze starym formatem ["url1", "url2"]
            if isinstance(item, str):
                url = item
                date_added = "brak daty"
            else:
                url = item["url"]
                date_added = item["date_added"]

            col1, col2 = st.columns([5, 1])

            with col1:
                st.write(f"{i+1}. {url}")
                st.caption(f"Dodano: {date_added}")

            with col2:
                if st.button("Usuń", key=f"delete_{i}"):
                    data[email].remove(item)
                    save_data(data)
                    st.rerun()
    else:
        st.write("Nie masz jeszcze zapisanych produktów.")

    # ==============================
    # DODAWANIE NOWYCH PRODUKTÓW
    # ==============================
    st.subheader("Dodaj nowe produkty")

    with st.form("add_products_form"):
        product_urls = st.text_area("Wklej linki (każdy w nowej linii)")
        submitted = st.form_submit_button("Dodaj produkty 💖")

        if submitted:
            urls = [url.strip() for url in product_urls.splitlines() if url.strip()]

            if urls:
                existing_urls = set()

                for item in data.get(email, []):
                    if isinstance(item, str):
                        existing_urls.add(item)
                    else:
                        existing_urls.add(item["url"])

                new_items = []

                for url in urls:
                    if url not in existing_urls:
                        new_items.append({
                            "url": url,
                            "date_added": datetime.now().strftime("%Y-%m-%d %H:%M")
                        })

                if email not in data:
                    data[email] = []

                data[email].extend(new_items)
                save_data(data)

                st.success("Produkty zostały zapisane ✨")
                st.rerun()
            else:
                st.error("Wklej co najmniej jeden link 💔")

st.markdown('</div>', unsafe_allow_html=True)