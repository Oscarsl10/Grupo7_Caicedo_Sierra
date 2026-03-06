#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from sqlalchemy import func, and_
import sys
sys.path.insert(0, '.')

from scripts.database import SessionLocal
from scripts.models import Ciudad, RegistroClima

st.set_page_config(
    page_title="Dashboard Interactivo",
    page_icon="🎛️",
    layout="wide"
)

st.title("🎛️ Dashboard Interactivo - Control Total")

db = SessionLocal()

# =============================
# SIDEBAR CONTROLS
# =============================
st.sidebar.markdown("### 🔧 Controles")

ciudades_disponibles = [c.nombre for c in db.query(Ciudad).all()]

if not ciudades_disponibles:
    st.warning("No hay ciudades registradas en la base de datos")
    st.stop()

ciudades_seleccionadas = st.sidebar.multiselect(
    "🏙️ Ciudades a Mostrar",
    options=ciudades_disponibles,
    default=ciudades_disponibles
)

fecha_inicio = st.sidebar.date_input(
    "📅 Desde:",
    value=datetime.now() - timedelta(days=30)
)

fecha_fin = st.sidebar.date_input(
    "📅 Hasta:",
    value=datetime.now()
)

# convertir date -> datetime
fecha_inicio = datetime.combine(fecha_inicio, datetime.min.time())
fecha_fin = datetime.combine(fecha_fin, datetime.max.time())

temp_min = st.sidebar.slider("🌡️ Temp Mín (°C):", -50, 50, -10)
temp_max = st.sidebar.slider("🌡️ Temp Máx (°C):", -50, 50, 40)

# =============================
# QUERY FILTRADA
# =============================
registros_filtrados = db.query(
    RegistroClima,
    Ciudad.nombre
).join(Ciudad).filter(
    and_(
        Ciudad.nombre.in_(ciudades_seleccionadas),
        RegistroClima.fecha_extraccion >= fecha_inicio,
        RegistroClima.fecha_extraccion <= fecha_fin,
        RegistroClima.temperatura >= temp_min,
        RegistroClima.temperatura <= temp_max
    )
).all()

# =============================
# DATAFRAME
# =============================
data = []

for registro, ciudad_nombre in registros_filtrados:
    data.append({
        'Ciudad': ciudad_nombre,
        'Temperatura': registro.temperatura,
        'Sensación': registro.sensacion_termica,
        'Humedad': registro.humedad,
        'Viento': registro.velocidad_viento,
        'Descripción': registro.descripcion,
        'Fecha': registro.fecha_extraccion
    })

df = pd.DataFrame(data) if data else pd.DataFrame()

# =============================
# DASHBOARD
# =============================
if not df.empty:

    st.markdown("### 📊 Indicadores Clave")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("🌡️ Temp Max", f"{df['Temperatura'].max():.1f}°C")
    col2.metric("🌡️ Temp Min", f"{df['Temperatura'].min():.1f}°C")
    col3.metric("🌡️ Temp Prom", f"{df['Temperatura'].mean():.1f}°C")
    col4.metric("💧 Humedad Prom", f"{df['Humedad'].mean():.1f}%")
    col5.metric("💨 Viento Max", f"{df['Viento'].max():.1f} km/h")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.box(
            df,
            x='Ciudad',
            y='Temperatura',
            color='Ciudad',
            title='Distribución de Temperaturas'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        humedad_ciudad = df.groupby('Ciudad')['Humedad'].mean().reset_index()
        fig = px.bar(
            humedad_ciudad,
            x='Ciudad',
            y='Humedad',
            color='Humedad',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.markdown("#### 📈 Evolución Temporal")

    df['Fecha'] = pd.to_datetime(df['Fecha'])

    fig = px.line(
        df,
        x='Fecha',
        y='Temperatura',
        color='Ciudad',
        markers=True
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.markdown("#### 📋 Datos Detallados")

    mostrar_todos = st.checkbox("Mostrar todos los registros", value=False)

    columnas_mostrar = st.multiselect(
        "Columnas a mostrar:",
        df.columns.tolist(),
        default=['Ciudad', 'Temperatura', 'Humedad', 'Descripción', 'Fecha']
    )

    if mostrar_todos:
        st.dataframe(df[columnas_mostrar], use_container_width=True, height=600)
    else:
        st.dataframe(df[columnas_mostrar].head(20), use_container_width=True)

    st.markdown("---")

    csv = df.to_csv(index=False)

    st.download_button(
        label="⬇️ Descargar datos como CSV",
        data=csv,
        file_name=f"clima_datos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

else:
    st.warning("⚠️ No hay datos que coincidan con los filtros seleccionados")

db.close()