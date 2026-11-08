from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title='Natural Gas Market Dashboard', page_icon='🔥', layout='wide')
DATA = Path(__file__).resolve().parent / 'data'

@st.cache_data
def load(name):
    p = DATA / name
    if not p.exists():
        st.error(f'Missing data file: data/{name}')
        st.stop()
    df = pd.read_csv(p)
    for c in ['Date', 'Origin_Date', 'Target_Date']:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors='coerce')
    return df

prices = load('henry_hub_prices.csv')
uk = load('uk_gas_three_series_validated.csv')
storage = load('eia_natural_gas_storage.csv')
seasonal = load('eia_gas_storage_seasonality.csv')
# Multiple exports can have the same filename but different schemas.
# Prefer the 12-week scenario file with explicit scenario columns.
def load_storage_scenarios():
    candidates = sorted(DATA.glob('natural_gas_storage_forecast*.csv'))
    required = {'Date', 'Base_Storage_Bcf', 'Higher_Storage_Bcf', 'Lower_Storage_Bcf'}
    for path in candidates:
        df = pd.read_csv(path)
        df.columns = df.columns.astype(str).str.strip()
        if required.issubset(df.columns):
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df = df.dropna(subset=['Date']).sort_values('Date')
            if not df.empty:
                return df, path.name
    return pd.DataFrame(), None

forecast, forecast_source = load_storage_scenarios()
intel = load('natural_gas_market_intelligence.csv')
backtest = load('natural_gas_forecast_backtest.csv')
exports = load('eia_us_lng_exports.csv')
weather = load('natural_gas_weather_analysis.csv')

st.title('Natural Gas Market Dashboard')
st.caption('UK · Europe · United States | Historical portfolio research, not live trading data')
st.info('Source snapshots: data through November 2026 where available. The European benchmark is monthly and is not a live TTF/NBP quote. Scenario forecasts are illustrative, not investment advice.')

last_price = prices.dropna(subset=['Henry_Hub_USD_MMBtu']).sort_values('Date').iloc[-1]
last_storage = storage.dropna(subset=['Storage_Bcf']).sort_values('Date').iloc[-1]
last_forecast = forecast.iloc[-1] if not forecast.empty else None
uk_latest = uk.sort_values('Date').groupby('Category').tail(1).set_index('Category')
a,b,c,d = st.columns(4)
a.metric('Henry Hub spot', f"${last_price['Henry_Hub_USD_MMBtu']:.2f}/MMBtu", help=f"Observation: {last_price['Date']:%Y-%m-%d}")
b.metric('US working gas', f"{last_storage['Storage_Bcf']:,.0f} Bcf", help=f"Observation: {last_storage['Date']:%Y-%m-%d}")
if last_forecast is not None:
    c.metric('12-week base storage', f"{last_forecast['Base_Storage_Bcf']:,.1f} Bcf", help=f"Scenario target: {last_forecast['Date']:%Y-%m-%d}")
else:
    c.metric('12-week base storage', 'Unavailable', help='No compatible 12-week scenario CSV was found')
if {'LNG','Demand'}.issubset(uk_latest.index) and uk_latest.loc['Demand','Value']:
    d.metric('Latest LNG / NTS demand', f"{100*uk_latest.loc['LNG','Value']/uk_latest.loc['Demand','Value']:.1f}%", help='Partial indicator; not a complete UK gas balance')

t1,t2,t3,t4,t5 = st.tabs(['Prices & Europe','UK fundamentals','US storage & forecast','Backtesting','Market intelligence'])
with t1:
    st.subheader('Henry Hub daily spot price')
    min_year = int(prices['Date'].dt.year.min())
    year = st.slider('Show prices from year', min_year, int(prices['Date'].dt.year.max()), max(2018,min_year))
    p = prices.loc[prices['Date'].dt.year >= year].set_index('Date')
    st.line_chart(p[['Henry_Hub_USD_MMBtu','MA_30']].rename(columns={'Henry_Hub_USD_MMBtu':'Henry Hub USD/MMBtu','MA_30':'30-day moving average'}))
    eu = intel[intel['Indicator'].astype(str).str.contains('Europe minus Henry Hub premium',case=False,na=False)].copy()
    if not eu.empty:
        st.subheader('European benchmark minus Henry Hub — monthly')
        eu['Value'] = pd.to_numeric(eu['Value'], errors='coerce')
        st.line_chart(eu.dropna(subset=['Date','Value']).sort_values('Date').set_index('Date')['Value'])
    st.caption('European prices use the IMF/FRED monthly European benchmark; the differential is not an executable LNG arbitrage margin and excludes liquefaction, shipping and regasification.')
with t2:
    st.subheader('National Gas Transmission operational series')
    st.warning('The source data manifest flags a late-period LNG spike for independent verification. These are published system-entry observations, not LNG cargo arrivals.')
    for category,title in [('Demand','NTS actual demand (mscm)'),('Linepack','Closing linepack (mscm)'),('LNG','LNG physical system entry (mscm)')]:
        part = uk[uk['Category'].eq(category)].sort_values('Date')
        st.markdown(f'**{title}**')
        st.line_chart(part.set_index('Date')['Value'])
    demand = uk[uk['Category'].eq('Demand')][['Date','Value']].rename(columns={'Value':'Demand'})
    lng = uk[uk['Category'].eq('LNG')][['Date','Value']].rename(columns={'Value':'LNG'})
    ratio = demand.merge(lng,on='Date').query('Demand > 0').sort_values('Date')
    ratio['LNG entry / NTS demand (%)'] = 100*ratio['LNG']/ratio['Demand']
    st.subheader('LNG entry as a share of NTS demand')
    st.line_chart(ratio.set_index('Date')['LNG entry / NTS demand (%)'])
    st.caption('This ratio does not capture pipeline imports, domestic production, other entry points, exports or all storage flows. It is not a full supply-demand balance.')
with t3:
    st.subheader('US Lower 48 working gas in storage')
    years = st.slider('Storage history from year', int(storage['Date'].dt.year.min()), int(storage['Date'].dt.year.max()), 2018)
    st.line_chart(storage[storage['Date'].dt.year >= years].set_index('Date')['Storage_Bcf'])
    st.subheader('12-week seasonal storage scenarios')
    if not forecast.empty:
        f = forecast.set_index('Date')
        st.line_chart(f[['Lower_Storage_Bcf','Base_Forecast_Bcf','Higher_Storage_Bcf']].rename(columns={'Lower_Storage_Bcf':'Lower storage','Base_Forecast_Bcf':'Base forecast','Higher_Storage_Bcf':'Higher storage'}))
        origin = str(forecast['Forecast_Origin_Date'].iloc[0]) if 'Forecast_Origin_Date' in forecast else 'see source data'
        adjustment = f"±{forecast['Scenario_Adjustment_Bcf_Per_Week'].iloc[0]:g} Bcf/week" if 'Scenario_Adjustment_Bcf_Per_Week' in forecast else 'illustrative'
        st.caption(f'Forecast origin: {origin}. Scenario adjustments: {adjustment}. These are not probability bounds or official EIA forecasts. Source: {forecast_source}.')
    else:
        st.warning('No compatible storage-scenario CSV was found. The historical storage chart remains available.')
    st.subheader('Recent storage versus five-year seasonal average')
    recent = seasonal.dropna(subset=['Storage_Bcf','Five_Year_Avg_Bcf']).sort_values('Date').tail(104).set_index('Date')
    st.line_chart(recent[['Storage_Bcf','Five_Year_Avg_Bcf']])
    st.subheader('US LNG exports — monthly')
    st.line_chart(exports.sort_values('Date').set_index('Date')['LNG_Exports_Bcf_Per_Day'])
with t4:
    st.subheader('Historical seasonal forecast backtest')
    st.caption('Errors are measured against historical storage observations. Forecast windows overlap; results are not independent. The no-change forecast is a baseline, not a competing seasonal model.')
    bt = backtest.dropna(subset=['Horizon_Weeks','Absolute_Error_Bcf','Naive_Absolute_Error_Bcf'])
    summary = bt.groupby('Horizon_Weeks').agg(Tests=('Absolute_Error_Bcf','size'),Seasonal_MAE_Bcf=('Absolute_Error_Bcf','mean'),No_Change_MAE_Bcf=('Naive_Absolute_Error_Bcf','mean')).reset_index()
    summary['MAE_Improvement_Pct'] = 100*(1-summary['Seasonal_MAE_Bcf']/summary['No_Change_MAE_Bcf'])
    st.dataframe(summary.style.format({'Seasonal_MAE_Bcf':'{:.2f}','No_Change_MAE_Bcf':'{:.2f}','MAE_Improvement_Pct':'{:.1f}%'}),use_container_width=True,hide_index=True)
    st.bar_chart(summary.set_index('Horizon_Weeks')[['Seasonal_MAE_Bcf','No_Change_MAE_Bcf']])
    st.subheader('Illustrative three-city weather proxy')
    st.line_chart(weather.sort_values('Date').tail(156).set_index('Date')[['HDD_Weekly','CDD_Weekly']])
    st.caption('Chicago, New York and Dallas weather proxy is not a nationally weighted US gas demand indicator.')
with t5:
    st.subheader('Evidence and market intelligence')
    final_path = DATA / 'natural_gas_final_trading_intelligence.csv'
    if final_path.exists():
        st.markdown('**Final corrected trading intelligence**')
        st.dataframe(pd.read_csv(final_path), use_container_width=True, hide_index=True)
    corrected_path = DATA / 'natural_gas_corrected_market_analysis.csv'
    if corrected_path.exists():
        with st.expander('Corrected market analysis — source table'):
            st.dataframe(pd.read_csv(corrected_path), use_container_width=True, hide_index=True)
    st.caption('The following observations are sourced from the exported analysis. Interpretations should be read alongside their observation dates and limitations.')
    categories = sorted(intel['Category'].dropna().astype(str).unique())
    selection = st.selectbox('Select analysis category',categories)
    view = intel[intel['Category'].astype(str).eq(selection)].copy().sort_values('Date',ascending=False)
    st.dataframe(view, use_container_width=True, hide_index=True)
    st.markdown('**Interpretation safeguards:** European benchmark spreads are not LNG netbacks; UK LNG entry is not a full balance; US storage forecasts are not price forecasts; no trading signal is a recommendation.')

st.divider()
st.caption('Data sources: EIA, FRED/IMF, National Gas Transmission and Open-Meteo. See README and the original research notebook for methods and source limitations.')
