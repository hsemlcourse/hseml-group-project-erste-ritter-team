from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import os
import uvicorn

app = FastAPI(
    title="Olist Profitability Predictor",
    description="API для предсказания прибыльности заказов на основе модели Random Forest",
    version="1.0.0"
)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "profit_rf_gs.pkl")

# Загрузка модели при старте сервера
try:
    with open(MODEL_PATH, "rb") as f:
        model_data = joblib.load(f)

    if isinstance(model_data, dict):
        model = model_data.get("model")
        EXPECTED_FEATURES = model_data.get("features") or model_data.get("feature_names")
    else:
        model = model_data
        EXPECTED_FEATURES = None

    if EXPECTED_FEATURES is None:
        EXPECTED_FEATURES = [
            'delivery_days', 'is_delayed', 'product_length_cm', 'product_height_cm',
            'product_width_cm', 'product_photos_qty', 'customer_state', 'seller_state',
            'product_category_name', 'product_volume', 'order_month', 'order_dayofweek'
        ]

    if model is None:
        raise ValueError("Объект модели не найден в файле .pkl")

    print(f"Модель успешно загружена: {MODEL_PATH}")
    print(f"Ожидаемый порядок признаков: {EXPECTED_FEATURES}")

except Exception as e:
    print(f"Критическая ошибка загрузки модели: {e}")
    model = None
    EXPECTED_FEATURES = []


# Pydantic-схема для валидации входных данных
class OrderInput(BaseModel):
    delivery_days: float
    is_delayed: int
    product_length_cm: float
    product_height_cm: float
    product_width_cm: float
    product_photos_qty: int
    customer_state: int
    seller_state: int
    product_category_name: int
    order_month: int
    order_dayofweek: int

    class Config:
        json_schema_extra = {
            "example": {
                "delivery_days": 12.0,
                "is_delayed": 0,
                "product_length_cm": 25.0,
                "product_height_cm": 15.0,
                "product_width_cm": 20.0,
                "product_photos_qty": 4,
                "customer_state": 1,
                "seller_state": 3,
                "product_category_name": 5,
                "order_month": 6,
                "order_dayofweek": 2
            }
        }


# Эндпоинты
@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Olist Profitability API. Перейдите в /docs для тестирования.",
        "model_loaded": model is not None
    }

@app.post("/predict")
def predict(order: OrderInput):
    if model is None:
        raise HTTPException(status_code=500, detail="Модель не загружена")

    # Превращаем входные данные в словарь
    data_dict = order.model_dump()

    # Автоматически считаем объем
    data_dict['product_volume'] = data_dict['product_length_cm'] * data_dict['product_height_cm'] * data_dict[
        'product_width_cm']

    # Создаем DataFrame
    df = pd.DataFrame([data_dict])

    # Выстраиваем колонки в точном порядке, как при обучении
    df = df[EXPECTED_FEATURES]

    # Предсказание
    proba = model.predict_proba(df)[0][1]

    return {
        "is_profitable": int(proba >= 0.5),
        "probability": round(float(proba), 4),
        "model": "RandomForest_GridSearchCV"
    }

# Запуск при прямом вызове python api.py
if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)