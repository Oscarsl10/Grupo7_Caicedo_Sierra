#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sys
sys.path.insert(0, '.')

from scripts.database import SessionLocal
from scripts.models import Ciudad, RegistroClima, MetricasETL

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Clima ETL",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🌍 Dashboard de Clima - ETL Weatherstack")
st.markdown("---")

db = SessionLocal()

try:
    registros = db.query(RegistroClima, Ciudad.nombre).join(
        Ciudad
    ).order_by(RegistroClima.fecha_extraccion.desc()).all()

    data = []
    for registro, ciudad_nombre in registros:
        data.append({
            'Ciudad': ciudad_nombre,
            'Temperatura': registro.temperatura,
            'Sensacion_Termica': registro.sensacion_termica,
            'Humedad': registro.humedad,
            'Viento': registro.velocidad_viento,
            'Descripcion': registro.descripcion,
            'Fecha': registro.fecha_extraccion
        })

    df = pd.DataFrame(data)

    # ✅ NUEVO: Manejo cuando no hay datos
    if df.empty:
        st.warning("⚠️ No hay datos en la base de datos todavía.")
        st.stop()

    # Sidebar
    st.sidebar.title("🔧 Filtros")

    ciudades_disponibles = df['Ciudad'].unique()

    ciudades_filtro = st.sidebar.multiselect(
        "Selecciona Ciudades:",
        options=ciudades_disponibles,
        default=ciudades_disponibles
    )

    df_filtrado = df[df['Ciudad'].isin(ciudades_filtro)]

    if df_filtrado.empty:
        st.warning("⚠️ No hay datos para el filtro seleccionado.")
        st.stop()

    # =============================
    # MÉTRICAS
    # =============================
    st.subheader("📈 Métricas Principales")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        temp_promedio = df_filtrado['Temperatura'].mean()
        st.metric("🌡️ Temp. Promedio", f"{temp_promedio:.1f}°C")

    with col2:
        humedad_promedio = df_filtrado['Humedad'].mean()
        st.metric("💧 Humedad Promedio", f"{humedad_promedio:.1f}%")

    with col3:
        viento_maximo = df_filtrado['Viento'].max()
        ciudad_viento = df_filtrado.loc[
            df_filtrado['Viento'] == viento_maximo, 'Ciudad'
        ].iloc[0]
        st.metric("💨 Viento Máximo", f"{viento_maximo:.1f} km/h", f"en {ciudad_viento}")

    with col4:
        total_registros = len(df_filtrado)
        st.metric("📊 Total Registros", total_registros)

    st.markdown("---")

    # =============================
    # GRÁFICAS
    # =============================
    st.subheader("📉 Visualizaciones")

    col1, col2 = st.columns(2)

    with col1:
        fig_temp = px.bar(
            df_filtrado.sort_values('Temperatura', ascending=False),
            x='Ciudad',
            y='Temperatura',
            title="Temperatura por Ciudad",
            color='Temperatura',
            color_continuous_scale='RdYlBu_r'
        )
        st.plotly_chart(fig_temp, use_container_width=True)

    with col2:
        fig_humid = px.bar(
            df_filtrado,
            x='Ciudad',
            y='Humedad',
            title="Humedad por Ciudad",
            color='Humedad',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_humid, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        fig_scatter = px.scatter(
            df_filtrado,
            x='Temperatura',
            y='Humedad',
            size='Viento',
            color='Ciudad',
            title="Temperatura vs Humedad",
            hover_data=['Descripcion']
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col2:
        fig_wind = px.bar(
            df_filtrado.sort_values('Viento', ascending=False),
            x='Ciudad',
            y='Viento',
            title="Velocidad del Viento",
            color='Viento',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_wind, use_container_width=True)

    st.markdown("---")

    # =============================
    # TABLA
    # =============================
    st.subheader("📋 Datos Detallados")
    st.dataframe(
        df_filtrado.sort_values('Fecha', ascending=False),
        use_container_width=True,
        height=400
    )

finally:
    db.close()