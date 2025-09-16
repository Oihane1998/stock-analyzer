#!/usr/bin/env python3
"""
Analizador Completo de Acciones por Mercado
Incluye análisis fundamental, dividendos, persistencia de datos y predicción de rentabilidad
IBEX35, Medium Cap España, S&P 500 y NASDAQ
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import warnings
import os
import pickle
from pathlib import Path
import logging

warnings.filterwarnings('ignore')

class StockAnalyzer:
    def __init__(self, data_dir="data", cache_hours=24):
        """
        Analizador completo de acciones
        Args:
            data_dir: Directorio para archivos de cache
            cache_hours: Horas antes de considerar datos obsoletos
        """
        # Configurar persistencia de datos
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.cache_hours = cache_hours
        
        # Archivos de datos
        self.markets_file = self.data_dir / "markets_data.parquet"
        self.all_stocks_file = self.data_dir / "all_stocks.parquet"
        self.metadata_file = self.data_dir / "metadata.pkl"
        
        # Configurar logging
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger(__name__)
        
        # Símbolos de mercados (limpios, sin delisted)
        self.ibex35_symbols = [
            'SAN.MC', 'BBVA.MC', 'ITX.MC', 'TEF.MC', 'IBE.MC', 'REP.MC',
            'CABK.MC', 'AMS.MC', 'ENG.MC', 'FER.MC', 'ACS.MC', 'AENA.MC',
            'SAB.MC', 'ELE.MC', 'GRF.MC', 'IAG.MC', 'MTS.MC', 'ACX.MC',
            'CLNX.MC', 'COL.MC', 'MAP.MC', 'MRL.MC', 'ANA.MC', 'NTGY.MC',
            'RED.MC', 'SCYR.MC', 'UNI.MC', 'VIS.MC', 'FDR.MC',
            'IDR.MC', 'LOG.MC', 'MEL.MC', 'PHM.MC', 'RJF.MC'
        ]
        
        self.medium_cap_symbols = [
            'ALM.MC', 'CAF.MC', 'CIE.MC', 'DIA.MC', 'ENC.MC',
            'FCC.MC', 'GAM.MC', 'MDF.MC', 'NEA.MC', 'NHH.MC',
            'PRS.MC', 'PSG.MC', 'SLR.MC', 'TRE.MC', 'TUB.MC'
        ]
        
        self.sp500_top_symbols = [
            'AAPL', 'MSFT', 'AMZN', 'NVDA', 'GOOGL', 'TSLA', 'META', 'BRK-B',
            'UNH', 'JNJ', 'JPM', 'V', 'PG', 'XOM', 'HD', 'CVX', 'MA',
            'PFE', 'ABBV', 'BAC', 'KO', 'COST', 'AVGO', 'PEP', 'TMO',
            'WMT', 'DIS', 'ABT', 'CRM', 'ACN', 'VZ', 'ADBE', 'DHR', 'TXN',
            'NEE', 'NKE', 'BMY', 'NFLX', 'PM', 'RTX', 'T', 'LOW', 'QCOM',
            'HON', 'UPS', 'SPGI', 'LIN', 'SBUX', 'AMD', 'AMGN'
        ]
        
        self.nasdaq_top_symbols = [
            'AAPL', 'MSFT', 'AMZN', 'NVDA', 'GOOGL', 'GOOG', 'META', 'TSLA',
            'AVGO', 'PEP', 'COST', 'NFLX', 'ADBE', 'QCOM', 'TXN', 'INTC',
            'AMGN', 'HON', 'SBUX', 'AMD', 'INTU', 'ISRG', 'BKNG', 'GILD',
            'LRCX', 'REGN', 'ADI', 'MDLZ', 'VRTX', 'KLAC', 'MELI', 'SNPS',
            'CDNS', 'MAR', 'CSX', 'ORLY', 'FTNT', 'NXPI', 'ADSK', 'MCHP',
            'ABNB', 'ROP', 'WDAY', 'MNST', 'PCAR', 'CPRT', 'FANG', 'PAYX',
            'ODFL', 'FAST', 'ROST', 'BZ', 'EA', 'VRSK', 'CTSH', 'DDOG',
            'TEAM', 'CHTR', 'ZS', 'CRWD'
        ]
        
        # Pesos para análisis de rentabilidad
        self.profitability_weights = {
            'dividend_yield': 0.25,
            'dividend_growth': 0.15,
            'price_momentum': 0.20,
            'fundamental_strength': 0.25,
            'valuation_attractiveness': 0.15
        }

    # ===== MÉTODOS DE OBTENCIÓN DE DATOS =====
    
    def get_stock_data(self, symbols: List[str], market_name: str) -> pd.DataFrame:
        """Obtiene datos de acciones para una lista de símbolos"""
        # print(f"Obteniendo datos para {market_name}...")
        
        stock_data = []
        
        for symbol in symbols:
            try:
                stock = yf.Ticker(symbol)
                info = stock.info
                hist = stock.history(period="1y")
                
                if hist.empty or not info:
                    continue
                
                # Datos básicos
                data = {
                    'Symbol': symbol,
                    'Name': info.get('longName', symbol),
                    'Market': market_name,
                    'Price': hist['Close'].iloc[-1] if not hist.empty else None,
                    'Market_Cap': info.get('marketCap', None),
                    'Currency': info.get('currency', 'EUR' if '.MC' in symbol else 'USD'),
                }
                
                # Ratios fundamentales
                data.update({
                    'PE_Ratio': info.get('forwardPE', info.get('trailingPE', None)),
                    'PB_Ratio': info.get('priceToBook', None),
                    'PS_Ratio': info.get('priceToSalesTrailing12Months', None),
                    'EV_Revenue': info.get('enterpriseToRevenue', None),
                    'EV_EBITDA': info.get('enterpriseToEbitda', None),
                    'ROE': info.get('returnOnEquity', None),
                    'ROA': info.get('returnOnAssets', None),
                    'Profit_Margin': info.get('profitMargins', None),
                    'Debt_Equity': info.get('debtToEquity', None),
                })
                
                # Datos de dividendos
                data.update({
                    'Dividend_Yield': info.get('dividendYield', None),
                    'Dividend_Rate': info.get('dividendRate', None),
                    'Payout_Ratio': info.get('payoutRatio', None),
                    'Ex_Dividend_Date': info.get('exDividendDate', None),
                })
                
                # Datos adicionales
                data.update({
                    'Beta': info.get('beta', None),
                    'Volume': hist['Volume'].iloc[-1] if not hist.empty else None,
                    'Avg_Volume': info.get('averageVolume', None),
                    '52W_High': info.get('fiftyTwoWeekHigh', None),
                    '52W_Low': info.get('fiftyTwoWeekLow', None),
                    'Price_Change_1Y': ((hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100) if len(hist) > 0 else None,
                })
                
                stock_data.append(data)
                
            except Exception as e:
                # print(f"Error obteniendo datos para {symbol}: {str(e)}")
                continue
        
        return pd.DataFrame(stock_data)

    def get_all_markets_data(self) -> Dict[str, pd.DataFrame]:
        """Obtiene datos de todos los mercados"""
        markets_data = {}
        
        # IBEX 35
        markets_data['IBEX35'] = self.get_stock_data(self.ibex35_symbols, 'IBEX35')
        
        # Medium Cap Españolas  
        markets_data['Medium_Cap'] = self.get_stock_data(self.medium_cap_symbols, 'Medium Cap España')
        
        # S&P 500 (top 50)
        markets_data['SP500'] = self.get_stock_data(self.sp500_top_symbols, 'S&P 500')
        
        # NASDAQ (top 60)
        markets_data['NASDAQ'] = self.get_stock_data(self.nasdaq_top_symbols, 'NASDAQ')
        
        return markets_data

    # ===== MÉTODOS DE PERSISTENCIA =====
    
    def _is_data_fresh(self) -> bool:
        """Verifica si los datos locales están actualizados"""
        if not self.metadata_file.exists():
            return False
        
        try:
            with open(self.metadata_file, 'rb') as f:
                metadata = pickle.load(f)
            
            last_update = metadata.get('last_update')
            if not last_update:
                return False
            
            time_diff = datetime.now() - last_update
            return time_diff.total_seconds() < (self.cache_hours * 3600)
            
        except Exception as e:
            self.logger.error(f"Error leyendo metadata: {e}")
            return False

    def _save_metadata(self, markets_data: dict, all_stocks: pd.DataFrame):
        """Guarda metadata de la sesión"""
        metadata = {
            'last_update': datetime.now(),
            'total_stocks': len(all_stocks),
            'markets': {name: len(df) for name, df in markets_data.items()},
            'cache_hours': self.cache_hours
        }
        
        with open(self.metadata_file, 'wb') as f:
            pickle.dump(metadata, f)

    def _save_to_cache(self, markets_data: dict, all_stocks: pd.DataFrame):
        """Guarda datos en cache local"""
        try:
            all_stocks.to_parquet(self.all_stocks_file, compression='snappy')
            self._save_metadata(markets_data, all_stocks)
            
            for market_name, df in markets_data.items():
                market_file = self.data_dir / f"{market_name}_data.parquet"
                df.to_parquet(market_file, compression='snappy')
            
            self.logger.info(f"✅ Datos guardados en cache: {len(all_stocks)} acciones")
            
        except Exception as e:
            self.logger.error(f"Error guardando cache: {e}")

    def _get_market_key(self, market_name: str) -> str:
        """Convierte nombre de mercado a clave estándar"""
        market_mapping = {
            'IBEX35': 'IBEX35',
            'Medium Cap España': 'Medium_Cap',
            'S&P 500': 'SP500',
            'NASDAQ': 'NASDAQ'
        }
        
        for key, value in market_mapping.items():
            if market_name == key:
                return value
        
        return market_name.replace(' ', '_').replace('&', '')

    def load_data(self, force_refresh: bool = False) -> tuple:
        """
        Carga datos desde cache local o descarga nuevos si es necesario
        """
        if not force_refresh and self._is_data_fresh() and self.all_stocks_file.exists():
            try:
                self.logger.info("Cargando datos desde cache local...")
                
                all_stocks = pd.read_parquet(self.all_stocks_file)
                
                markets_data = {}
                for market in all_stocks['Market'].unique():
                    markets_data[self._get_market_key(market)] = all_stocks[
                        all_stocks['Market'] == market
                    ].copy()
                
                self.logger.info(f"✅ Datos cargados desde cache: {len(all_stocks)} acciones")
                return markets_data, all_stocks
                
            except Exception as e:
                self.logger.error(f"Error cargando cache: {e}")
                self.logger.info("Procediendo a descargar datos nuevos...")

        # Descargar datos nuevos
        self.logger.info("Descargando datos actualizados...")
        markets_data = self.get_all_markets_data()
        all_stocks = pd.concat(markets_data.values(), ignore_index=True)
        
        self._save_to_cache(markets_data, all_stocks)
        
        return markets_data, all_stocks

    def get_cache_info(self) -> dict:
        """Retorna información del cache actual"""
        if not self.metadata_file.exists():
            return {"status": "No cache", "last_update": None}
        
        try:
            with open(self.metadata_file, 'rb') as f:
                metadata = pickle.load(f)
            
            last_update = metadata.get('last_update')
            age_hours = (datetime.now() - last_update).total_seconds() / 3600
            
            return {
                "status": "Fresh" if age_hours < self.cache_hours else "Stale",
                "last_update": last_update,
                "age_hours": round(age_hours, 1),
                "total_stocks": metadata.get('total_stocks', 0),
                "markets": metadata.get('markets', {}),
                "cache_file_size": self._get_file_size(self.all_stocks_file)
            }
        except Exception as e:
            return {"status": "Error", "error": str(e)}

    def _get_file_size(self, filepath: Path) -> str:
        """Retorna tamaño del archivo en formato legible"""
        if not filepath.exists():
            return "0 KB"
        
        size_bytes = filepath.stat().st_size
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes/1024:.1f} KB"
        else:
            return f"{size_bytes/(1024**2):.1f} MB"

    def clear_cache(self):
        """Elimina todos los archivos de cache"""
        try:
            files_deleted = 0
            for file in self.data_dir.glob("*.parquet"):
                file.unlink()
                files_deleted += 1
            
            if self.metadata_file.exists():
                self.metadata_file.unlink()
                files_deleted += 1
            
            self.logger.info(f"✅ Cache limpiado: {files_deleted} archivos eliminados")
        except Exception as e:
            self.logger.error(f"Error limpiando cache: {e}")

    # ===== MÉTODOS DE ANÁLISIS FUNDAMENTAL =====

    def sort_by_fundamentals(self, df: pd.DataFrame, sort_by: str = 'PE_Ratio', ascending: bool = True) -> pd.DataFrame:
        """Ordena el DataFrame por análisis fundamental"""
        if sort_by not in df.columns:
            # print(f"Columna {sort_by} no encontrada. Columnas disponibles:")
            # print(df.columns.tolist())
            return df
        
        return df.sort_values(by=sort_by, ascending=ascending, na_position='last')

    def filter_by_criteria(self, df: pd.DataFrame, **criteria) -> pd.DataFrame:
        """Filtra acciones por criterios específicos"""
        filtered_df = df.copy()
        
        for key, value in criteria.items():
            if key in df.columns:
                if isinstance(value, tuple):
                    min_val, max_val = value
                    if min_val is not None:
                        filtered_df = filtered_df[filtered_df[key] >= min_val]
                    if max_val is not None:
                        filtered_df = filtered_df[filtered_df[key] <= max_val]
                else:
                    filtered_df = filtered_df[filtered_df[key] == value]
        
        return filtered_df

    def display_summary(self, df: pd.DataFrame, title: str = "Resumen de Acciones"):
        """Muestra un resumen de las acciones"""
        # print(f"\n{'='*60}")
        # print(f"{title}")
        # print(f"{'='*60}")
        # print(f"Total de acciones: {len(df)}")
        
        if len(df) > 0:
            display_cols = [
                'Symbol', 'Name', 'Price', 'Market_Cap', 'PE_Ratio', 
                'Dividend_Yield', 'ROE', 'Price_Change_1Y'
            ]
            
            available_cols = [col for col in display_cols if col in df.columns]
            
            # print("\nPrimeras 10 acciones:")
            display_df = df[available_cols].head(10)
            
            # Formatear números
            if 'Price' in display_df.columns:
                display_df['Price'] = display_df['Price'].round(2)
            if 'PE_Ratio' in display_df.columns:
                display_df['PE_Ratio'] = display_df['PE_Ratio'].round(2)
            if 'Dividend_Yield' in display_df.columns:
                display_df['Dividend_Yield'] = (display_df['Dividend_Yield'] * 100).round(2)
            if 'ROE' in display_df.columns:
                display_df['ROE'] = (display_df['ROE'] * 100).round(2)
            if 'Price_Change_1Y' in display_df.columns:
                display_df['Price_Change_1Y'] = display_df['Price_Change_1Y'].round(2)
            
            # print(display_df.to_string(index=False))

    # ===== MÉTODOS DE ANÁLISIS DE RENTABILIDAD =====

    def calculate_dividend_score(self, df: pd.DataFrame) -> pd.Series:
        """Calcula score de dividendos basado en yield y sostenibilidad (CORREGIDO)"""
        dividend_yield = df['Dividend_Yield'].fillna(0)
        # Normalizar dividend yield: 5% = 10 puntos, máximo 10 puntos
        yield_score = np.clip(dividend_yield * 200, 0, 10)
        
        payout_ratio = df['Payout_Ratio'].fillna(0.7)  # Asumir 70% si no hay datos
        sustainability_score = np.where(
            payout_ratio <= 0.6, 8,      # Excelente sostenibilidad
            np.where(payout_ratio <= 0.8, 6,   # Buena sostenibilidad
                     np.where(payout_ratio <= 1.0, 3, 0))  # Regular/mala
        )
        
        return (yield_score * 0.6) + (sustainability_score * 0.4)
    
    def calculate_dividend_growth_score(self, df: pd.DataFrame) -> pd.Series:
        """Estima potencial de crecimiento de dividendos (CORREGIDO)"""
        roe = df['ROE'].fillna(0)
        payout_ratio = df['Payout_Ratio'].fillna(0.6)  # Asumir 60% si no hay datos
        
        # Tasa de retención para reinversión
        retention_ratio = np.clip(1 - payout_ratio, 0, 1)
        
        # Potencial de crecimiento sostenible
        sustainable_growth = roe * retention_ratio
        
        # Normalizar a escala 0-10: 15% crecimiento = 10 puntos
        growth_score = np.clip(sustainable_growth * 66.67, 0, 10)
        
        return growth_score
    
    def calculate_price_momentum_score(self, df: pd.DataFrame) -> pd.Series:
        """Calcula momentum de precio y tendencia"""
        price_change_1y = df['Price_Change_1Y'].fillna(0)
        
        return np.where(
            price_change_1y > 20, 9,
            np.where(price_change_1y > 10, 8,
                     np.where(price_change_1y > 0, 6,
                              np.where(price_change_1y > -10, 4,
                                       np.where(price_change_1y > -20, 2, 0))))
        )
    
    def calculate_fundamental_strength_score(self, df: pd.DataFrame) -> pd.Series:
        """Evalúa fortaleza fundamental (ROE, ROA, Margen)"""
        roe = df['ROE'].fillna(0)
        roa = df['ROA'].fillna(0)
        profit_margin = df['Profit_Margin'].fillna(0)
        
        roe_score = np.where(
            roe > 0.20, 4,
            np.where(roe > 0.15, 3,
                     np.where(roe > 0.10, 2,
                              np.where(roe > 0.05, 1, 0)))
        )
        
        roa_score = np.where(
            roa > 0.10, 3,
            np.where(roa > 0.05, 2,
                     np.where(roa > 0.02, 1, 0))
        )
        
        margin_score = np.where(
            profit_margin > 0.20, 3,
            np.where(profit_margin > 0.10, 2,
                     np.where(profit_margin > 0.05, 1, 0))
        )
        
        return roe_score + roa_score + margin_score
    
    def calculate_valuation_attractiveness_score(self, df: pd.DataFrame) -> pd.Series:
        """Evalúa atractivo de valoración (P/E, P/B)"""
        pe_ratio = df['PE_Ratio'].fillna(50)
        pb_ratio = df['PB_Ratio'].fillna(5)
        
        pe_score = np.where(
            pe_ratio < 10, 6,
            np.where(pe_ratio < 15, 5,
                     np.where(pe_ratio < 20, 4,
                              np.where(pe_ratio < 25, 3,
                                       np.where(pe_ratio < 30, 2, 1))))
        )
        
        pb_score = np.where(
            pb_ratio < 1.0, 4,
            np.where(pb_ratio < 1.5, 3,
                     np.where(pb_ratio < 2.0, 2,
                              np.where(pb_ratio < 3.0, 1, 0)))
        )
        
        return pe_score + pb_score

    def calculate_total_expected_return(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula rentabilidad esperada total para el próximo año"""
        result_df = df.copy()
        
        # Calcular cada componente del score
        dividend_score = self.calculate_dividend_score(df)
        dividend_growth_score = self.calculate_dividend_growth_score(df)
        momentum_score = self.calculate_price_momentum_score(df)
        fundamental_score = self.calculate_fundamental_strength_score(df)
        valuation_score = self.calculate_valuation_attractiveness_score(df)
        
        # Aplicar pesos y calcular score total
        total_score = (
            dividend_score * self.profitability_weights['dividend_yield'] +
            dividend_growth_score * self.profitability_weights['dividend_growth'] +
            momentum_score * self.profitability_weights['price_momentum'] +
            fundamental_score * self.profitability_weights['fundamental_strength'] +
            valuation_score * self.profitability_weights['valuation_attractiveness']
        )
        
        # Calcular rentabilidad esperada (CORREGIDO - VERSIÓN REALISTA)
        current_dividend_yield = df['Dividend_Yield'].fillna(0)
        
        # Apreciación basada en score total, máximo realista 15% anual
        score_factor = np.clip(total_score / 10, 0, 1)  # Normalizar 0-1
        potential_appreciation = score_factor * 0.15  # Máximo 15% apreciación
        
        # Rentabilidad total realista
        total_expected_return = current_dividend_yield + potential_appreciation
        
        # Añadir columnas al DataFrame
        result_df['Dividend_Score'] = dividend_score.round(2)
        result_df['Dividend_Growth_Score'] = dividend_growth_score.round(2)
        result_df['Momentum_Score'] = momentum_score.round(2)
        result_df['Fundamental_Score'] = fundamental_score.round(2)
        result_df['Valuation_Score'] = valuation_score.round(2)
        result_df['Total_Score'] = total_score.round(2)
        result_df['Expected_Total_Return'] = (total_expected_return * 100).round(2)
        
        # Calcular dividendos esperados próximo año (CORREGIDO)
        # Crecimiento de dividendos realista: máximo 3% adicional al yield actual
        dividend_growth_factor = np.clip(dividend_growth_score / 200, 0, 0.03)  # Máximo 3% adicional
        next_year_dividend_yield = current_dividend_yield * (1 + dividend_growth_factor)
        result_df['Expected_Dividend_Yield'] = (next_year_dividend_yield * 100).round(2)
        
        # Calcular apreciación esperada del precio
        result_df['Expected_Price_Appreciation'] = (potential_appreciation * 100).round(2)
        
        return result_df

    def get_top_profitable_stocks(self, df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
        """Obtiene las top N acciones más rentables esperadas"""
        analyzed_df = self.calculate_total_expected_return(df)
        
        # Filtrar acciones con datos mínimos
        valid_stocks = analyzed_df[
            (analyzed_df['PE_Ratio'].notna()) |
            (analyzed_df['Dividend_Yield'].notna()) |
            (analyzed_df['ROE'].notna())
        ].copy()
        
        # Ordenar por rentabilidad esperada total
        top_stocks = valid_stocks.nlargest(top_n, 'Expected_Total_Return')
        
        return top_stocks

    def create_profitability_summary(self, df: pd.DataFrame) -> dict:
        """Crea resumen de rentabilidad por mercado"""
        summary = {}
        
        for market in df['Market'].unique():
            market_data = df[df['Market'] == market]
            
            if len(market_data) > 0:
                summary[market] = {
                    'avg_expected_return': market_data['Expected_Total_Return'].mean(),
                    'avg_dividend_yield': market_data['Expected_Dividend_Yield'].mean(),
                    'avg_score': market_data['Total_Score'].mean(),
                    'top_stock': market_data.nlargest(1, 'Expected_Total_Return')['Symbol'].iloc[0]
                }
        
        return summary

    # ===== MÉTODOS DE EXPORTACIÓN =====

    def export_to_excel(self, all_stocks: pd.DataFrame, markets_data: dict, filename: str = None):
        """Exporta datos a Excel con formato mejorado"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"analisis_acciones_{timestamp}.xlsx"
        
        filepath = self.data_dir / filename
        
        try:
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Hoja principal
                all_stocks.to_excel(writer, sheet_name='Todas_Acciones', index=False)
                
                # Hojas por mercado
                for market_name, df in markets_data.items():
                    sheet_name = market_name.replace(' ', '_')[:31]
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Hoja de estadísticas
                stats_data = []
                for market_name, df in markets_data.items():
                    stats_data.append({
                        'Mercado': market_name,
                        'Acciones': len(df),
                        'P/E Promedio': df['PE_Ratio'].mean(),
                        'Dividend Yield Promedio': df['Dividend_Yield'].mean(),
                        'ROE Promedio': df['ROE'].mean(),
                        'Cap. Mercado Promedio': df['Market_Cap'].mean()
                    })
                
                stats_df = pd.DataFrame(stats_data)
                stats_df.to_excel(writer, sheet_name='Estadisticas_Mercados', index=False)
                
                # Hoja de top rentabilidad (si existe)
                if 'Expected_Total_Return' in all_stocks.columns:
                    top_profitable = self.get_top_profitable_stocks(all_stocks, 20)
                    top_profitable.to_excel(writer, sheet_name='Top_Rentabilidad', index=False)
            
            self.logger.info(f"✅ Datos exportados a: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Error exportando Excel: {e}")
            return None


def main():
    """Función principal para ejecutar el análisis"""
    analyzer = StockAnalyzer()
    
    # print("Iniciando análisis completo de mercados de acciones...")
    # print("Esto puede tomar varios minutos...")
    
    # Obtener datos de todos los mercados
    markets_data, all_stocks = analyzer.load_data()
    
    # Mostrar resúmenes por mercado
    for market_name, df in markets_data.items():
        analyzer.display_summary(df, f"Mercado: {market_name}")
    
    # Análisis de rentabilidad
    # print(f"\n{'='*60}")
    # print("ANÁLISIS DE RENTABILIDAD ESPERADA")
    # print(f"{'='*60}")
    
    # Calcular rentabilidad esperada
    all_stocks_analyzed = analyzer.calculate_total_expected_return(all_stocks)
    
    # Top 20 más rentables
    top_profitable = analyzer.get_top_profitable_stocks(all_stocks_analyzed, 20)
    analyzer.display_summary(top_profitable, "Top 20 - Mayor Rentabilidad Esperada")
    
    # Análisis comparativo tradicional
    # print(f"\n{'='*60}")
    # print("ANÁLISIS COMPARATIVO TRADICIONAL")
    # print(f"{'='*60}")
    
    # Top dividendos
    high_dividend = analyzer.sort_by_fundamentals(
        all_stocks[all_stocks['Dividend_Yield'] > 0], 
        'Dividend_Yield', 
        ascending=False
    )
    analyzer.display_summary(high_dividend.head(10), "Top 10 - Mayores Dividendos")
    
    # Mejor ROE
    high_roe = analyzer.sort_by_fundamentals(
        all_stocks[all_stocks['ROE'] > 0], 
        'ROE', 
        ascending=False
    )
    analyzer.display_summary(high_roe.head(10), "Top 10 - Mayor ROE")
    
    # Menor P/E (más baratas)
    low_pe = analyzer.sort_by_fundamentals(
        all_stocks[(all_stocks['PE_Ratio'] > 0) & (all_stocks['PE_Ratio'] < 50)], 
        'PE_Ratio', 
        ascending=True
    )
    analyzer.display_summary(low_pe.head(10), "Top 10 - Menor P/E (Más Baratas)")
    
    return markets_data, all_stocks_analyzed


if __name__ == "__main__":
    markets_data, all_stocks = main()