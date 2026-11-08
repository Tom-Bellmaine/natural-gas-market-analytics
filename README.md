Natural Gas Market Analytics

Python | Energy Markets | LNG | Storage Forecasting | Trading Intelligence

Project Overview

A Python-based natural gas market analytics project examining UK, European and US gas fundamentals.

The project combines publicly available energy market data with seasonal forecasting, historical backtesting and evidence-based market analysis. It is designed to demonstrate skills relevant to natural gas trading, commodity research and energy market analyst roles.

Key Features

1. European and US Gas Pricing

* Compared European natural gas benchmark prices with US Henry Hub spot prices.
* Calculated monthly price differentials to examine transatlantic market relationships.
* Identified a European benchmark premium of $22.54/MMBtu in September 2026.
* Distinguished benchmark price spreads from executable LNG arbitrage margins.

2. UK Gas Market Fundamentals

* Analysed National Gas Transmission data covering UK NTS demand, linepack and LNG entry volumes.
* Developed visualisations of all three operational indicators.
* Validated 119 LNG observations against the published National Gas dataset, with all 119 values matching.
* Calculated LNG entry as a proportion of NTS demand, reaching 26.08% on 6 November 2026.
* Flagged elevated LNG observations for review while retaining the source’s original quality indicators.

3. US Natural Gas Storage Forecasting

* Analysed EIA working gas storage data and historical seasonal patterns.
* Developed a 12-week forward storage forecast using five-year seasonal averages.
* Constructed lower, base and higher storage scenarios.
* Backtested the seasonal forecasting approach against historical observations at 4-, 8- and 12-week horizons.

Historical backtest performance:

Forecast Horizon	Seasonal Model MAE	No-Change Baseline MAE	Improvement
4 weeks	82.85 Bcf	300.98 Bcf	72.47%
8 weeks	127.13 Bcf	569.29 Bcf	77.67%
12 weeks	165.21 Bcf	804.34 Bcf	79.46%

The historical backtest used overlapping forecast windows. Results do not guarantee future accuracy.

4. Market Intelligence and Trading Scenarios

* Assessed UK operational conditions using demand, LNG entry and linepack indicators.
* Distinguished UK/European market signals from US Henry Hub fundamentals.
* Developed conditional bullish, neutral and bearish scenarios.
* Documented risks including weather uncertainty, supply disruptions, infrastructure constraints and data limitations.
* Avoided treating storage projections as direct natural gas price forecasts.

Selected Results

* European gas benchmark premium: $22.54/MMBtu (September 2026).
* UK LNG source verification: 119/119 observations matched the National Gas publication.
* US 12-week base storage projection: 2,771.4 Bcf for 22 January 2027.
* 12-week model improvement: 79.46% lower mean absolute error versus a no-change baseline in historical testing.

Data Sources

* US Energy Information Administration (EIA): Natural gas working storage and LNG export data.
* Federal Reserve Economic Data (FRED): Henry Hub spot prices and the IMF European natural gas benchmark.
* National Gas Transmission: UK NTS demand, linepack and LNG entry volumes.
* Open-Meteo: Historical weather data used for illustrative heating and cooling degree-day analysis.

Tools and Skills

Python, Pandas, NumPy, Matplotlib, API data retrieval, data cleaning, time-series analysis, seasonal forecasting, backtesting, scenario analysis and commodity market interpretation.

Notebook

View the Natural Gas Market Analytics notebook

The notebook contains the Python analysis, calculations and visualisations.

Methodology and Limitations

This project is an analytical portfolio demonstration, not a production trading system.

* European benchmark prices are monthly observations, not live TTF or NBP quotes.
* European versus Henry Hub price differentials exclude LNG transportation and processing costs.
* UK LNG entry divided by NTS demand is not a complete UK supply-demand balance.
* LNG source verification confirms agreement with published data, not independent auditing of physical flows.
* Storage scenario sensitivities are illustrative, not statistical confidence intervals.
* Historical backtest windows overlap, and historical accuracy does not establish future performance.
* Market assessments are conditional and are not investment or trading recommendations.

Purpose

Developed to demonstrate the application of Python, quantitative analysis and operational energy-market knowledge to natural gas trading and market research.