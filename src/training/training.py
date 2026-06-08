import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score
from sklearn.model_selection import train_test_split
import mlflow



def entrenar_xgboost(X: pd.DataFrame,
                     y:pd.Series,
                     test_size:float,
                     n_estimators: int = 500,
                     learning_rate: float = 0.05):
    """
    Entrena un XGBRegressor con los parámetros dados y registra con mlflow.
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, shuffle=False, random_state=0
    )

    model = XGBRegressor(
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        random_state=0
    )

    with mlflow.start_run():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 =  r2_score(y_test, y_pred)


        mlflow.log_param("n_estimators",n_estimators)
        mlflow.log_param("learning_rate",learning_rate)
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("rmse",rmse)
        mlflow.log_metric("r2",r2)
        mlflow.xgboost.log_model(model,"model")

        trains_ds = mlflow.data.from_pandas(pd.concat([X,y],axis = 1),source = "training_data")
        mlflow.log_input(trains_ds, context = "training")

        print(f"Modelo entrenado. mae: {mae}, rmse: {rmse}, r2: {r2}")
        return model, y_test, y_pred



