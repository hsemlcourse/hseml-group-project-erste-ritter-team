import pandas as pd

def load_and_clean_data():
    customers = pd.read_csv('hseml-group-project-erste-ritter-team/data/raw/olist_customers_dataset.csv')
    geolocation = pd.read_csv('hseml-group-project-erste-ritter-team/data/raw/olist_geolocation_dataset.csv')
    order_items = pd.read_csv('hseml-group-project-erste-ritter-team/data/raw/olist_order_items_dataset.csv')
    order_payments = pd.read_csv('hseml-group-project-erste-ritter-team/data/raw/olist_order_payments_dataset.csv')
    orders = pd.read_csv('hseml-group-project-erste-ritter-team/data/raw/olist_orders_dataset.csv')
    products = pd.read_csv('hseml-group-project-erste-ritter-team/data/raw/olist_products_dataset.csv')
    sellers = pd.read_csv('hseml-group-project-erste-ritter-team/data/raw/olist_sellers_dataset.csv')
    category_name_t = pd.read_csv('hseml-group-project-erste-ritter-team/data/raw/product_category_name_translation.csv')
    review = pd.read_csv('hseml-group-project-erste-ritter-team/data/raw/olist_order_reviews_dataset.csv')

    orders['is_delivered'] = orders['order_delivered_customer_date'].notna().astype(int)
    orders['is_approved'] = orders['order_approved_at'].notna().astype(int)
    orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
    orders['order_delivered_customer_date'] = pd.to_datetime(orders['order_delivered_customer_date'])
    orders['delivery_days'] = (orders['order_delivered_customer_date'] - orders['order_purchase_timestamp']).dt.days
    orders['delivery_days'] = orders['delivery_days'].fillna(-1)
    orders['is_delayed'] = ((orders['order_delivered_customer_date'] > orders['order_estimated_delivery_date']) & (orders['is_delivered'] == 1)).astype(int)

    products['product_category_name'] = products['product_category_name'].fillna('unknown')
    for col in ['product_name_lenght', 'product_description_lenght', 'product_photos_qty']:
        products[col] = products[col].fillna(0)
    for col in ['product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm']:
        products[col] = products[col].fillna(products[col].median())

    return {
        'customers': customers,
        'geolocation': geolocation,
        'order_items': order_items,
        'order_payments': order_payments,
        'orders': orders,
        'products': products,
        'sellers': sellers,
        'category_name_t': category_name_t,
        'review': review
    }