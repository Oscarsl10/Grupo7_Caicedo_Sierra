#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine

st.set_page_config(
    page_title="Dashboard Avanzado - Videojuegos",
    page_icon="🎮",
    layout="wide",
)

st.title("🎮 Dashboard Avanzado - Análisis Histórico y ETL")
st.markdown("---")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

transformed_path = os.path.join(DATA_DIR, "videojuegos_transformed.csv")
clean_path = os.path.join(DATA_DIR, "videojuegos_clean.csv")

# Cargar variables de entorno para la DB (opcional)
load_dotenv()
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "1234")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "tienda")
DATABASE_URL = os.getenv("DATABASE_URL", f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")


def load_data():
    # Leer exclusivamente desde la base de datos. Si falla, lanzar excepción con la razón.
    try:
        engine = create_engine(DATABASE_URL)
        df = pd.read_sql_table('videojuegos', con=engine)
    except Exception as e:
        raise ConnectionError(f"No se pudo conectar a la base de datos o leer la tabla 'videojuegos': {e}")

    # Normalizaciones
    if "fecha_lanzamiento" in df.columns:
        df["fecha_lanzamiento"] = pd.to_datetime(df["fecha_lanzamiento"], errors="coerce")
    else:
        df["fecha_lanzamiento"] = pd.NaT

    if "rating" in df.columns:
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    else:
        df["rating"] = pd.NA

    if "metacritic" not in df.columns:
        df["metacritic"] = pd.NA

    return df


try:
    df = load_data()
except Exception as e:
    st.error("❌ No se pudieron recibir datos desde la base de datos.")
    st.error(str(e))
    st.stop()


# Pestañas
tab1, tab2, tab3, tab4 = st.tabs(["📊 Vista General", "📈 Histórico", "🔍 Análisis", "📋 Métricas ETL"])

with tab1:
    st.subheader("Vista General")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total = len(df)
        st.metric("🎮 Total Juegos", total)

    with col2:
        avg_rating = df["rating"].mean()
        st.metric("⭐ Rating Promedio", f"{avg_rating:.2f}" if pd.notna(avg_rating) else "N/A")

    with col3:
        if df["fecha_lanzamiento"].notna().any():
            latest = df["fecha_lanzamiento"].max()
            st.metric("⏰ Última Fecha de Lanzamiento", latest.strftime("%Y-%m-%d"))
        else:
            st.metric("⏰ Última Fecha de Lanzamiento", "N/A")

    with col4:
        count_meta = df["metacritic"].notna().sum()
        st.metric("🎯 Con Metacritic", f"{int(count_meta)}")

    st.markdown("---")

    # Visualizaciones principales
    col1, col2 = st.columns(2)

    with col1:
        top10 = df.nlargest(10, "rating")[["nombre", "rating"]].sort_values("rating")
        fig = px.bar(top10, x="rating", y="nombre", orientation='h', color="rating", color_continuous_scale='Viridis', title="Top 10 Juegos por Rating")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        pie_df = pd.DataFrame({
            "Has Metacritic": [int(df["metacritic"].notna().sum()), int(df["metacritic"].isna().sum())],
            "Categoria": ["Con Metacritic", "Sin Metacritic"]
        })
        fig2 = px.pie(pie_df, values="Has Metacritic", names="Categoria", title="Distribución Metacritic")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.dataframe(df.sort_values("rating", ascending=False).head(50), use_container_width=True)

with tab2:
    st.subheader("Análisis Histórico")
    if df["fecha_lanzamiento"].notna().any():
        min_date = df["fecha_lanzamiento"].min().date()
        max_date = df["fecha_lanzamiento"].max().date()
    else:
        min_date = datetime.now().date() - timedelta(days=365)
        max_date = datetime.now().date()

    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Desde:", value=min_date, min_value=min_date, max_value=max_date)
    with col2:
        fecha_fin = st.date_input("Hasta:", value=max_date, min_value=min_date, max_value=max_date)

    if fecha_inicio > fecha_fin:
        st.error("La fecha 'Desde' no puede ser posterior a 'Hasta'")
    else:
        mask = (df["fecha_lanzamiento"].dt.date >= fecha_inicio) & (df["fecha_lanzamiento"].dt.date <= fecha_fin)
        df_hist = df.loc[mask].copy()

        if df_hist.empty:
            st.warning("No hay juegos en ese rango de fechas")
        else:
            # Agrupar por mes
            df_hist["AñoMes"] = df_hist["fecha_lanzamiento"].dt.to_period("M").dt.to_timestamp()
            series_count = df_hist.groupby("AñoMes").size().reset_index(name="Cantidad")
            series_rating = df_hist.groupby("AñoMes")["rating"].mean().reset_index(name="RatingPromedio")

            fig_count = px.line(series_count, x="AñoMes", y="Cantidad", title="Cantidad de Lanzamientos por Mes", markers=True)
            fig_rating = px.line(series_rating, x="AñoMes", y="RatingPromedio", title="Rating Promedio por Mes", markers=True)

            st.plotly_chart(fig_count, use_container_width=True)
            st.plotly_chart(fig_rating, use_container_width=True)
            st.markdown("---")
            st.dataframe(df_hist.sort_values("fecha_lanzamiento", ascending=False).reset_index(drop=True), use_container_width=True)

with tab3:
    st.subheader("Análisis Estadístico")
    st.write("Estadísticas por Año")
    if df["fecha_lanzamiento"].notna().any():
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
        año_sel = st.selectbox("Selecciona Año:", options=summary["Año"].tolist())
        año_df = stats[stats["Año"] == año_sel]
        st.write(f"Estadísticas para {año_sel}")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🌡️ Rating Prom.", f"{año_df['rating'].mean():.2f}")
        with col2:
            st.metric("🔢 Juegos", len(año_df))
        with col3:
            st.metric("🔼 Rating Máx.", f"{año_df['rating'].max():.2f}")
        with col4:
            st.metric("🔽 Rating Mín.", f"{año_df['rating'].min():.2f}")
    else:
        st.info("No hay fechas de lanzamiento para generar estadísticas")

with tab4:
    st.subheader("Métricas ETL y Logs")
    rows = []
    for path in [clean_path, transformed_path]:
        if os.path.exists(path):
            stat = os.stat(path)
            rows.append({
                "Archivo": os.path.basename(path),
                "Filas": sum(1 for _ in open(path)) - 1,
                "Tamaño (bytes)": stat.st_size,
                "Modificado": datetime.fromtimestamp(stat.st_mtime)
            })

    df_etl = pd.DataFrame(rows)
    if not df_etl.empty:
        st.dataframe(df_etl, use_container_width=True)
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(df_etl, x="Archivo", y="Filas", title="Filas por Archivo")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig2 = px.bar(df_etl, x="Archivo", y="Tamaño (bytes)", title="Tamaño de Archivos")
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No hay archivos CSV para mostrar métricas ETL")

    # Mostrar últimas líneas del log si existe
    log_path = os.path.join(LOGS_DIR, "etl.log")
    if os.path.exists(log_path):
        st.markdown("---")
        st.subheader("Últimas entradas del log ETL")
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()[-50:]
        st.text("".join(lines))

st.markdown("---")
st.write("Dashboard avanzado listo. Usa los filtros y pestañas para explorar.")
