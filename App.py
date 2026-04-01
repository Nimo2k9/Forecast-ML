import streamlit as st
import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error

from xgboost import XGBRegressor
from statsmodels.tsa.arima.model import ARIMA

import plotly.express as px

st.set_page_config(page_title="Enterprise Demand Forecast System", layout="wide")

# ==============================
# LOAD DATA
# ==============================
@st.cache_data
def load_data(file):
    df = pd.read_excel(file)
    df = df[df["LCM"] == "Local"]
    return df

uploaded_file = st.file_uploader("Upload Dataset", type=["xlsx"])

if uploaded_file is None:
    st.stop()

df = load_data(uploaded_file)

# ==============================
# PREPROCESS
# ==============================
static_cols = ["Item Code","Item Name","Price"]

month_cols = [
    c for c in df.columns
    if c not in static_cols and c not in ["LCM","Total"]
]

df_long = df.melt(
    id_vars=static_cols,
    value_vars=month_cols,
    var_name="Date",
    value_name="Demand"
)

df_long["Date"] = pd.to_datetime(df_long["Date"], errors="coerce")
df_long = df_long.dropna(subset=["Date"])

df_long["Demand"] = pd.to_numeric(df_long["Demand"], errors="coerce")
df_long["Price"] = pd.to_numeric(df_long["Price"], errors="coerce")

df_long = df_long.dropna()
df_long = df_long.sort_values(["Item Code","Date"])

# ==============================
# FEATURES
# ==============================
df_long["Lag1"] = df_long.groupby("Item Code")["Demand"].shift(1)
df_long["Lag2"] = df_long.groupby("Item Code")["Demand"].shift(2)
df_long["Lag3"] = df_long.groupby("Item Code")["Demand"].shift(3)

df_long["RollingMean3"] = (
    df_long.groupby("Item Code")["Demand"]
    .shift(1)
    .rolling(3)
    .mean()
)

features = ["Lag1","Lag2","Lag3","RollingMean3","Price"]

for col in features:
    df_long[col] = pd.to_numeric(df_long[col], errors="coerce")

df_long = df_long.dropna()

# ==============================
# RUN FULL SYSTEM
# ==============================
if st.button("🚀 Run Enterprise Forecast System"):

    results = []

    for item in df_long["Item Code"].unique():

        item_df = df_long[df_long["Item Code"] == item]

        if len(item_df) < 12:
            continue

        split = int(len(item_df)*0.8)
        train = item_df.iloc[:split]
        val = item_df.iloc[split:]

        X_train = train[features].astype(float)
        y_train = train["Demand"]

        X_val = val[features].astype(float)
        y_val = val["Demand"]

        models = {}
        scores = {}

        # RF
        try:
            rf = RandomForestRegressor()
            rf.fit(X_train, y_train)
            pred = rf.predict(X_val)
            scores["RF"] = np.sqrt(mean_squared_error(y_val, pred))
            models["RF"] = rf
        except:
            pass

        # XGB
        try:
            xgb = XGBRegressor()
            xgb.fit(X_train, y_train)
            pred = xgb.predict(X_val)
            scores["XGB"] = np.sqrt(mean_squared_error(y_val, pred))
            models["XGB"] = xgb
        except:
            pass

        # SVR
        try:
            scaler = StandardScaler()
            X_train_s = scaler.fit_transform(X_train)
            X_val_s = scaler.transform(X_val)

            svr = SVR()
            svr.fit(X_train_s, y_train)
            pred = svr.predict(X_val_s)

            scores["SVR"] = np.sqrt(mean_squared_error(y_val, pred))
            models["SVR"] = (svr, scaler)
        except:
            pass

        # ARIMA
        try:
            ts = train.set_index("Date")["Demand"].asfreq("MS")
            arima = ARIMA(ts, order=(1,1,1)).fit()
            forecast = arima.forecast(steps=len(val))

            scores["ARIMA"] = np.sqrt(mean_squared_error(y_val, forecast))
            models["ARIMA"] = arima
        except:
            pass

        if len(scores) == 0:
            continue

        best_model = min(scores, key=scores.get)

        # ==============================
        # FORECAST
        # ==============================
        forecast = models[best_model].forecast(steps=6) if best_model=="ARIMA" else [0]*6

        if best_model != "ARIMA":
            temp_df = item_df.copy()

            forecast = []
            for i in range(6):

                last = temp_df.iloc[-1]

                X_new = np.array([[
                    last["Demand"],
                    temp_df.iloc[-2]["Demand"],
                    temp_df.iloc[-3]["Demand"],
                    temp_df["Demand"].iloc[-3:].mean(),
                    last["Price"]
                ]])

                if best_model == "SVR":
                    model, scaler = models["SVR"]
                    X_new = scaler.transform(X_new)
                    pred = model.predict(X_new)[0]
                else:
                    pred = models[best_model].predict(X_new)[0]

                forecast.append(pred)

                new_row = last.copy()
                new_row["Demand"] = pred
                temp_df = pd.concat([temp_df, pd.DataFrame([new_row])])

        # ==============================
        # INVENTORY KPIs
        # ==============================
        rmse = scores[best_model]
        LT = 1.2
        Z = 1.65

        safety = Z * rmse * np.sqrt(LT)
        avg_fc = np.mean(forecast)
        rop_ml = avg_fc * LT + safety

        mean = item_df["Demand"].mean()
        std = item_df["Demand"].std()

        rop_trad = mean * LT + Z * std * np.sqrt(LT)

        results.append({
            "Item": item,
            "Best Model": best_model,
            "RMSE": rmse,
            "Forecast Avg": avg_fc,
            "ML ROP": rop_ml,
            "Traditional ROP": rop_trad
        })

    result_df = pd.DataFrame(results)

    # ==============================
    # ABC CLASSIFICATION
    # ==============================
    result_df = result_df.sort_values("Forecast Avg", ascending=False)
    result_df["Cum %"] = result_df["Forecast Avg"].cumsum() / result_df["Forecast Avg"].sum()

    def abc(x):
        if x <= 0.8:
            return "A"
        elif x <= 0.95:
            return "B"
        else:
            return "C"

    result_df["ABC"] = result_df["Cum %"].apply(abc)

    # ==============================
    # DASHBOARD KPIs
    # ==============================
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Forecast", round(result_df["Forecast Avg"].sum(),2))
    col2.metric("Avg ML ROP", round(result_df["ML ROP"].mean(),2))
    col3.metric("Avg RMSE", round(result_df["RMSE"].mean(),2))

    # ==============================
    # VISUALS
    # ==============================
    st.subheader("ABC Distribution")
    st.plotly_chart(px.histogram(result_df, x="ABC"))

    st.subheader("Top 10 Critical Items")
    st.dataframe(result_df.head(10))

    st.subheader("Full Results")
    st.dataframe(result_df)

    # ==============================
    # DOWNLOAD
    # ==============================
    st.download_button(
        "Download Results",
        result_df.to_csv(index=False),
        "enterprise_forecast.csv"
    )
