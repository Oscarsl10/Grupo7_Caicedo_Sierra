#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# cargar entorno
load_dotenv()

# configuración página
st.set_page_config(
    page_title="Dashboard Interactivo - Videojuegos",
    page_icon="🎛️",
    layout="wide",
)

st.title("🎛️ Dashboard Interactivo - Control Total de Videojuegos")

def _normalize_database_url(raw_url: str) -> str:
    if raw_url is None:
        return None
    url = raw_url
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    # Añadir sslmode=require para conexiones remotas si no está presente
    if "localhost" not in url and "127.0.0.1" not in url and "sslmode" not in url:
        if "?" in url:
            url = url + "&sslmode=require"
        else:
            url = url + "?sslmode=require"
    return url


def _get_database_url():
    # Priorizar st.secrets (Streamlit Cloud), luego env vars, luego construcción por partes
    db_url = None
    try:
        db_url = st.secrets.get("DATABASE_URL")
    except Exception:
        # st.secrets puede no existir fuera de Streamlit
        db_url = None

    if not db_url:
        db_url = os.getenv("DATABASE_URL")

    if db_url:
        return _normalize_database_url(db_url)

    # Fallback: construir desde variables individuales (útil en local)
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "1234")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "tienda")
    return _normalize_database_url(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")


@st.cache_data
def load_from_db():
    DATABASE_URL = _get_database_url()
    if not DATABASE_URL:
        raise ConnectionError("DATABASE_URL no está configurada. Define DATABASE_URL en st.secrets o en las variables de entorno.")

    try:
        engine = create_engine(DATABASE_URL)
        df = pd.read_sql_table('videojuegos', con=engine)
        return df
    except SQLAlchemyError as e:
        raise ConnectionError(f"No se pudo obtener datos de la base de datos: {e}")

# intentar cargar datos

df = None
try:
    df = load_from_db()
except Exception as err:
    st.warning("⚠️ No se pudo leer la base de datos")
    st.warning(str(err))

# si df es None o está vacío, intentamos cargar CSV de respaldo
if df is None or (hasattr(df, 'shape') and df.shape[0] == 0):
    csv_path = os.path.join(os.path.dirname(__file__), "data", "videojuegos_transformed.csv")
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        st.info("ℹ️ Usando CSV transformado como fallback")

if df is None:
    st.error("❌ No se pudieron obtener datos de ninguna fuente")
    st.stop()

# depuración para nube
with st.expander("Debug datos cargados"):
    st.write("shape:", df.shape)
    st.write(df.head())
    st.write(df.dtypes)

# normalizar encabezados y tipos
if 'fecha_lanzamiento' in df.columns:
    df['fecha_lanzamiento'] = pd.to_datetime(df['fecha_lanzamiento'], errors='coerce')
else:
    df['fecha_lanzamiento'] = pd.NaT

if 'rating' in df.columns:
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
else:
    df['rating'] = pd.NA

if 'metacritic' not in df.columns:
    df['metacritic'] = pd.NA

# Sidebar controls
st.sidebar.markdown("### 🔧 Controles")

# búsqueda por nombre
nombre_busqueda = st.sidebar.text_input("🔍 Buscar por nombre", value="")

# rango fechas
col1, col2 = st.sidebar.columns(2)
with col1:
    desde = st.sidebar.date_input("📅 Desde:", value=df['fecha_lanzamiento'].min().date() if df['fecha_lanzamiento'].notna().any() else datetime.now().date())
with col2:
    hasta = st.sidebar.date_input("📅 Hasta:", value=df['fecha_lanzamiento'].max().date() if df['fecha_lanzamiento'].notna().any() else datetime.now().date())

# rango rating - manejar NaN correctamente
rating_valid = df['rating'].dropna()
if len(rating_valid) > 0:
    min_r, max_r = st.sidebar.slider("⭐ Rating", 
                                     float(rating_valid.min()), float(rating_valid.max()),
                                     (float(rating_valid.min()), float(rating_valid.max())), step=0.01)
else:
    st.sidebar.warning("No hay datos de Rating disponibles")
    min_r, max_r = (0.0, 5.0)

# rango metacritic - manejar NaN correctamente
metacritic_valid = df['metacritic'].dropna()
if len(metacritic_valid) > 0:
    min_m, max_m = st.sidebar.slider("🎯 Metacritic", 
                                     float(metacritic_valid.min()), float(metacritic_valid.max()),
                                     (float(metacritic_valid.min()), float(metacritic_valid.max())), step=1.0)
else:
    st.sidebar.info("No hay datos de Metacritic disponibles")
    min_m, max_m = (None, None)

# aplicar filtros
df_filt = df.copy()
if nombre_busqueda:
    df_filt = df_filt[df_filt['nombre'].str.contains(nombre_busqueda, case=False, na=False)]
if df_filt['fecha_lanzamiento'].notna().any():
    df_filt = df_filt[(df_filt['fecha_lanzamiento'].dt.date >= desde) & (df_filt['fecha_lanzamiento'].dt.date <= hasta)]

if pd.notna(min_r) and pd.notna(max_r):
    df_filt = df_filt[(df_filt['rating'] >= min_r) & (df_filt['rating'] <= max_r)]

if min_m is not None:
    df_filt = df_filt[(df_filt['metacritic'] >= min_m) & (df_filt['metacritic'] <= max_m)]

# resultados
if df_filt.empty:
    st.warning("⚠️ No hay datos que coincidan con los filtros seleccionados")
else:
    # KPIs
    st.markdown("### 📊 Indicadores Clave")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Proteger contra NaN en rating
    rating_valid = df_filt['rating'].dropna()
    with col1:
        if len(rating_valid) > 0:
            st.metric("⭐ Rating Máx", f"{rating_valid.max():.2f}")
        else:
            st.metric("⭐ Rating Máx", "N/A")
    with col2:
        if len(rating_valid) > 0:
            st.metric("⭐ Rating Mín", f"{rating_valid.min():.2f}")
        else:
            st.metric("⭐ Rating Mín", "N/A")
    with col3:
        if len(rating_valid) > 0:
            st.metric("⭐ Rating Prom", f"{rating_valid.mean():.2f}")
        else:
            st.metric("⭐ Rating Prom", "N/A")
    
    # Proteger contra NaN en metacritic
    metacritic_valid = df_filt['metacritic'].dropna()
    with col4:
        if len(metacritic_valid) > 0:
            st.metric("🎯 Metacritic Prom", f"{metacritic_valid.mean():.1f}")
        else:
            st.metric("🎯 Metacritic Prom", "N/A")
    with col5:
        st.metric("🎮 Total Juegos", len(df_filt))

    st.markdown("---")
    # visualizaciones
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Distribución de Ratings")
        fig = px.box(df_filt, x='rating', title='Boxplot de Ratings')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown("#### Metacritic vs Rating")
        if df_filt['metacritic'].notna().any():
            fig = px.scatter(df_filt, x='rating', y='metacritic', hover_data=['nombre'])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay valores de Metacritic para graficar")

    st.markdown("---")
    # evol temporal
    if df_filt['fecha_lanzamiento'].notna().any():
        st.markdown("#### 📈 Evolución Temporal")
        df_filt['Año'] = df_filt['fecha_lanzamiento'].dt.year
        temp_tiempo = df_filt.groupby('Año')['rating'].mean().reset_index()
        fig = px.line(temp_tiempo, x='Año', y='rating', markers=True, title='Rating Promedio por Año')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    # tabla
    st.markdown("#### 📋 Datos Detallados")
    mostrar_todos = st.checkbox("Mostrar todos los registros", value=False)
    columnas_mostrar = st.multiselect(
        "Columnas a mostrar:",
        df_filt.columns.tolist(),
        default=['nombre','fecha_lanzamiento','rating','metacritic']
    )
    if mostrar_todos:
        st.dataframe(df_filt[columnas_mostrar], use_container_width=True, height=600)
    else:
        st.dataframe(df_filt[columnas_mostrar].head(20), use_container_width=True)

    # descarga
    st.markdown("---")
    csv = df_filt.to_csv(index=False)
    st.download_button(
        label="⬇️ Descargar datos como CSV",
        data=csv,
        file_name=f"videojuegos_filtrados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
