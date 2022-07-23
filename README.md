# Stock Dashboard App

App is available in-browser at: https://share.streamlit.io/ross-wgh/stock-dashboard/main/StockWebApp.py

## Changelog

### Version 2.3 7/22/2022
- Added more information in holding profile (headquarters, ex-dividend date, EPS, cash/revenue per share, book value, beta)

### Version 2.2 7/21/2022
- Added price updates by minute when markets are open (available when '1d' time period is selected)
- Added daily price change, daily volume, and daily price range metrics
- Added previous close price to '1d' plot
- Added daily volume plot
- Added basic info about holding (sector, dividend yield, ebitda and profit margins)

### Version 2.1 7/11/2022
- Displays stock prices starting with most recent dates (was sorted by date ascending before)
- Fixed issue where some companies with invalid logos would lead to runtime error

### Version 2.0 7/10/2022
- Added error handling for custom date picklist value
- Added load time indicator
- Added option to plot stocks relative performance with S&P 500
- Added option to use neural network (FBProphet) to predict future prices of stocks if data has 75 or more observations over selected time period.
- Revised code to make functions more flexible

### Version 1.2 7/8/2022
- Added data validation and error handling to ensure a valid ticker is input
- Added option to input a custom date range

### Version 1.1 7/7/2022
- Added option to display bollinger bands on share price plot

### Version 1.0 7/6/2022
- Base version of app: ability to view price of share with a valid ticker from a picklist of dates.
- Display companies logo and plot prices over time period with slider bar
