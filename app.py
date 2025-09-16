#!/usr/bin/env python3
"""
Aplicación Streamlit Completa para el Analizador de Acciones
Incluye análisis de rentabilidad esperada y letras más grandes
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from stock_analyzer import StockAnalyzer
import time

# Configuración de la página
st.set_page_config(
    page_title="Analizador de Acciones por Mercado",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado con letras más grandes
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .stButton > button {
        background-color: #1f77b4;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #0d5aa7;
    }
    /* Hacer las tablas ENORMES */
    .dataframe {
        font-size: 22px !important;
    }
    .dataframe th {
        font-size: 24px !important;
        font-weight: bold !important;
    }
    .dataframe td {
        font-size: 22px !important;
    }
    /* Hacer métricas ENORMES */
    .metric-value {
        font-size: 3rem !important;
    }
    .metric-label {
        font-size: 1.8rem !important;
    }
    /* Texto general ENORME */
    .stMarkdown {
        font-size: 24px !important;
    }
    .stMarkdown p {
        font-size: 24px !important;
    }
    /* Selectbox ENORME */
    .stSelectbox > div > div > select {
        font-size: 22px !important;
        padding: 8px !important;
    }
    .stSelectbox label {
        font-size: 20px !important;
    }
    /* Slider labels ENORME */
    .stSlider > div > div > div > div {
        font-size: 20px !important;
    }
    .stSlider label {
        font-size: 20px !important;
    }
    /* Botones ENORMES */
    .stButton > button {
        font-size: 20px !important;
        padding: 1rem 2rem !important;
    }
    /* Sidebar text ENORME */
    .sidebar .sidebar-content {
        font-size: 20px !important;
    }
    /* Títulos de pestañas ENORMES */
    .stTabs [data-baseweb="tab"] {
        font-size: 22px !important;
        font-weight: bold !important;
        padding: 12px 16px !important;
    }
    /* Headers ENORMES */
    .stSubheader {
        font-size: 28px !important;
    }
    /* Multiselect ENORME */
    .stMultiSelect label {
        font-size: 20px !important;
    }
    .stMultiSelect > div > div {
        font-size: 20px !important;
    }
    /* Input labels ENORMES */
    label {
        font-size: 20px !important;
    }
    /* Text input ENORME */
    .stTextInput > div > div > input {
        font-size: 20px !important;
    }
    /* Radio buttons ENORME */
    .stRadio label {
        font-size: 20px !important;
    }
    /* Checkbox ENORME */
    .stCheckbox label {
        font-size: 20px !important;
    }
    /* Info/warning boxes ENORME */
    .stAlert {
        font-size: 20px !important;
    }
</style>
""", unsafe_allow_html=True)

def load_market_data(force_refresh=False):
    """Carga los datos usando StockAnalyzer unificado con persistencia"""
    analyzer = StockAnalyzer(cache_hours=24)
    
    if force_refresh:
        st.info("🔄 Forzando descarga de datos nuevos...")
    else:
        cache_info = analyzer.get_cache_info()
        if cache_info['status'] == 'Fresh':
            st.success(f"✅ Usando datos en cache (actualizado hace {cache_info['age_hours']} horas)")
        elif cache_info['status'] == 'Stale':
            st.warning(f"⚠️ Datos obsoletos ({cache_info['age_hours']} horas), descargando actualizados...")
    
    with st.spinner('Cargando datos... Esto puede tardar algunos minutos si es la primera vez.'):
        markets_data, all_stocks = analyzer.load_data(force_refresh=force_refresh)
    
    return analyzer, markets_data, all_stocks

def format_number(value, is_percentage=False, is_currency=False):
    """Formatea números para mostrar"""
    if pd.isna(value) or value is None:
        return "N/A"
    
    if is_percentage:
        return f"{value:.2f}%"
    elif is_currency:
        if value >= 1e9:
            return f"${value/1e9:.2f}B"
        elif value >= 1e6:
            return f"${value/1e6:.2f}M"
        else:
            return f"${value:.2f}"
    else:
        return f"{value:.2f}"

def create_comparison_chart(data, metric, title):
    """Crea gráfico de comparación entre mercados"""
    if metric not in data.columns:
        st.warning(f"Métrica {metric} no disponible")
        return None
    
    market_avg = data.groupby('Market')[metric].mean().reset_index()
    market_avg = market_avg.dropna()
    
    if market_avg.empty:
        st.warning(f"No hay datos disponibles para {metric}")
        return None
    
    fig = px.bar(
        market_avg, 
        x='Market', 
        y=metric, 
        title=title,
        color='Market',
        text=metric,
        height=500  # Gráficos más grandes
    )
    
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside', textfont_size=20)
    fig.update_layout(showlegend=False, font=dict(size=18))
    
    return fig

def create_top_stocks_chart(data, metric, title, top_n=10):
    """Crea gráfico de top acciones por métrica"""
    if metric not in data.columns:
        return None
    
    filtered_data = data[data[metric].notna()]
    if filtered_data.empty:
        return None
    
    ascending = metric in ['PE_Ratio', 'PB_Ratio', 'Debt_Equity']
    top_stocks = filtered_data.nlargest(top_n, metric) if not ascending else filtered_data.nsmallest(top_n, metric)
    
    fig = px.bar(
        top_stocks, 
        x=metric, 
        y='Name', 
        orientation='h',
        title=title,
        color='Market',
        text='Symbol',
        height=600  # Gráficos más grandes
    )
    
    fig.update_traces(textposition='inside', textfont_size=18)
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, font=dict(size=18))
    
    return fig

def create_scatter_plot(data, x_metric, y_metric, title):
    """Crea gráfico de dispersión"""
    if x_metric not in data.columns or y_metric not in data.columns:
        return None
    
    filtered_data = data[(data[x_metric].notna()) & (data[y_metric].notna())]
    if filtered_data.empty:
        return None
    
    fig = px.scatter(
        filtered_data,
        x=x_metric,
        y=y_metric,
        color='Market',
        size='Market_Cap',
        hover_data=['Symbol', 'Name'],
        title=title,
        height=600  # Gráficos más grandes
    )
    
    fig.update_layout(font=dict(size=20))
    
    return fig

def main():
    # Header
    st.markdown('<h1 class="main-header">📈 Analizador de Acciones por Mercado</h1>', unsafe_allow_html=True)
    st.markdown("### IBEX 35 | Medium Cap España | S&P 500 | NASDAQ")
    
    # Sidebar
    st.sidebar.title("🔧 Configuración")
    
    # Cargar datos
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    
    # Botones de carga
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        load_button = st.button("🔄 Cargar Datos", help="Carga datos (usa cache si está disponible)")
    
    with col2:
        refresh_button = st.button("🆕 Forzar Actualizar", help="Descarga datos nuevos ignorando cache")
    
    if load_button or refresh_button:
        try:
            force_refresh = refresh_button
            analyzer, markets_data, all_stocks = load_market_data(force_refresh)
            
            st.session_state.analyzer = analyzer
            st.session_state.markets_data = markets_data
            st.session_state.all_stocks = all_stocks
            st.session_state.data_loaded = True
            
            st.sidebar.success("✅ Datos cargados exitosamente!")
            
        except Exception as e:
            st.sidebar.error(f"❌ Error al cargar datos: {str(e)}")
            return
    
    # Información del cache
    if st.session_state.data_loaded and 'analyzer' in st.session_state:
        cache_info = st.session_state.analyzer.get_cache_info()
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 Info del Cache")
        st.sidebar.write(f"**Estado:** {cache_info.get('status', 'N/A')}")
        
        if cache_info.get('last_update'):
            st.sidebar.write(f"**Actualizado:** {cache_info['last_update'].strftime('%d/%m/%Y %H:%M')}")
            st.sidebar.write(f"**Antigüedad:** {cache_info.get('age_hours', 0):.1f} horas")
        
        st.sidebar.write(f"**Total acciones:** {cache_info.get('total_stocks', 0)}")
        st.sidebar.write(f"**Tamaño archivo:** {cache_info.get('cache_file_size', 'N/A')}")
        
        # Botón para limpiar cache
        if st.sidebar.button("🗑️ Limpiar Cache", help="Elimina archivos de cache local"):
            st.session_state.analyzer.clear_cache()
            st.sidebar.success("✅ Cache limpiado")
    
    if not st.session_state.data_loaded:
        st.info("👆 Haz clic en 'Cargar Datos' en la barra lateral para comenzar")
        return
    
    # Datos cargados
    markets_data = st.session_state.markets_data
    all_stocks = st.session_state.all_stocks
    analyzer = st.session_state.analyzer
    
    # Resumen rápido con métricas más grandes
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Acciones", len(all_stocks))
    
    with col2:
        avg_pe = all_stocks['PE_Ratio'].mean()
        st.metric("💰 P/E Promedio", format_number(avg_pe))
    
    with col3:
        avg_dividend = all_stocks['Dividend_Yield'].mean() * 100
        st.metric("💵 Dividend Yield Promedio", format_number(avg_dividend, is_percentage=True))
    
    with col4:
        avg_roe = all_stocks['ROE'].mean() * 100
        st.metric("📈 ROE Promedio", format_number(avg_roe, is_percentage=True))
    
    # Pestañas principales - AÑADIENDO LA NUEVA PESTAÑA DE RENTABILIDAD
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏢 Por Mercado", 
        "📊 Análisis Fundamental", 
        "💰 Dividendos", 
        "🎯 Filtros Avanzados",
        "🚀 Top Rentabilidad",  # NUEVA PESTAÑA
        "📋 Datos Completos"
    ])
    
    # TAB 1: Por Mercado
    with tab1:
        st.subheader("📈 Análisis por Mercado")
        
        # Descripción de la pestaña
        with st.expander("ℹ️ ¿Qué es el Análisis por Mercado?", expanded=False):
            st.markdown("""
            ### 📊 **Análisis por Mercado - Definiciones y Cálculos**
            
            **📈 Price (Precio):** Precio actual de la acción en el mercado.
            
            **💰 Market Cap (Capitalización de Mercado):** 
            - **Qué es:** Valor total de todas las acciones de la empresa
            - **Cálculo:** Precio por acción × Número total de acciones
            - **Interpretación:** Empresas grandes (>10B), medianas (1B-10B), pequeñas (<1B)
            
            **📊 P/E Ratio (Precio/Beneficio):**
            - **Qué es:** Cuánto pagan los inversores por cada euro de beneficio
            - **Cálculo:** Precio por acción ÷ Beneficio por acción
            - **Interpretación:** Menor = más barata, Mayor = más cara o con expectativas de crecimiento
            
            **💵 Dividend Yield (Rentabilidad por Dividendo):**
            - **Qué es:** Porcentaje de dividendos anuales respecto al precio
            - **Cálculo:** (Dividendo anual ÷ Precio de la acción) × 100
            - **Interpretación:** >4% = alto, 2-4% = moderado, <2% = bajo
            
            **🏆 ROE (Return on Equity - Rentabilidad sobre Patrimonio):**
            - **Qué es:** Capacidad de generar beneficios con el patrimonio de los accionistas
            - **Cálculo:** (Beneficio neto ÷ Patrimonio neto) × 100
            - **Interpretación:** >15% = excelente, 10-15% = bueno, <10% = regular
            
            **📈 Price Change 1Y (Cambio de Precio 1 Año):**
            - **Qué es:** Porcentaje de subida/bajada del precio en el último año
            - **Cálculo:** ((Precio actual - Precio hace 1 año) ÷ Precio hace 1 año) × 100
            - **Interpretación:** Positivo = subida, Negativo = bajada
            
            **⚖️ Beta:**
            - **Qué es:** Medida de volatilidad respecto al mercado
            - **Cálculo:** Correlación de movimientos con el índice de referencia
            - **Interpretación:** Beta = 1 (igual al mercado), >1 (más volátil), <1 (menos volátil)
            """)
        
        st.markdown("---")
        
        market_options = ["Todos"] + list(markets_data.keys())
        selected_market = st.selectbox("Selecciona Mercado:", market_options)
        
        if selected_market == "Todos":
            display_data = all_stocks
        else:
            display_data = markets_data[selected_market]
        
        # Métricas del mercado seleccionado
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Acciones", len(display_data))
        with col2:
            avg_cap = display_data['Market_Cap'].mean()
            st.metric("Cap. Mercado Prom.", format_number(avg_cap, is_currency=True))
        with col3:
            avg_pe = display_data['PE_Ratio'].mean()
            st.metric("P/E Promedio", format_number(avg_pe))
        with col4:
            avg_div = display_data['Dividend_Yield'].mean() * 100
            st.metric("Dividend Yield Prom.", format_number(avg_div, is_percentage=True))
        with col5:
            avg_roe = display_data['ROE'].mean() * 100
            st.metric("ROE Promedio", format_number(avg_roe, is_percentage=True))
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            top_cap = display_data.nlargest(10, 'Market_Cap')
            if not top_cap.empty:
                fig_cap = px.bar(
                    top_cap, 
                    x='Market_Cap', 
                    y='Name',
                    orientation='h',
                    title="Top 10 - Mayor Capitalización de Mercado",
                    text='Symbol',
                    height=500
                )
                fig_cap.update_traces(textposition='inside', textfont_size=18)
                fig_cap.update_layout(font=dict(size=14))
                st.plotly_chart(fig_cap, use_container_width=True)
        
        with col2:
            if selected_market == "Todos":
                market_counts = all_stocks['Market'].value_counts()
                fig_pie = px.pie(
                    values=market_counts.values,
                    names=market_counts.index,
                    title="Distribución de Acciones por Mercado",
                    height=500
                )
                fig_pie.update_layout(font=dict(size=14))
                st.plotly_chart(fig_pie, use_container_width=True)
        
        # Tabla de datos más grande
        st.subheader("📋 Datos del Mercado")
        
        display_columns = [
            'Symbol', 'Name', 'Price', 'Market_Cap', 'PE_Ratio', 
            'Dividend_Yield', 'ROE', 'Price_Change_1Y', 'Beta'
        ]
        
        display_df = display_data[display_columns].copy()
        
        # Formatear columnas
        if 'Price' in display_df.columns:
            display_df['Price'] = display_df['Price'].apply(lambda x: format_number(x, is_currency=True))
        if 'Market_Cap' in display_df.columns:
            display_df['Market_Cap'] = display_df['Market_Cap'].apply(lambda x: format_number(x, is_currency=True))
        if 'PE_Ratio' in display_df.columns:
            display_df['PE_Ratio'] = display_df['PE_Ratio'].apply(lambda x: format_number(x))
        if 'Dividend_Yield' in display_df.columns:
            display_df['Dividend_Yield'] = display_df['Dividend_Yield'].apply(lambda x: format_number(x*100 if x else x, is_percentage=True))
        if 'ROE' in display_df.columns:
            display_df['ROE'] = display_df['ROE'].apply(lambda x: format_number(x*100 if x else x, is_percentage=True))
        if 'Price_Change_1Y' in display_df.columns:
            display_df['Price_Change_1Y'] = display_df['Price_Change_1Y'].apply(lambda x: format_number(x, is_percentage=True))
        if 'Beta' in display_df.columns:
            display_df['Beta'] = display_df['Beta'].apply(lambda x: format_number(x))
        
        st.dataframe(display_df, use_container_width=True, height=500)
    
    # TAB 2: Análisis Fundamental
    with tab2:
        st.subheader("📊 Análisis Fundamental")
        
        # Descripción de la pestaña
        with st.expander("ℹ️ ¿Qué son los Ratios Fundamentales?", expanded=False):
            st.markdown("""
            ### 📊 **Análisis Fundamental - Ratios Clave**
            
            **📊 P/E Ratio (Price-to-Earnings):**
            - **Qué es:** Múltiplo que indica cuánto pagan los inversores por cada euro de beneficio
            - **Cálculo:** Precio por acción ÷ Beneficio por acción (BPA)
            - **Interpretación:** 
              - <10 = Muy barata (posible value trap)
              - 10-15 = Razonable 
              - 15-25 = Cara pero puede tener crecimiento
              - >25 = Muy cara (expectativas altas)
            
            **📈 P/B Ratio (Price-to-Book):**
            - **Qué es:** Precio de la acción vs. valor contable
            - **Cálculo:** Precio por acción ÷ Valor contable por acción
            - **Interpretación:** 
              - <1 = Cotiza por debajo del valor contable (valor)
              - 1-2 = Rango normal
              - >3 = Muy cara (empresas de crecimiento/tecnología)
            
            **🏆 ROE (Return on Equity):**
            - **Qué es:** Rentabilidad que obtiene la empresa sobre el patrimonio
            - **Cálculo:** (Beneficio neto ÷ Patrimonio neto) × 100
            - **Interpretación:**
              - >20% = Excelente
              - 15-20% = Muy bueno
              - 10-15% = Bueno
              - <10% = Regular/malo
            
            **💼 ROA (Return on Assets):**
            - **Qué es:** Eficiencia en el uso de activos para generar beneficios
            - **Cálculo:** (Beneficio neto ÷ Activos totales) × 100
            - **Interpretación:**
              - >10% = Excelente eficiencia
              - 5-10% = Buena eficiencia
              - <5% = Eficiencia regular
            
            **💰 Margen de Beneficio (Profit Margin):**
            - **Qué es:** Porcentaje de ingresos que se convierte en beneficio
            - **Cálculo:** (Beneficio neto ÷ Ingresos totales) × 100
            - **Interpretación:**
              - >20% = Excelente (empresas con ventaja competitiva)
              - 10-20% = Bueno
              - 5-10% = Regular
              - <5% = Bajo (sectores competitivos)
            
            **⚖️ Deuda/Patrimonio (Debt-to-Equity):**
            - **Qué es:** Nivel de endeudamiento respecto al patrimonio
            - **Cálculo:** Deuda total ÷ Patrimonio neto
            - **Interpretación:**
              - <0.3 = Poco endeudada (conservadora)
              - 0.3-0.6 = Endeudamiento moderado
              - >1.0 = Muy endeudada (riesgo)
            """)
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            metric_options = {
                'P/E Ratio': 'PE_Ratio',
                'P/B Ratio': 'PB_Ratio', 
                'ROE': 'ROE',
                'ROA': 'ROA',
                'Margen de Beneficio': 'Profit_Margin',
                'Deuda/Patrimonio': 'Debt_Equity'
            }
            selected_metric_name = st.selectbox("Métrica:", list(metric_options.keys()))
            selected_metric = metric_options[selected_metric_name]
        
        with col2:
            sort_order = st.selectbox("Ordenar:", ["Menor a Mayor", "Mayor a Menor"])
            ascending = sort_order == "Menor a Mayor"
        
        with col3:
            top_n = st.slider("Mostrar top:", 5, 50, 20)
        
        # Gráfico principal
        title = f"Top {top_n} - {selected_metric_name}"
        fig = create_top_stocks_chart(all_stocks, selected_metric, title, top_n)
        
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        # Comparación entre mercados
        st.subheader("🔄 Comparación entre Mercados")
        fig_comparison = create_comparison_chart(all_stocks, selected_metric, f"{selected_metric_name} Promedio por Mercado")
        
        if fig_comparison:
            st.plotly_chart(fig_comparison, use_container_width=True)
        
        # Análisis de correlación
        st.subheader("🔗 Análisis de Correlación")
        col1, col2 = st.columns(2)
        
        with col1:
            x_metric = st.selectbox("Eje X:", list(metric_options.keys()), key="x_metric")
        with col2:
            y_metric = st.selectbox("Eje Y:", list(metric_options.keys()), index=1, key="y_metric")
        
        x_col = metric_options[x_metric]
        y_col = metric_options[y_metric]
        
        fig_scatter = create_scatter_plot(all_stocks, x_col, y_col, f"{x_metric} vs {y_metric}")
        if fig_scatter:
            st.plotly_chart(fig_scatter, use_container_width=True)
    
    # TAB 3: Dividendos
    with tab3:
        st.subheader("💰 Análisis de Dividendos")
        
        # Descripción de la pestaña
        with st.expander("ℹ️ ¿Qué son los Dividendos y sus Ratios?", expanded=False):
            st.markdown("""
            ### 💰 **Análisis de Dividendos - Conceptos Clave**
            
            **💵 Dividend Yield (Rentabilidad por Dividendo):**
            - **Qué es:** Retorno anual en dividendos como porcentaje del precio de la acción
            - **Cálculo:** (Dividendo anual por acción ÷ Precio por acción) × 100
            - **Interpretación:**
              - >6% = Muy alto (posible riesgo o sector especial)
              - 4-6% = Alto (atractivo para ingresos)
              - 2-4% = Moderado (equilibrado)
              - 1-2% = Bajo (empresa de crecimiento)
              - 0% = No paga dividendos
            
            **💰 Dividend Rate (Tasa de Dividendo):**
            - **Qué es:** Cantidad total en euros/dólares pagada por acción al año
            - **Cálculo:** Suma de todos los dividendos pagados en 12 meses
            - **Interpretación:** Cantidad absoluta que recibirás por cada acción que poseas
            
            **📊 Payout Ratio (Ratio de Pago):**
            - **Qué es:** Porcentaje de beneficios que la empresa destina a dividendos
            - **Cálculo:** (Dividendos pagados ÷ Beneficio neto) × 100
            - **Interpretación:**
              - <40% = Conservador (mucho margen para crecer dividendos)
              - 40-60% = Equilibrado (sostenible)
              - 60-80% = Alto (menos margen para crecer)
              - >100% = Insostenible (pagando más de lo que gana)
            
            **📅 Ex-Dividend Date (Fecha Ex-Dividendo):**
            - **Qué es:** Fecha límite para tener derecho al próximo dividendo
            - **Interpretación:** Debes poseer la acción antes de esta fecha para recibir el dividendo
            
            ### 🎯 **Estrategias de Inversión en Dividendos:**
            
            **🏆 Dividend Aristocrats:** Empresas que han aumentado dividendos >25 años consecutivos
            
            **💎 High Quality Dividend:** Payout ratio 40-70% + Dividend yield 3-6%
            
            **⚠️ Dividend Traps:** Yields muy altos (>8%) pueden indicar problemas empresariales
            
            **📈 Dividend Growth:** Empresas que aumentan dividendos consistentemente año tras año
            """)
        
        st.markdown("---")
        
        dividend_stocks = all_stocks[all_stocks['Dividend_Yield'] > 0].copy()
        
        if dividend_stocks.empty:
            st.warning("No se encontraron acciones con dividendos")
            return
        
        # Métricas de dividendos
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Acciones con Dividendos", len(dividend_stocks))
        with col2:
            avg_yield = dividend_stocks['Dividend_Yield'].mean() * 100
            st.metric("Yield Promedio", format_number(avg_yield, is_percentage=True))
        with col3:
            max_yield = dividend_stocks['Dividend_Yield'].max() * 100
            st.metric("Yield Máximo", format_number(max_yield, is_percentage=True))
        with col4:
            avg_payout = dividend_stocks['Payout_Ratio'].mean() * 100
            st.metric("Payout Ratio Promedio", format_number(avg_payout, is_percentage=True))
        
        # Filtros de dividendos
        col1, col2 = st.columns(2)
        
        with col1:
            min_yield = st.slider("Yield mínimo (%):", 0.0, 15.0, 2.0, 0.5)
        with col2:
            max_payout = st.slider("Payout ratio máximo (%):", 0, 200, 100, 10)
        
        # Filtrar datos
        filtered_div = dividend_stocks[
            (dividend_stocks['Dividend_Yield'] >= min_yield/100) &
            (dividend_stocks['Payout_Ratio'] <= max_payout/100)
        ]
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            top_div = filtered_div.nlargest(15, 'Dividend_Yield')
            if not top_div.empty:
                fig_div = px.bar(
                    top_div,
                    x='Dividend_Yield',
                    y='Name',
                    orientation='h',
                    title="Top 15 - Mayores Dividendos",
                    text='Symbol',
                    color='Market',
                    height=600
                )
                fig_div.update_traces(textposition='inside', textfont_size=18)
                fig_div.update_layout(font=dict(size=14))
                st.plotly_chart(fig_div, use_container_width=True)
        
        with col2:
            fig_div_pe = create_scatter_plot(
                filtered_div, 'PE_Ratio', 'Dividend_Yield', 
                "Dividend Yield vs P/E Ratio"
            )
            if fig_div_pe:
                st.plotly_chart(fig_div_pe, use_container_width=True)
        
        # Tabla de dividendos más grande
        st.subheader("📋 Acciones con Mejores Dividendos")
        div_columns = ['Symbol', 'Name', 'Market', 'Price', 'Dividend_Yield', 'Dividend_Rate', 'Payout_Ratio', 'PE_Ratio']
        div_display = filtered_div[div_columns].copy()
        
        # Formatear
        div_display['Price'] = div_display['Price'].apply(lambda x: format_number(x, is_currency=True))
        div_display['Dividend_Yield'] = div_display['Dividend_Yield'].apply(lambda x: format_number(x*100, is_percentage=True))
        div_display['Dividend_Rate'] = div_display['Dividend_Rate'].apply(lambda x: format_number(x, is_currency=True))
        div_display['Payout_Ratio'] = div_display['Payout_Ratio'].apply(lambda x: format_number(x*100 if x else x, is_percentage=True))
        div_display['PE_Ratio'] = div_display['PE_Ratio'].apply(lambda x: format_number(x))
        
        st.dataframe(div_display.head(20), use_container_width=True, height=500)
    
    # TAB 4: Filtros Avanzados
    with tab4:
        st.subheader("🎯 Filtros Avanzados")
        
        # Descripción de la pestaña
        with st.expander("ℹ️ ¿Qué son las Estrategias de Inversión?", expanded=False):
            st.markdown("""
            ### 🎯 **Estrategias de Inversión - Filtros Explicados**
            
            ### 🚀 **Estrategias Predefinidas:**
            
            **💎 Value Stocks (Acciones de Valor):**
            - **Criterios:** P/E < 15 AND Dividend Yield > 2%
            - **Filosofía:** Comprar empresas infravaloradas que pagan dividendos
            - **Perfil:** Conservador, busca seguridad y valor
            - **Riesgo:** Bajo-Medio
            - **Ejemplos:** Bancos, utilities, industrias maduras
            
            **🚀 Growth Stocks (Acciones de Crecimiento):**
            - **Criterios:** ROE > 15% AND Crecimiento precio > 10%
            - **Filosofía:** Empresas que crecen rápidamente y reinvierten beneficios
            - **Perfil:** Agresivo, busca apreciación del capital
            - **Riesgo:** Alto
            - **Ejemplos:** Tecnología, biotecnología, startups exitosas
            
            **🏆 High Quality (Alta Calidad):**
            - **Criterios:** ROE > 20% AND Margen beneficio > 15%
            - **Filosofía:** Empresas con ventajas competitivas sostenibles
            - **Perfil:** Equilibrado, busca calidad y crecimiento
            - **Riesgo:** Medio
            - **Ejemplos:** Marcas fuertes, monopolios naturales, líderes de mercado
            
            **💰 High Dividend (Alto Dividendo):**
            - **Criterios:** Dividend Yield > 5%
            - **Filosofía:** Maximizar ingresos por dividendos
            - **Perfil:** Conservador, busca ingresos regulares
            - **Riesgo:** Medio (riesgo de recorte de dividendos)
            - **Ejemplos:** REITs, utilities, telecomunicaciones
            
            ### 🔧 **Filtros Personalizados - Rangos Recomendados:**
            
            **📊 P/E Ratio:**
            - Value: 5-15
            - Balanced: 10-25
            - Growth: 20-40+
            
            **🏆 ROE (%):**
            - Excelente: >20%
            - Bueno: 15-20%
            - Regular: 10-15%
            
            **💵 Dividend Yield (%):**
            - Alto: >4%
            - Moderado: 2-4%
            - Bajo: <2%
            
            **💰 Market Cap (B$):**
            - Large Cap: >10B
            - Mid Cap: 1-10B
            - Small Cap: <1B
            
            **⚖️ Beta:**
            - Conservador: <1
            - Mercado: ~1
            - Volátil: >1.5
            """)
        
        st.markdown("---")
        
        # Filtros preconfigurados
        st.subheader("🚀 Estrategias Predefinidas")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("💎 Value Stocks", help="P/E < 15 y Dividend Yield > 2%"):
                st.session_state.filter_type = "value"
        
        with col2:
            if st.button("🚀 Growth Stocks", help="ROE > 15% y Crecimiento > 10%"):
                st.session_state.filter_type = "growth"
        
        with col3:
            if st.button("🏆 High Quality", help="ROE > 20% y Margen > 15%"):
                st.session_state.filter_type = "quality"
        
        with col4:
            if st.button("💰 High Dividend", help="Dividend Yield > 5%"):
                st.session_state.filter_type = "dividend"
        
        # Filtros personalizados
        st.subheader("🔧 Filtros Personalizados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            pe_range = st.slider("P/E Ratio:", 0.0, 100.0, (0.0, 50.0), 1.0)
            roe_range = st.slider("ROE (%):", -50.0, 100.0, (0.0, 100.0), 1.0)
            div_range = st.slider("Dividend Yield (%):", 0.0, 20.0, (0.0, 20.0), 0.5)
        
        with col2:
            market_cap_range = st.slider("Market Cap (B$):", 0.0, 5000.0, (0.0, 5000.0), 10.0)
            beta_range = st.slider("Beta:", 0.0, 3.0, (0.0, 3.0), 0.1)
            selected_markets = st.multiselect("Mercados:", list(markets_data.keys()), default=list(markets_data.keys()))
        
        # Aplicar filtros
        filtered_data = all_stocks.copy()
        
        # Filtros predefinidos
        if hasattr(st.session_state, 'filter_type'):
            if st.session_state.filter_type == "value":
                filtered_data = filtered_data[
                    (filtered_data['PE_Ratio'] < 15) & 
                    (filtered_data['PE_Ratio'] > 0) &
                    (filtered_data['Dividend_Yield'] > 0.02)
                ]
            elif st.session_state.filter_type == "growth":
                filtered_data = filtered_data[
                    (filtered_data['ROE'] > 0.15) & 
                    (filtered_data['Price_Change_1Y'] > 10)
                ]
            elif st.session_state.filter_type == "quality":
                filtered_data = filtered_data[
                    (filtered_data['ROE'] > 0.20) & 
                    (filtered_data['Profit_Margin'] > 0.15)
                ]
            elif st.session_state.filter_type == "dividend":
                filtered_data = filtered_data[filtered_data['Dividend_Yield'] > 0.05]
        
        # Filtros personalizados
        filtered_data = filtered_data[
            (filtered_data['PE_Ratio'].between(pe_range[0], pe_range[1]) | filtered_data['PE_Ratio'].isna()) &
            (filtered_data['ROE'].between(roe_range[0]/100, roe_range[1]/100) | filtered_data['ROE'].isna()) &
            (filtered_data['Dividend_Yield'].between(div_range[0]/100, div_range[1]/100) | filtered_data['Dividend_Yield'].isna()) &
            (filtered_data['Market_Cap'].between(market_cap_range[0]*1e9, market_cap_range[1]*1e9) | filtered_data['Market_Cap'].isna()) &
            (filtered_data['Beta'].between(beta_range[0], beta_range[1]) | filtered_data['Beta'].isna()) &
            (filtered_data['Market'].isin(selected_markets))
        ]
        
        st.subheader(f"📊 Resultados ({len(filtered_data)} acciones)")
        
        if not filtered_data.empty:
            # Gráfico de resultados
            if len(filtered_data) <= 20:
                fig_results = px.bar(
                    filtered_data,
                    x='Name',
                    y='ROE',
                    color='Market',
                    title="ROE de Acciones Filtradas",
                    text='Symbol',
                    height=500
                )
                fig_results.update_traces(textposition='outside', textfont_size=18)
                fig_results.update_xaxes(tickangle=45)
                fig_results.update_layout(font=dict(size=14))
                st.plotly_chart(fig_results, use_container_width=True)
            
            # Tabla de resultados más grande
            result_columns = ['Symbol', 'Name', 'Market', 'Price', 'PE_Ratio', 'ROE', 'Dividend_Yield', 'Market_Cap']
            result_display = filtered_data[result_columns].copy()
            
            # Formatear
            result_display['Price'] = result_display['Price'].apply(lambda x: format_number(x, is_currency=True))
            result_display['PE_Ratio'] = result_display['PE_Ratio'].apply(lambda x: format_number(x))
            result_display['ROE'] = result_display['ROE'].apply(lambda x: format_number(x*100 if x else x, is_percentage=True))
            result_display['Dividend_Yield'] = result_display['Dividend_Yield'].apply(lambda x: format_number(x*100 if x else x, is_percentage=True))
            result_display['Market_Cap'] = result_display['Market_Cap'].apply(lambda x: format_number(x, is_currency=True))
            
            st.dataframe(result_display, use_container_width=True, height=500)
        else:
            st.warning("No se encontraron acciones que cumplan los criterios seleccionados")
    
    # TAB 5: TOP RENTABILIDAD - NUEVA PESTAÑA
    with tab5:
        st.subheader("🚀 Top 20 Acciones - Mayor Rentabilidad Esperada")
        
        # Descripción de la pestaña
        with st.expander("ℹ️ ¿Cómo se Calcula la Rentabilidad Esperada?", expanded=False):
            st.markdown("""
            ### 🚀 **Rentabilidad Esperada - Metodología y Cálculos**
            
            **📊 Rentabilidad Total Esperada:**
            - **Qué es:** Estimación del retorno total en el próximo año
            - **Componentes:** Dividendos Esperados + Apreciación de Precio Esperada
            - **Fórmula:** Expected Total Return = Expected Dividend Yield + Expected Price Appreciation
            
            **💰 Dividendos Esperados (Expected Dividend Yield):**
            - **Cálculo Base:** Dividend Yield actual × Factor de Crecimiento
            - **Factor de Crecimiento:** Basado en ROE, Payout Ratio y crecimiento histórico
            - **Límites:** Máximo 12% para evitar proyecciones irrealistas
            - **Consideraciones:** Empresas con Payout Ratio >80% tienen menor crecimiento esperado
            
            **📈 Apreciación de Precio Esperada (Expected Price Appreciation):**
            - **Metodología:** Basada en Score de Calidad Fundamental
            - **Score de Calidad:** Promedio ponderado de 5 componentes:
              - 🏆 **ROE Score** (30%): Return on Equity normalizado
              - 📊 **P/E Score** (25%): Valoración (P/E más bajo = mejor score)
              - 💰 **Profit Margin Score** (20%): Eficiencia operativa
              - ⚖️ **Debt Score** (15%): Solidez financiera (menos deuda = mejor)
              - 📈 **Growth Score** (10%): Crecimiento del precio histórico
            
            **🎯 Score de Calidad (0-10 puntos):**
            - **Cálculo:** (ROE×0.3 + P/E×0.25 + Margin×0.2 + Debt×0.15 + Growth×0.1)
            - **Interpretación:**
              - 8-10: Excelente calidad (alta apreciación esperada)
              - 6-8: Buena calidad (apreciación moderada)
              - 4-6: Calidad regular (apreciación baja)
              - <4: Baja calidad (poca apreciación)
            
            **📐 Fórmula de Apreciación:**
            - **Cálculo:** (Total Score ÷ 10) × 15% máximo
            - **Límite:** Máximo 15% de apreciación para mantener realismo
            - **Ejemplo:** Score 8.0 → (8.0÷10) × 15% = 12% de apreciación esperada
            
            ### 🔍 **Componentes del Score Explicados:**
            
            **🏆 ROE Score:** ROE ÷ 30% (máximo 10 puntos)
            **📊 P/E Score:** 10 - (P/E ÷ 4) (P/E menor = score mayor)
            **💰 Profit Margin Score:** Profit Margin ÷ 30% (máximo 10 puntos)  
            **⚖️ Debt Score:** 10 - (Debt/Equity × 5) (menos deuda = mejor score)
            **📈 Growth Score:** Price Change 1Y ÷ 100% × 10 (crecimiento pasado)
            
            ### ⚠️ **Limitaciones y Consideraciones:**
            - Los cálculos son **estimaciones** basadas en datos históricos
            - No garantizan rentabilidades futuras
            - Factores externos (crisis, cambios regulatorios) no están contemplados
            - Recomendado para análisis comparativo, no como garantía de retorno
            - Diversificación sigue siendo clave en cualquier cartera
            """)
        
        st.markdown("---")
        
        # Calcular rentabilidad esperada
        all_stocks_analyzed = analyzer.calculate_total_expected_return(all_stocks)
        
        # Obtener top 20
        top_profitable = analyzer.get_top_profitable_stocks(all_stocks_analyzed, 20)
        
        if len(top_profitable) > 0:
            # Métricas de rentabilidad
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_expected_return = top_profitable['Expected_Total_Return'].mean()
                st.metric("🎯 Rentabilidad Esperada Promedio", f"{avg_expected_return:.2f}%")
            
            with col2:
                max_expected_return = top_profitable['Expected_Total_Return'].max()
                best_stock = top_profitable[top_profitable['Expected_Total_Return'] == max_expected_return]['Symbol'].iloc[0]
                st.metric("🏆 Mejor Rentabilidad Esperada", f"{max_expected_return:.2f}%")
                st.caption(f"Acción: {best_stock}")
            
            with col3:
                avg_dividend_expected = top_profitable['Expected_Dividend_Yield'].mean()
                st.metric("💰 Dividendo Esperado Promedio", f"{avg_dividend_expected:.2f}%")
            
            with col4:
                avg_appreciation = top_profitable['Expected_Price_Appreciation'].mean()
                st.metric("📈 Apreciación Esperada Promedio", f"{avg_appreciation:.2f}%")
            
            # Gráfico principal de rentabilidad esperada
            st.subheader("📊 Ranking de Rentabilidad Esperada")
            
            fig_profitability = px.bar(
                top_profitable.head(20),
                x='Expected_Total_Return',
                y='Name',
                orientation='h',
                title="Top 20 - Mayor Rentabilidad Esperada (Dividendos + Apreciación)",
                color='Market',
                text='Symbol',
                height=800
            )
            
            fig_profitability.update_traces(textposition='inside', textfont_size=18)
            fig_profitability.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                font=dict(size=14),
                xaxis_title="Rentabilidad Esperada (%)",
                yaxis_title="Empresa"
            )
            
            st.plotly_chart(fig_profitability, use_container_width=True)
            
            # Desglose de componentes
            st.subheader("🔍 Desglose de Rentabilidad")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de componentes de rentabilidad
                fig_components = go.Figure()
                
                fig_components.add_trace(go.Bar(
                    name='Dividendos Esperados',
                    x=top_profitable['Name'].head(10),
                    y=top_profitable['Expected_Dividend_Yield'].head(10),
                    text=top_profitable['Expected_Dividend_Yield'].head(10).round(2),
                    textposition='inside'
                ))
                
                fig_components.add_trace(go.Bar(
                    name='Apreciación Esperada',
                    x=top_profitable['Name'].head(10),
                    y=top_profitable['Expected_Price_Appreciation'].head(10),
                    text=top_profitable['Expected_Price_Appreciation'].head(10).round(2),
                    textposition='inside'
                ))
                
                fig_components.update_layout(
                    title='Top 10 - Desglose Dividendos vs Apreciación (%)',
                    barmode='stack',
                    xaxis_tickangle=-45,
                    height=500,
                    font=dict(size=14)
                )
                
                st.plotly_chart(fig_components, use_container_width=True)
            
            with col2:
                # Scatter plot Score Total vs Rentabilidad Esperada
                fig_score_vs_return = px.scatter(
                    top_profitable.head(15),
                    x='Total_Score',
                    y='Expected_Total_Return',
                    size='Market_Cap',
                    color='Market',
                    hover_name='Name',
                    title='Score Total vs Rentabilidad Esperada',
                    height=500
                )
                
                fig_score_vs_return.update_layout(font=dict(size=14))
                st.plotly_chart(fig_score_vs_return, use_container_width=True)
            
            # Resumen por mercado
            st.subheader("🌍 Resumen por Mercado")
            
            profitability_summary = analyzer.create_profitability_summary(all_stocks_analyzed)
            
            summary_data = []
            for market, stats in profitability_summary.items():
                summary_data.append({
                    'Mercado': market,
                    'Rentabilidad Esperada Promedio (%)': f"{stats['avg_expected_return']:.2f}",
                    'Dividendo Esperado Promedio (%)': f"{stats['avg_dividend_yield']:.2f}",
                    'Score Promedio': f"{stats['avg_score']:.2f}",
                    'Mejor Acción': stats['top_stock']
                })
            
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True, height=300)
            
            # Tabla detallada del Top 20
            st.subheader("📋 Tabla Detallada - Top 20 Rentabilidad")
            
            # Columnas para mostrar en la tabla
            detail_columns = [
                'Symbol', 'Name', 'Market', 'Price', 'Expected_Total_Return',
                'Expected_Dividend_Yield', 'Expected_Price_Appreciation', 
                'Total_Score', 'PE_Ratio', 'ROE', 'Dividend_Yield'
            ]
            
            detail_df = top_profitable[detail_columns].copy()
            
            # Formatear columnas
            detail_df['Price'] = detail_df['Price'].apply(lambda x: format_number(x, is_currency=True))
            detail_df['Expected_Total_Return'] = detail_df['Expected_Total_Return'].apply(lambda x: f"{x:.2f}%")
            detail_df['Expected_Dividend_Yield'] = detail_df['Expected_Dividend_Yield'].apply(lambda x: f"{x:.2f}%")
            detail_df['Expected_Price_Appreciation'] = detail_df['Expected_Price_Appreciation'].apply(lambda x: f"{x:.2f}%")
            detail_df['Total_Score'] = detail_df['Total_Score'].apply(lambda x: f"{x:.2f}")
            detail_df['PE_Ratio'] = detail_df['PE_Ratio'].apply(lambda x: format_number(x))
            detail_df['ROE'] = detail_df['ROE'].apply(lambda x: format_number(x*100 if x else x, is_percentage=True))
            detail_df['Dividend_Yield'] = detail_df['Dividend_Yield'].apply(lambda x: format_number(x*100 if x else x, is_percentage=True))
            
            st.dataframe(detail_df, use_container_width=True, height=500)
            
        else:
            st.warning("No se pudieron calcular datos de rentabilidad esperada")
    
    # TAB 6: Datos Completos (código original con mejoras)
    with tab6:
        st.subheader("📋 Tabla Completa de Datos")
        
        # Descripción de la pestaña
        with st.expander("ℹ️ ¿Qué Contiene la Tabla Completa de Datos?", expanded=False):
            st.markdown("""
            ### 📋 **Tabla Completa de Datos - Todas las Métricas Disponibles**
            
            **🎯 Propósito de esta Pestaña:**
            Esta sección permite acceder a **todos los datos** de las acciones analizadas de forma customizable y exportable.
            
            **📊 Datos de Identificación:**
            - **Symbol:** Ticker o símbolo bursátil (ej: AAPL, GOOGL, SAN)
            - **Name:** Nombre completo de la empresa
            - **Market:** Mercado donde cotiza (IBEX 35, Medium Cap España, S&P 500, NASDAQ)
            
            **💰 Datos de Precio y Valoración:**
            - **Price:** Precio actual de la acción
            - **Market_Cap:** Capitalización de mercado (precio × acciones en circulación)
            - **PE_Ratio:** Price-to-Earnings (precio/beneficios)
            - **PB_Ratio:** Price-to-Book (precio/valor contable)
            - **Enterprise_Value:** Valor de la empresa (Market Cap + Deuda - Efectivo)
            
            **📈 Métricas de Rentabilidad:**
            - **ROE:** Return on Equity (rentabilidad sobre patrimonio)
            - **ROA:** Return on Assets (rentabilidad sobre activos)
            - **Profit_Margin:** Margen de beneficio neto
            - **Operating_Margin:** Margen operativo
            - **Gross_Margin:** Margen bruto
            
            **💵 Datos de Dividendos:**
            - **Dividend_Yield:** Rentabilidad por dividendo (%)
            - **Dividend_Rate:** Cantidad anual de dividendo por acción
            - **Payout_Ratio:** Porcentaje de beneficios destinado a dividendos
            - **Ex_Dividend_Date:** Fecha límite para tener derecho al dividendo
            
            **⚖️ Métricas de Solidez Financiera:**
            - **Debt_Equity:** Ratio deuda/patrimonio
            - **Current_Ratio:** Ratio de liquidez corriente
            - **Quick_Ratio:** Ratio de liquidez rápida (acid test)
            - **Cash_Per_Share:** Efectivo por acción
            
            **📊 Métricas de Crecimiento:**
            - **Revenue_Growth:** Crecimiento de ingresos
            - **Earnings_Growth:** Crecimiento de beneficios
            - **Price_Change_1Y:** Cambio de precio en 1 año
            - **Price_Change_YTD:** Cambio de precio año actual
            
            **🎲 Métricas de Riesgo:**
            - **Beta:** Volatilidad respecto al mercado
            - **52_Week_High:** Máximo precio en 52 semanas
            - **52_Week_Low:** Mínimo precio en 52 semanas
            - **Average_Volume:** Volumen promedio de transacciones
            
            **🚀 Métricas de Rentabilidad Esperada (si calculadas):**
            - **Expected_Total_Return:** Rentabilidad total esperada
            - **Expected_Dividend_Yield:** Dividendo esperado
            - **Expected_Price_Appreciation:** Apreciación de precio esperada
            - **Total_Score:** Score de calidad fundamental
            
            ### 🛠️ **Funcionalidades de la Tabla:**
            
            **🔍 Filtrado por Mercado:**
            - Puedes filtrar para ver solo acciones de un mercado específico
            - "Todos" muestra todas las acciones de todos los mercados
            
            **📋 Selección de Columnas:**
            - Elige exactamente qué métricas quieres ver
            - Útil para análisis específicos o reportes customizados
            
            **📊 Control de Filas:**
            - Limita el número de acciones mostradas
            - Útil para focalizar el análisis en subconjuntos
            
            **📥 Exportación de Datos:**
            - Descarga los datos filtrados en formato CSV
            - Perfecto para análisis adicional en Excel o otras herramientas
            - El archivo incluye timestamp para organización
            
            ### 💡 **Casos de Uso Sugeridos:**
            - **Análisis Sectorial:** Filtrar por mercado y exportar datos específicos
            - **Screening Personalizado:** Seleccionar métricas clave para tu estrategia
            - **Reportes de Cartera:** Exportar datos de acciones específicas
            - **Análisis Cuantitativo:** Descargar dataset completo para análisis estadístico
            """)
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            show_market = st.selectbox("Filtrar por mercado:", ["Todos"] + list(markets_data.keys()), key="table_market")
        
        with col2:
            columns_to_show = st.multiselect(
                "Columnas a mostrar:",
                all_stocks.columns.tolist(),
                default=['Symbol', 'Name', 'Market', 'Price', 'Market_Cap', 'PE_Ratio', 'Dividend_Yield', 'ROE']
            )
        
        with col3:
            max_rows = st.slider("Máximo filas:", 10, len(all_stocks), min(100, len(all_stocks)))
        
        # Filtrar datos
        if show_market == "Todos":
            table_data = all_stocks
        else:
            table_data = markets_data[show_market]
        
        # Mostrar tabla más grande
        if columns_to_show:
            display_table = table_data[columns_to_show].head(max_rows)
            st.dataframe(display_table, use_container_width=True, height=500)
            
            # Botón de descarga
            csv = display_table.to_csv(index=False)
            st.download_button(
                label="📥 Descargar CSV",
                data=csv,
                file_name=f"acciones_{show_market}_{time.strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("Selecciona al menos una columna para mostrar")
    
    # Footer
    st.markdown("---")
    st.markdown("**Fuente de datos:** Yahoo Finance | **Actualización:** Tiempo real")
    st.markdown("⚠️ *Los datos pueden tener un retraso de 15-20 minutos*")

if __name__ == "__main__":
    main()