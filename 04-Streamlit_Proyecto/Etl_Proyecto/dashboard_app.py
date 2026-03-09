#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import select
from datetime import datetime

from scripts.database import engine
from scripts.models import VideojuegoTop

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Videojuegos ETL",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🎮 Dashboard de Videojuegos - ETL RAWG")
st.markdown("---")

try:

    # =============================
    # CARGAR DATOS DESDE LA BASE
    # =============================

    query = select(
        VideojuegoTop.nombre,
        VideojuegoTop.fecha_lanzamiento,
        VideojuegoTop.rating,
        VideojuegoTop.metacritic
    )

    df = pd.read_sql(query, engine)

    if df.empty:
        st.warning("La tabla videojuegos_top está vacía. Ejecuta primero el ETL.")
        st.stop()

    df['fecha_lanzamiento'] = pd.to_datetime(df['fecha_lanzamiento'], errors='coerce')

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
    # MÉTRICAS PRINCIPALES
    # =============================

    st.markdown("### 📊 Métricas Principales")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        rating_promedio = df_filtrado['rating'].mean()
        st.metric(
            label="⭐ Rating Promedio",
            value=f"{rating_promedio:.2f}",
            delta=f"de {df_filtrado['rating'].max():.2f} máx."
        )

    with col2:
        metacritic_promedio = df_filtrado['metacritic'].mean()

        if not pd.isna(metacritic_promedio):
            st.metric(
                label="🎯 Metacritic Promedio",
                value=f"{metacritic_promedio:.1f}",
                delta=f"de {df_filtrado['metacritic'].max():.0f} máx."
            )
        else:
            st.metric(label="🎯 Metacritic Promedio", value="N/A")

    with col3:
        total_juegos = len(df_filtrado)

        st.metric(
            label="🎮 Total de Juegos",
            value=total_juegos,
            delta=f"de {len(df)} en total"
        )

    with col4:
        años_representados = df_filtrado['fecha_lanzamiento'].dt.year.nunique()

        st.metric(
            label="📅 Años Representados",
            value=años_representados
        )

    st.markdown("---")

    # =============================
    # VISUALIZACIONES
    # =============================

    st.subheader("📈 Visualizaciones")

    col1, col2 = st.columns(2)

    # Top 10 Rating
    with col1:

        top_10_rating = df_filtrado.nlargest(10, 'rating')[['nombre', 'rating']].sort_values('rating')

        fig_rating = px.bar(
            top_10_rating,
            y='nombre',
            x='rating',
            orientation='h',
            title="Top 10 Juegos por Rating",
            color='rating',
            color_continuous_scale='Viridis'
        )

        fig_rating.update_layout(
            xaxis_title="Rating",
            yaxis_title="Juego",
            height=400
        )

        st.plotly_chart(fig_rating, use_container_width=True)

    # Scatter rating vs metacritic
    with col2:

        df_con_metacritic = df_filtrado[df_filtrado['metacritic'].notna()]

        if len(df_con_metacritic) > 0:

            fig_scatter = px.scatter(
                df_con_metacritic,
                x='rating',
                y='metacritic',
                hover_data=['nombre'],
                title="Rating RAWG vs Metacritic",
                color='rating',
                color_continuous_scale='RdYlGn'
            )

            fig_scatter.update_layout(
                xaxis_title="Rating RAWG",
                yaxis_title="Metacritic Score",
                height=400
            )

            st.plotly_chart(fig_scatter, use_container_width=True)

        else:
            st.info("No hay datos de Metacritic disponibles para la selección actual")

    st.markdown("---")

    # =============================
    # SEGUNDA FILA DE GRÁFICAS
    # =============================

    col1, col2 = st.columns(2)

    # Distribución de ratings
    with col1:

        fig_dist = px.histogram(
            df_filtrado,
            x='rating',
            nbins=20,
            title="Distribución de Ratings"
        )

        fig_dist.update_layout(
            xaxis_title="Rating",
            yaxis_title="Cantidad de Juegos",
            height=400
        )

        st.plotly_chart(fig_dist, use_container_width=True)

    # Juegos por año
    with col2:

        juegos_por_año = df_filtrado.groupby(df_filtrado['fecha_lanzamiento'].dt.year).size().reset_index()

        juegos_por_año.columns = ['Año', 'Cantidad']

        fig_año = px.line(
            juegos_por_año,
            x='Año',
            y='Cantidad',
            title="Cantidad de Juegos por Año de Lanzamiento",
            markers=True
        )

        fig_año.update_layout(
            xaxis_title="Año",
            yaxis_title="Cantidad",
            height=400
        )

        st.plotly_chart(fig_año, use_container_width=True)

    st.markdown("---")

    # =============================
    # TABLA DETALLADA
    # =============================

    st.subheader("📋 Datos Detallados")

    df_display = df_filtrado[['nombre', 'fecha_lanzamiento', 'rating', 'metacritic']].copy()

    df_display['fecha_lanzamiento'] = df_display['fecha_lanzamiento'].dt.strftime('%Y-%m-%d')

    df_display = df_display.sort_values('rating', ascending=False)

    st.dataframe(
        df_display,
        use_container_width=True,
        height=400,
        hide_index=True
    )

    # =============================
    # ESTADÍSTICAS AVANZADAS
    # =============================

    st.markdown("---")
    st.subheader("📊 Estadísticas Avanzadas")

    col1, col2 = st.columns(2)

    with col1:

        st.write("**Estadísticas de Rating:**")

        stats_rating = {
            "Mínimo": f"{df_filtrado['rating'].min():.2f}",
            "Máximo": f"{df_filtrado['rating'].max():.2f}",
            "Promedio": f"{df_filtrado['rating'].mean():.2f}",
            "Mediana": f"{df_filtrado['rating'].median():.2f}",
            "Desv. Estándar": f"{df_filtrado['rating'].std():.2f}"
        }

        for key, value in stats_rating.items():
            st.write(f"• {key}: {value}")

    with col2:

        if df_filtrado['metacritic'].notna().any():

            st.write("**Estadísticas de Metacritic:**")

            df_meta = df_filtrado[df_filtrado['metacritic'].notna()]

            stats_meta = {
                "Mínimo": f"{df_meta['metacritic'].min():.0f}",
                "Máximo": f"{df_meta['metacritic'].max():.0f}",
                "Promedio": f"{df_meta['metacritic'].mean():.1f}",
                "Mediana": f"{df_meta['metacritic'].median():.0f}",
                "Desv. Estándar": f"{df_meta['metacritic'].std():.2f}"
            }

            for key, value in stats_meta.items():
                st.write(f"• {key}: {value}")

        else:
            st.info("No hay suficientes datos de Metacritic")

except Exception as e:
    st.error(f"❌ Error al cargar el dashboard: {e}")