import streamlit as st
import pandas as pd
from PIL import Image
import urllib.request
import yfinance as yf
from plotly import graph_objs as go
from matplotlib import pyplot as plt
import datetime
from prophet import Prophet
from prophet.plot import plot_plotly

def load_data(ticker, time_period):
    if time_period == '1d':
        data = yf.download(ticker, period=time_period, interval='1m')
        close_info = yf.download(ticker, period = '5d')
    elif time_period in time_periods:
        data = yf.download(ticker, period=time_period)
    else:
        data = yf.download(ticker, period, today)
    data.reset_index(inplace=True)
    #This code removes the hh:mm:ss timestamp from date (unnecessary for time periods > 1 day)
    if time_period == '1d':
        date = data['Datetime'].dt.strftime("%Y-%m-%d %H:%M")
        data.insert(loc = 0, column = 'Date', value = date)
        data = data.drop(columns = 'Datetime')
        #cols = data.columns.tolist()
        #cols = cols[-1:] + cols[:-1]
        #data = data[cols]
    else:
        data['Date'] = data['Date'].dt.date
    return data


def get_input():
    ticker = st.sidebar.text_input("Stock Ticker", "MSFT")

    time_period = st.sidebar.selectbox("Which time period?", time_periods)
    display_bollinger_bands = False
    start = today
    predict_future = False
    prediction_period = 1
    compare = False

    if time_period == 'custom':
        start = st.sidebar.date_input("Enter Start Date", today- datetime.timedelta(days = 2), max_value = today- datetime.timedelta(days = 1))

    if today - start > datetime.timedelta(days = 45) or time_period not in ['1d','5d', 'custom']:
        display_bollinger_bands = st.sidebar.checkbox("Display Bollinger Bands?", False)

    # Compare performance to S&P 500 index or something else with percentage changes if time period is longer than a day
    if (len(yf.download(ticker, start, today)) > 1) or (time_period not in  ['1d','custom']):
        compare = st.sidebar.checkbox("Compare relative performance with S&P 500?", False)

    #if time period is long enough (longer than 75 days), ask if user wants to make predictions
    if (today - start > datetime.timedelta(days = 75)) or (time_period not in ['1d','5d', '1mo','custom']):
        predict_future = st.sidebar.checkbox("Predict future share price?", False)
        if predict_future:
            prediction_period = st.sidebar.slider("How many weeks into the future would you like to predict", 1, max_value = 52)


    #If there is an invalid ticker, stop the program
    if len(yf.download(ticker)) == 0:
        st.exception(RuntimeError("Invalid Ticker Id"))
        st.stop()

    if time_period == 'custom':
        time_period = start

    return ticker, display_bollinger_bands, time_period, predict_future, prediction_period, compare


def load_company_logo(stock_info):
    logo_url = stock_info.info['logo_url']
    urllib.request.urlretrieve(
      logo_url,
       "logo.png")
    image = Image.open("logo.png")
    return image


def calculate_bollinger_bands(data, n_lookback, n_std = 2):
    hlc_avg = (data.High + data.Low + data.Close)/3
    mean = hlc_avg.rolling(n_lookback).mean()
    std = hlc_avg.rolling(n_lookback).std()
    upper = mean + std * n_std
    lower = mean - std * n_std
    boll_data = data
    boll_data['upper_band'], boll_data['lower_band'] = upper, lower
    return boll_data


def plot_raw_data(data, plot_bollinger_bands = False, y_1 = 'Open', title = 'Price Chart with adjustable window', one_day = False):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x = data['Date'], y = data[y_1], name = y_1))
    if one_day:
        fig.add_hline(y = get_prev_close_price(selected_stock), line_dash = 'dot', annotation_text = 'Previous close: ' + str(get_prev_close_price(selected_stock)))
    if plot_bollinger_bands:
        fig.add_trace(go.Scatter(x = data['Date'], y = data['upper_band'], name = 'upper_band',
                                 fill = None, mode = 'lines', line_color = 'indigo', opacity = .1))
        fig.add_trace(go.Scatter(x = data['Date'], y = data['lower_band'], name = 'lower_band',
                                 fill = 'tonexty', fillcolor = 'rgba(25,150,65,.1)', mode = 'lines',
                                 line_color = 'indigo', opacity = .1))
    fig.layout.update(title_text= title, xaxis_rangeslider_visible=True, yaxis_title = 'Holding Price')
    st.plotly_chart(fig)


def get_prev_close_price(ticker):
    prev = yf.download(ticker, period = '5d')
    prev_price = prev.iloc[-2].Close
    return round(prev_price,2)

def compare_with_snp500(data, ticker):
    snp_data = load_data('^GSPC', period)
    data_to_plot = data.merge(snp_data, left_on = 'Date', right_on = 'Date')
    col_name =  ticker + "_pct_change"
    data_to_plot[col_name] = data_to_plot.Close_x.pct_change() * 100
    data_to_plot['snp_pct_change'] = data_to_plot.Close_y.pct_change() * 100
    plot_raw_data(data_to_plot, False, col_name, 'snp_pct_change', title = 'Relative Performance compared to S&P 500')


def display_data(data):
    display = data.sort_values(by = ['Date'], ascending = False)
    return display

def build_prophet_model(df, weeks_into_future):
    #Want to add overall trends of markets to neural net
    #For small cap, find specific indices, for large cap, s&p 500
    training_df = df[['Date', 'Close']]
    training_df = training_df.rename(columns = {"Date": "ds", "Close":"y"})
    model = Prophet()
    model.fit(training_df)
    #Predict value of stock one week into future
    future = model.make_future_dataframe(periods = weeks_into_future * 7)
    #Remove weekends from prediction
    future = future[future['ds'].dt.dayofweek < 5]
    forecast = model.predict(future)
    return model, forecast


st.write("# Stock Market Web App")
st.caption("##### Click to view project on [GitHub](https://github.com/ross-wgh/stock-dashboard)")

#Create a sidebar
st.sidebar.header('User Input')

#Time periods compatible with yfinance, eventually want to add a custom range
time_periods = ("6mo", "1d", "5d", "1mo", "3mo", "1y", "2y", "5y", "10y", "ytd", "max", "custom")
today = datetime.date.today()

data_load_state = st.text('Loading data...')

selected_stock, display_bands, period, predict, weeks, snp = get_input()

#Get metadata about holding
stock_info = yf.Ticker(selected_stock)
#Display Logo for stock, takes about 5 seconds to load image
try:
    st.image(load_company_logo(stock_info))
except:
    #Image not found
    pass

stock_data = load_data(selected_stock, period)
data_load_state.text('')


col1, col2, col3 = st.columns(3)
col1.metric("Price", value = "$" + str(stock_info.info['currentPrice']),
            delta = str(round(stock_info.info['currentPrice'] - stock_info.info['previousClose'],2)) +
                    " (" +
                    str(round((stock_info.info['currentPrice'] - stock_info.info['previousClose'])/stock_info.info['previousClose']*100,2)) + "%) today")
col2.metric("Price", value = "$" + str(stock_info.info['currentPrice']),
            delta = str(round(stock_info.info['currentPrice'] - stock_info.info['previousClose'],2)) +
                    " (" +
                    str(round((stock_info.info['currentPrice'] - stock_info.info['previousClose'])/stock_info.info['previousClose']*100,2)) + "%) today")
col3.metric("Price", value = "$" + str(stock_info.info['currentPrice']),
            delta = str(round(stock_info.info['currentPrice'] - stock_info.info['previousClose'],2)) +
                    " (" +
                    str(round((stock_info.info['currentPrice'] - stock_info.info['previousClose'])/stock_info.info['previousClose']*100,2)) + "%) today")


# Plot data
if display_bands:
    plot_raw_data(calculate_bollinger_bands(stock_data, 10), True)
else:
    if period == '1d':
        plot_raw_data(stock_data, one_day=True)
    else:
        plot_raw_data(stock_data)

st.subheader('Holding Profile')

#Put in container
col1, col2, col3 = st.columns(3)
with col1:
    st.write("Sector: " + stock_info.info['sector'])
    st.write("Industry: " + stock_info.info['industry'])

with col2:
    st.write("Dividend Yield: " + str(round(stock_info.info['dividendYield'] * 100, 2)) + "%")
    st.write("ebitdaMargins: " + str(stock_info.info['ebitdaMargins']))

with col3:
    st.write("Website: " + stock_info.info['website'])
    st.write("profitMargins: " + str(stock_info.info['profitMargins']))

st.subheader('Trading Data for ' + stock_info.info['shortName'] + ' ($' + selected_stock.upper() + ')')
st.write(display_data(stock_data))

if snp and period != '1d':
    compare_with_snp500(stock_data, selected_stock.lower())

if predict:
    data_load_state.text('Training Neural Network...')
    st.info("Note: This is a very rough estimate given current trend of stock price and overall direction of markets.")
    model, forecast = build_prophet_model(stock_data, weeks)
    st.subheader("Stock Price Forecast with FBProphet")
    fig1 = plot_plotly(model, forecast)
    st.plotly_chart(fig1)
    fig2 = model.plot_components(forecast)
    st.write(fig2)
    st.caption("""This plot refers to relative performance of share price based on day of week. Since markets are closed 
            on weekends, the values of Saturday and Sunday reflect the price change from when markets close on Friday 
            to when markets open on Monday.""")

data_load_state.text('')
