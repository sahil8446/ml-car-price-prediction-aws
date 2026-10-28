from xgboost import XGBRegressor
import pickle

# load model
with open(r"C:\Users\swath\new_app\models\xgb_car_price_model.pkl", "rb") as f:
    xgb_model = pickle.load(f)

print(xgb_model.predict([[10000, 20, 5, 1, 0, 0]]))
