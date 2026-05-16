import pandas as pd

def load_and_clean_data(data_path="data/raw/"):
    """
    Загружает и очищает данные (логика из EDA)
    """

    customers = pd.read_csv(f"{data_path}/olist_customers_dataset.csv")
    geolocation = pd.read_csv(f"{data_path}/olist_geolocation_dataset.csv")
    order_items = pd.read_csv(f"{data_path}/olist_order_items_dataset.csv")
    order_payments = pd.read_csv(f"{data_path}/olist_order_payments_dataset.csv")
    orders = pd.read_csv(f"{data_path}/olist_orders_dataset.csv")
    products = pd.read_csv(f"{data_path}/olist_products_dataset.csv")
    sellers = pd.read_csv(f"{data_path}/olist_sellers_dataset.csv")
    category_name_t = pd.read_csv(f"{data_path}/product_category_name_translation.csv")
    review = pd.read_csv(f"{data_path}/olist_order_reviews_dataset.csv")

    # фичи из orders
    orders["is_delivered"] = orders["order_delivered_customer_date"].notna().astype('int32')
    orders["is_approved"] = orders["order_approved_at"].notna().astype('int32')

    orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"])
    orders["order_delivered_customer_date"] = pd.to_datetime(orders["order_delivered_customer_date"])

    orders["delivery_days"] = (
        orders["order_delivered_customer_date"] - orders["order_purchase_timestamp"]
    ).dt.days

    orders["delivery_days"] = orders["delivery_days"].fillna(-1)

    orders["is_delayed"] = (
        (orders["order_delivered_customer_date"] > orders["order_estimated_delivery_date"]) &
        (orders["is_delivered"] == 1)
    ).astype('int32')

    # CLEAN products
    products["product_category_name"] = products["product_category_name"].fillna("unknown")

    for col in ["product_name_lenght", "product_description_lenght", "product_photos_qty"]:
        products[col] = products[col].fillna(0)

    for col in ["product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm"]:
        products[col] = products[col].fillna(products[col].median())

    return {
        "customers": customers,
        "geolocation": geolocation,
        "order_items": order_items,
        "order_payments": order_payments,
        "orders": orders,
        "products": products,
        "sellers": sellers,
        "category_name_t": category_name_t,
        "review": review
    }

# Мерж
def merge_data(data):
    """
    Собираем единый датасет
    """

    df = data["orders"] \
        .merge(data["order_items"], on="order_id", how="left") \
        .merge(data["products"], on="product_id", how="left") \
        .merge(data["customers"], on="customer_id", how="left") \
        .merge(data["sellers"], on="seller_id", how="left") \
        .merge(data["order_payments"], on="order_id", how="left")

    return df

# Фич инженеринг
def create_features(df):
    """
    Дополнительные признаки
    """

    # объем
    df["product_volume"] = (
        df["product_length_cm"] *
        df["product_height_cm"] *
        df["product_width_cm"]
    )

    # время
    df["order_month"] = df["order_purchase_timestamp"].dt.month
    df["order_dayofweek"] = df["order_purchase_timestamp"].dt.dayofweek

    return df

# TARGET

def create_target(df):
    COST_PER_GRAM = 0.02

    df["estimated_cost"] = df["product_weight_g"] * COST_PER_GRAM
    df["total_cost"] = df["estimated_cost"] + df["freight_value"]

    df["profit"] = df["price"] - df["total_cost"]

    df["profit_margin"] = df["profit"] / (df["total_cost"] + 1e-6)

    df["target"] = (df["profit_margin"] >= 0.2).astype('int32')

    return df

def encode_categories(df):
    """
    Простое кодирование категорий
    """

    cat_cols = [
        "customer_state",
        "seller_state",
        "product_category_name"
    ]

    for col in cat_cols:
        df[col] = df[col].astype("category").cat.codes

    return df

def final_clean(df):
    """
    Финальная зачистка после merge
    """

    # удаляем строки без ключевых числовых признаков
    df = df.dropna(subset=[
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
        "product_photos_qty"
    ])

    # категории
    df["customer_state"] = df["customer_state"].fillna("unknown")
    df["seller_state"] = df["seller_state"].fillna("unknown")

    return df

# Собираем датасет
def build_dataset(data_path="data/raw/"):
    """
    Полный pipeline подготовки данных
    """

    data = load_and_clean_data(data_path)
    df = merge_data(data)
    df = final_clean(df)
    df = create_features(df)
    df = create_target(df)
    df = encode_categories(df)

    return df