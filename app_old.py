#!/usr/bin/env python3
"""
Aplicación Streamlit para el Analizador de Acciones por Mercado
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

# CSS personalizado
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
</style>
""", unsafe_allow_html=True)

def load_market_data(force_refresh=False):
    """Carga los datos usando StockAnalyzer unificado con persistencia"""
    analyzer = StockAnalyzer(cache_hours=24)  # Cache por 24 horas
    
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
    
    # Agrupar por mercado y calcular promedio
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
        text=metric
    )
    
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig.update_layout(showlegend=False, height=400)
    
    return fig

def create_top_stocks_chart(data, metric, title, top_n=10):
    """Crea gráfico de top acciones por métrica"""
    if metric not in data.columns:
        return None
    
    # Filtrar y ordenar
    filtered_data = data[data[metric].notna()]
    if filtered_data.empty:
        return None
    
    # Determinar si mayor es mejor
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
        height=500
    )
    
    fig.update_traces(textposition='inside')
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    
    return fig

def create_scatter_plot(data, x_metric, y_metric, title):
    """Crea gráfico de dispersión"""
    if x_metric not in data.columns or y_metric not in data.columns:
        return None
    
    # Filtrar datos válidos
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
        height=500
    )
    
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
            analyzer, markets_data, all_stocks, data_manager = load_market_data(force_refresh)
            
            st.session_state.analyzer = analyzer
            st.session_state.markets_data = markets_data
            st.session_state.all_stocks = all_stocks
            st.session_state.data_manager = data_manager
            st.session_state.data_loaded = True
            
            st.sidebar.success("✅ Datos cargados exitosamente!")
            
        except Exception as e:
            st.sidebar.error(f"❌ Error al cargar datos: {str(e)}")
            return
    
    # Información del cache (si está disponible)
    if st.session_state.data_loaded and 'data_manager' in st.session_state:
        cache_info = st.session_state.data_manager.get_cache_info()
        
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
            st.session_state.data_manager.clear_cache()
            st.sidebar.success("✅ Cache limpiado")
    
    if not st.session_state.data_loaded:
        st.info("👆 Haz clic en 'Cargar/Actualizar Datos' en la barra lateral para comenzar")
        return
    
    # Datos cargados
    markets_data = st.session_state.markets_data
    all_stocks = st.session_state.all_stocks
    
    # Resumen rápido
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
    
    # Pestañas principales
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏢 Por Mercado", 
        "📊 Análisis Fundamental", 
        "💰 Dividendos", 
        "🎯 Filtros Avanzados",
        "📋 Datos Completos"
    ])
    
    # TAB 1: Por Mercado
    with tab1:
        st.subheader("📈 Análisis por Mercado")
        
        # Selector de mercado
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
            # Top 10 por capitalización
            top_cap = display_data.nlargest(10, 'Market_Cap')
            if not top_cap.empty:
                fig_cap = px.bar(
                    top_cap, 
                    x='Market_Cap', 
                    y='Name',
                    orientation='h',
                    title="Top 10 - Mayor Capitalización de Mercado",
                    text='Symbol'
                )
                fig_cap.update_traces(textposition='inside')
                st.plotly_chart(fig_cap, use_container_width=True)
        
        with col2:
            # Distribución por mercado
            if selected_market == "Todos":
                market_counts = all_stocks['Market'].value_counts()
                fig_pie = px.pie(
                    values=market_counts.values,
                    names=market_counts.index,
                    title="Distribución de Acciones por Mercado"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
        
        # Tabla de datos
        st.subheader("📋 Datos del Mercado")
        
        # Columnas para mostrar
        display_columns = [
            'Symbol', 'Name', 'Price', 'Market_Cap', 'PE_Ratio', 
            'Dividend_Yield', 'ROE', 'Price_Change_1Y', 'Beta'
        ]
        
        # Formatear datos para mostrar
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
        
        st.dataframe(display_df, use_container_width=True)
    
    # TAB 2: Análisis Fundamental
    with tab2:
        st.subheader("📊 Análisis Fundamental")
        
        # Selectores
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
        
        # Filtrar acciones con dividendos
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
            # Top dividendos
            top_div = filtered_div.nlargest(15, 'Dividend_Yield')
            if not top_div.empty:
                fig_div = px.bar(
                    top_div,
                    x='Dividend_Yield',
                    y='Name',
                    orientation='h',
                    title="Top 15 - Mayores Dividendos",
                    text='Symbol',
                    color='Market'
                )
                fig_div.update_traces(textposition='inside')
                st.plotly_chart(fig_div, use_container_width=True)
        
        with col2:
            # Dividendos vs P/E
            fig_div_pe = create_scatter_plot(
                filtered_div, 'PE_Ratio', 'Dividend_Yield', 
                "Dividend Yield vs P/E Ratio"
            )
            if fig_div_pe:
                st.plotly_chart(fig_div_pe, use_container_width=True)
        
        # Tabla de dividendos
        st.subheader("📋 Acciones con Mejores Dividendos")
        div_columns = ['Symbol', 'Name', 'Market', 'Price', 'Dividend_Yield', 'Dividend_Rate', 'Payout_Ratio', 'PE_Ratio']
        div_display = filtered_div[div_columns].copy()
        
        # Formatear
        div_display['Price'] = div_display['Price'].apply(lambda x: format_number(x, is_currency=True))
        div_display['Dividend_Yield'] = div_display['Dividend_Yield'].apply(lambda x: format_number(x*100, is_percentage=True))
        div_display['Dividend_Rate'] = div_display['Dividend_Rate'].apply(lambda x: format_number(x, is_currency=True))
        div_display['Payout_Ratio'] = div_display['Payout_Ratio'].apply(lambda x: format_number(x*100 if x else x, is_percentage=True))
        div_display['PE_Ratio'] = div_display['PE_Ratio'].apply(lambda x: format_number(x))
        
        st.dataframe(div_display.head(20), use_container_width=True)
    
    # TAB 4: Filtros Avanzados
    with tab4:
        st.subheader("🎯 Filtros Avanzados")
        
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
                    text='Symbol'
                )
                fig_results.update_traces(textposition='outside')
                fig_results.update_xaxes(tickangle=45)
                st.plotly_chart(fig_results, use_container_width=True)
            
            # Tabla de resultados
            result_columns = ['Symbol', 'Name', 'Market', 'Price', 'PE_Ratio', 'ROE', 'Dividend_Yield', 'Market_Cap']
            result_display = filtered_data[result_columns].copy()
            
            # Formatear
            result_display['Price'] = result_display['Price'].apply(lambda x: format_number(x, is_currency=True))
            result_display['PE_Ratio'] = result_display['PE_Ratio'].apply(lambda x: format_number(x))
            result_display['ROE'] = result_display['ROE'].apply(lambda x: format_number(x*100 if x else x, is_percentage=True))
            result_display['Dividend_Yield'] = result_display['Dividend_Yield'].apply(lambda x: format_number(x*100 if x else x, is_percentage=True))
            result_display['Market_Cap'] = result_display['Market_Cap'].apply(lambda x: format_number(x, is_currency=True))
            
            st.dataframe(result_display, use_container_width=True)
        else:
            st.warning("No se encontraron acciones que cumplan los criterios seleccionados")
    
    # TAB 5: Datos Completos
    with tab5:
        st.subheader("📋 Tabla Completa de Datos")
        
        # Opciones de visualización
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
        
        # Mostrar tabla
        if columns_to_show:
            display_table = table_data[columns_to_show].head(max_rows)
            st.dataframe(display_table, use_container_width=True)
            
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