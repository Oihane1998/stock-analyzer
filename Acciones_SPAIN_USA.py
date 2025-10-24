"""
Sistema de Análisis Multi-Mercado con Base de Datos SQLite
IBEX 35 + NASDAQ Top 25 + S&P 500 Top 25 + Medium Cap España
Ejecutar: streamlit run Acciones_SPAIN_USA.py
Versión: 9.1 - Portable con rutas relativas
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
import sqlite3
import os
from pathlib import Path
warnings.filterwarnings('ignore')


# PARA MOVILES

st.set_page_config(
    page_title="Análisis Multi-Mercado",
    layout="wide",  # Ya lo tienes
    initial_sidebar_state="collapsed"  # Oculta sidebar en móvil por defecto
)

# Detectar si es móvil
if st.sidebar.checkbox("Vista compacta (móvil)", value=False):
    # Ajustar tamaño de gráficos
    fig_height = 300
    show_full_table = False
else:
    fig_height = 600
    show_full_table = True





# ============================================================================
# CONFIGURACIÓN DE RUTAS (PORTABLE)
# ============================================================================

# Obtener la ruta del directorio donde está este script
SCRIPT_DIR = Path(__file__).parent.absolute()

# Definir la ruta de la carpeta 'dat' relativa al script
DAT_DIR = SCRIPT_DIR / "dat"

# Crear la carpeta 'dat' si no existe
DAT_DIR.mkdir(exist_ok=True)

def get_db_path(db_name):
    """Retorna la ruta completa a la base de datos en la carpeta dat"""
    return str(DAT_DIR / db_name)



# ============================================================================
# CONFIGURACIÓN MULTI-MERCADO
# ============================================================================

# IBEX 35 (35 empresas)
IBEX35_SYMBOLS = {
    "ITX.MC": "Inditex",
    "IBE.MC": "Iberdrola", 
    "SAN.MC": "Banco Santander",
    "BBVA.MC": "BBVA",
    "TEF.MC": "Telefónica",
    "REP.MC": "Repsol",
    "CABK.MC": "CaixaBank",
    "ENG.MC": "Enagás",
    "FER.MC": "Ferrovial",
    "ACS.MC": "ACS",
    "AENA.MC": "Aena",
    "AMS.MC": "Amadeus",
    "ANA.MC": "Acciona",
    "CLNX.MC": "Cellnex",
    "IAG.MC": "IAG",
    "GRF.MC": "Grifols",
    "MAP.MC": "Mapfre",
    "MEL.MC": "Meliá Hotels",
    "MRL.MC": "Merlin Properties",
    "RED.MC": "Redeia",
    "SAB.MC": "Banco Sabadell",
    "SCYR.MC": "Sacyr",
    "SGRE.MC": "Siemens Gamesa",
    "UNI.MC": "Unicaja",
    "ACX.MC": "Acerinox",
    "BKT.MC": "Bankinter",
    "COL.MC": "Inmobiliaria Colonial",
    "FDR.MC": "Fluidra",
    "IDR.MC": "Indra",
    "LOG.MC": "Logista",
    "NTGY.MC": "Naturgy",
    "PHM.MC": "PharmaMar",
    "REN.MC": "Talgo",
    "SLR.MC": "Solaria",
    "VIS.MC": "Viscofan"
}

# NASDAQ Top 25 (por capitalización)
NASDAQ_TOP25 = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "NVDA": "NVIDIA",
    "GOOGL": "Alphabet (Google)",
    "AMZN": "Amazon",
    "META": "Meta Platforms",
    "TSLA": "Tesla",
    "AVGO": "Broadcom",
    "COST": "Costco",
    "NFLX": "Netflix",
    "AMD": "AMD",
    "ADBE": "Adobe",
    "CSCO": "Cisco",
    "INTC": "Intel",
    "CMCSA": "Comcast",
    "PEP": "PepsiCo",
    "QCOM": "Qualcomm",
    "TXN": "Texas Instruments",
    "INTU": "Intuit",
    "AMGN": "Amgen",
    "AMAT": "Applied Materials",
    "ISRG": "Intuitive Surgical",
    "BKNG": "Booking Holdings",
    "HON": "Honeywell",
    "VRTX": "Vertex Pharmaceuticals"
}

# S&P 500 Top 25 (por capitalización)
SP500_TOP25 = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "NVDA": "NVIDIA",
    "GOOGL": "Alphabet",
    "AMZN": "Amazon",
    "META": "Meta Platforms",
    "BRK-B": "Berkshire Hathaway",
    "TSLA": "Tesla",
    "LLY": "Eli Lilly",
    "V": "Visa",
    "UNH": "UnitedHealth",
    "XOM": "Exxon Mobil",
    "MA": "Mastercard",
    "JNJ": "Johnson & Johnson",
    "PG": "Procter & Gamble",
    "AVGO": "Broadcom",
    "JPM": "JPMorgan Chase",
    "HD": "Home Depot",
    "CVX": "Chevron",
    "ABBV": "AbbVie",
    "MRK": "Merck",
    "COST": "Costco",
    "KO": "Coca-Cola",
    "ORCL": "Oracle",
    "WMT": "Walmart"
}

# España Continuo - 25 empresas de MAYOR capitalización NO incluidas en IBEX 35
SPAIN_MEDIUMCAP = {
    "ELE.MC": "Endesa",
    "EBRO.MC": "Ebro Foods",
    "GCO.MC": "Gestamp",
    "ALM.MC": "Almirall",
    "VID.MC": "Vidrala",
    "CIE.MC": "CIE Automotive",
    "TRE.MC": "Técnicas Reunidas",
    "CAF.MC": "CAF",
    "FCC.MC": "FCC",
    "PSG.MC": "Prosegur Cash",
    "ENC.MC": "Ence",
    "NHH.MC": "NH Hotel Group",
    "APAM.MC": "Applus",
    "TUB.MC": "Tubacex",
    "FAE.MC": "Faes Farma",
    "ZOT.MC": "Zardoya Otis",
    "NXT.MC": "Neinor Homes",
    "MVC.MC": "Miquel y Costas",
    "ACS.MC": "Construcciones ACS",
    "DIA.MC": "DIA",
    "PRISA.MC": "Prisa",
    "BME.MC": "BME",
    "OHL.MC": "OHL",
    "AZK.MC": "Azkoyen",
    "LGT.MC": "Lingotes Especiales"
}

# Mapeo de mercados con sus bases de datos
MERCADOS = {
    "IBEX 35": {
        "symbols": IBEX35_SYMBOLS,
        "db_name": "Ibex35.db"
    },
    "NASDAQ Top 25": {
        "symbols": NASDAQ_TOP25,
        "db_name": "NDX25.db"
    },
    "S&P 500 Top 25": {
        "symbols": SP500_TOP25,
        "db_name": "SP500_25.db"
    },
    "España Medium Cap": {
        "symbols": SPAIN_MEDIUMCAP,
        "db_name": "SP_CONTINUO.db"
    }
}

# Sectores por mercado
SECTORES_IBEX = {
    "ITX.MC": "Retail", "FER.MC": "Construcción", "ACS.MC": "Construcción",
    "IBE.MC": "Utilities", "ENG.MC": "Utilities", "RED.MC": "Utilities", "NTGY.MC": "Utilities",
    "SAN.MC": "Banca", "BBVA.MC": "Banca", "CABK.MC": "Banca", "SAB.MC": "Banca", 
    "BKT.MC": "Banca", "UNI.MC": "Banca",
    "TEF.MC": "Telecomunicaciones", "CLNX.MC": "Telecomunicaciones",
    "REP.MC": "Energía", "SLR.MC": "Energía", "ANA.MC": "Energía",
    "AENA.MC": "Transporte", "IAG.MC": "Transporte", "REN.MC": "Transporte",
    "AMS.MC": "Tecnología", "IDR.MC": "Tecnología",
    "GRF.MC": "Farmacia", "PHM.MC": "Farmacia",
    "MAP.MC": "Seguros", "MEL.MC": "Turismo",
    "MRL.MC": "Inmobiliario", "COL.MC": "Inmobiliario",
    "SCYR.MC": "Construcción", "SGRE.MC": "Industrial",
    "ACX.MC": "Industrial", "FDR.MC": "Industrial", "VIS.MC": "Industrial",
    "LOG.MC": "Logística", 
    # España Continuo (NO IBEX 35) - Mayor capitalización
    "ELE.MC": "Utilities", "EBRO.MC": "Alimentación", "GCO.MC": "Automoción",
    "ALM.MC": "Farmacia", "VID.MC": "Industrial", "CIE.MC": "Automoción", 
    "TRE.MC": "Construcción", "CAF.MC": "Industrial", "FCC.MC": "Construcción",
    "PSG.MC": "Servicios", "ENC.MC": "Utilities", "NHH.MC": "Turismo", 
    "APAM.MC": "Servicios", "TUB.MC": "Industrial", "FAE.MC": "Farmacia", 
    "ZOT.MC": "Industrial", "NXT.MC": "Inmobiliario", "MVC.MC": "Industrial",
    "DIA.MC": "Retail", "PRISA.MC": "Media", "BME.MC": "Financiero",
    "OHL.MC": "Construcción", "AZK.MC": "Industrial", "LGT.MC": "Industrial"
}

SECTORES_NASDAQ = {
    "AAPL": "Technology", "MSFT": "Technology", "NVDA": "Technology",
    "GOOGL": "Technology", "AMZN": "Consumer", "META": "Technology",
    "TSLA": "Automotive", "AVGO": "Technology", "COST": "Retail",
    "NFLX": "Media", "AMD": "Technology", "ADBE": "Technology",
    "CSCO": "Technology", "INTC": "Technology", "CMCSA": "Media",
    "PEP": "Consumer", "QCOM": "Technology", "TXN": "Technology",
    "INTU": "Technology", "AMGN": "Healthcare", "AMAT": "Technology",
    "ISRG": "Healthcare", "BKNG": "Travel", "HON": "Industrial",
    "VRTX": "Healthcare"
}

SECTORES_SP500 = {
    "AAPL": "Technology", "MSFT": "Technology", "NVDA": "Technology",
    "GOOGL": "Technology", "AMZN": "Consumer", "META": "Technology",
    "BRK-B": "Financial", "TSLA": "Automotive", "LLY": "Healthcare",
    "V": "Financial", "UNH": "Healthcare", "XOM": "Energy",
    "MA": "Financial", "JNJ": "Healthcare", "PG": "Consumer",
    "AVGO": "Technology", "JPM": "Financial", "HD": "Retail",
    "CVX": "Energy", "ABBV": "Healthcare", "MRK": "Healthcare",
    "COST": "Retail", "KO": "Consumer", "ORCL": "Technology",
    "WMT": "Retail"
}

def obtener_sectores(mercado):
    """Retorna el diccionario de sectores según el mercado"""
    if mercado == "IBEX 35" or mercado == "España Medium Cap":
        return SECTORES_IBEX
    elif mercado == "NASDAQ Top 25":
        return SECTORES_NASDAQ
    elif mercado == "S&P 500 Top 25":
        return SECTORES_SP500
    return {}


# ============================================================================
# SCORE PROPIETARIO MEJORADO v2.0
# ============================================================================

def calcular_score_mejorado(datos_corregidos, sector=""):
    """
    Score Propietario Mejorado v2.0
    Rango: 0-100 puntos
    """
    
    score = 0
    
    # 1. RENTABILIDAD ESPERADA (35 puntos máximo)
    upside = datos_corregidos.get('Upside_%', 0)
    if upside >= 25:
        score += 20
    elif upside >= 20:
        score += 18
    elif upside >= 15:
        score += 15
    elif upside >= 10:
        score += 12
    elif upside >= 5:
        score += 8
    elif upside >= 0:
        score += 4
    elif upside >= -5:
        score += 2
    
    div_yield = datos_corregidos.get('Dividend_Yield', 0)
    if div_yield >= 7:
        score += 15
    elif div_yield >= 5:
        score += 13
    elif div_yield >= 4:
        score += 11
    elif div_yield >= 3:
        score += 8
    elif div_yield >= 2:
        score += 5
    elif div_yield >= 1:
        score += 3
    
    # 2. VALORACIÓN (20 puntos máximo)
    pe = datos_corregidos.get('PE_Ratio', 15)
    if pe <= 0:
        score += 0
    elif pe < 10:
        score += 15
    elif pe < 12:
        score += 13
    elif pe < 15:
        score += 11
    elif pe < 18:
        score += 8
    elif pe < 22:
        score += 5
    elif pe < 30:
        score += 2
    
    pb = datos_corregidos.get('Price_Book', 2)
    if 0 < pb < 1:
        score += 5
    elif 1 <= pb < 2:
        score += 4
    elif 2 <= pb < 3:
        score += 3
    elif 3 <= pb < 5:
        score += 2
    
    # 3. CALIDAD FUNDAMENTAL (20 puntos máximo)
    roe = datos_corregidos.get('ROE', 10)
    if roe >= 25:
        score += 10
    elif roe >= 20:
        score += 9
    elif roe >= 15:
        score += 7
    elif roe >= 10:
        score += 5
    elif roe >= 5:
        score += 3
    elif roe >= 0:
        score += 1
    
    growth = datos_corregidos.get('Revenue_Growth', 0)
    if growth >= 20:
        score += 5
    elif growth >= 15:
        score += 4
    elif growth >= 10:
        score += 3
    elif growth >= 5:
        score += 2
    elif growth >= 0:
        score += 1
    
    roa = datos_corregidos.get('ROA', 5)
    if roa >= 15:
        score += 5
    elif roa >= 10:
        score += 4
    elif roa >= 7:
        score += 3
    elif roa >= 5:
        score += 2
    elif roa >= 2:
        score += 1
    
    # 4. CONFIANZA DEL MERCADO (15 puntos máximo)
    num_analysts = datos_corregidos.get('Num_Analysts', 0)
    if num_analysts >= 20:
        score += 10
    elif num_analysts >= 15:
        score += 9
    elif num_analysts >= 10:
        score += 7
    elif num_analysts >= 7:
        score += 5
    elif num_analysts >= 5:
        score += 3
    elif num_analysts >= 3:
        score += 1
    
    recommendation = datos_corregidos.get('Recommendation', 'N/A').lower()
    if recommendation == 'strong_buy':
        score += 5
    elif recommendation == 'buy':
        score += 4
    elif recommendation == 'hold':
        score += 2
    elif recommendation == 'sell':
        score += 0
    elif recommendation == 'strong_sell':
        score -= 5
    
    # 5. PENALIZACIONES POR RIESGO (hasta -20 puntos)
    volatilidad = datos_corregidos.get('Volatilidad', 20)
    if volatilidad > 60:
        score -= 10
    elif volatilidad > 45:
        score -= 6
    elif volatilidad > 35:
        score -= 3
    
    beta = datos_corregidos.get('Beta', 1.0)
    if beta > 2.0:
        score -= 5
    elif beta < 0.3:
        score -= 3
    
    market_cap = datos_corregidos.get('Market_Cap', 5)
    if market_cap < 0.5:
        score -= 8
    elif market_cap < 1:
        score -= 5
    elif market_cap < 2:
        score -= 2
    
    # 6. BONUS POR EXCELENCIA (hasta +10 puntos)
    if upside > 15 and pe < 15 and roe > 15:
        score += 5
    
    if div_yield > 4 and growth > 5:
        score += 3
    
    if roe > 20 and roa > 10 and pe < 20:
        score += 2
    
    # 7. AJUSTE POR SECTOR
    sector_ajustes = {
        "Technology": {"pe_tolerance": 5},
        "Healthcare": {"pe_tolerance": 3},
        "Media": {"pe_tolerance": 3},
        "Utilities": {"div_bonus": 2},
        "Banca": {"div_bonus": 2},
        "Financial": {"div_bonus": 2},
        "Seguros": {"div_bonus": 2},
        "Energy": {"vol_tolerance": 3},
        "Industrial": {"vol_tolerance": 2},
        "Construcción": {"vol_tolerance": 2},
        "Automotive": {"vol_tolerance": 2},
    }
    
    if sector in sector_ajustes:
        ajustes = sector_ajustes[sector]
        
        if "pe_tolerance" in ajustes and pe < 30:
            score += ajustes["pe_tolerance"]
        
        if "div_bonus" in ajustes and div_yield > 3:
            score += ajustes["div_bonus"]
        
        if "vol_tolerance" in ajustes and volatilidad > 35:
            score += ajustes["vol_tolerance"]
    
    score = max(0, min(100, score))
    
    return int(score)


def clasificar_score(score):
    """Clasifica el score en categorías"""
    if score >= 85:
        return "🟢🟢 EXCEPCIONAL", "Oportunidad extraordinaria - Alta convicción"
    elif score >= 75:
        return "🟢 MUY ATRACTIVA", "Excelente oportunidad - Fuerte recomendación"
    elif score >= 65:
        return "🟡 ATRACTIVA", "Buena oportunidad - Considerar"
    elif score >= 55:
        return "⚪ NEUTRAL", "Oportunidad moderada - Analizar más"
    elif score >= 45:
        return "🟠 POCO ATRACTIVA", "Oportunidad limitada - Precaución"
    elif score >= 35:
        return "🔴 NO RECOMENDADA", "Riesgos superan oportunidades"
    else:
        return "🔴🔴 EVITAR", "Alto riesgo - No invertir"


# ============================================================================
# FUNCIONES DE BASE DE DATOS SQLITE
# ============================================================================

def crear_base_datos(db_name="Ibex35.db"):
    """Crea la base de datos SQLite y las tablas necesarias"""
    conn = sqlite3.connect(get_db_path(db_name))
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS empresas (
        ticker TEXT PRIMARY KEY,
        empresa TEXT NOT NULL,
        sector TEXT NOT NULL,
        mercado TEXT NOT NULL,
        fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS datos_fundamentales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        precio_actual REAL,
        target_mean REAL,
        target_high REAL,
        target_low REAL,
        upside_pct REAL,
        dividend_yield REAL,
        total_return_pct REAL,
        pe_ratio REAL,
        pe_forward REAL,
        price_book REAL,
        roe REAL,
        roa REAL,
        revenue_growth REAL,
        market_cap REAL,
        beta REAL,
        volatilidad REAL,
        num_analysts INTEGER,
        recommendation TEXT,
        score INTEGER,
        FOREIGN KEY (ticker) REFERENCES empresas(ticker)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS historico_precios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        fecha DATE NOT NULL,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume INTEGER,
        FOREIGN KEY (ticker) REFERENCES empresas(ticker),
        UNIQUE(ticker, fecha)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alertas_validacion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        mensaje TEXT NOT NULL,
        FOREIGN KEY (ticker) REFERENCES empresas(ticker)
    )
    ''')
    
    conn.commit()
    conn.close()
    st.success(f"✅ Base de datos '{db_name}' creada correctamente en: {get_db_path(db_name)}")


def verificar_y_actualizar_estructura_bd(db_name="Ibex35.db"):
    """Verifica y actualiza la estructura de la BD si es necesario"""
    try:
        conn = sqlite3.connect(get_db_path(db_name))
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(empresas)")
        columnas = [col[1] for col in cursor.fetchall()]
        
        if 'mercado' not in columnas:
            st.warning(f"⚠️ Actualizando estructura de {db_name}...")
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS empresas_new (
                ticker TEXT PRIMARY KEY,
                empresa TEXT NOT NULL,
                sector TEXT NOT NULL,
                mercado TEXT NOT NULL DEFAULT 'IBEX 35',
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            cursor.execute('''
            INSERT INTO empresas_new (ticker, empresa, sector, mercado, fecha_actualizacion)
            SELECT ticker, empresa, sector, 
                   CASE 
                       WHEN ticker LIKE '%.MC' THEN 'IBEX 35'
                       ELSE 'IBEX 35'
                   END as mercado,
                   fecha_actualizacion
            FROM empresas
            ''')
            
            cursor.execute('DROP TABLE empresas')
            cursor.execute('ALTER TABLE empresas_new RENAME TO empresas')
            
            conn.commit()
            st.success(f"✅ Estructura de {db_name} actualizada")
        
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error actualizando estructura: {e}")
        return False


def insertar_empresa(ticker, nombre, sector, mercado, db_name="Ibex35.db"):
    """Inserta o actualiza una empresa en la base de datos"""
    conn = sqlite3.connect(get_db_path(db_name))
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT OR REPLACE INTO empresas (ticker, empresa, sector, mercado, fecha_actualizacion)
    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (ticker, nombre, sector, mercado))
    
    conn.commit()
    conn.close()


def insertar_datos_fundamentales(ticker, datos, db_name="Ibex35.db"):
    """Inserta datos fundamentales de una empresa"""
    conn = sqlite3.connect(get_db_path(db_name))
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO datos_fundamentales (
        ticker, precio_actual, target_mean, target_high, target_low,
        upside_pct, dividend_yield, total_return_pct, pe_ratio, pe_forward,
        price_book, roe, roa, revenue_growth, market_cap, beta, volatilidad,
        num_analysts, recommendation, score
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        ticker,
        datos['Precio_Actual'],
        datos['Target_Mean'],
        datos.get('Target_High', 0),
        datos.get('Target_Low', 0),
        datos['Upside_%'],
        datos['Dividend_Yield'],
        datos['Total_Return_%'],
        datos['PE_Ratio'],
        datos.get('PE_Forward', 0),
        datos.get('Price_Book', 0),
        datos['ROE'],
        datos.get('ROA', 0),
        datos.get('Revenue_Growth', 0),
        datos.get('Market_Cap', 0),
        datos.get('Beta', 1.0),
        datos.get('Volatilidad', 0),
        datos.get('Num_Analysts', 0),
        datos.get('Recommendation', 'N/A'),
        datos['Score']
    ))
    
    conn.commit()
    conn.close()


def insertar_historico_precios(ticker, hist_df, db_name="Ibex35.db"):
    """Inserta el histórico de precios de una empresa"""
    if hist_df.empty:
        return
    
    conn = sqlite3.connect(get_db_path(db_name))
    cursor = conn.cursor()
    
    for index, row in hist_df.iterrows():
        try:
            cursor.execute('''
            INSERT OR REPLACE INTO historico_precios (ticker, fecha, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                ticker,
                index.strftime('%Y-%m-%d'),
                float(row['Open']),
                float(row['High']),
                float(row['Low']),
                float(row['Close']),
                int(row['Volume'])
            ))
        except:
            continue
    
    conn.commit()
    conn.close()


def insertar_alerta(ticker, mensaje, db_name="Ibex35.db"):
    """Inserta una alerta de validación"""
    conn = sqlite3.connect(get_db_path(db_name))
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO alertas_validacion (ticker, mensaje)
    VALUES (?, ?)
    ''', (ticker, mensaje))
    
    conn.commit()
    conn.close()


def cargar_datos_desde_bd(mercado=None, db_name="Ibex35.db"):
    """Carga todos los datos desde la base de datos"""
    try:
        conn = sqlite3.connect(get_db_path(db_name))
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='empresas'")
        if not cursor.fetchone():
            conn.close()
            return pd.DataFrame()
        
        query = '''
        SELECT 
            e.ticker, e.empresa, e.sector, e.mercado,
            df.precio_actual, df.target_mean, df.target_high, df.target_low,
            df.upside_pct, df.dividend_yield, df.total_return_pct,
            df.pe_ratio, df.pe_forward, df.price_book,
            df.roe, df.roa, df.revenue_growth,
            df.market_cap, df.beta, df.volatilidad,
            df.num_analysts, df.recommendation, df.score,
            df.fecha_actualizacion
        FROM empresas e
        LEFT JOIN datos_fundamentales df ON e.ticker = df.ticker
        WHERE df.id IN (
            SELECT MAX(id) FROM datos_fundamentales GROUP BY ticker
        )
        ORDER BY df.score DESC
        '''
        df = pd.read_sql_query(query, conn)
        
        conn.close()
        
        if df.empty:
            return pd.DataFrame()
        
        df.columns = [
            'Ticker', 'Empresa', 'Sector', 'Mercado', 'Precio_Actual', 'Target_Mean',
            'Target_High', 'Target_Low', 'Upside_%', 'Dividend_Yield',
            'Total_Return_%', 'PE_Ratio', 'PE_Forward', 'Price_Book',
            'ROE', 'ROA', 'Revenue_Growth', 'Market_Cap', 'Beta',
            'Volatilidad', 'Num_Analysts', 'Recommendation', 'Score',
            'Fecha_Actualizacion'
        ]
        
        return df
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return pd.DataFrame()


def cargar_historico_desde_bd(ticker, periodo_dias=365, db_name="Ibex35.db"):
    """Carga el histórico de precios de una empresa desde la BD"""
    conn = sqlite3.connect(get_db_path(db_name))
    
    fecha_inicio = (datetime.now() - timedelta(days=periodo_dias)).strftime('%Y-%m-%d')
    
    query = '''
    SELECT fecha, open, high, low, close, volume
    FROM historico_precios
    WHERE ticker = ? AND fecha >= ?
    ORDER BY fecha ASC
    '''
    
    df = pd.read_sql_query(query, conn, params=(ticker, fecha_inicio))
    conn.close()
    
    if not df.empty:
        df['fecha'] = pd.to_datetime(df['fecha'])
        df.set_index('fecha', inplace=True)
        df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    
    return df


def limpiar_datos_antiguos(db_name="Ibex35.db"):
    """Elimina datos de fundamentales antiguos, manteniendo solo los más recientes"""
    conn = sqlite3.connect(get_db_path(db_name))
    cursor = conn.cursor()
    
    cursor.execute('''
    DELETE FROM datos_fundamentales
    WHERE id NOT IN (
        SELECT MAX(id) FROM datos_fundamentales GROUP BY ticker
    )
    ''')
    
    conn.commit()
    filas_eliminadas = cursor.rowcount
    conn.close()
    
    return filas_eliminadas


def obtener_estadisticas_bd(db_name="Ibex35.db"):
    """Obtiene estadísticas de la base de datos"""
    try:
        conn = sqlite3.connect(get_db_path(db_name))
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='empresas'")
        if not cursor.fetchone():
            conn.close()
            return {
                'num_empresas': 0,
                'num_historicos': 0,
                'ultima_actualizacion': None,
                'num_alertas': 0,
                'tablas_existen': False
            }
        
        cursor.execute('SELECT COUNT(*) FROM empresas')
        num_empresas = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM historico_precios')
        num_historicos = cursor.fetchone()[0]
        
        cursor.execute('SELECT MAX(fecha_actualizacion) FROM datos_fundamentales')
        ultima_actualizacion = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM alertas_validacion')
        num_alertas = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'num_empresas': num_empresas,
            'num_historicos': num_historicos,
            'ultima_actualizacion': ultima_actualizacion,
            'num_alertas': num_alertas,
            'tablas_existen': True
        }
    except Exception as e:
        return {
            'num_empresas': 0,
            'num_historicos': 0,
            'ultima_actualizacion': None,
            'num_alertas': 0,
            'tablas_existen': False
        }


# ============================================================================
# FUNCIONES DE VALIDACIÓN Y CORRECCIÓN
# ============================================================================

def validar_y_corregir_datos(info, ticker, hist, sector, db_name="Ibex35.db"):
    """Valida y corrige datos sospechosos de Yahoo Finance - CON SCORE MEJORADO"""
    datos_corregidos = {}
    alertas = []
    
    if not hist.empty:
        precio_actual = hist['Close'].iloc[-1]
    else:
        precio_actual = info.get('currentPrice', 0)
        if precio_actual == 0:
            precio_actual = info.get('regularMarketPrice', 0)
    
    datos_corregidos['Precio_Actual'] = precio_actual
    
    # Dividend yield
    div_yield_raw = info.get('dividendYield', 0)
    
    if 0 < div_yield_raw < 1:
        div_yield = div_yield_raw * 100
    else:
        div_yield = div_yield_raw
    
    if div_yield > 15:
        alertas.append(f"⚠️ Dividend Yield muy alto: {div_yield:.1f}%")
        div_yield = 0
        alertas.append("✅ Ajustado a 0% (verificar manualmente)")
    elif div_yield < 0:
        alertas.append(f"⚠️ Dividend Yield negativo: {div_yield:.1f}%")
        div_yield = 0
        alertas.append("✅ Ajustado a 0%")
    
    datos_corregidos['Dividend_Yield'] = div_yield
    
    target_mean = info.get('targetMeanPrice', 0)
    target_high = info.get('targetHighPrice', 0)
    target_low = info.get('targetLowPrice', 0)
    
    if target_mean > 0 and precio_actual > 0:
        upside = ((target_mean - precio_actual) / precio_actual) * 100
        
        if abs(upside) > 50:
            alertas.append(f"⚠️ Upside sospechoso: {upside:.1f}%")
            target_mean = precio_actual * 1.08
            upside = 8
            alertas.append("✅ Ajustado a +8%")
    else:
        upside = 5
        target_mean = precio_actual * 1.05 if precio_actual > 0 else 0
    
    datos_corregidos['Target_Mean'] = target_mean
    datos_corregidos['Target_High'] = target_high if target_high > 0 else target_mean * 1.15
    datos_corregidos['Target_Low'] = target_low if target_low > 0 else target_mean * 0.85
    datos_corregidos['Upside_%'] = upside
    
    pe_ratio = info.get('trailingPE', 0)
    if pe_ratio > 100 or pe_ratio < 0:
        alertas.append(f"⚠️ PE Ratio sospechoso: {pe_ratio:.1f}")
        pe_ratio = 15
    
    datos_corregidos['PE_Ratio'] = pe_ratio
    datos_corregidos['PE_Forward'] = min(info.get('forwardPE', 0), 100)
    datos_corregidos['Price_Book'] = min(info.get('priceToBook', 0), 20)
    datos_corregidos['Market_Cap'] = info.get('marketCap', 0) / 1e9
    
    roe = info.get('returnOnEquity', 0)
    if 0 < roe < 1:
        roe = roe * 100
    datos_corregidos['ROE'] = min(max(roe, -50), 100)
    
    roa = info.get('returnOnAssets', 0)
    if 0 < roa < 1:
        roa = roa * 100
    datos_corregidos['ROA'] = min(max(roa, -20), 50)
    
    datos_corregidos['Num_Analysts'] = info.get('numberOfAnalystOpinions', 0)
    datos_corregidos['Recommendation'] = info.get('recommendationKey', 'N/A')
    
    revenue_growth = info.get('revenueGrowth', 0)
    if 0 < revenue_growth < 1:
        revenue_growth = revenue_growth * 100
    datos_corregidos['Revenue_Growth'] = max(min(revenue_growth, 100), -50)
    
    datos_corregidos['Beta'] = info.get('beta', 1.0)
    datos_corregidos['Total_Return_%'] = datos_corregidos['Upside_%'] + datos_corregidos['Dividend_Yield']
    
    # Volatilidad
    if not hist.empty:
        returns = hist['Close'].pct_change().dropna()
        datos_corregidos['Volatilidad'] = returns.std() * np.sqrt(252) * 100
    else:
        datos_corregidos['Volatilidad'] = 0
    
    # ⭐ USAR SCORE MEJORADO v2.0
    datos_corregidos['Score'] = calcular_score_mejorado(datos_corregidos, sector)
    
    for alerta in alertas:
        insertar_alerta(ticker, alerta, db_name)
    
    return datos_corregidos, alertas


def obtener_datos_empresa(ticker, nombre, mercado, sectores_dict, db_name="Ibex35.db"):
    """Obtiene y valida datos de una empresa, guardándolos en la BD"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="1y")
        
        sector = sectores_dict.get(ticker, "Otros")
        datos, alertas = validar_y_corregir_datos(info, ticker, hist, sector, db_name)
        
        datos['Ticker'] = ticker
        datos['Empresa'] = nombre
        datos['Sector'] = sector
        datos['Mercado'] = mercado
        datos['Alertas'] = alertas
        
        insertar_empresa(ticker, nombre, datos['Sector'], mercado, db_name)
        insertar_datos_fundamentales(ticker, datos, db_name)
        insertar_historico_precios(ticker, hist, db_name)
        
        return datos
        
    except Exception as e:
        st.warning(f"Error con {ticker}: {e}")
        return {
            'Ticker': ticker,
            'Empresa': nombre,
            'Sector': sectores_dict.get(ticker, "Otros"),
            'Mercado': mercado,
            'Precio_Actual': 0,
            'Target_Mean': 0,
            'Upside_%': 0,
            'Dividend_Yield': 0,
            'Total_Return_%': 0,
            'PE_Ratio': 15,
            'ROE': 10,
            'Market_Cap': 0,
            'Num_Analysts': 0,
            'Recommendation': 'N/A',
            'Score': 30,
            'Volatilidad': 20,
            'Beta': 1,
            'Alertas': [f"Error obteniendo datos de {ticker}"]
        }


# ============================================================================
# CONFIGURACIÓN DE STREAMLIT
# ============================================================================

st.set_page_config(
    page_title="Análisis Multi-Mercado v2.0",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header {
        font-size: 48px;
        font-weight: bold;
        background: linear-gradient(120deg, #1976D2, #42A5F5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)


# ============================================================================
# APLICACIÓN PRINCIPAL
# ============================================================================

def main():
    st.markdown('<h1 class="main-header">Análisis Técnico y Fundamental de Acciones </h1>', 
                unsafe_allow_html=True)
    
    # SELECTOR DE MERCADO
    st.sidebar.header("🌍 Selección de Mercado")
    
    mercado_seleccionado = st.sidebar.selectbox(
        "Elige el mercado a analizar:",
        options=list(MERCADOS.keys()),
        index=0
    )
    
    mercado_info = MERCADOS[mercado_seleccionado]
    symbols_mercado = mercado_info["symbols"]
    db_name = mercado_info["db_name"]
    sectores_mercado = obtener_sectores(mercado_seleccionado)
    
    st.sidebar.info(f"📊 **{mercado_seleccionado}**\n\n{len(symbols_mercado)} empresas\n\n💾 BD: `{db_name}`\n\n⭐ **Score Mejorado v2.0**")
    
    # Verificar BD
    db_existe = os.path.exists(get_db_path(db_name))
    
    if db_existe:
        verificar_y_actualizar_estructura_bd(db_name)
        stats = obtener_estadisticas_bd(db_name)
        if not stats.get('tablas_existen', False):
            db_existe = False
    
    # Panel de control
    st.sidebar.markdown("---")
    st.sidebar.header("🗄️ Gestión Base de Datos")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button(f"🆕 Crear BD\n{db_name}"):
            crear_base_datos(db_name)
            db_existe = True
            st.rerun()
        
        if db_existe and st.button("🔧 Reparar BD"):
            if verificar_y_actualizar_estructura_bd(db_name):
                st.rerun()
    
    with col2:
        if st.button("🔄 Actualizar"):
            if db_existe:
                with st.spinner(f"Actualizando {mercado_seleccionado}..."):
                    progress_bar = st.progress(0)
                    total = len(symbols_mercado)
                    for idx, (ticker, nombre) in enumerate(symbols_mercado.items()):
                        obtener_datos_empresa(ticker, nombre, mercado_seleccionado, sectores_mercado, db_name)
                        progress_bar.progress((idx + 1) / total)
                    progress_bar.empty()
                    limpiar_datos_antiguos(db_name)
                st.success(f"✅ {mercado_seleccionado} actualizado")
                st.rerun()
            else:
                st.error("❌ Primero crea la base de datos")
    
    # Actualizar TODOS
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Actualizar TODOS los Mercados"):
        with st.spinner("Actualizando TODOS los mercados..."):
            progress_bar = st.progress(0)
            total_empresas = sum(len(m["symbols"]) for m in MERCADOS.values())
            contador = 0
            
            for mercado_nombre, mercado_data in MERCADOS.items():
                st.sidebar.write(f"📊 {mercado_nombre}...")
                symbols = mercado_data["symbols"]
                db = mercado_data["db_name"]
                sectores = obtener_sectores(mercado_nombre)
                
                if not os.path.exists(get_db_path(db)):
                    crear_base_datos(db)
                
                for ticker, nombre in symbols.items():
                    obtener_datos_empresa(ticker, nombre, mercado_nombre, sectores, db)
                    contador += 1
                    progress_bar.progress(contador / total_empresas)
                
                limpiar_datos_antiguos(db)
            
            progress_bar.empty()
        st.success("✅ ¡Todos actualizados!")
        st.rerun()
    
    # Mostrar BDs disponibles
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💾 Bases de Datos")
    for mercado, data in MERCADOS.items():
        db = data["db_name"]
        existe = "✅" if os.path.exists(get_db_path(db)) else "❌"
        if os.path.exists(get_db_path(db)):
            size_mb = os.path.getsize(get_db_path(db)) / (1024 * 1024)
            st.sidebar.text(f"{existe} {db} ({size_mb:.1f} MB)")
        else:
            st.sidebar.text(f"{existe} {db} (no existe)")
    
    if db_existe:
        stats = obtener_estadisticas_bd(db_name)
        if stats.get('tablas_existen', False):
            st.sidebar.markdown(f"""
            **📊 Estadísticas {db_name}:**
            - Empresas: {stats['num_empresas']}
            - Históricos: {stats['num_historicos']:,}
            - Última: {stats['ultima_actualizacion'][:16] if stats['ultima_actualizacion'] else 'N/A'}
            - Alertas: {stats['num_alertas']}
            """)
            
            if st.sidebar.button("🧹 Limpiar"):
                filas = limpiar_datos_antiguos(db_name)
                st.sidebar.success(f"✅ {filas} eliminadas")
    
    if not db_existe:
        st.info(f"""
        ### 👋 Bienvenido al Sistema Multi-Mercado v2.0
        
        **Mercado: {mercado_seleccionado}**
        BD: `{db_name}`
        
        **✨ NUEVO: Score Propietario Mejorado v2.0**
        - Más factores (ROE, ROA, crecimiento, P/B)
        - Penalizaciones por riesgo
        - Bonus por excelencia
        - Ajustes por sector
        
        **4 mercados:**
        - 📊 IBEX 35 → `Ibex35.db`
        - 💻 NASDAQ Top 25 → `NDX25.db`
        - 📈 S&P 500 Top 25 → `SP500_25.db`
        - 🇪🇸 España Medium Cap → `SP_CONTINUO.db`
        
        **Para empezar:**
        1. Clic en "🆕 Crear BD"
        2. Clic en "🔄 Actualizar"
        3. ¡Analiza!
        """)
        return
    
    # Cargar datos
    try:
        df = cargar_datos_desde_bd(None, db_name)
        
        if df.empty:
            st.warning(f"⚠️ Sin datos en {db_name}. Actualiza.")
            return
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return
    
    # Filtros
    st.sidebar.header("🔍 Filtros Avanzados")
    
    # Botón para resetear filtros
    col_reset1, col_reset2 = st.sidebar.columns([2, 1])
    with col_reset2:
        if st.button("🔄 Reset", help="Resetear todos los filtros para ver TODAS las acciones"):
            st.rerun()
    with col_reset1:
        st.caption("Usa filtros para refinar")
    
    if 'Sector' in df.columns:
        sectores_unicos = sorted(df['Sector'].unique().tolist())
    else:
        sectores_unicos = sorted(list(set(sectores_mercado.values())))
    
    sectores_seleccionados = st.sidebar.multiselect(
        "Sectores:",
        options=sectores_unicos,
        default=sectores_unicos
    )
    
    st.sidebar.markdown("### 📈 Filtros de Rentabilidad")
    min_upside = st.sidebar.slider("Upside mínimo (%)", -50, 50, -50, help="Ajusta a -50 para ver TODAS")
    min_dividend = st.sidebar.slider("Dividendo mínimo (%)", 0, 15, 0)
    min_total_return = st.sidebar.slider("Rentabilidad total mínima (%)", -50, 50, -50, help="Ajusta a -50 para ver TODAS")
    
    st.sidebar.markdown("### 📊 Filtros Fundamentales")
    max_pe = st.sidebar.slider("PE máximo", 0, 100, 100, help="Ajusta a 100 para ver TODAS")
    min_roe = st.sidebar.slider("ROE mínimo (%)", -50, 50, -50, help="Ajusta a -50 para ver TODAS")
    min_analysts = st.sidebar.slider("Mínimo analistas", 0, 30, 0, help="Ajusta a 0 para ver TODAS")
    
    st.sidebar.markdown("### ⚡ Otros Filtros")
    max_volatilidad = st.sidebar.slider("Volatilidad máxima (%)", 0, 150, 150, help="Ajusta a 150 para ver TODAS")
    min_market_cap = st.sidebar.slider("Market Cap mínimo (€B)", 0, 100, 0, help="Ajusta a 0 para ver TODAS")
    
    # Aplicar filtros
    df_filtrado = df[
        (df['Sector'].isin(sectores_seleccionados)) &
        (df['Upside_%'] >= min_upside) &
        (df['Dividend_Yield'] >= min_dividend) &
        (df['Total_Return_%'] >= min_total_return) &
        ((df['PE_Ratio'] <= max_pe) | (df['PE_Ratio'] == 0)) &
        (df['ROE'] >= min_roe) &
        (df['Num_Analysts'] >= min_analysts) &
        (df['Volatilidad'] <= max_volatilidad) &
        (df['Market_Cap'] >= min_market_cap)
    ]
    
    # Métricas
    st.markdown(f"## 📈 Resumen: {mercado_seleccionado}")
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("🏢 Empresas", f"{len(df_filtrado)}/{len(df)}")
    with col2:
        st.metric("🎯 Upside", f"{df_filtrado['Upside_%'].mean():.1f}%")
    with col3:
        st.metric("💰 Dividendo", f"{df_filtrado['Dividend_Yield'].mean():.1f}%")
    with col4:
        st.metric("💎 Total", f"{df_filtrado['Total_Return_%'].mean():.1f}%")
    with col5:
        st.metric("⚡ Volatilidad", f"{df_filtrado['Volatilidad'].mean():.1f}%")
    with col6:
        score_medio = df_filtrado['Score'].mean()
        categoria, _ = clasificar_score(score_medio)
        emoji = categoria.split()[0]
        st.metric(f"{emoji} Score Usuario", f"{score_medio:.0f}/100")
    
    st.markdown("---")
    
    # Tabs para diferentes vistas
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Ranking Completo",
        "🏆 Top Oportunidades", 
        "📈 Análisis por Sector",
        "💎 Matriz Estratégica",
        "📋 Tabla Detallada",
        "📉 Gráficos Técnicos",
        "📖 Diccionario"
    ])
    
    with tab1:
        st.markdown(f"### 📊 Ranking de {mercado_seleccionado} por Rentabilidad Total")
        
        df_ranking = df_filtrado.sort_values('Total_Return_%', ascending=False)
        df_ranking['Label'] = df_ranking['Ticker'] + ' - ' + df_ranking['Empresa']
        
        # Ajustar altura del gráfico según número de acciones
        # Más acciones = más altura para mejor legibilidad
        altura_minima = 600
        altura_por_accion = 20
        altura_grafico = max(altura_minima, len(df_ranking) * altura_por_accion)
        
        # Preparar datos adicionales para el hover
        # Formatear Market Cap en formato legible
        def format_market_cap(mc):
            if mc >= 1:
                return f"{mc:.1f}B€"
            else:
                return f"{mc*1000:.0f}M€"
        
        customdata = np.column_stack([
            df_ranking['Total_Return_%'].values,
            df_ranking['Score'].values,
            df_ranking['PE_Ratio'].values,
            [format_market_cap(x) for x in df_ranking['Market_Cap'].values],
            df_ranking['ROE'].values,
            df_ranking['Volatilidad'].values,
            df_ranking['Beta'].values,
            df_ranking['Sector'].values,
            df_ranking['Num_Analysts'].values,
            df_ranking['Recommendation'].values
        ])
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Potencial Revalorización',
            x=df_ranking['Label'],
            y=df_ranking['Upside_%'],
            marker_color='#1976D2',
            text=df_ranking['Upside_%'].apply(lambda x: f"{x:.1f}%"),
            textposition='inside',
            textfont=dict(size=9),
            customdata=customdata,
            hovertemplate='<b>%{x}</b><br>' +
                         '━━━━━━━━━━━━━━━━━━━━<br>' +
                         '<b>📊 RENTABILITAT</b><br>' +
                         '  Upside: <b>%{y:.1f}%</b><br>' +
                         '  Total Return: <b>%{customdata[0]:.1f}%</b><br>' +
                         '  Score: <b>%{customdata[1]:.0f}/100</b><br>' +
                         '━━━━━━━━━━━━━━━━━━━━<br>' +
                         '<b>💼 FONAMENTALS</b><br>' +
                         '  PE Ratio: %{customdata[2]:.1f}<br>' +
                         '  ROE: %{customdata[4]:.1f}%<br>' +
                         '  Market Cap: %{customdata[3]}<br>' +
                         '━━━━━━━━━━━━━━━━━━━━<br>' +
                         '<b>⚡ RISC</b><br>' +
                         '  Volatilitat: %{customdata[5]:.1f}%<br>' +
                         '  Beta: %{customdata[6]:.2f}<br>' +
                         '━━━━━━━━━━━━━━━━━━━━<br>' +
                         '<b>🏷️ ALTRES</b><br>' +
                         '  Sector: %{customdata[7]}<br>' +
                         '  Analistes: %{customdata[8]:.0f}<br>' +
                         '  Recomanació: %{customdata[9]}<br>' +
                         '<extra></extra>'
        ))
        fig.add_trace(go.Bar(
            name='Dividend Yield',
            x=df_ranking['Label'],
            y=df_ranking['Dividend_Yield'],
            marker_color='#42A5F5',
            text=df_ranking['Dividend_Yield'].apply(lambda x: f"{x:.1f}%" if x > 0.5 else ""),
            textposition='inside',
            textfont=dict(size=9),
            customdata=customdata,
            hovertemplate='<b>%{x}</b><br>' +
                         '━━━━━━━━━━━━━━━━━━━━<br>' +
                         '<b>📊 RENTABILITAT</b><br>' +
                         '  Dividend: <b>%{y:.1f}%</b><br>' +
                         '  Total Return: <b>%{customdata[0]:.1f}%</b><br>' +
                         '  Score: <b>%{customdata[1]:.0f}/100</b><br>' +
                         '━━━━━━━━━━━━━━━━━━━━<br>' +
                         '<b>💼 FONAMENTALS</b><br>' +
                         '  PE Ratio: %{customdata[2]:.1f}<br>' +
                         '  ROE: %{customdata[4]:.1f}%<br>' +
                         '  Market Cap: %{customdata[3]}<br>' +
                         '━━━━━━━━━━━━━━━━━━━━<br>' +
                         '<b>⚡ RISC</b><br>' +
                         '  Volatilitat: %{customdata[5]:.1f}%<br>' +
                         '  Beta: %{customdata[6]:.2f}<br>' +
                         '━━━━━━━━━━━━━━━━━━━━<br>' +
                         '<b>🏷️ ALTRES</b><br>' +
                         '  Sector: %{customdata[7]}<br>' +
                         '  Analistes: %{customdata[8]:.0f}<br>' +
                         '  Recomanació: %{customdata[9]}<br>' +
                         '<extra></extra>'
        ))
        fig.update_layout(
            barmode='stack',
            height=altura_grafico,
            title=f"Rentabilidad Total Esperada (12 meses) - {mercado_seleccionado} ({len(df_ranking)} empresas)",
            xaxis_title="Empresa",
            yaxis_title="Rentabilidad Esperada (%)",
            hovermode='closest',
            template='plotly_white',
            showlegend=True,
            xaxis={'tickangle': -45, 'tickfont': {'size': 10}},
            margin=dict(b=150)
        )
        fig.add_hline(y=10, line_dash="dash", line_color="green", opacity=0.3, annotation_text="Objetivo 10%")
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2, col3, col4 = st.columns(4)
        if len(df_ranking) >= 20:
            q1 = df_ranking.head(int(len(df_ranking)*0.25))
            q2 = df_ranking.iloc[int(len(df_ranking)*0.25):int(len(df_ranking)*0.5)]
            q3 = df_ranking.iloc[int(len(df_ranking)*0.5):int(len(df_ranking)*0.75)]
            q4 = df_ranking.tail(int(len(df_ranking)*0.25))
            
            with col1:
                st.metric("🥇 Top 25%", f"{q1['Total_Return_%'].mean():.1f}%")
            with col2:
                st.metric("🥈 Segundo 25%", f"{q2['Total_Return_%'].mean():.1f}%")
            with col3:
                st.metric("🥉 Tercer 25%", f"{q3['Total_Return_%'].mean():.1f}%")
            with col4:
                st.metric("📉 Último 25%", f"{q4['Total_Return_%'].mean():.1f}%")
    
    with tab2:
        st.markdown("### 🏆 Top 10 Mejores Oportunidades")
        
        # 🔍 EXPLICACIÓN DETALLADA - POR QUÉ ESTE TOP 10 ES DIFERENTE
        st.info("""
        ### 💡 **¿Por qué estas 10 NO son las mismas que en la Pestaña 1?**
        
        **Pestaña 1 ("Ranking Completo")** ordena por **Rentabilidad Total** = Upside + Dividendo
        - Solo mira cuánto puedes ganar (revalorización + dividendo)
        - NO considera riesgo, calidad de la empresa, ni otros factores
        
        **Pestaña 2 ("Top Oportunidades")** ordena por **Score Propietario v2.0** (0-100 puntos)
        - Analiza 7 dimensiones para encontrar OPORTUNIDADES REALES de inversión
        - Balance entre rentabilidad, calidad, riesgo y confianza del mercado
        """)
        
        with st.expander("📊 **VER EXPLICACIÓN DETALLADA - ¿Cómo se calcula el Score?**"):
            st.markdown("""
            ### 🎯 El Score es una evaluación integral de 7 factores:
            
            #### **1️⃣ RENTABILIDAD ESPERADA (35 puntos)**
            - Upside potencial (0-20 pts): ¿Cuánto puede subir?
            - Dividend Yield (0-15 pts): ¿Cuánto paga en dividendos?
            
            #### **2️⃣ VALORACIÓN (20 puntos)**
            - PE Ratio (0-15 pts): ¿Está cara o barata? PE bajo = más puntos
            - Price/Book (0-5 pts): ¿Cotiza por debajo de su valor en libros?
            
            #### **3️⃣ CALIDAD FUNDAMENTAL (20 puntos)**
            - ROE (0-10 pts): ¿Qué tan rentable es para sus accionistas?
            - Revenue Growth (0-5 pts): ¿Está creciendo sus ingresos?
            - ROA (0-5 pts): ¿Genera beneficio con sus activos?
            
            #### **4️⃣ CONFIANZA DEL MERCADO (15 puntos)**
            - Número de Analistas (0-10 pts): ¿Cuántos expertos la siguen?
            - Recomendación (0-5 pts): ¿Qué dicen los analistas? (buy/hold/sell)
            
            #### **5️⃣ PENALIZACIONES (-20 puntos máximo)**
            - 🚨 Volatilidad >60%: -10 puntos (muy arriesgada)
            - 🚨 Beta >2.0: -5 puntos (muy sensible al mercado)
            - 🚨 Market Cap <500M: -8 puntos (empresa pequeña, más riesgo)
            
            #### **6️⃣ BONUS (+10 puntos máximo)**
            - ✅ Combo Value: Upside>15% + PE<15 + ROE>15: +5 puntos
            - ✅ Dividend Aristocrat: Div>4% + Growth>5%: +3 puntos
            - ✅ Calidad Premium: ROE>20% + ROA>10% + PE<20: +2 puntos
            
            #### **7️⃣ AJUSTES POR SECTOR (+5 puntos máximo)**
            - Tech/Healthcare: Tolerancia a PE alto (son caras por naturaleza)
            - Utilities/Banca: Bonus por dividendo alto
            - Energy/Industrial: Tolerancia a volatilidad
            
            ---
            
            ### 🔑 **EJEMPLO PRÁCTICO - ¿Por qué una acción con 40% de rentabilidad NO está en el Top 10?**
            
            **Empresa X:** Rentabilidad Total = 40% (¡primera en Pestaña 1!)
            - ✅ Upside: 35%
            - ✅ Dividendo: 5%
            - ❌ PE Ratio: 85 (MUY CARA, -5 puntos)
            - ❌ ROE: 2% (MALA CALIDAD, -10 puntos)
            - ❌ Volatilidad: 75% (MUY ARRIESGADA, -10 puntos)
            - ❌ Solo 2 analistas (POCA CONFIANZA, -8 puntos)
            - ❌ Market Cap: 200M (EMPRESA PEQUEÑA, -8 puntos)
            - **Score Final: 38/100** ❌ (NO RECOMENDADA)
            
            **Empresa Y:** Rentabilidad Total = 18% (puesto 15 en Pestaña 1)
            - ✅ Upside: 12%
            - ✅ Dividendo: 6%
            - ✅ PE Ratio: 11 (BARATA, +13 puntos)
            - ✅ ROE: 22% (EXCELENTE, +9 puntos)
            - ✅ Volatilidad: 18% (BAJA, sin penalización)
            - ✅ 18 analistas (BUENA COBERTURA, +9 puntos)
            - ✅ Market Cap: 15B (EMPRESA SÓLIDA, sin penalización)
            - ✅ Bonus Combo Value: +5 puntos
            - **Score Final: 78/100** ✅ (MUY ATRACTIVA - En Top 10!)
            
            ---
            
            ### 🎓 **CONCLUSIÓN:**
            
            La **Pestaña 1** te muestra dónde puedes ganar MÁS dinero (mayor rentabilidad bruta).
            
            La **Pestaña 2** te muestra las MEJORES oportunidades considerando:
            - ✅ Buena rentabilidad esperada
            - ✅ Precio razonable (no sobrevaloradas)
            - ✅ Empresas de calidad (ROE, ROA, crecimiento)
            - ✅ Bajo riesgo (volatilidad y beta controlados)
            - ✅ Respaldadas por analistas
            
            **💎 El Score identifica acciones infravaloradas de calidad, no solo las que más suben.**
            """)
        
        st.warning("""
        ⚠️ **IMPORTANTE:** Una acción con 50% de rentabilidad esperada puede NO estar aquí si:
        - Tiene volatilidad extrema (>60%)
        - Está sobrevalorada (PE >50)
        - Tiene fundamentales débiles (ROE bajo, sin crecimiento)
        - Es una empresa pequeña con poco seguimiento de analistas
        
        👉 **Usa ambas pestañas:** Pestaña 1 para rentabilidad, Pestaña 2 para oportunidades equilibradas.
        """)
        
        st.markdown("---")
        df_top10 = df_filtrado.nlargest(10, 'Score')
        
        categorias = ['Upside', 'Dividendo', 'PE Inverso', 'ROE', 'Analistas']
        fig = go.Figure()
        for _, empresa in df_top10.head(5).iterrows():
            valores = [
                min(100, max(0, (empresa['Upside_%'] + 20) * 2)),
                min(100, empresa['Dividend_Yield'] * 10),
                100 - min(100, empresa['PE_Ratio'] * 2) if empresa['PE_Ratio'] > 0 else 50,
                min(100, max(0, empresa['ROE'])),
                min(100, empresa['Num_Analysts'] * 5)
            ]
            fig.add_trace(go.Scatterpolar(
                r=valores,
                theta=categorias,
                fill='toself',
                name=f"{empresa['Empresa']}"
            ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            height=500,
            title="Top 5 Oportunidades - Análisis Multidimensional"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("#### 📋 Detalle Top 10")
        df_top10_display = df_top10[['Ticker', 'Empresa', 'Sector', 'Score', 'Total_Return_%', 
                                     'Upside_%', 'Dividend_Yield', 'PE_Ratio', 'ROE', 'Num_Analysts']].copy()
        st.dataframe(df_top10_display, use_container_width=True, hide_index=True)
    
    with tab3:
        st.markdown("### 📈 Análisis por Sector")
        sector_stats = df_filtrado.groupby('Sector').agg({
            'Total_Return_%': 'mean',
            'Upside_%': 'mean',
            'Dividend_Yield': 'mean',
            'PE_Ratio': 'mean',
            'ROE': 'mean',
            'Volatilidad': 'mean',
            'Ticker': 'count'
        }).round(2)
        sector_stats.columns = ['Rent. Total', 'Upside', 'Dividendo', 'PE', 'ROE', 'Volatilidad', 'Nº Empresas']
        sector_stats = sector_stats.sort_values('Rent. Total', ascending=False)
        
        fig = px.bar(sector_stats, x=sector_stats.index, y='Rent. Total', color='Rent. Total',
                    color_continuous_scale='RdYlGn', title='Rentabilidad Media por Sector', text='Rent. Total')
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(height=400, xaxis_title="Sector", yaxis_title="Rentabilidad Total (%)")
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("#### 📊 Estadísticas por Sector")
        st.dataframe(sector_stats, use_container_width=True)
    
    with tab4:
        st.markdown("### 💎 Matriz Estratégica de Inversión")
        
        df_filtrado['Label'] = df_filtrado['Ticker'] + ' - ' + df_filtrado['Empresa']
        
        fig = px.scatter(df_filtrado, x='Volatilidad', y='Total_Return_%', size='Market_Cap',
            color='Score', hover_data=['Empresa', 'Sector', 'PE_Ratio', 'Dividend_Yield'],
            text='Ticker', color_continuous_scale='RdYlGn',
            title='Rentabilidad vs Riesgo (Tamaño = Market Cap)')
        fig.update_traces(textposition='top center', textfont_size=8)
        fig.update_layout(height=600, xaxis_title="Volatilidad Anual (%)", 
                         yaxis_title="Rentabilidad Total Esperada (%)", template='plotly_white')
        fig.add_hline(y=df_filtrado['Total_Return_%'].median(), line_dash="dash", line_color="gray", opacity=0.3)
        fig.add_vline(x=df_filtrado['Volatilidad'].median(), line_dash="dash", line_color="gray", opacity=0.3)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 💰 Matriz Dividendo vs Potencial")
        fig2 = px.scatter(df_filtrado, x='Dividend_Yield', y='Upside_%', size='Num_Analysts',
            color='Sector', hover_data=['Empresa', 'Total_Return_%', 'PE_Ratio'],
            text='Ticker', title='Estrategia: Dividendo vs Crecimiento')
        fig2.update_traces(textposition='top center', textfont_size=8)
        fig2.update_layout(height=500, xaxis_title="Dividend Yield (%)", 
                          yaxis_title="Potencial de Revalorización (%)")
        fig2.add_hline(y=10, line_dash="dash", line_color="gray", opacity=0.3)
        fig2.add_vline(x=4, line_dash="dash", line_color="gray", opacity=0.3)
        st.plotly_chart(fig2, use_container_width=True)
    
    with tab5:
        st.markdown("### 🌍 TOP EMPRESAS DE MERCADOS SELECCIONADOS")
        
        # ========== CONTROLES DE SELECCIÓN ==========
        col_control1, col_control2 = st.columns([2, 1])
        
        with col_control1:
            mercados_disponibles = list(MERCADOS.keys())
            mercados_seleccionados_tab5 = st.multiselect(
                "🌍 Selecciona los mercados a analizar:",
                options=mercados_disponibles,
                default=mercados_disponibles,  # Por defecto todos seleccionados
                help="Elige uno o más mercados para comparar"
            )
        
        with col_control2:
            num_empresas_mostrar = st.slider(
                "📊 Número de empresas a mostrar:",
                min_value=10,
                max_value=50,
                value=25,
                step=5,
                help="Cuántas empresas quieres ver en el ranking"
            )
        
        if not mercados_seleccionados_tab5:
            st.warning("⚠️ Por favor, selecciona al menos un mercado para analizar.")
            return
        
        # Información sobre la selección
        st.info(f"""
        📊 **Analizando:**
        - **Mercados seleccionados:** {len(mercados_seleccionados_tab5)} de {len(MERCADOS)}
        - **Mostrando:** TOP {num_empresas_mostrar} empresas por Score
        
        🎯 **Mercados incluidos:** {', '.join(mercados_seleccionados_tab5)}
        """)
        
        # Cargar datos SOLO de los mercados seleccionados
        df_todos_mercados = pd.DataFrame()
        mercados_cargados = []
        
        # Información de debug
        debug_info = []
        
        with st.spinner(f"Cargando datos de {len(mercados_seleccionados_tab5)} mercado(s)..."):
            for nombre_mercado in mercados_seleccionados_tab5:
                info_mercado = MERCADOS[nombre_mercado]
                db_mercado = info_mercado["db_name"]
                db_path = get_db_path(db_mercado)
                
                if os.path.exists(db_path):
                    try:
                        df_mercado = cargar_datos_desde_bd(None, db_mercado)
                        if not df_mercado.empty:
                            # Añadir columna de mercado si no existe
                            if 'Mercado' not in df_mercado.columns:
                                df_mercado['Mercado'] = nombre_mercado
                            df_todos_mercados = pd.concat([df_todos_mercados, df_mercado], ignore_index=True)
                            mercados_cargados.append(nombre_mercado)
                            debug_info.append(f"✅ {nombre_mercado}: {len(df_mercado)} empresas")
                        else:
                            debug_info.append(f"⚠️ {nombre_mercado}: BD vacía")
                    except Exception as e:
                        debug_info.append(f"❌ {nombre_mercado}: Error - {str(e)[:50]}")
                else:
                    debug_info.append(f"❌ {nombre_mercado}: BD no existe ({db_mercado})")
        
        # Mostrar información de debug
        with st.expander("🔍 Ver detalles de carga", expanded=False):
            for info in debug_info:
                st.text(info)
            st.text(f"\n📊 Total empresas cargadas: {len(df_todos_mercados)}")
            if not df_todos_mercados.empty and 'Mercado' in df_todos_mercados.columns:
                st.text("\n📈 Distribución por mercado:")
                for mercado, count in df_todos_mercados['Mercado'].value_counts().items():
                    st.text(f"   • {mercado}: {count} empresas")
        
        if df_todos_mercados.empty:
            st.error(f"""
            ❌ **No hay datos disponibles en los mercados seleccionados.**
            
            **Mercados seleccionados:** {', '.join(mercados_seleccionados_tab5)}
            
            **Para solucionar esto:**
            1. Ve al sidebar
            2. Selecciona cada mercado uno por uno
            3. Haz clic en "🔄 Actualizar" para cada uno
            4. O usa "🔄 Actualizar TODOS los Mercados" (puede tardar varios minutos)
            
            **Bases de datos necesarias:**
            """)
            for nombre_mercado in mercados_seleccionados_tab5:
                db_name = MERCADOS[nombre_mercado]["db_name"]
                st.text(f"- {nombre_mercado} → {db_name}")
            return
        else:
            # Aplicar filtros (los mismos que se usan en el mercado actual)
            # IMPORTANTE: Para sectores, usar TODOS los sectores disponibles en todos los mercados
            sectores_todos_mercados = sorted(df_todos_mercados['Sector'].unique().tolist()) if 'Sector' in df_todos_mercados.columns else []
            
            # NO aplicar filtro de sectores del sidebar (porque son sectores del mercado actual, no de todos)
            # En su lugar, permitir TODOS los sectores de TODOS los mercados
            df_todos_filtrado = df_todos_mercados[
                (df_todos_mercados['Upside_%'] >= min_upside) &
                (df_todos_mercados['Dividend_Yield'] >= min_dividend) &
                (df_todos_mercados['Total_Return_%'] >= min_total_return) &
                ((df_todos_mercados['PE_Ratio'] <= max_pe) | (df_todos_mercados['PE_Ratio'] == 0)) &
                (df_todos_mercados['ROE'] >= min_roe) &
                (df_todos_mercados['Num_Analysts'] >= min_analysts) &
                (df_todos_mercados['Volatilidad'] <= max_volatilidad) &
                (df_todos_mercados['Market_Cap'] >= min_market_cap)
            ]
            
            # Ordenar por Score y tomar TOP N (según selección del usuario)
            df_top_global = df_todos_filtrado.nlargest(num_empresas_mostrar, 'Score')
            
            # Estadísticas rápidas
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("🌍 Mercados", len(mercados_cargados))
            with col2:
                st.metric("📊 Total cargadas", len(df_todos_mercados))
            with col3:
                st.metric("🔍 Pasan filtros", len(df_todos_filtrado))
            with col4:
                st.metric(f"⭐ Score TOP {num_empresas_mostrar}", f"{df_top_global['Score'].mean():.0f}/100")
            with col5:
                st.metric(f"💎 Return TOP {num_empresas_mostrar}", f"{df_top_global['Total_Return_%'].mean():.1f}%")
            
            st.markdown("---")
            
            # Mostrar tabla TOP 25
            columnas_mostrar = ['Mercado', 'Ticker', 'Empresa', 'Sector', 'Precio_Actual', 'Target_Mean',
                               'Upside_%', 'Dividend_Yield', 'Total_Return_%', 'Score',
                               'PE_Ratio', 'ROE', 'Market_Cap', 'Volatilidad', 
                               'Beta', 'Num_Analysts', 'Recommendation']
            
            # Asegurarse de que todas las columnas existen
            columnas_existentes = [col for col in columnas_mostrar if col in df_top_global.columns]
            df_tabla = df_top_global[columnas_existentes].copy()
            
            # Formatear columnas numéricas
            if 'Precio_Actual' in df_tabla.columns:
                df_tabla['Precio_Actual'] = df_tabla['Precio_Actual'].round(2)
            if 'Target_Mean' in df_tabla.columns:
                df_tabla['Target_Mean'] = df_tabla['Target_Mean'].round(2)
            if 'Market_Cap' in df_tabla.columns:
                df_tabla['Market_Cap'] = df_tabla['Market_Cap'].round(2)
            
            st.dataframe(
                df_tabla, 
                use_container_width=True, 
                hide_index=True, 
                height=600,
                column_config={
                    "Score": st.column_config.NumberColumn(
                        "Score",
                        help="Puntuación 0-100",
                        format="%d ⭐"
                    ),
                    "Total_Return_%": st.column_config.NumberColumn(
                        "Total Return %",
                        help="Upside + Dividendo",
                        format="%.1f%%"
                    ),
                    "Upside_%": st.column_config.NumberColumn(
                        "Upside %",
                        format="%.1f%%"
                    ),
                    "Dividend_Yield": st.column_config.NumberColumn(
                        "Dividend %",
                        format="%.1f%%"
                    ),
                    "Market_Cap": st.column_config.NumberColumn(
                        "Market Cap (B€)",
                        format="%.1f B€"
                    )
                }
            )
            
            # Distribución por mercado en TOP N
            st.markdown("---")
            st.markdown(f"### 📊 Distribución de TOP {num_empresas_mostrar} por Mercado")
            
            mercado_count = df_top_global['Mercado'].value_counts()
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig_mercados = go.Figure(data=[go.Pie(
                    labels=mercado_count.index,
                    values=mercado_count.values,
                    hole=0.4,
                    marker=dict(colors=['#1976D2', '#42A5F5', '#64B5F6', '#90CAF9'])
                )])
                fig_mercados.update_layout(
                    title=f"¿De qué mercados son las TOP {num_empresas_mostrar}?",
                    height=400
                )
                st.plotly_chart(fig_mercados, use_container_width=True)
            
            with col2:
                st.markdown("#### 🏆 Conteo por Mercado:")
                for mercado, count in mercado_count.items():
                    porcentaje = (count / num_empresas_mostrar) * 100
                    st.metric(mercado, f"{count}/{num_empresas_mostrar}", f"{porcentaje:.0f}%")
            
            st.markdown("---")
        
        st.markdown("### 💾 Descargar Datos")
        
        # Botones para datos globales (mercados seleccionados)
        mercados_texto = ', '.join(mercados_seleccionados_tab5) if len(mercados_seleccionados_tab5) <= 2 else f"{len(mercados_seleccionados_tab5)} mercados"
        st.markdown(f"#### 🌍 Datos Globales ({mercados_texto})")
        col1, col2 = st.columns(2)
        with col1:
            if not df_todos_mercados.empty:
                csv_todos = df_todos_mercados.to_csv(index=False)
                st.download_button(f"📥 TODAS las empresas ({len(df_todos_mercados)})", csv_todos,
                    file_name=f"MERCADOS_SELECCIONADOS_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv")
        with col2:
            if not df_top_global.empty:
                csv_top_global = df_top_global.to_csv(index=False)
                st.download_button(f"🏆 TOP {num_empresas_mostrar} Global", csv_top_global,
                    file_name=f"TOP{num_empresas_mostrar}_GLOBAL_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv")
        
        # Botones para mercado actual
        st.markdown(f"#### 📊 {mercado_seleccionado} (mercado actual)")
        col1, col2, col3 = st.columns(3)
        with col1:
            csv_completo = df.to_csv(index=False)
            st.download_button("📥 Completo", csv_completo,
                file_name=f"{mercado_seleccionado.replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv")
        with col2:
            csv_filtrado = df_filtrado.to_csv(index=False)
            st.download_button("🎯 Filtrado", csv_filtrado,
                file_name=f"{mercado_seleccionado.replace(' ','_')}_filtrado_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv")
        with col3:
            df_top10_export = df.nlargest(10, 'Score')
            csv_top10 = df_top10_export.to_csv(index=False)
            st.download_button("🏆 Top 10", csv_top10,
                file_name=f"{mercado_seleccionado.replace(' ','_')}_top10_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv")
    
    with tab6:
        st.markdown("### 📉 Análisis Técnico - Gráficos de Velas y MACD")
        col1, col2 = st.columns([3, 1])
        with col1:
            empresa_tecnica = st.selectbox("Selecciona una empresa:",
                options=df['Ticker'].tolist(),
                format_func=lambda x: f"{x} - {df[df['Ticker']==x]['Empresa'].iloc[0]}",
                key="empresa_tecnica")
        with col2:
            periodo_map = {"1 mes": 30, "3 meses": 90, "6 meses": 180, "1 año": 365}
            periodo_txt = st.selectbox("Período:", options=list(periodo_map.keys()), index=3)
            periodo_dias = periodo_map[periodo_txt]
        
        hist_tecnico = cargar_historico_desde_bd(empresa_tecnica, periodo_dias, db_name)
        if hist_tecnico.empty:
            try:
                stock = yf.Ticker(empresa_tecnica)
                periodo_yf = "1mo" if periodo_dias <= 30 else "3mo" if periodo_dias <= 90 else "6mo" if periodo_dias <= 180 else "1y"
                hist_tecnico = stock.history(period=periodo_yf)
            except:
                hist_tecnico = pd.DataFrame()
        
        if not hist_tecnico.empty:
            def calcular_macd(df, fast=12, slow=26, signal=9):
                ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
                ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()
                macd_line = ema_fast - ema_slow
                signal_line = macd_line.ewm(span=signal, adjust=False).mean()
                histogram = macd_line - signal_line
                return macd_line, signal_line, histogram
            
            macd_line, signal_line, histogram = calcular_macd(hist_tecnico)
            
            fig_tecnico = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                row_heights=[0.7, 0.3], subplot_titles=(f'{empresa_tecnica} - Precio', 'MACD'))
            
            fig_tecnico.add_trace(go.Candlestick(x=hist_tecnico.index,
                open=hist_tecnico['Open'], high=hist_tecnico['High'],
                low=hist_tecnico['Low'], close=hist_tecnico['Close'],
                name='Precio', increasing_line_color='#26a69a', decreasing_line_color='#ef5350'),
                row=1, col=1)
            
            sma_20 = hist_tecnico['Close'].rolling(window=20).mean()
            sma_50 = hist_tecnico['Close'].rolling(window=50).mean()
            fig_tecnico.add_trace(go.Scatter(x=hist_tecnico.index, y=sma_20, name='SMA 20',
                line=dict(color='orange', width=1)), row=1, col=1)
            fig_tecnico.add_trace(go.Scatter(x=hist_tecnico.index, y=sma_50, name='SMA 50',
                line=dict(color='blue', width=1)), row=1, col=1)
            
            fig_tecnico.add_trace(go.Scatter(x=hist_tecnico.index, y=macd_line, name='MACD',
                line=dict(color='#2196F3', width=2)), row=2, col=1)
            fig_tecnico.add_trace(go.Scatter(x=hist_tecnico.index, y=signal_line, name='Signal',
                line=dict(color='#FF6D00', width=2)), row=2, col=1)
            
            colors_histogram = ['#26a69a' if val >= 0 else '#ef5350' for val in histogram]
            fig_tecnico.add_trace(go.Bar(x=hist_tecnico.index, y=histogram, name='Histograma',
                marker_color=colors_histogram), row=2, col=1)
            
            fig_tecnico.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5, row=2, col=1)
            fig_tecnico.update_layout(height=700, xaxis_rangeslider_visible=False, 
                template='plotly_dark', hovermode='x unified', showlegend=True)
            fig_tecnico.update_xaxes(title_text="Fecha", row=2, col=1)
            fig_tecnico.update_yaxes(title_text="Precio", row=1, col=1)
            fig_tecnico.update_yaxes(title_text="MACD", row=2, col=1)
            st.plotly_chart(fig_tecnico, use_container_width=True)
            
            col1, col2, col3, col4 = st.columns(4)
            empresa_data = df[df['Ticker'] == empresa_tecnica].iloc[0]
            with col1:
                precio_actual = hist_tecnico['Close'].iloc[-1]
                precio_anterior = hist_tecnico['Close'].iloc[-2] if len(hist_tecnico) > 1 else precio_actual
                cambio = ((precio_actual - precio_anterior) / precio_anterior) * 100
                st.metric("Precio Actual", f"€{precio_actual:.2f}", delta=f"{cambio:.2f}%")
            with col2:
                st.metric("Target", f"€{empresa_data['Target_Mean']:.2f}", 
                         delta=f"Upside: {empresa_data['Upside_%']:.1f}%")
            with col3:
                señal_macd = "COMPRA" if macd_line.iloc[-1] > signal_line.iloc[-1] else "VENTA"
                color = "🟢" if señal_macd == "COMPRA" else "🔴"
                st.metric("Señal MACD", f"{color} {señal_macd}")
            with col4:
                tendencia = "ALCISTA" if precio_actual > sma_20.iloc[-1] > sma_50.iloc[-1] else "BAJISTA"
                color = "📈" if tendencia == "ALCISTA" else "📉"
                st.metric("Tendencia", f"{color} {tendencia}")
            
            # ANÁLISIS DE ANALISTAS
            st.markdown("---")
            st.markdown("### 👥 Análisis y Consenso de Analistas")
            
            try:
                stock_analistas = yf.Ticker(empresa_tecnica)
                info_analistas = stock_analistas.info
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    num_analistas = info_analistas.get('numberOfAnalystOpinions', 0)
                    st.metric("👥 Número de Analistas", num_analistas)
                
                with col2:
                    recomendacion = info_analistas.get('recommendationKey', 'N/A')
                    recom_emoji = {
                        'strong_buy': '🟢🟢',
                        'buy': '🟢',
                        'hold': '🟡',
                        'sell': '🔴',
                        'strong_sell': '🔴🔴'
                    }.get(recomendacion.lower() if recomendacion != 'N/A' else '', '⚪')
                    recom_texto = {
                        'strong_buy': 'COMPRA FUERTE',
                        'buy': 'COMPRA',
                        'hold': 'MANTENER',
                        'sell': 'VENDER',
                        'strong_sell': 'VENTA FUERTE'
                    }.get(recomendacion.lower() if recomendacion != 'N/A' else '', 'N/A')
                    st.metric("📊 Recomendación", f"{recom_emoji} {recom_texto}")
                
                with col3:
                    target_mean = info_analistas.get('targetMeanPrice', 0)
                    if target_mean > 0:
                        st.metric("🎯 Target Medio", f"€{target_mean:.2f}")
                    else:
                        st.metric("🎯 Target Medio", "N/A")
                
                with col4:
                    target_high = info_analistas.get('targetHighPrice', 0)
                    target_low = info_analistas.get('targetLowPrice', 0)
                    if target_high > 0 and target_low > 0:
                        st.metric("🔍 Rango Targets", f"€{target_low:.2f} - €{target_high:.2f}")
                    else:
                        st.metric("🔍 Rango Targets", "N/A")
                
                # Gráfico de targets
                if target_mean > 0 and target_high > 0 and target_low > 0:
                    st.markdown("#### 📊 Comparativa: Precio Actual vs Targets de Analistas")
                    
                    fig_targets = go.Figure()
                    
                    fig_targets.add_trace(go.Scatter(
                        x=['Precio Actual'],
                        y=[precio_actual],
                        mode='markers+text',
                        marker=dict(size=20, color='#2196F3'),
                        text=[f'€{precio_actual:.2f}'],
                        textposition='top center',
                        name='Precio Actual',
                        textfont=dict(size=14, color='#2196F3')
                    ))
                    
                    fig_targets.add_trace(go.Scatter(
                        x=['Target Bajo'],
                        y=[target_low],
                        mode='markers+text',
                        marker=dict(size=15, color='#FF6B6B'),
                        text=[f'€{target_low:.2f}'],
                        textposition='top center',
                        name='Target Bajo',
                        textfont=dict(size=12, color='#FF6B6B')
                    ))
                    
                    fig_targets.add_trace(go.Scatter(
                        x=['Target Medio'],
                        y=[target_mean],
                        mode='markers+text',
                        marker=dict(size=18, color='#FFA726'),
                        text=[f'€{target_mean:.2f}'],
                        textposition='top center',
                        name='Target Medio',
                        textfont=dict(size=13, color='#FFA726')
                    ))
                    
                    fig_targets.add_trace(go.Scatter(
                        x=['Target Alto'],
                        y=[target_high],
                        mode='markers+text',
                        marker=dict(size=15, color='#66BB6A'),
                        text=[f'€{target_high:.2f}'],
                        textposition='top center',
                        name='Target Alto',
                        textfont=dict(size=12, color='#66BB6A')
                    ))
                    
                    fig_targets.add_hline(y=precio_actual, line_dash="dash", 
                                         line_color="#2196F3", opacity=0.3,
                                         annotation_text="Precio Actual")
                    
                    fig_targets.update_layout(
                        height=400,
                        showlegend=True,
                        template='plotly_white',
                        yaxis_title="Precio (€)",
                        xaxis_title="",
                        hovermode='x'
                    )
                    
                    st.plotly_chart(fig_targets, use_container_width=True)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        potencial_medio = ((target_mean - precio_actual) / precio_actual) * 100
                        color_medio = "🟢" if potencial_medio > 0 else "🔴"
                        st.metric(f"{color_medio} Potencial al Target Medio", f"{potencial_medio:+.1f}%")
                    with col2:
                        potencial_alto = ((target_high - precio_actual) / precio_actual) * 100
                        st.metric("📈 Potencial al Target Alto", f"{potencial_alto:+.1f}%")
                    with col3:
                        potencial_bajo = ((target_low - precio_actual) / precio_actual) * 100
                        st.metric("📉 Riesgo al Target Bajo", f"{potencial_bajo:+.1f}%")
                
                # Historial de recomendaciones
                try:
                    recommendations = stock_analistas.recommendations
                    if recommendations is not None and not recommendations.empty:
                        st.markdown("#### 📋 Historial Reciente de Recomendaciones")
                        
                        rec_recientes = recommendations.tail(10).sort_index(ascending=False)
                        
                        if 'strongBuy' in rec_recientes.columns:
                            rec_summary = rec_recientes[['strongBuy', 'buy', 'hold', 'sell', 'strongSell']].iloc[0]
                            
                            fig_rec = go.Figure()
                            fig_rec.add_trace(go.Bar(
                                x=['Compra Fuerte', 'Compra', 'Mantener', 'Vender', 'Venta Fuerte'],
                                y=[rec_summary['strongBuy'], rec_summary['buy'], 
                                   rec_summary['hold'], rec_summary['sell'], rec_summary['strongSell']],
                                marker_color=['#00C853', '#66BB6A', '#FFA726', '#FF7043', '#E53935'],
                                text=[rec_summary['strongBuy'], rec_summary['buy'], 
                                      rec_summary['hold'], rec_summary['sell'], rec_summary['strongSell']],
                                textposition='auto',
                            ))
                            fig_rec.update_layout(
                                title="Distribución de Recomendaciones",
                                xaxis_title="Tipo de Recomendación",
                                yaxis_title="Número de Analistas",
                                height=350,
                                template='plotly_white'
                            )
                            st.plotly_chart(fig_rec, use_container_width=True)
                        
                        st.markdown("**Últimas actualizaciones:**")
                        st.dataframe(rec_recientes.head(5), use_container_width=True)
                except:
                    st.info("ℹ️ Historial detallado de recomendaciones no disponible")
                
            except Exception as e:
                st.warning(f"⚠️ No se pudo obtener información de analistas: {str(e)}")
        
        else:
            st.warning("⚠️ No hay datos históricos disponibles")
    
    with tab7:
        st.markdown("### 📖 Diccionario de Términos y Métricas")
        
        st.markdown("""
        Esta pestaña explica todos los indicadores, métricas y términos utilizados en el sistema de análisis multi-mercado.
        """)
        
        # Crear expanders por categorías
        with st.expander("📊 **MÉTRICAS DE RENTABILIDAD**", expanded=True):
            st.markdown("""
            **Precio Actual**
            - Último precio de cotización de la acción
            - Actualizado diariamente desde Yahoo Finance
            
            **Target Mean (Precio Objetivo Medio)**
            - Precio objetivo promedio estimado por los analistas para los próximos 12 meses
            - Basado en el consenso de múltiples analistas
            
            **Target High / Target Low**
            - Precio objetivo más alto/bajo entre todos los analistas
            - Representa el rango de expectativas del mercado
            
            **Upside % (Potencial de Revalorización)**
            - Porcentaje de ganancia esperada si el precio alcanza el Target Mean
            - Fórmula: `((Target Mean - Precio Actual) / Precio Actual) × 100`
            - **Interpretación:**
              - > 15%: Muy atractivo
              - 5-15%: Potencial moderado
              - < 5%: Potencial limitado
            
            **Dividend Yield (Rentabilidad por Dividendo)**
            - Rentabilidad anual por dividendos en relación al precio actual
            - Expresado en porcentaje (%)
            - **Interpretación:**
              - > 5%: Dividendo alto
              - 3-5%: Dividendo atractivo
              - < 3%: Dividendo bajo o empresa de crecimiento
            
            **Total Return % (Rentabilidad Total Esperada)**
            - Suma del Upside % + Dividend Yield
            - Representa la rentabilidad total esperada a 12 meses
            - **Es la métrica clave para comparar oportunidades**
            """)
        
        with st.expander("💰 **VALORACIÓN Y RATIOS FUNDAMENTALES**"):
            st.markdown("""
            **PE Ratio (Price/Earnings - PER)**
            - Precio de la acción dividido entre el beneficio por acción
            - Mide cuántas veces pagamos el beneficio anual
            - **Interpretación:**
              - < 12: Empresa infravalorada o bajo crecimiento
              - 12-18: Valoración normal
              - > 18: Sobrevalorada o alto crecimiento esperado
              - > 30: Muy cara o sector tecnológico
            
            **PE Forward (PER Futuro)**
            - Similar al PE Ratio pero usando beneficios estimados futuros
            - Más relevante para evaluar perspectivas
            
            **Price/Book (Precio/Valor Contable)**
            - Precio de la acción dividido entre el valor contable por acción
            - **Interpretación:**
              - < 1: Cotiza por debajo de su valor en libros (ganga o problemas)
              - 1-3: Valoración razonable
              - > 3: Prima por activos intangibles o crecimiento
            
            **Market Cap (Capitalización Bursátil)**
            - Valor total de mercado de la empresa (en miles de millones €)
            - Precio × Número de acciones
            - **Categorías:**
              - > 100B: Mega cap
              - 10-100B: Large cap
              - 2-10B: Mid cap
              - < 2B: Small cap
            """)
        
        with st.expander("📈 **RENTABILIDAD Y EFICIENCIA OPERATIVA**"):
            st.markdown("""
            **ROE (Return on Equity - Rentabilidad sobre Fondos Propios)**
            - Beneficio neto / Patrimonio neto × 100
            - Mide la rentabilidad que genera la empresa con el capital de los accionistas
            - **Interpretación:**
              - > 20%: Excelente
              - 15-20%: Muy bueno
              - 10-15%: Bueno
              - < 10%: Mejorable o sector de baja rentabilidad
            
            **ROA (Return on Assets - Rentabilidad sobre Activos)**
            - Beneficio neto / Activos totales × 100
            - Mide la eficiencia en el uso de los activos
            - **Interpretación:**
              - > 10%: Muy eficiente
              - 5-10%: Eficiencia normal
              - < 5%: Baja eficiencia o sector intensivo en capital
            
            **Revenue Growth (Crecimiento de Ingresos)**
            - Tasa de crecimiento anual de las ventas
            - **Interpretación:**
              - > 15%: Alto crecimiento
              - 5-15%: Crecimiento moderado
              - 0-5%: Crecimiento bajo
              - < 0%: Decrecimiento (señal de alerta)
            """)
        
        with st.expander("⚡ **MÉTRICAS DE RIESGO Y VOLATILIDAD**"):
            st.markdown("""
            **Volatilidad**
            - Desviación estándar de los retornos anualizada (%)
            - Mide la variabilidad del precio de la acción
            - **Interpretación:**
              - < 20%: Baja volatilidad (defensivas, utilities)
              - 20-30%: Volatilidad moderada
              - 30-50%: Alta volatilidad
              - > 50%: Muy alta volatilidad (pequeñas empresas, tech)
            
            **Beta**
            - Sensibilidad de la acción respecto al mercado
            - Beta del mercado = 1.0
            - **Interpretación:**
              - < 0.5: Muy defensiva
              - 0.5-1.0: Defensiva
              - 1.0: Neutral (se mueve con el mercado)
              - 1.0-1.5: Agresiva
              - > 1.5: Muy agresiva
            """)
        
        with st.expander("👥 **ANALISTAS Y RECOMENDACIONES**"):
            st.markdown("""
            **Num Analysts (Número de Analistas)**
            - Cantidad de analistas que cubren la acción
            - **Interpretación:**
              - > 15: Cobertura muy alta (más fiable)
              - 10-15: Buena cobertura
              - 5-10: Cobertura moderada
              - < 5: Cobertura limitada (menos fiable)
            
            **Recommendation (Recomendación)**
            - Consenso de analistas
            - **Categorías:**
              - `strong_buy`: Compra fuerte
              - `buy`: Compra
              - `hold`: Mantener
              - `sell`: Vender
              - `strong_sell`: Venta fuerte
            """)
        
        with st.expander("⭐ **SCORE PROPIETARIO MEJORADO v2.0 (0-100)**"):
            st.markdown("""
            **Score de Oportunidad**
            - Puntuación compuesta que evalúa múltiples factores
            - Rango: 0 (peor) a 100 (mejor)
            
            **Componentes del Score:**
            
            **1. RENTABILIDAD ESPERADA (35 puntos)**
            - Upside (0-20 puntos):
              - ≥25%: 20 puntos
              - 20-25%: 18 puntos
              - 15-20%: 15 puntos
              - 10-15%: 12 puntos
              - 5-10%: 8 puntos
            - Dividend Yield (0-15 puntos):
              - ≥7%: 15 puntos
              - 5-7%: 13 puntos
              - 4-5%: 11 puntos
              - 3-4%: 8 puntos
            
            **2. VALORACIÓN (20 puntos)**
            - PE Ratio (0-15 puntos):
              - <10: 15 puntos
              - 10-12: 13 puntos
              - 12-15: 11 puntos
              - 15-18: 8 puntos
            - Price/Book (0-5 puntos):
              - <1: 5 puntos
              - 1-2: 4 puntos
              - 2-3: 3 puntos
            
            **3. CALIDAD FUNDAMENTAL (20 puntos)**
            - ROE (0-10 puntos):
              - ≥25%: 10 puntos
              - 20-25%: 9 puntos
              - 15-20%: 7 puntos
            - Revenue Growth (0-5 puntos):
              - ≥20%: 5 puntos
              - 15-20%: 4 puntos
            - ROA (0-5 puntos):
              - ≥15%: 5 puntos
              - 10-15%: 4 puntos
            
            **4. CONFIANZA DEL MERCADO (15 puntos)**
            - Número Analistas (0-10 puntos):
              - ≥20: 10 puntos
              - 15-20: 9 puntos
              - 10-15: 7 puntos
            - Recomendación (0-5 puntos):
              - strong_buy: 5 puntos
              - buy: 4 puntos
              - hold: 2 puntos
            
            **5. PENALIZACIONES (-20 puntos máximo)**
            - Volatilidad >60%: -10 puntos
            - Volatilidad 45-60%: -6 puntos
            - Beta >2.0: -5 puntos
            - Market Cap <0.5B: -8 puntos
            
            **6. BONUS (+10 puntos máximo)**
            - Combo Value: Upside>15% + PE<15 + ROE>15: +5 puntos
            - Dividend Aristocrat: Div>4% + Growth>5%: +3 puntos
            - Calidad Premium: ROE>20% + ROA>10% + PE<20: +2 puntos
            
            **7. AJUSTES POR SECTOR (+5 puntos máximo)**
            - Tech/Healthcare: Tolerancia PE alto
            - Utilities/Banca: Bonus por dividendo
            - Energy/Industrial: Tolerancia volatilidad
            
            **Interpretación:**
            - 85-100: 🟢🟢 EXCEPCIONAL
            - 75-84: 🟢 MUY ATRACTIVA
            - 65-74: 🟡 ATRACTIVA
            - 55-64: ⚪ NEUTRAL
            - 45-54: 🟠 POCO ATRACTIVA
            - 35-44: 🔴 NO RECOMENDADA
            - 0-34: 🔴🔴 EVITAR
            """)
        
        with st.expander("📉 **INDICADORES TÉCNICOS**"):
            st.markdown("""
            **Gráfico de Velas (Candlestick)**
            - Cada vela representa un día de cotización
            - Verde: Precio de cierre > precio de apertura (día alcista)
            - Rojo: Precio de cierre < precio de apertura (día bajista)
            
            **SMA 20 (Media Móvil Simple 20 días)**
            - Promedio del precio de los últimos 20 días
            - Línea naranja en el gráfico
            - Indica tendencia de corto plazo
            
            **SMA 50 (Media Móvil Simple 50 días)**
            - Promedio del precio de los últimos 50 días
            - Línea azul en el gráfico
            - Indica tendencia de medio plazo
            
            **MACD (Moving Average Convergence Divergence)**
            - Indicador de momentum que sigue la tendencia
            - **Componentes:**
              - **Línea MACD** (azul): Diferencia entre EMA(12) y EMA(26)
              - **Línea de Señal** (naranja): EMA(9) de la línea MACD
              - **Histograma**: Diferencia entre MACD y Señal
            - **Señales:**
              - MACD cruza señal hacia arriba: Señal de COMPRA
              - MACD cruza señal hacia abajo: Señal de VENTA
              - Histograma positivo: Momentum alcista
              - Histograma negativo: Momentum bajista
            
            **Tendencia**
            - **ALCISTA**: Precio > SMA20 > SMA50
            - **BAJISTA**: Precio < SMA20 < SMA50
            """)
        
        with st.expander("🏢 **SECTORES Y MERCADOS**"):
            st.markdown("""
            **IBEX 35**
            - Principales 35 empresas españolas por capitalización
            - Sectores: Banca, Utilities, Construcción, Retail, etc.
            
            **NASDAQ Top 25**
            - 25 mayores empresas tecnológicas del NASDAQ
            - Enfoque: Technology, Consumer, Media
            - Empresas: Apple, Microsoft, NVIDIA, Google, etc.
            
            **S&P 500 Top 25**
            - 25 mayores empresas del S&P 500 por capitalización
            - Mayor diversificación sectorial
            - Incluye: Tech, Financial, Healthcare, Energy, Retail
            
            **España Medium Cap**
            - 25 empresas españolas de mediana capitalización
            - Empresas no incluidas en IBEX 35
            - Mayor potencial de crecimiento y mayor riesgo
            
            **Sectores Principales:**
            - **Technology**: Software, semiconductores, hardware
            - **Financial**: Banca, seguros, servicios financieros
            - **Healthcare**: Farmacéuticas, biotecnología
            - **Energy**: Petróleo, gas, renovables
            - **Consumer**: Retail, productos de consumo
            - **Utilities**: Eléctricas, gas, agua
            - **Industrial**: Construcción, ingeniería, manufactura
            """)
        
        with st.expander("🎯 **MATRIZ ESTRATÉGICA**"):
            st.markdown("""
            **Matriz Rentabilidad vs Riesgo**
            - Eje X: Volatilidad (riesgo)
            - Eje Y: Total Return (rentabilidad esperada)
            - Tamaño de burbuja: Market Cap
            - Color: Score
            
            **Cuadrantes:**
            1. **Superior Izquierda**: Alto retorno, bajo riesgo (IDEAL)
            2. **Superior Derecha**: Alto retorno, alto riesgo (agresivo)
            3. **Inferior Izquierda**: Bajo retorno, bajo riesgo (conservador)
            4. **Inferior Derecha**: Bajo retorno, alto riesgo (EVITAR)
            
            **Matriz Dividendo vs Crecimiento**
            - Eje X: Dividend Yield
            - Eje Y: Upside %
            - Identifica estrategia: ¿Prefieres dividendos o crecimiento?
            """)
        
        st.markdown("---")
        st.info("""
        💡 **Consejo**: Ningún indicador es definitivo por sí solo. 
        Usa el **Score Mejorado v2.0** como punto de partida y analiza múltiples métricas 
        en conjunto para tomar decisiones informadas. El análisis técnico 
        complementa el análisis fundamental.
        """)


if __name__ == '__main__':
    main()