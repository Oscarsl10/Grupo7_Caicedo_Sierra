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
        VideojuegoTop.metacritic,
        VideojuegoTop.ratings_count,
        VideojuegoTop.added,
        VideojuegoTop.playtime,
        VideojuegoTop.rating_top,
        VideojuegoTop.genres,
        VideojuegoTop.platforms,
        VideojuegoTop.esrb_rating,
        VideojuegoTop.developers,
        VideojuegoTop.publishers
    )

    df = pd.read_sql(query, engine)

    if not df.empty:
        df['fecha_lanzamiento'] = pd.to_datetime(df['fecha_lanzamiento'], errors='coerce')

        # Procesar datos JSON
        import json
        import ast

        def safe_json_loads(x):
            if pd.isna(x):
                return []
            try:
                if isinstance(x, str):
                    # Intentar parsear como JSON primero
                    return json.loads(x)
                else:
                    return x
            except (json.JSONDecodeError, TypeError):
                try:
                    # Intentar parsear como literal de Python
                    return ast.literal_eval(x)
                except (ValueError, SyntaxError):
                    return []

        df['genres_list'] = df['genres'].apply(safe_json_loads)
        df['platforms_list'] = df['platforms'].apply(safe_json_loads)
        df['developers_list'] = df['developers'].apply(safe_json_loads)
        df['publishers_list'] = df['publishers'].apply(safe_json_loads)

        # Extraer nombres para análisis
        df['genres_names'] = df['genres_list'].apply(lambda x: [item.get('name', item) if isinstance(item, dict) else str(item) for item in x] if isinstance(x, list) else [])
        df['platforms_names'] = df['platforms_list'].apply(lambda x: [item.get('name', item) if isinstance(item, dict) else str(item) for item in x] if isinstance(x, list) else [])
        df['developers_names'] = df['developers_list'].apply(lambda x: [item.get('name', item) if isinstance(item, dict) else str(item) for item in x] if isinstance(x, list) else [])
        df['publishers_names'] = df['publishers_list'].apply(lambda x: [item.get('name', item) if isinstance(item, dict) else str(item) for item in x] if isinstance(x, list) else [])

        # Crear strings legibles para display
        df['genres_str'] = df['genres_names'].apply(lambda x: ', '.join(x) if x else 'N/A')
        df['platforms_str'] = df['platforms_names'].apply(lambda x: ', '.join(x) if x else 'N/A')
        df['developers_str'] = df['developers_names'].apply(lambda x: ', '.join(x) if x else 'N/A')
        df['publishers_str'] = df['publishers_names'].apply(lambda x: ', '.join(x) if x else 'N/A')

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

    # Métricas adicionales
    st.markdown("### 📈 Métricas Adicionales")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_devs = df_filtrado['developers_names'].explode().nunique()
        st.metric("🏗️ Desarrolladores Únicos", total_devs)

    with col2:
        total_pubs = df_filtrado['publishers_names'].explode().nunique()
        st.metric("📦 Publishers Únicos", total_pubs)

    with col3:
        avg_genres = df_filtrado['genres_names'].apply(len).mean()
        st.metric("🎭 Géneros Promedio por Juego", f"{avg_genres:.1f}")

    with col4:
        avg_platforms = df_filtrado['platforms_names'].apply(len).mean()
        st.metric("🖥️ Plataformas Promedio por Juego", f"{avg_platforms:.1f}")

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
    # TERCERA FILA - DESARROLLADORES Y PUBLISHERS
    # =============================

    st.subheader("🏗️ Análisis de Desarrolladores y Publishers")

    col1, col2 = st.columns(2)

    with col1:
        # Top Desarrolladores
        dev_counts = df_filtrado['developers_names'].explode().value_counts().head(10)

        if not dev_counts.empty:
            fig = px.bar(
                dev_counts.reset_index(),
                x="count",
                y="developers_names",
                orientation="h",
                color="count",
                color_continuous_scale="Blues",
                title="Top 10 Desarrolladores"
            )
            fig.update_layout(yaxis_title="Desarrollador", xaxis_title="Cantidad de Juegos")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de desarrolladores")

    with col2:
        # Top Publishers
        pub_counts = df_filtrado['publishers_names'].explode().value_counts().head(10)

        if not pub_counts.empty:
            fig = px.bar(
                pub_counts.reset_index(),
                x="count",
                y="publishers_names",
                orientation="h",
                color="count",
                color_continuous_scale="Greens",
                title="Top 10 Publishers"
            )
            fig.update_layout(yaxis_title="Publisher", xaxis_title="Cantidad de Juegos")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de publishers")

    st.markdown("---")

    # =============================
    # CUARTA FILA - GÉNEROS Y PLATAFORMAS
    # =============================

    st.subheader("🎭 Análisis de Géneros y Plataformas")

    col1, col2 = st.columns(2)

    with col1:
        # Top Géneros
        genre_counts = df_filtrado['genres_names'].explode().value_counts().head(10)

        if not genre_counts.empty:
            fig = px.bar(
                genre_counts.reset_index(),
                x="count",
                y="genres_names",
                orientation="h",
                color="count",
                color_continuous_scale="Purples",
                title="Top 10 Géneros"
            )
            fig.update_layout(yaxis_title="Género", xaxis_title="Cantidad de Juegos")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de géneros")

    with col2:
        # Top Plataformas
        platform_counts = df_filtrado['platforms_names'].explode().value_counts().head(10)

        if not platform_counts.empty:
            fig = px.bar(
                platform_counts.reset_index(),
                x="count",
                y="platforms_names",
                orientation="h",
                color="count",
                color_continuous_scale="Oranges",
                title="Top 10 Plataformas"
            )
            fig.update_layout(yaxis_title="Plataforma", xaxis_title="Cantidad de Juegos")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de plataformas")

    st.markdown("---")

    # =============================
    # TABLA
    # =============================

    st.subheader("📋 Datos Detallados")

    df_tabla = df_filtrado[[
        'nombre', 'fecha_lanzamiento', 'rating', 'metacritic',
        'ratings_count', 'added', 'playtime', 'rating_top',
        'genres_str', 'platforms_str', 'developers_str', 'publishers_str', 'esrb_rating'
    ]].copy()

    df_tabla['fecha_lanzamiento'] = df_tabla['fecha_lanzamiento'].dt.strftime('%Y-%m-%d')

    df_tabla = df_tabla.sort_values('rating', ascending=False)

    # Renombrar columnas para mejor display
    df_tabla.columns = [
        'Nombre', 'Fecha Lanzamiento', 'Rating', 'Metacritic',
        'Cantidad Ratings', 'Agregados', 'Tiempo Juego (hrs)', 'Rating Top',
        'Géneros', 'Plataformas', 'Desarrolladores', 'Publishers', 'Clasificación ESRB'
    ]

    st.dataframe(
        df_tabla,
        use_container_width=True,
        height=400,
        hide_index=True
    )

except Exception as e:

    st.error("❌ Error al cargar el dashboard")
    st.error(str(e))