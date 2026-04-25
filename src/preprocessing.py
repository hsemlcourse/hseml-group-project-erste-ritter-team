import pandas as pd

customers = pd.read_csv('hseml-group-project-erste-ritter-team/data/raw/olist_customers_dataset.csv')
geolocation = pd.read_csv('hseml-group-project-erste-ritter-team/data/raw/olist_geolocation_dataset.csv')
order_items = pd.read_csv('hseml-group-project-erste-ritter-team/data/raw/olist_order_items_dataset.csv')
order_payments = pd.read_csv('hseml-group-project-erste-ritter-team/data/raw/olist_order_payments_dataset.csv')
orders = pd.read_csv('hseml-group-project-erste-ritter-team/data/raw/olist_orders_dataset.csv')
products = pd.read_csv('hseml-group-project-erste-ritter-team/data/raw/olist_products_dataset.csv')
sellers = pd.read_csv('hseml-group-project-erste-ritter-team/data/raw/olist_sellers_dataset.csv')
category_name_t = pd.read_csv('hseml-group-project-erste-ritter-team/data/raw/product_category_name_translation.csv')
review = pd.read_csv('hseml-group-project-erste-ritter-team/data/raw/olist_order_reviews_dataset.csv')

cust_orders = customers.merge(orders, on = 'customer_id', how = 'left')
cust_geo = customers.merge(geolocation, left_on = 'customer_zip_code_prefix', right_on = 'geolocation_zip_code_prefix', how = 'left')
state_counts = customers['customer_state'].value_counts()
orders_payments = orders.merge(order_payments, on='order_id')