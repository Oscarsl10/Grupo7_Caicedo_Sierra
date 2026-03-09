#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# ===============================
# CARGAR VARIABLES DE ENTORNO
# ===============================

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ===============================
# CONFIGURACIÓN STREAMLIT
# ===============================

st.set_page_config(
    page_title="Dashboard Interactivo - Videojuegos",
    page_icon="🎛️",
    layout="wide",
)

st.title("🎛️ Dashboard Interactivo - Control Total de Videojuegos")

# ===============================
# CONEXIÓN A LA BASE DE DATOS
# ===============================

@st.cache_data
def load_from_db():
    try:
        engine = create_engine(DATABASE_URL)
        df = pd.read_sql_table("videojuegos_top", con=engine)
        return df
    except Exception as e:
        raise ConnectionError(f"No se pudo obtener datos de la base de datos: {e}")

# ===============================
# CARGAR DATOS
# ===============================

try:
    df = load_from_db()
except Exception as err:
    st.error("❌ Error al leer la base de datos")
    st.error(str(err))
    st.stop()

# ===============================
# NORMALIZAR TIPOS
# ===============================

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

# ===============================
# SIDEBAR CONTROLS
# ===============================

st.sidebar.markdown("### 🔧 Controles")

# búsqueda por nombre
nombre_busqueda = st.sidebar.text_input("🔍 Buscar por nombre", value="")

# rango fechas
col1, col2 = st.sidebar.columns(2)

with col1:
    desde = st.sidebar.date_input(
        "📅 Desde:",
        value=df["fecha_lanzamiento"].min().date()
        if df["fecha_lanzamiento"].notna().any()
        else datetime.now().date()
    )

with col2:
    hasta = st.sidebar.date_input(
        "📅 Hasta:",
        value=df["fecha_lanzamiento"].max().date()
        if df["fecha_lanzamiento"].notna().any()
        else datetime.now().date()
    )

# rango rating
min_r, max_r = st.sidebar.slider(
    "⭐ Rating",
    float(df["rating"].min()),
    float(df["rating"].max()),
    (float(df["rating"].min()), float(df["rating"].max())),
    step=0.01
)

# rango metacritic
if df["metacritic"].notna().any():
    min_m, max_m = st.sidebar.slider(
        "🎯 Metacritic",
        float(df["metacritic"].min()),
        float(df["metacritic"].max()),
        (float(df["metacritic"].min()), float(df["metacritic"].max())),
        step=1.0
    )
else:
    min_m, max_m = (None, None)

# ===============================
# APLICAR FILTROS
# ===============================

df_filt = df.copy()

if nombre_busqueda:
    df_filt = df_filt[df_filt["nombre"].str.contains(nombre_busqueda, case=False, na=False)]

if df_filt["fecha_lanzamiento"].notna().any():
    df_filt = df_filt[
        (df_filt["fecha_lanzamiento"].dt.date >= desde) &
        (df_filt["fecha_lanzamiento"].dt.date <= hasta)
    ]

if pd.notna(min_r) and pd.notna(max_r):
    df_filt = df_filt[(df_filt["rating"] >= min_r) & (df_filt["rating"] <= max_r)]

if min_m is not None:
    df_filt = df_filt[(df_filt["metacritic"] >= min_m) & (df_filt["metacritic"] <= max_m)]

# ===============================
# RESULTADOS
# ===============================

if df_filt.empty:
    st.warning("⚠️ No hay datos que coincidan con los filtros seleccionados")

else:

    # KPIs
    st.markdown("### 📊 Indicadores Clave")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("⭐ Rating Máx", f"{df_filt['rating'].max():.2f}")

    with col2:
        st.metric("⭐ Rating Mín", f"{df_filt['rating'].min():.2f}")

    with col3:
        st.metric("⭐ Rating Prom", f"{df_filt['rating'].mean():.2f}")

    with col4:
        if df_filt["metacritic"].notna().any():
            st.metric("🎯 Metacritic Prom", f"{df_filt['metacritic'].mean():.1f}")
        else:
            st.metric("🎯 Metacritic Prom", "N/A")

    with col5:
        st.metric("🎮 Total Juegos", len(df_filt))

    st.markdown("---")

    # ===============================
    # VISUALIZACIONES
    # ===============================

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Distribución de Ratings")

        fig = px.box(df_filt, x="rating", title="Boxplot de Ratings")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Metacritic vs Rating")

        if df_filt["metacritic"].notna().any():

            fig = px.scatter(
                df_filt,
                x="rating",
                y="metacritic",
                hover_data=["nombre"]
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("No hay valores de Metacritic para graficar")

    st.markdown("---")

    # ===============================
    # EVOLUCIÓN TEMPORAL
    # ===============================

    if df_filt["fecha_lanzamiento"].notna().any():

        st.markdown("#### 📈 Evolución Temporal")

        df_filt["Año"] = df_filt["fecha_lanzamiento"].dt.year

        temp_tiempo = df_filt.groupby("Año")["rating"].mean().reset_index()

        fig = px.line(
            temp_tiempo,
            x="Año",
            y="rating",
            markers=True,
            title="Rating Promedio por Año"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ===============================
    # TABLA
    # ===============================

    st.markdown("#### 📋 Datos Detallados")

    mostrar_todos = st.checkbox("Mostrar todos los registros", value=False)

    columnas_mostrar = st.multiselect(
        "Columnas a mostrar:",
        df_filt.columns.tolist(),
        default=["nombre", "fecha_lanzamiento", "rating", "metacritic"]
    )

    if mostrar_todos:
        st.dataframe(df_filt[columnas_mostrar], use_container_width=True, height=600)
    else:
        st.dataframe(df_filt[columnas_mostrar].head(20), use_container_width=True)

    # ===============================
    # DESCARGA CSV
    # ===============================

    st.markdown("---")

    csv = df_filt.to_csv(index=False)

    st.download_button(
        label="⬇️ Descargar datos como CSV",
        data=csv,
        file_name=f"videojuegos_filtrados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )