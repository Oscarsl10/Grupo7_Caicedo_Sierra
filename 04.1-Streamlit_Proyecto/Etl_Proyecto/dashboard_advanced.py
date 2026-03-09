#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

# ===============================
# CONFIGURACIÓN STREAMLIT
# ===============================

st.set_page_config(
    page_title="Dashboard Avanzado - Videojuegos",
    page_icon="🎮",
    layout="wide",
)

st.title("🎮 Dashboard Avanzado - Análisis Histórico y ETL")
st.markdown("---")

# ===============================
# VARIABLES DE ENTORNO
# ===============================

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    st.error("❌ DATABASE_URL no está configurado")
    st.stop()

# ===============================
# CONEXIÓN A RAILWAY
# ===============================

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300
)

# ===============================
# CARGA DE DATOS (CACHE)
# ===============================

@st.cache_data(ttl=600)
def load_data():

    df = pd.read_sql_table("videojuegos_top", con=engine)

    df["fecha_lanzamiento"] = pd.to_datetime(
        df["fecha_lanzamiento"],
        errors="coerce"
    )

    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

    if "metacritic" not in df.columns:
        df["metacritic"] = pd.NA

    return df


@st.cache_data(ttl=600)
def load_etl_metrics():

    try:
        df_metrics = pd.read_sql_table("metricas_etl", con=engine)
        return df_metrics.sort_values("fecha_ejecucion", ascending=False)

    except Exception:
        return pd.DataFrame()


# ===============================
# CARGAR DATOS
# ===============================

try:

    df = load_data()
    df_metrics = load_etl_metrics()

except Exception as e:

    st.error("❌ Error al conectar con la base de datos")
    st.error(str(e))
    st.stop()

# ===============================
# TABS
# ===============================

tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Vista General", "📈 Histórico", "🔍 Análisis", "📋 Métricas ETL"]
)

# ===============================
# TAB 1
# ===============================

with tab1:

    st.subheader("Vista General")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("🎮 Total Juegos", len(df))

    with col2:
        st.metric("⭐ Rating Promedio", f"{df['rating'].mean():.2f}")

    with col3:

        if df["fecha_lanzamiento"].notna().any():
            latest = df["fecha_lanzamiento"].max()
            st.metric("⏰ Último Lanzamiento", latest.strftime("%Y-%m-%d"))
        else:
            st.metric("⏰ Último Lanzamiento", "N/A")

    with col4:
        st.metric("🎯 Con Metacritic", int(df["metacritic"].notna().sum()))

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:

        top10 = df.nlargest(10, "rating")[["nombre", "rating"]].sort_values("rating")

        fig = px.bar(
            top10,
            x="rating",
            y="nombre",
            orientation="h",
            color="rating",
            color_continuous_scale="Viridis",
            title="Top 10 Juegos por Rating"
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:

        pie_df = pd.DataFrame({
            "Cantidad": [
                int(df["metacritic"].notna().sum()),
                int(df["metacritic"].isna().sum())
            ],
            "Categoria": ["Con Metacritic", "Sin Metacritic"]
        })

        fig2 = px.pie(
            pie_df,
            values="Cantidad",
            names="Categoria",
            title="Distribución Metacritic"
        )

        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    st.dataframe(
        df.sort_values("rating", ascending=False).head(50),
        use_container_width=True
    )

# ===============================
# TAB 2
# ===============================

with tab2:

    st.subheader("Análisis Histórico")

    min_date = df["fecha_lanzamiento"].min().date()
    max_date = df["fecha_lanzamiento"].max().date()

    col1, col2 = st.columns(2)

    with col1:
        fecha_inicio = st.date_input("Desde:", value=min_date)

    with col2:
        fecha_fin = st.date_input("Hasta:", value=max_date)

    mask = (
        (df["fecha_lanzamiento"].dt.date >= fecha_inicio) &
        (df["fecha_lanzamiento"].dt.date <= fecha_fin)
    )

    df_hist = df.loc[mask].copy()

    if df_hist.empty:

        st.warning("No hay juegos en ese rango")

    else:

        df_hist["AñoMes"] = (
            df_hist["fecha_lanzamiento"]
            .dt.to_period("M")
            .dt.to_timestamp()
        )

        series_count = df_hist.groupby("AñoMes").size().reset_index(name="Cantidad")
        series_rating = df_hist.groupby("AñoMes")["rating"].mean().reset_index(name="RatingPromedio")

        fig1 = px.line(series_count, x="AñoMes", y="Cantidad", markers=True)
        fig2 = px.line(series_rating, x="AñoMes", y="RatingPromedio", markers=True)

        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig2, use_container_width=True)

        st.dataframe(df_hist, use_container_width=True)

# ===============================
# TAB 3
# ===============================

with tab3:

    st.subheader("Análisis Estadístico")

    stats = df.dropna(subset=["fecha_lanzamiento"]).copy()
    stats["Año"] = stats["fecha_lanzamiento"].dt.year

    summary = stats.groupby("Año").agg(
        Juegos=("nombre", "count"),
        RatingPromedio=("rating", "mean"),
        RatingMediana=("rating", "median"),
        RatingStd=("rating", "std")
    ).reset_index()

    st.dataframe(summary, use_container_width=True)

    st.markdown("---")

    año_sel = st.selectbox("Selecciona Año:", summary["Año"])

    año_df = stats[stats["Año"] == año_sel]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("⭐ Promedio", f"{año_df['rating'].mean():.2f}")

    with col2:
        st.metric("🎮 Juegos", len(año_df))

    with col3:
        st.metric("⬆ Máximo", f"{año_df['rating'].max():.2f}")

    with col4:
        st.metric("⬇ Mínimo", f"{año_df['rating'].min():.2f}")

# ===============================
# TAB 4
# ===============================

with tab4:

    st.subheader("Métricas ETL")

    if not df_metrics.empty:

        st.dataframe(df_metrics, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:

            fig = px.bar(
                df_metrics.head(10),
                x="fecha_ejecucion",
                y="registros_guardados",
                title="Registros Procesados"
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:

            fig2 = px.line(
                df_metrics.head(10),
                x="fecha_ejecucion",
                y="tiempo_ejecucion_segundos",
                title="Tiempo de Ejecución ETL"
            )

            st.plotly_chart(fig2, use_container_width=True)

    else:
        st.info("No hay métricas ETL registradas")

st.markdown("---")
st.write("Dashboard avanzado listo.")