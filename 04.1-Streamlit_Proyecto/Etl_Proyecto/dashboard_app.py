#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import select
from datetime import datetime

from scripts.database import engine
from scripts.models import VideojuegoTop

# =============================
# CONFIGURACIÓN STREAMLIT
# =============================

st.set_page_config(
    page_title="Dashboard de Videojuegos ETL",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎮 Dashboard de Videojuegos - ETL RAWG")
st.markdown("---")


# =============================
# FUNCIÓN PARA CARGAR DATOS
# =============================

@st.cache_data(ttl=600)  # cache 10 minutos
def cargar_datos():

    query = select(
        VideojuegoTop.nombre,
        VideojuegoTop.fecha_lanzamiento,
        VideojuegoTop.rating,
        VideojuegoTop.metacritic
    )

    df = pd.read_sql(query, engine)

    if not df.empty:
        df['fecha_lanzamiento'] = pd.to_datetime(df['fecha_lanzamiento'], errors='coerce')

    return df


# =============================
# CARGAR DATOS DESDE RAILWAY
# =============================

try:

    df = cargar_datos()

    if df.empty:
        st.warning("⚠️ La tabla videojuegos_top está vacía. Ejecuta primero el ETL.")
        st.stop()

    # =============================
    # SIDEBAR - FILTROS
    # =============================

    st.sidebar.title("🔧 Filtros")

    min_rating, max_rating = st.sidebar.slider(
        "Rango de Rating:",
        min_value=float(df['rating'].min()),
        max_value=float(df['rating'].max()),
        value=(float(df['rating'].min()), float(df['rating'].max())),
        step=0.1
    )

    min_año = int(df['fecha_lanzamiento'].dt.year.min())
    max_año = int(df['fecha_lanzamiento'].dt.year.max())

    año_filtro = st.sidebar.slider(
        "Año de Lanzamiento:",
        min_value=min_año,
        max_value=max_año,
        value=(min_año, max_año)
    )

    solo_metacritic = st.sidebar.checkbox("Solo juegos con Metacritic", value=False)

    # =============================
    # APLICAR FILTROS
    # =============================

    df_filtrado = df[
        (df['rating'] >= min_rating) &
        (df['rating'] <= max_rating) &
        (df['fecha_lanzamiento'].dt.year >= año_filtro[0]) &
        (df['fecha_lanzamiento'].dt.year <= año_filtro[1])
    ]

    if solo_metacritic:
        df_filtrado = df_filtrado[df_filtrado['metacritic'].notna()]

    # =============================
    # MÉTRICAS
    # =============================

    st.markdown("### 📊 Métricas Principales")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "⭐ Rating Promedio",
            f"{df_filtrado['rating'].mean():.2f}"
        )

    with col2:

        meta_avg = df_filtrado['metacritic'].mean()

        if pd.notna(meta_avg):
            st.metric("🎯 Metacritic Promedio", f"{meta_avg:.1f}")
        else:
            st.metric("🎯 Metacritic Promedio", "N/A")

    with col3:
        st.metric("🎮 Total Juegos", len(df_filtrado))

    with col4:
        st.metric("📅 Años Representados", df_filtrado['fecha_lanzamiento'].dt.year.nunique())

    st.markdown("---")

    # =============================
    # VISUALIZACIONES
    # =============================

    st.subheader("📈 Visualizaciones")

    col1, col2 = st.columns(2)

    # TOP 10 RATING
    with col1:

        top_10 = df_filtrado.nlargest(10, 'rating')[['nombre', 'rating']].sort_values('rating')

        fig = px.bar(
            top_10,
            y="nombre",
            x="rating",
            orientation="h",
            color="rating",
            color_continuous_scale="viridis",
            title="Top 10 Juegos por Rating"
        )

        st.plotly_chart(fig, use_container_width=True)

    # SCATTER
    with col2:

        df_meta = df_filtrado[df_filtrado['metacritic'].notna()]

        if not df_meta.empty:

            fig = px.scatter(
                df_meta,
                x="rating",
                y="metacritic",
                hover_data=["nombre"],
                color="rating",
                color_continuous_scale="RdYlGn",
                title="Rating RAWG vs Metacritic"
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("No hay datos de Metacritic")

    st.markdown("---")

    # =============================
    # SEGUNDA FILA
    # =============================

    col1, col2 = st.columns(2)

    with col1:

        fig = px.histogram(
            df_filtrado,
            x="rating",
            nbins=20,
            title="Distribución de Ratings"
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:

        juegos_por_año = (
            df_filtrado
            .groupby(df_filtrado['fecha_lanzamiento'].dt.year)
            .size()
            .reset_index(name="Cantidad")
        )

        juegos_por_año.columns = ["Año", "Cantidad"]

        fig = px.line(
            juegos_por_año,
            x="Año",
            y="Cantidad",
            markers=True,
            title="Juegos por Año"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # =============================
    # TABLA
    # =============================

    st.subheader("📋 Datos Detallados")

    df_tabla = df_filtrado[['nombre', 'fecha_lanzamiento', 'rating', 'metacritic']].copy()

    df_tabla['fecha_lanzamiento'] = df_tabla['fecha_lanzamiento'].dt.strftime('%Y-%m-%d')

    df_tabla = df_tabla.sort_values('rating', ascending=False)

    st.dataframe(
        df_tabla,
        use_container_width=True,
        height=400,
        hide_index=True
    )

except Exception as e:

    st.error("❌ Error al cargar el dashboard")
    st.error(str(e))