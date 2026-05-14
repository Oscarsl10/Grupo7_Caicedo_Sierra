# 🚀 Grupo7_Caicedo_Sierra - ETL y Machine Learning para Videojuegos 🎮

**Proyecto integrado de ingeniería de datos, análisis estadístico y machine learning con datos de videojuegos de la API RAWG**

---

## 📌 Descripción del Proyecto

Este repositorio contiene una serie de proyectos progresivos enfocados en el procesamiento, análisis y modelado predictivo de datos de videojuegos. Desde pruebas de concepto hasta implementaciones completas con dashboards interactivos y modelos de machine learning.

**Tema Central**: Extracción, transformación, análisis y predicción de características de videojuegos usando la API RAWG como fuente de datos primaria.

---

## 🎯 Objetivos del Proyecto

1. ✅ **ETL**: Implementar un pipeline completo de extracción, transformación y carga de datos
2. ✅ **Análisis Exploratorio**: Descubrir patrones y relaciones en datos de videojuegos
3. ✅ **Visualización**: Crear dashboards interactivos para exploración de datos
4. ✅ **Machine Learning**: Desarrollar modelos predictivos para ratings y clasificación
5. ✅ **Base de Datos**: Implementar almacenamiento confiable con PostgreSQL y migraciones
6. ✅ **Automatización**: Implementar pipelines automáticos de procesamiento

---

## 📊 Descripción de los Datos

### 📁 Fuente de los Datos
- **API RAWG** (https://rawg.io) - Base de datos de videojuegos más completa
- Plan gratuito con acceso a información de miles de juegos

### 📈 Tipo de Datos
- **Características de Videojuegos**: Nombre, fecha lanzamiento, géneros, plataformas, desarrolladores, publishers
- **Métricas de Popularidad**: Rating RAWG, Rating Metacritic, cantidad de ratings, playtime promedio
- **Datos de Contenido**: Clasificación ESRB, descripción, captura de pantallas

### 🧹 Procesamiento Realizado
- Limpieza de valores nulos
- Normalización de características numéricas
- Filtrado por calidad de datos (representatividad)
- Detección y manejo de outliers
- Codificación de variables categóricas

---

## 📏 Alcance

### ✅ Qué Incluye el Proyecto

- **7 sub-proyectos** con diferentes niveles de complejidad
- Extracción automatizada desde API RAWG
- Transformación y validación de datos
- Base de datos PostgreSQL con versionado (Alembic)
- 3 dashboards Streamlit interactivos
- 4 notebooks Jupyter con análisis ML
- Modelos de regresión lineal y clasificación
- Documentación completa

### ❌ Qué No Incluye

- Scraping de otros sitios web
- Datos en tiempo real (se extrae bajo demanda)
- Deployment en producción
- Análisis de sentimiento en reseñas

### 🎯 Resultados Esperados

- R² > 0.50 en modelos de regresión de Metacritic
- Precisión > 75% en clasificación de videojuegos
- Dashboards funcionales con datos actualizados
- Documentación de todo el pipeline

---

## 🛠️ Herramientas Utilizadas

### Backend & Data Processing
- 🐍 **Python 3.9+** - Lenguaje principal
- 🐘 **PostgreSQL 12+** - Base de datos relacional
- 🐳 **Docker** - Containerización (opcional)
- 🐧 **WSL/Linux** - Entorno de desarrollo

### Librerías Python Principales
- **pandas (2.2.2)** - Manipulación de datos
- **SQLAlchemy** - ORM y gestión de BD
- **Alembic** - Versionado de esquemas
- **scikit-learn (1.8.0)** - Modelos de ML
- **statsmodels (0.14.2)** - Análisis estadístico
- **plotly** - Gráficos interactivos
- **seaborn (0.13.2)** - Visualizaciones estadísticas

### Herramientas de Visualización
- 🌐 **Streamlit ≥1.31.0** - Dashboards web
- 📊 **Jupyter Notebook** - Análisis interactivo
- 📈 **Plotly** - Gráficos dinámicos

### Herramientas de Desarrollo
- 💻 **VS Code** - Editor principal
- 🔧 **Git** - Control de versiones

---

## 💡 Solución Propuesta

### 🔎 Análisis
El proyecto sigue un enfoque iterativo:
1. **Exploración inicial** de datos disponibles en RAWG API
2. **Identificación de variables** relevantes para predicción
3. **Análisis de correlaciones** y dependencias

### ⚙️ Implementación
1. **Pipeline ETL automatizado** para extracción y transformación
2. **Base de datos relacional** con modelos ORM en SQLAlchemy
3. **Transformaciones avanzadas** para mejora de calidad de datos
4. **Modelos ML múltiples** para comparación y selección

### 📊 Resultados
- Predicciones de Metacritic con R² > 0.50
- Clasificación de videojuegos con precisión > 75%
- Dashboards que permiten exploración interactiva de datos
- Documentación y reproducibilidad del análisis

---

## 🗂️ Estructura del Proyecto

```
Grupo7_Caicedo_Sierra/
│
├── 📄 README.md (este archivo)
│
├── 📂 01-Etl_Prueba/              ← Prueba inicial de ETL básico
│   ├── scripts/
│   │   ├── extractor.py
│   │   ├── scheduler.py
│   │   └── visualizador.py
│   └── requirements.txt
│
├── 📂 02-Etl_Proyecto/            ← ETL mejorado con Docker
│   ├── data/
│   ├── scripts/
│   │   ├── extractor.py
│   │   ├── loader.py
│   │   ├── transformador.py
│   │   └── visualizador.py
│   └── docker-compose.yml
│
├── 📂 03-Streamlit_Prueba/        ← Prueba de dashboards Streamlit
│   └── etl-weatherstack/
│       ├── dashboard_app.py
│       ├── scripts/
│       ├── alembic/
│       └── requirements.txt
│
├── 📂 04-Streamlit_Proyecto/      ← Dashboards con BD PostgreSQL
│   └── Etl_Proyecto/
│       ├── dashboard_*.py
│       ├── scripts/
│       ├── alembic/
│       └── requirements.txt
│
├── 📂 04.1-Streamlit_Proyecto/    ← Versión mejorada
│   └── Etl_Proyecto/
│       ├── dashboard_*.py
│       ├── scripts/
│       └── alembic/
│
├── 📂 05-JupyterNotebook_Prueba/  ← Análisis con Jupyter
│   └── etl-weatherstack/
│       ├── notebooks/
│       │   └── regresion_clima.ipynb
│       └── scripts/
│
├── 📂 06-JupyterNotebook_Proyecto/← ML avanzado en Notebooks
│   └── Etl_Proyecto/
│       ├── notebooks/
│       └── scripts/
│
└── 📂 07-Regresion-Clasificacion_Proyecto/ ← ⭐ PROYECTO FINAL
    └── Etl_Proyecto/
        ├── dashboard_*.py (3 dashboards)
        ├── scripts/
        │   ├── extractor_db.py
        │   ├── transformador.py
        │   ├── models.py
        │   ├── database.py
        │   ├── visualizador.py
        │   └── consultas.py
        ├── notebooks/ (4 notebooks ML)
        │   ├── regresion_videojuegos.ipynb
        │   ├── regresion_logistica_clasificacion_videojuegos.ipynb
        │   ├── arbol_decision_videojuegos.ipynb
        │   └── arbol_clasificacion_videojuegos.ipynb
        ├── alembic/ (migrations BD)
        ├── data/
        ├── logs/
        └── requirements.txt
```

---

## 🚀 Inicio Rápido

### Requisitos Previos
- Python 3.9+
- PostgreSQL 12+
- pip/conda
- Cuenta en RAWG (API gratuita)

### Instalación Rápida (Proyecto 07)

```bash
# 1. Navegar al proyecto final
cd 07-Regresion-Clasificacion_Proyecto/Etl_Proyecto

# 2. Crear entorno virtual
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
# Crear archivo .env con:
# RAWG_API_KEY=tu_api_key
# DATABASE_URL=postgresql://user:pass@localhost/videojuegos_etl

# 5. Crear base de datos
createdb videojuegos_etl

# 6. Aplicar migrations
alembic upgrade head

# 7. Ejecutar ETL
python scripts/extractor_db.py
python scripts/transformador.py

# 8. Iniciar dashboard
streamlit run dashboard_app.py
```

---

## 📈 Progresión de Proyectos

| # | Nombre | Objetivo | Tecnologías |
|---|--------|----------|-------------|
| 01 | ETL Prueba | Aprender extracción básica | Python, API, CSV |
| 02 | ETL Proyecto | ETL mejorado | Docker, Python |
| 03 | Streamlit Prueba | Aprender dashboards | Streamlit, Plotly |
| 04 | Streamlit Proyecto | Dashboards con BD | Streamlit, PostgreSQL |
| 04.1 | Streamlit Mejorado | Versión refinada | Streamlit, BD |
| 05 | Jupyter Prueba | Análisis exploratorio | Jupyter, Pandas |
| 06 | Jupyter Proyecto | ML avanzado | Jupyter, Scikit-learn |
| **07** | **Regresión & Clasificación** | **Proyecto Completo** | **Todos los anteriores** ⭐ |

---

## 🤖 Modelos de Machine Learning (Proyecto 07)

### Regresión Lineal
- **Predicción**: Metacritic Rating
- **Variables**: Rating RAWG, playtime, año, géneros, plataformas
- **Métrica**: R² > 0.50

### Clasificación
- **Regresión Logística**: Clasificación binaria/multiclase
- **Árbol de Decisión**: Interpretabilidad
- **Árbol de Clasificación**: Mejor desempeño
- **Métrica**: Precisión > 75%

---

## 💾 Base de Datos

### Arquitectura PostgreSQL
- **videojuegos**: Datos crudos de API
- **videojuegos_top**: Datos limpios y transformados
- **metricas_etl**: Logs de ejecuciones

### Migrations con Alembic
```bash
alembic current          # Ver versión actual
alembic upgrade head     # Aplicar últimas migrations
alembic downgrade -1     # Revertir última migración
```

---

## 🐛 Troubleshooting

**Error: "Cannot connect to PostgreSQL"**
```bash
# Verificar que PostgreSQL está corriendo
sudo service postgresql status
```

**Error: "ModuleNotFoundError"**
```bash
# Asegurar entorno activado
source env/bin/activate
pip install -r requirements.txt
```

**Error: "API Key inválida"**
- Obtener en: https://rawg.io/api
- Verificar en archivo `.env`

---

## 📥 Clonar Repositorio

```bash
git clone https://github.com/Oscarsl10/Grupo7_Caicedo_Sierra.git
cd Grupo7_Caicedo_Sierra
```

---

## 👥 Autores del Proyecto

- **kjcaicedo-2023a@corhuila.edu.co** 👨‍💻
- **ogsierra-2023a@corhuila.edu.co** 👨‍💻

**Grupo 7** 

---

## 📄 Licencia

Proyecto educativo - Libre para uso académico

---
