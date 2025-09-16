#!/usr/bin/env python3
"""
Menú Interactivo para el Analizador de Acciones
"""

from stock_analyzer import StockAnalyzer
import pandas as pd

class InteractiveMenu:
    def __init__(self):
        self.analyzer = StockAnalyzer()
        self.markets_data = {}
        self.all_stocks = pd.DataFrame()
        self.data_loaded = False

    def display_main_menu(self):
        """Muestra el menú principal"""
        print("\n" + "="*60)
        print("          ANALIZADOR DE ACCIONES POR MERCADO")
        print("="*60)
        print("1. Cargar datos de mercados")
        print("2. Ver resumen por mercado")
        print("3. Análisis por ratios fundamentales")
        print("4. Análisis de dividendos")
        print("5. Filtros personalizados")
        print("6. Comparativa entre mercados")
        print("7. Exportar datos a Excel")
        print("0. Salir")
        print("-"*60)

    def load_market_data(self):
        """Carga los datos de todos los mercados"""
        print("\nCargando datos de mercados...")
        print("Esto puede tomar varios minutos, por favor espera...")
        
        try:
            self.markets_data = self.analyzer.get_all_markets_data()
            self.all_stocks = pd.concat(self.markets_data.values(), ignore_index=True)
            self.data_loaded = True
            print("✓ Datos cargados exitosamente!")
            
            # Mostrar resumen rápido
            total_stocks = len(self.all_stocks)
            print(f"Total de acciones analizadas: {total_stocks}")
            
            for market_name, df in self.markets_data.items():
                print(f"  - {market_name}: {len(df)} acciones")
                
        except Exception as e:
            print(f"✗ Error al cargar datos: {str(e)}")

    def show_market_summary(self):
        """Muestra resumen por mercado"""
        if not self.data_loaded:
            print("⚠ Primero debes cargar los datos (opción 1)")
            return

        print("\n¿Qué mercado quieres ver?")
        print("1. IBEX 35")
        print("2. Medium Cap España")
        print("3. S&P 500")
        print("4. NASDAQ")
        print("5. Todos los mercados")
        
        choice = input("Selecciona una opción (1-5): ").strip()
        
        if choice == "1":
            self.analyzer.display_summary(self.markets_data['IBEX35'], "IBEX 35")
        elif choice == "2":
            self.analyzer.display_summary(self.markets_data['Medium_Cap'], "Medium Cap España")
        elif choice == "3":
            self.analyzer.display_summary(self.markets_data['SP500'], "S&P 500")
        elif choice == "4":
            self.analyzer.display_summary(self.markets_data['NASDAQ'], "NASDAQ")
        elif choice == "5":
            for market_name, df in self.markets_data.items():
                self.analyzer.display_summary(df, f"Mercado: {market_name}")
        else:
            print("Opción no válida")

    def fundamental_analysis_menu(self):
        """Menú de análisis fundamental"""
        if not self.data_loaded:
            print("⚠ Primero debes cargar los datos (opción 1)")
            return

        print("\n" + "="*50)
        print("         ANÁLISIS FUNDAMENTAL")
        print("="*50)
        print("1. Ordenar por P/E Ratio (menor = más barata)")
        print("2. Ordenar por P/B Ratio")
        print("3. Ordenar por ROE (mayor = mejor)")
        print("4. Ordenar por ROA")
        print("5. Ordenar por Margen de Beneficio")
        print("6. Ordenar por Deuda/Patrimonio")
        print("0. Volver al menú principal")
        
        choice = input("Selecciona una opción (0-6): ").strip()
        
        sort_options = {
            "1": ("PE_Ratio", True, "P/E Ratio (Menores primero)"),
            "2": ("PB_Ratio", True, "P/B Ratio (Menores primero)"),
            "3": ("ROE", False, "ROE (Mayores primero)"),
            "4": ("ROA", False, "ROA (Mayores primero)"),
            "5": ("Profit_Margin", False, "Margen de Beneficio (Mayores primero)"),
            "6": ("Debt_Equity", True, "Deuda/Patrimonio (Menores primero)")
        }
        
        if choice in sort_options:
            column, ascending, title = sort_options[choice]
            
            # Filtrar datos válidos
            valid_data = self.all_stocks[self.all_stocks[column].notna()]
            if column in ['PE_Ratio', 'PB_Ratio']:
                valid_data = valid_data[valid_data[column] > 0]
            
            sorted_data = self.analyzer.sort_by_fundamentals(valid_data, column, ascending)
            self.analyzer.display_summary(sorted_data.head(20), f"Top 20 - {title}")
        elif choice == "0":
            return
        else:
            print("Opción no válida")

    def dividend_analysis_menu(self):
        """Menú de análisis de dividendos"""
        if not self.data_loaded:
            print("⚠ Primero debes cargar los datos (opción 1)")
            return

        print("\n" + "="*50)
        print("         ANÁLISIS DE DIVIDENDOS")
        print("="*50)
        print("1. Mayores yields de dividendo")
        print("2. Mayores dividendos en euros/dólares")
        print("3. Menores payout ratios (más sostenibles)")
        print("4. Acciones con dividendos > 3%")
        print("5. Acciones con dividendos > 5%")
        print("0. Volver al menú principal")
        
        choice = input("Selecciona una opción (0-5): ").strip()
        
        if choice == "1":
            dividend_stocks = self.all_stocks[self.all_stocks['Dividend_Yield'] > 0]
            sorted_data = self.analyzer.sort_by_fundamentals(dividend_stocks, 'Dividend_Yield', False)
            self.analyzer.display_summary(sorted_data.head(20), "Top 20 - Mayores Yields de Dividendo")
            
        elif choice == "2":
            dividend_stocks = self.all_stocks[self.all_stocks['Dividend_Rate'] > 0]
            sorted_data = self.analyzer.sort_by_fundamentals(dividend_stocks, 'Dividend_Rate', False)
            self.analyzer.display_summary(sorted_data.head(20), "Top 20 - Mayores Dividendos Absolutos")
            
        elif choice == "3":
            payout_stocks = self.all_stocks[(self.all_stocks['Payout_Ratio'] > 0) & (self.all_stocks['Payout_Ratio'] < 1)]
            sorted_data = self.analyzer.sort_by_fundamentals(payout_stocks, 'Payout_Ratio', True)
            self.analyzer.display_summary(sorted_data.head(20), "Top 20 - Menores Payout Ratios")
            
        elif choice == "4":
            high_yield = self.all_stocks[self.all_stocks['Dividend_Yield'] > 0.03]
            sorted_data = self.analyzer.sort_by_fundamentals(high_yield, 'Dividend_Yield', False)
            self.analyzer.display_summary(sorted_data, "Acciones con Dividendo > 3%")
            
        elif choice == "5":
            very_high_yield = self.all_stocks[self.all_stocks['Dividend_Yield'] > 0.05]
            sorted_data = self.analyzer.sort_by_fundamentals(very_high_yield, 'Dividend_Yield', False)
            self.analyzer.display_summary(sorted_data, "Acciones con Dividendo > 5%")
            
        elif choice == "0":
            return
        else:
            print("Opción no válida")

    def custom_filters_menu(self):
        """Menú de filtros personalizados"""
        if not self.data_loaded:
            print("⚠ Primero debes cargar los datos (opción 1)")
            return

        print("\n" + "="*50)
        print("         FILTROS PERSONALIZADOS")
        print("="*50)
        print("1. Acciones Value (P/E < 15 y Dividend Yield > 2%)")
        print("2. Acciones Growth (ROE > 15% y Price Change > 10%)")
        print("3. Acciones con alta rentabilidad (ROE > 20%)")
        print("4. Acciones baratas y con dividendo (P/E < 12 y Div > 3%)")
        print("5. Filtro personalizado manual")
        print("0. Volver al menú principal")
        
        choice = input("Selecciona una opción (0-5): ").strip()
        
        if choice == "1":
            value_stocks = self.all_stocks[
                (self.all_stocks['PE_Ratio'] < 15) & 
                (self.all_stocks['PE_Ratio'] > 0) &
                (self.all_stocks['Dividend_Yield'] > 0.02)
            ]
            self.analyzer.display_summary(value_stocks, "Acciones Value")
            
        elif choice == "2":
            growth_stocks = self.all_stocks[
                (self.all_stocks['ROE'] > 0.15) & 
                (self.all_stocks['Price_Change_1Y'] > 10)
            ]
            self.analyzer.display_summary(growth_stocks, "Acciones Growth")
            
        elif choice == "3":
            high_roe_stocks = self.all_stocks[self.all_stocks['ROE'] > 0.20]
            sorted_data = self.analyzer.sort_by_fundamentals(high_roe_stocks, 'ROE', False)
            self.analyzer.display_summary(sorted_data, "Acciones con ROE > 20%")
            
        elif choice == "4":
            cheap_dividend = self.all_stocks[
                (self.all_stocks['PE_Ratio'] < 12) & 
                (self.all_stocks['PE_Ratio'] > 0) &
                (self.all_stocks['Dividend_Yield'] > 0.03)
            ]
            self.analyzer.display_summary(cheap_dividend, "Acciones Baratas con Buen Dividendo")
            
        elif choice == "5":
            self.manual_filter()
            
        elif choice == "0":
            return
        else:
            print("Opción no válida")

    def manual_filter(self):
        """Permite crear filtros manuales"""
        print("\nFiltros disponibles:")
        print("PE_Ratio, PB_Ratio, ROE, ROA, Dividend_Yield, Market_Cap, Beta")
        
        try:
            filter_col = input("¿Qué columna quieres filtrar?: ").strip()
            if filter_col not in self.all_stocks.columns:
                print("Columna no válida")
                return
            
            min_val = input("Valor mínimo (Enter para omitir): ").strip()
            max_val = input("Valor máximo (Enter para omitir): ").strip()
            
            filtered_data = self.all_stocks.copy()
            
            if min_val:
                filtered_data = filtered_data[filtered_data[filter_col] >= float(min_val)]
            
            if max_val:
                filtered_data = filtered_data[filtered_data[filter_col] <= float(max_val)]
            
            # Ordenar por la columna filtrada
            sorted_data = self.analyzer.sort_by_fundamentals(filtered_data, filter_col, False)
            self.analyzer.display_summary(sorted_data, f"Filtro personalizado: {filter_col}")
            
        except Exception as e:
            print(f"Error en el filtro: {str(e)}")

    def market_comparison(self):
        """Comparación entre mercados"""
        if not self.data_loaded:
            print("⚠ Primero debes cargar los datos (opción 1)")
            return

        print("\n" + "="*60)
        print("         COMPARATIVA ENTRE MERCADOS")
        print("="*60)
        
        for market_name, df in self.markets_data.items():
            if len(df) > 0:
                print(f"\n{market_name}:")
                print(f"  Acciones: {len(df)}")
                print(f"  P/E promedio: {df['PE_Ratio'].mean():.2f}")
                print(f"  Dividend Yield promedio: {df['Dividend_Yield'].mean()*100:.2f}%")
                print(f"  ROE promedio: {df['ROE'].mean()*100:.2f}%")
                print(f"  Rentabilidad 1Y promedio: {df['Price_Change_1Y'].mean():.2f}%")

    def export_to_excel(self):
        """Exporta los datos a Excel"""
        if not self.data_loaded:
            print("⚠ Primero debes cargar los datos (opción 1)")
            return

        try:
            filename = f"analisis_acciones_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Hoja con todos los datos
                self.all_stocks.to_excel(writer, sheet_name='Todas_las_Acciones', index=False)
                
                # Hojas por mercado
                for market_name, df in self.markets_data.items():
                    sheet_name = market_name.replace(' ', '_')[:31]  # Límite de Excel
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Hoja de top dividendos
                high_dividend = self.all_stocks[self.all_stocks['Dividend_Yield'] > 0]
                if len(high_dividend) > 0:
                    sorted_dividend = self.analyzer.sort_by_fundamentals(high_dividend, 'Dividend_Yield', False)
                    sorted_dividend.head(50).to_excel(writer, sheet_name='Top_Dividendos', index=False)
            
            print(f"✓ Datos exportados a: {filename}")
            
        except Exception as e:
            print(f"✗ Error al exportar: {str(e)}")

    def run(self):
        """Ejecuta el menú principal"""
        while True:
            self.display_main_menu()
            choice = input("Selecciona una opción (0-7): ").strip()
            
            if choice == "0":
                print("¡Hasta luego!")
                break
            elif choice == "1":
                self.load_market_data()
            elif choice == "2":
                self.show_market_summary()
            elif choice == "3":
                self.fundamental_analysis_menu()
            elif choice == "4":
                self.dividend_analysis_menu()
            elif choice == "5":
                self.custom_filters_menu()
            elif choice == "6":
                self.market_comparison()
            elif choice == "7":
                self.export_to_excel()
            else:
                print("Opción no válida. Por favor, selecciona un número del 0 al 7.")
            
            if choice != "0":
                input("\nPresiona Enter para continuar...")

def main():
    menu = InteractiveMenu()
    menu.run()

if __name__ == "__main__":
    main()