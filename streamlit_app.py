import streamlit as st
import json
from pathlib import Path

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
max-width: 600px;
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

/* --- PLACEHOLDER --- */
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder {
color: #cc6699 !important;
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

/* --- SUCCESS --- */
[data-testid="stSuccess"] {
background-color: #ffe6f2 !important;
color: #cc0066 !important;
border-radius: 10px;
}

/* --- ERROR --- */
[data-testid="stError"] {
background-color: #ffe6e6 !important;
color: #cc0000 !important;
border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# ==============================
# DANE
# ==============================

DATA_FILE = Path('products.json')

if DATA_FILE.exists():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
else:
    data = {}

# ==============================
# UI
# ==============================

st.markdown('<div class="main-box">', unsafe_allow_html=True)

st.title('Glow Tracker ✨')

st.markdown(
    '<p class="description">Śledź ceny swoich ulubionych kosmetyków 💄</p>',
    unsafe_allow_html=True
)

# ==============================
# FORMULARZ
# ==============================

with st.form('product_form'):
    email = st.text_input('Adres e-mail')
    product_urls = st.text_area('Wklej linki (każdy w nowej linii)')

    submitted = st.form_submit_button('Zapisz produkty 💖')

    if submitted:
        urls = [url.strip() for url in product_urls.splitlines() if url.strip()]

        if email and urls:
            data[email] = urls

            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            st.success('Twoje produkty zostały zapisane ✨')
        else:
            st.error('Podaj poprawny e-mail i co najmniej jeden link 💔')

st.markdown('</div>', unsafe_allow_html=True)
    

    