import streamlit as st
import requests
import json

st.title("Предсказание прибыльности заказа")
st.write("Введите параметры заказа, чтобы узнать, принесет ли он прибыль.")

API_URL = "http://127.0.0.1:8000/predict"

# Словари для маппинга
STATE_CODES = {
    'AC': 0, 'AL': 1, 'AM': 2, 'AP': 3, 'BA': 4, 'CE': 5, 'DF': 6, 'ES': 7,
    'GO': 8, 'MA': 9, 'MG': 10, 'MS': 11, 'MT': 12, 'PA': 13, 'PB': 14,
    'PE': 15, 'PI': 16, 'PR': 17, 'RJ': 18, 'RN': 19, 'RO': 20, 'RR': 21,
    'RS': 22, 'SC': 23, 'SE': 24, 'SP': 25, 'TO': 26
}

CATEGORY_CODES_RU = {
    "Агробизнес и промышленность": 0,
    "Продукты питания": 1,
    "Еда и напитки": 2,
    "Искусство": 3,
    "Товары для рукоделия": 4,
    "Товары для вечеринок": 5,
    "Рождественские товары": 6,
    "Аудиотехника": 7,
    "Автотовары": 8,
    "Детские товары": 9,
    "Напитки": 10,
    "Красота и здоровье": 11,
    "Игрушки": 12,
    "Постельное белье и ванная": 13,
    "Товары для дома": 14,
    "Товары для дома (2)": 15,
    "Строительство и ремонт": 16,
    "Музыка (CD, DVD)": 17,
    "Фото и кино": 18,
    "Климатическая техника": 19,
    "Игровые приставки": 20,
    "Строительные инструменты": 21,
    "Инструменты": 22,
    "Освещение (Стройка)": 23,
    "Садовые инструменты": 24,
    "Средства безопасности": 25,
    "Разное / Интересное": 26,
    "DVD и Blu-ray": 27,
    "Бытовая техника": 28,
    "Бытовая техника (2)": 29,
    "Электроника": 30,
    "Мелкая бытовая техника": 31,
    "Спорт и отдых": 32,
    "Сумки и аксессуары": 33,
    "Обувь": 34,
    "Спортивная одежда": 35,
    "Женская одежда": 36,
    "Детская одежда": 37,
    "Мужская одежда": 38,
    "Нижнее белье и пляжная одежда": 39,
    "Садовые инструменты (Мода)": 40,
    "Цветы": 41,
    "Гигиена и подгузники": 42,
    "Промышленность и бизнес": 43,
    "Компьютерные аксессуары": 44,
    "Музыкальные инструменты": 45,
    "Кухонная утварь": 46,
    "Книги (Импорт)": 47,
    "Книги (Общие)": 48,
    "Книги (Технические)": 49,
    "Чемоданы и аксессуары": 50,
    "Маркетплейс": 51,
    "Мебель, матрасы и обивка": 52,
    "Мебель для кухни и сада": 53,
    "Мебель и декор": 54,
    "Офисная мебель": 55,
    "Мебель для спальни": 56,
    "Мебель для гостиной": 57,
    "Музыка": 58,
    "Канцелярия": 59,
    "Игровые ПК": 60,
    "Компьютеры": 61,
    "Парфюмерия": 62,
    "Зоотовары": 63,
    "Техника для дома и кофе": 64,
    "Кухонная техника": 65,
    "Часы и подарки": 66,
    "Страхование и услуги": 67,
    "Сигнализация и безопасность": 68,
    "Планшеты и печать": 69,
    "Телефония": 70,
    "Стационарные телефоны": 71,
    "Неизвестно": 72,
    "Хозяйственные товары": 73
}

# Создаем обратные словари для отображения
STATE_NAMES = {v: k for k, v in STATE_CODES.items()}
CATEGORY_NAMES = {v: k for k, v in CATEGORY_CODES_RU.items()}

with st.form("order_form"):
    st.header("Параметры заказа")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("География")
        customer_state = st.selectbox(
            "Штат клиента",
            options=list(STATE_CODES.keys()),
            index=list(STATE_CODES.keys()).index('SP')  # SP по умолчанию
        )

        seller_state = st.selectbox(
            "Штат продавца",
            options=list(STATE_CODES.keys()),
            index=list(STATE_CODES.keys()).index('SP')
        )

    with col2:
        st.subheader("Товар")
        product_category = st.selectbox(
            "Категория товара",
            options=list(CATEGORY_CODES_RU.keys()),
            index=0
        )

    st.subheader("Габариты и доставка")

    col3, col4, col5 = st.columns(3)
    with col3:
        product_length_cm = st.number_input("Длина (см)", min_value=0.0, value=20.0)
    with col4:
        product_height_cm = st.number_input("Высота (см)", min_value=0.0, value=10.0)
    with col5:
        product_width_cm = st.number_input("Ширина (см)", min_value=0.0, value=15.0)

    col6, col7 = st.columns(2)
    with col6:
        delivery_days = st.number_input("Дней доставки", min_value=0, value=15)
        product_photos_qty = st.number_input("Кол-во фото товара", min_value=0, value=3)
    with col7:
        is_delayed = st.selectbox("Была ли задержка?", options=[0, 1], format_func=lambda x: "Нет" if x == 0 else "Да")

    st.subheader("Время заказа")
    col8, col9 = st.columns(2)
    with col8:
        order_month = st.slider("Месяц", min_value=1, max_value=12, value=6)
    with col9:
        order_dayofweek = st.slider("День недели", min_value=0, max_value=6, value=1,
                                    help="0=Понедельник, 6=Воскресенье")

    submitted = st.form_submit_button("Предсказать прибыльность", type="primary")

    if submitted:
        # Подготавливаем payload с кодами
        payload = {
            "delivery_days": float(delivery_days),
            "is_delayed": int(is_delayed),
            "product_length_cm": float(product_length_cm),
            "product_height_cm": float(product_height_cm),
            "product_width_cm": float(product_width_cm),
            "product_photos_qty": int(product_photos_qty),
            "customer_state": STATE_CODES[customer_state],
            "seller_state": STATE_CODES[seller_state],
            "product_category_name": CATEGORY_CODES_RU[product_category],
            "order_month": int(order_month),
            "order_dayofweek": int(order_dayofweek)
        }

        try:
            with st.spinner("Анализирую данные..."):
                response = requests.post(API_URL, json=payload, timeout=10)
                response.raise_for_status()
                result = response.json()

            st.success("Предсказание готово!")

            # Отображаем результат
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Вероятность прибыли", f"{result['probability']:.1%}")
            with col_b:
                status = "Прибыльный!" if result['is_profitable'] == 1 else "Убыточный("
                st.metric("Результат", status)

            st.info(f"Модель: {result.get('model', 'RandomForest')}")

        except requests.exceptions.RequestException as e:
            st.error(f"Ошибка подключения к API: {e}")
            st.warning("Убедитесь, что API запущен командой: uvicorn api:app --reload")