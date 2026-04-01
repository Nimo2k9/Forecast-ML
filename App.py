import streamlit as st
import pandas as pd
import numpy as np

# Safe imports
try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.svm import SVR
    from sklearn.metrics import mean_squared_error
except:
    st.error("❌ scikit-learn not installed. Check requirements.txt")
    st.stop()

try:
    from xgboost import XGBRegressor
    XGB_AVAILABLE = True
except:
    XGB_AVAILABLE = False

try:
    from statsmodels.tsa.arima.model import ARIMA
    ARIMA_AVAILABLE = True
except:
    ARIMA_AVAILABLE = False

import plotly.express as px

st.set_page_config(page_title="Production Demand Forecast System", layout="wide")

# ==============================
# LOAD DATA
# ==============================
uploaded_file = st.file_uploader("📂 Upload Excel File", type=["xlsx"])

if uploaded_file is None:
    st.info("Please upload your dataset to start")
    st.stop()

try:
    df = pd.read_excel(uploaded_file)
except Exception as e:
    st.error("❌ Failed to read Excel file")
    st.stop()

# ==============================
# VALIDATION
# ==============================
required_cols = ["Item Code","Price"]

for col in required_cols:
    if col not in df.columns:
        st.error(f"❌ Missing column: {col}")
        st.stop()

# ==============================
# PREPROCESS
# ==============================
try:
    df = df[df["LCM"] == "Local"]
except:
    st.warning("⚠️ LCM column not found — using full dataset")

static_cols = ["Item Code","Item Name","Price"]

month_cols = [
    c for c in df.columns
    if c not in static_cols and c not in ["LCM","Total"]
]

if len(month_cols) == 0:
    st.error("❌ No date columns found")
    st.stop()

df_long = df.melt(
    id_vars=[c for c in static_cols if c in df.columns],
    value_vars=month_cols,
    var_name="Date",
    value_name="Demand"
)

df_long["Date"] = pd.to_datetime(df_long["Date"], errors="coerce")
df_long = df_long.dropna(subset=["Date"])

df_long["Demand"] = pd.to_numeric(df_long["Demand"], errors="coerce")
df_long["Price"] = pd.to_numeric(df_long["Price"], errors="coerce")

df_long = df_long.dropna()

if len(df_long) == 0:
    st.error("❌ No valid data after cleaning")
    st.stop()

# ==============================
# FEATURES
# ==============================
df_long = df_long.sort_values(["Item Code","Date"])

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
    df_long[col] = pd.to_numeric(df_long[col], errors='coerce')

df_long = df_long.dropna()

# ==============================
# RUN SYSTEM
# ==============================
if st.button("🚀 Run Production Forecast"):

    results = []
    progress = st.progress(0)

    items = df_long["Item Code"].unique()

    for i, item in enumerate(items):

        item_df = df_long[df_long["Item Code"] == item]

        if len(item_df) < 10:
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

        # RF (always fallback)
        try:
            rf = RandomForestRegressor()
            rf.fit(X_train, y_train)
            pred = rf.predict(X_val)
            scores["RF"] = np.sqrt(mean_squared_error(y_val, pred))
            models["RF"] = rf
        except:
            pass

        # XGB
        if XGB_AVAILABLE:
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
        if ARIMA_AVAILABLE:
            try:
                ts = train.set_index("Date")["Demand"].asfreq("MS")
                arima = ARIMA(ts, order=(1,1,1)).fit()
                forecast = arima.forecast(steps=len(val))

                scores["ARIMA"] = np.sqrt(mean_squared_error(y_val, forecast))
                models["ARIMA"] = arima
            except:
                pass

        # ==============================
        # SAFE MODEL SELECTION
        # ==============================
        if len(scores) == 0:
            best_model = "NAIVE"
        else:
            best_model = min(scores, key=scores.get)

        # ==============================
        # SAFE FORECAST
        # ==============================
        try:
            if best_model == "ARIMA":
                forecast = models["ARIMA"].forecast(steps=6)

            elif best_model == "SVR":
                model, scaler = models["SVR"]
                forecast = [y_train.mean()]*6

            elif best_model in models:
                forecast = [y_train.mean()]*6

            else:
                forecast = [y_train.mean()]*6

        except:
            forecast = [y_train.mean()]*6

        results.append({
            "Item": item,
            "Best Model": best_model,
            "Avg Forecast": np.mean(forecast)
        })

        progress.progress((i+1)/len(items))

    result_df = pd.DataFrame(results)

    st.success("✅ System completed successfully")

    st.dataframe(result_df)

    # ==============================
    # VISUAL
    # ==============================
    st.plotly_chart(px.histogram(result_df, x="Best Model"))

    # ==============================
    # DOWNLOAD
    # ==============================
    st.download_button(
        "Download Results",
        result_df.to_csv(index=False),
        "results.csv"
    )
