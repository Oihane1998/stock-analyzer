# 📈 Stock Analyzer - Analizador de Acciones

Aplicación web completa para análisis de acciones de múltiples mercados internacionales.

## 🌟 Características

- **📊 Análisis Multi-Mercado**: IBEX35, Medium Cap España, S&P 500, NASDAQ
- **💰 Análisis Fundamental**: P/E, ROE, ROA, márgenes, ratios de deuda
- **💵 Análisis de Dividendos**: Yields, sostenibilidad, crecimiento esperado
- **🚀 Predicción de Rentabilidad**: Algoritmo propio de rentabilidad esperada
- **🔍 Filtros Avanzados**: Estrategias predefinidas y filtros personalizados
- **📱 Interfaz Web Responsive**: Diseño moderno con Streamlit
- **💾 Cache Inteligente**: Persistencia de datos para mejor rendimiento

## 🚀 Instalación y Uso

### Requisitos
- Python 3.8+
- Conexión a internet para datos en tiempo real

### Instalación Local
```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/stock-analyzer.git
cd stock-analyzer

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
streamlit run app.py
```

### Acceso Web
La aplicación está desplegada en Streamlit Cloud:
**[🌐 Stock Analyzer Live](https://stock-analyzer.streamlit.app)**

### 📱 Menú interactivo en consola:
```bash
python menu.py
```

### ⚡ Ejecución directa del análisis:
```bash
python stock_analyzer.py
```

## Estructura del programa

```
ACCIONES JG/
├── app.py              # 🌐 Aplicación web Streamlit (PRINCIPAL)
├── stock_analyzer.py   # 🔧 Motor principal del análisis
├── menu.py            # 📱 Menú interactivo consola
├── requirements.txt   # 📦 Dependencias
└── README.md         # 📋 Este archivo
```

## 🌐 Interfaz Web Streamlit

La aplicación web incluye **5 pestañas principales**:

### 📊 **Pestañas Disponibles:**
1. **🏢 Por Mercado** - Análisis individual de cada mercado
2. **📊 Análisis Fundamental** - Ratios P/E, ROE, P/B con gráficos interactivos
3. **💰 Dividendos** - Filtros y rankings de dividendos
4. **🎯 Filtros Avanzados** - Estrategias predefinidas y filtros personalizables
5. **📋 Datos Completos** - Tabla completa con descarga CSV

### 🎯 **Características Web:**
- ✅ **Gráficos interactivos** con Plotly
- ✅ **Filtros en tiempo real**
- ✅ **Estrategias predefinidas** (Value, Growth, High Quality)
- ✅ **Comparativas visuales** entre mercados
- ✅ **Descarga de datos** en CSV
- ✅ **Cache inteligente** para mejor rendimiento

## 📱 Menú consola (menu.py)

```
1. Cargar datos de mercados
2. Ver resumen por mercado (IBEX35, Medium Cap, S&P500, NASDAQ)
3. Análisis por ratios fundamentales
4. Análisis de dividendos
5. Filtros personalizados
6. Comparativa entre mercados
7. Exportar datos a Excel
0. Salir
```

### Opciones destacadas:

**Análisis Fundamental (Opción 3):**
- Ordenar por P/E (acciones más baratas)
- Ordenar por ROE (mayor rentabilidad)
- Ordenar por margen de beneficio
- Y más ratios...

**Análisis de Dividendos (Opción 4):**
- Mayores yields de dividendo
- Acciones con dividendos > 3% o 5%
- Payout ratios más sostenibles

**Filtros Personalizados (Opción 5):**
- Acciones Value (P/E < 15 y Dividend > 2%)
- Acciones Growth (ROE > 15% y crecimiento > 10%)
- Filtros manuales personalizables

## Datos que obtiene

Para cada acción analiza:

**Datos básicos:**
- Precio actual, capitalización de mercado
- Volumen y precio máximo/mínimo 52 semanas
- Rentabilidad último año

**Ratios fundamentales:**
- P/E, P/B, P/S Ratios
- ROE, ROA, Margen de beneficio
- EV/Revenue, EV/EBITDA
- Relación Deuda/Patrimonio

**Información de dividendos:**
- Dividend Yield y tasa absoluta
- Payout Ratio
- Fecha ex-dividendo

**Datos adicionales:**
- Beta (volatilidad vs mercado)
- Volumen promedio
- Cambio de precio 1 año

## Fuente de datos

Utiliza **Yahoo Finance** através de la librería `yfinance`:
- Datos gratuitos y actualizados
- Información fundamental completa
- Histórico de precios y dividendos

## Símbolos incluidos

### IBEX 35
SAN.MC (Santander), BBVA.MC, ITX.MC (Inditex), TEF.MC (Telefónica), IBE.MC (Iberdrola), REP.MC (Repsol), y 29 más.

### Medium Cap España
ALM.MC (Almirall), CAF.MC, FCC.MC, GAM.MC (Grifols), y 22 más.

### S&P 500 (Top 50)
AAPL (Apple), MSFT (Microsoft), AMZN (Amazon), NVDA (Nvidia), GOOGL (Google), y 45 más.

### NASDAQ (Top 60)
AAPL (Apple), MSFT (Microsoft), AMZN (Amazon), NVDA (Nvidia), GOOGL (Google), GOOG, META (Meta), TSLA (Tesla), AVGO (Broadcom), INTC (Intel), AMD, NFLX (Netflix), y 48 más.

## Ejemplos de uso

### 🌐 **En la aplicación web:**

### 1. **Encontrar mejores acciones por dividendo:**
```
Pestaña "💰 Dividendos" → Ajustar filtros de yield → Ver ranking automático
```

### 2. **Buscar acciones baratas (Value):**
```
Pestaña "🎯 Filtros Avanzados" → Clic en "💎 Value Stocks"
```

### 3. **Comparar mercados visualmente:**
```
Pestaña "📊 Análisis Fundamental" → Seleccionar métrica → Ver gráfico comparativo
```

### 4. **Análisis de correlaciones:**
```
Pestaña "📊 Análisis Fundamental" → Seleccionar métricas X/Y → Ver gráfico scatter
```

### 📱 **En el menú consola:**

### 1. **Encontrar las mejores acciones por dividendo:**
```
Menu → Opción 4 → Opción 1 (Mayores yields)
```

### 2. **Buscar acciones baratas (bajo P/E):**
```
Menu → Opción 3 → Opción 1 (P/E Ratio)
```

### 3. **Acciones Value:**
```
Menu → Opción 5 → Opción 1 (Value stocks)
```

### 4. **Exportar análisis completo:**
```
Menu → Opción 7 (Exportar a Excel)
```

## Notas importantes

⚠️ **Tiempo de carga:** La primera carga puede tardar 3-5 minutos ya que descarga datos de ~100 acciones.

⚠️ **Conexión a Internet:** Requiere conexión estable para obtener datos actualizados.

⚠️ **Datos en tiempo real:** Los precios pueden tener 15-20 minutos de retraso.

## Solución de problemas

**Error de instalación:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Error de conexión:**
- Verificar conexión a Internet
- Algunos antivirus bloquean conexiones de Python

**Datos faltantes:**
- Algunas acciones pueden no tener todos los ratios disponibles
- El programa filtra automáticamente datos incompletos