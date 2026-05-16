import joblib
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import roc_auc_score

# Модели
def get_models():
    """
    5 моделей для экспериментов
    """

    return {
        "logreg": LogisticRegression(max_iter=1000),
        "random_forest": RandomForestClassifier(random_state=2804),
        "gradient_boosting": GradientBoostingClassifier(),
        "knn": KNeighborsClassifier(),
        "svm": SVC(probability=True)
    }

# pipeline
def build_pipeline(model_name, model):
    """
    Добавим scaler
    """

    if model_name in ["logreg", "knn", "svm"]:
        return Pipeline([
            ("scaler", StandardScaler()),
            ("model", model)
        ])
    else:
        return Pipeline([
            ("model", model)
        ])


# Обучение
def train_model(pipe, X_train, y_train):
    pipe.fit(X_train, y_train)
    return pipe


def evaluate_model(pipe, X_test, y_test):
    proba = pipe.predict_proba(X_test)[:, 1]
    return roc_auc_score(y_test, proba)


# Тюнинг
def tune_random_forest(X_train, y_train):

    pipe = Pipeline([
        ("model", RandomForestClassifier(random_state=2804))
    ])

    param_grid = {
        "model__n_estimators": [100, 200],
        "model__max_depth": [5, 10, None]
    }

    grid = GridSearchCV(
        pipe,
        param_grid,
        cv=3,
        scoring="roc_auc",
        n_jobs=-1
    )

    grid.fit(X_train, y_train)

    return grid

def tune_svm(X_train, y_train):

    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("model", SVC(probability=True))
    ])

    param_grid = {
        "model__C": [0.1, 1, 10],
        "model__kernel": ["rbf", "linear"]
    }

    grid = GridSearchCV(
        pipe,
        param_grid,
        cv=3,
        scoring="roc_auc",
        n_jobs=-1
    )

    grid.fit(X_train, y_train)

    return grid

# Сохраняем модели
def save_model(model, path="models/best_model.pkl"):
    joblib.dump(model, path)