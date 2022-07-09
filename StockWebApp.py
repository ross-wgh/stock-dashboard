import streamlit as st
import pandas as pd
from PIL import Image
import urllib.request
import yfinance as yf
from plotly import graph_objs as go
from matplotlib import pyplot as plt
import datetime

st.write("# Stock Market Web App")


#Create a sidebar
st.sidebar.header('User Input for five')

#Time periods compatible with yfinance, eventually want to add a custom range
time_periods = ("6mo", "1d", "5d", "1mo", "3mo", "1y", "2y", "5y", "10y", "ytd", "max", "custom")
today = datetime.date.today()

#@st.cache
def load_data(ticker, period):
    if period in time_periods:
        data = yf.download(ticker, period = period)
    else:
        data = yf.download(ticker, period, today)
    data.reset_index(inplace=True)
    #This code removes the hh:mm:ss timestamp from date (unnecessary for time periods > 1 day)
    data['Date'] = data['Date'].dt.date
    return data

#May want to cache this eventually
def get_input():
    ticker = st.sidebar.text_input("Stock Ticker", "MSFT")
    display_bollinger_bands = st.sidebar.checkbox("Display Bollinger Bands?", False)
    time_period = st.sidebar.selectbox("Which time period?", time_periods)
    if time_period == 'custom':
        start = st.sidebar.date_input("Enter Start Date", today- datetime.timedelta(days = 2), max_value = today- datetime.timedelta(days = 1))
        time_period = start

    #If there is an invalid ticker, stop the program
    if len(yf.download(ticker)) == 0:
        st.exception(RuntimeError("Invalid Ticker Id"))
        st.stop()

    return ticker, display_bollinger_bands, time_period


selected_stock, display_bands, period = get_input()


#Display Logo for stock, takes about 5 seconds to load image
stock_info = yf.Ticker(selected_stock)
def load_company_logo():
    logo_url = stock_info.info['logo_url']
    urllib.request.urlretrieve(
      logo_url,
       "logo.png")
    image = Image.open("logo.png")
    st.image(image)

load_company_logo()


#data_load_state = st.text('Loading data...')
stock_data = load_data(selected_stock, period)
#data_load_state.text('Loading data... done!')

def calculate_bollinger_bands(data, n_lookback, n_std = 2):
    hlc_avg = (data.High + data.Low + data.Close)/3
    mean = hlc_avg.rolling(n_lookback).mean()
    std = hlc_avg.rolling(n_lookback).std()
    upper = mean + std * n_std
    lower = mean - std * n_std
    data['upper_band'], data['lower_band'] = upper, lower
    return data

if display_bands:
    calculate_bollinger_bands(stock_data, 10)

st.subheader('Trading Data for ' + stock_info.info['shortName'] + ' ($' + selected_stock.upper() + ')')
st.write(stock_data)


# Plot raw data
def plot_raw_data(plot_bollinger_bands = display_bands):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x = stock_data['Date'], y = stock_data['Open'], name = "stock_open"))
    fig.add_trace(go.Scatter(x = stock_data['Date'], y = stock_data['Close'], name = "stock_close"))
    if(plot_bollinger_bands):
        fig.add_trace(go.Scatter(x = stock_data['Date'], y = stock_data['upper_band'], name = 'upper_band', fill = None, mode = 'lines', line_color = 'indigo', opacity = .1))
        fig.add_trace(go.Scatter(x = stock_data['Date'], y = stock_data['lower_band'], name = 'lower_band', fill = 'tonexty', fillcolor = 'rgba(25,150,65,.1)', mode = 'lines', line_color = 'indigo', opacity = .1))
    fig.layout.update(title_text='Time Series data with Rangeslider', xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)


plot_raw_data()
