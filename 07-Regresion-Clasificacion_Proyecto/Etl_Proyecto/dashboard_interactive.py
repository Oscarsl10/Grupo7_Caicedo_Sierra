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
# CONFIGURACIÓN STREAMLIT
# ===============================

st.set_page_config(
    page_title="Dashboard Interactivo - Videojuegos",
    page_icon="🎛️",
    layout="wide",
)

st.title("🎛️ Dashboard Interactivo - Control Total de Videojuegos")

# ===============================
# CARGAR DATOS DESDE DB
# ===============================

@st.cache_data(ttl=600)
def load_from_db():

    df = pd.read_sql_table("videojuegos_top", con=engine)

    df["fecha_lanzamiento"] = pd.to_datetime(
        df["fecha_lanzamiento"],
        errors="coerce"
    )

    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["metacritic"] = pd.to_numeric(df["metacritic"], errors="coerce")
    df["ratings_count"] = pd.to_numeric(df["ratings_count"], errors="coerce")
    df["added"] = pd.to_numeric(df["added"], errors="coerce")
    df["playtime"] = pd.to_numeric(df["playtime"], errors="coerce")
    df["rating_top"] = pd.to_numeric(df["rating_top"], errors="coerce")

    if "metacritic" not in df.columns:
        df["metacritic"] = pd.NA

    # Procesar datos JSON para nuevos campos
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

    # Procesar campos JSON si existen
    json_fields = ['genres', 'platforms', 'developers', 'publishers']
    for field in json_fields:
        if field in df.columns:
            df[f'{field}_list'] = df[field].apply(safe_json_loads)
            df[f'{field}_names'] = df[f'{field}_list'].apply(
                lambda x: [item.get('name', item) if isinstance(item, dict) else str(item) for item in x] if isinstance(x, list) else []
            )
            df[f'{field}_str'] = df[f'{field}_names'].apply(
                lambda x: ', '.join(x) if x else 'N/A'
            )

    return df


# ===============================
# CARGAR DATA
# ===============================

try:
    df = load_from_db()

except Exception as err:
    st.error("❌ Error al leer la base de datos")
    st.error(str(err))
    st.stop()


# ===============================
# SIDEBAR
# ===============================

st.sidebar.markdown("### 🔧 Controles")

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

# rating

min_r, max_r = st.sidebar.slider(
    "⭐ Rating",
    float(df["rating"].min()),
    float(df["rating"].max()),
    (float(df["rating"].min()), float(df["rating"].max())),
    step=0.01
)

# metacritic

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
# FILTROS
# ===============================

df_filt = df.copy()

if nombre_busqueda:

    df_filt = df_filt[
        df_filt["nombre"].str.contains(nombre_busqueda, case=False, na=False)
    ]

if df_filt["fecha_lanzamiento"].notna().any():

    df_filt = df_filt[
        (df_filt["fecha_lanzamiento"].dt.date >= desde) &
        (df_filt["fecha_lanzamiento"].dt.date <= hasta)
    ]

df_filt = df_filt[
    (df_filt["rating"] >= min_r) &
    (df_filt["rating"] <= max_r)
]

if min_m is not None:

    df_filt = df_filt[
        (df_filt["metacritic"] >= min_m) &
        (df_filt["metacritic"] <= max_m)
    ]

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
        st.metric("📊 Ratings Count Prom", f"{df_filt['ratings_count'].mean():.0f}")
        st.metric("➕ Added Prom", f"{df_filt['added'].mean():.0f}")
        st.metric("⏱️ Playtime Prom", f"{df_filt['playtime'].mean():.1f}h")

    with col4:

        if df_filt["metacritic"].notna().any():
            st.metric("🎯 Metacritic Prom", f"{df_filt['metacritic'].mean():.1f}")
        else:
            st.metric("🎯 Metacritic Prom", "N/A")

    with col5:
        st.metric("🎮 Total Juegos", len(df_filt))

    st.markdown("---")

    # ===============================
    # GRÁFICAS
    # ===============================

    col1, col2 = st.columns(2)

    with col1:

        fig = px.box(
            df_filt,
            x="rating",
            title="Distribución de Ratings"
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:

        if df_filt["metacritic"].notna().any():

            fig = px.scatter(
                df_filt,
                x="rating",
                y="metacritic",
                hover_data=["nombre"],
                title="Rating vs Metacritic"
            )

            st.plotly_chart(fig, use_container_width=True)

        else:

            st.info("No hay valores de Metacritic")

    st.markdown("---")

    # ===============================
    # ANÁLISIS DE DESARROLLADORES Y PUBLISHERS
    # ===============================

    st.markdown("### 🏗️ Análisis de Desarrolladores y Publishers")

    col1, col2 = st.columns(2)

    with col1:
        if 'developers_names' in df_filt.columns:
            dev_counts = df_filt['developers_names'].explode().value_counts().head(15)
            if not dev_counts.empty:
                fig = px.bar(
                    dev_counts.reset_index(),
                    x="count",
                    y="developers_names",
                    orientation="h",
                    color="count",
                    color_continuous_scale="Blues",
                    title="Top 15 Desarrolladores"
                )
                fig.update_layout(yaxis_title="Desarrollador", xaxis_title="Cantidad de Juegos")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay datos de desarrolladores")
        else:
            st.info("Campo 'developers' no disponible")

    with col2:
        if 'publishers_names' in df_filt.columns:
            pub_counts = df_filt['publishers_names'].explode().value_counts().head(15)
            if not pub_counts.empty:
                fig = px.bar(
                    pub_counts.reset_index(),
                    x="count",
                    y="publishers_names",
                    orientation="h",
                    color="count",
                    color_continuous_scale="Greens",
                    title="Top 15 Publishers"
                )
                fig.update_layout(yaxis_title="Publisher", xaxis_title="Cantidad de Juegos")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay datos de publishers")
        else:
            st.info("Campo 'publishers' no disponible")

    st.markdown("---")

    # ===============================
    # ANÁLISIS DE GÉNEROS Y PLATAFORMAS
    # ===============================

    st.markdown("### 🎭 Análisis de Géneros y Plataformas")

    col1, col2 = st.columns(2)

    with col1:
        if 'genres_names' in df_filt.columns:
            genre_counts = df_filt['genres_names'].explode().value_counts().head(15)
            if not genre_counts.empty:
                fig = px.bar(
                    genre_counts.reset_index(),
                    x="count",
                    y="genres_names",
                    orientation="h",
                    color="count",
                    color_continuous_scale="Purples",
                    title="Top 15 Géneros"
                )
                fig.update_layout(yaxis_title="Género", xaxis_title="Cantidad de Juegos")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay datos de géneros")
        else:
            st.info("Campo 'genres' no disponible")

    with col2:
        if 'platforms_names' in df_filt.columns:
            platform_counts = df_filt['platforms_names'].explode().value_counts().head(15)
            if not platform_counts.empty:
                fig = px.bar(
                    platform_counts.reset_index(),
                    x="count",
                    y="platforms_names",
                    orientation="h",
                    color="count",
                    color_continuous_scale="Oranges",
                    title="Top 15 Plataformas"
                )
                fig.update_layout(yaxis_title="Plataforma", xaxis_title="Cantidad de Juegos")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay datos de plataformas")
        else:
            st.info("Campo 'platforms' no disponible")

    st.markdown("---")

    # ===============================
    # TABLA
    # ===============================

    st.markdown("#### 📋 Datos Detallados")

    mostrar_todos = st.checkbox("Mostrar todos los registros", value=False)

    columnas = st.multiselect(
        "Columnas:",
        df_filt.columns.tolist(),
        default=["nombre", "fecha_lanzamiento", "rating", "metacritic"]
    )

    if mostrar_todos:

        st.dataframe(
            df_filt[columnas],
            use_container_width=True,
            height=600
        )

    else:

        st.dataframe(
            df_filt[columnas].head(20),
            use_container_width=True
        )

    # ===============================
    # DESCARGA
    # ===============================

    st.markdown("---")

    csv = df_filt.to_csv(index=False)

    st.download_button(
        "⬇️ Descargar CSV",
        csv,
        file_name=f"videojuegos_filtrados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )