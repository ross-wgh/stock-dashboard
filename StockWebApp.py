import streamlit as st
import pandas as pd
from PIL import Image
import urllib.request
import yfinance as yf
from plotly import graph_objs as go
from matplotlib import pyplot as plt

st.write("# Stock Market Web App")


#Create a sidebar
st.sidebar.header('User Input')


#May want to cache this eventually
def get_input():
    ticker = st.sidebar.text_input("Stock Ticker", "MSFT")
    return ticker


selected_stock = get_input()


#Time periods compatible with yfinance, eventually want to add a custom range
time_periods = ("6mo", "1d", "5d", "1mo", "3mo", "1y", "2y", "5y", "10y", "ytd", "max")
period = st.sidebar.selectbox("Which time period?", time_periods)


#Custom RANGE code skeleton
#if period == 'Custom':
#    start_date = st.sidebar.text_input("Start Date", ENTER DATETIME OBJECT HERE)
#    end_date = st.sidebar.text_input("End Date", ENTER DATETIME OBJECT HERE)


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


#Write logic for if ticker is not found, may need to do that at input step.
#if len(stock_data) == 0:
#    st.write("Make sure that the ticker is correct. No data for $" + selected_stock + " was found.")


@st.cache
def load_data(ticker):
    data = yf.download(ticker, period = period)
    data.reset_index(inplace=True)
    return data


#data_load_state = st.text('Loading data...')
stock_data = load_data(selected_stock)
#data_load_state.text('Loading data... done!')


st.subheader('Trading Data for ' + stock_info.info['shortName'] + ' ($' + selected_stock+ ')')
st.write(stock_data)


# Plot raw data
def plot_raw_data():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x = stock_data['Date'], y = stock_data['Open'], name = "stock_open"))
    fig.add_trace(go.Scatter(x = stock_data['Date'], y = stock_data['Close'], name = "stock_close"))
    fig.layout.update(title_text='Time Series data with Rangeslider', xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)


plot_raw_data()

st.subheader("Important Upcoming Dates")
