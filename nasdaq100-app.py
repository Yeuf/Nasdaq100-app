# Import necessary libraries
import pandas as pd
import numpy as np
import yfinance as yf
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from bs4 import BeautifulSoup
import requests

st.title('Nasdaq 100 App')

st.markdown("""
This app retrieves the list of the **Nasdaq 100** and some of the financial information about their respective stock.
\n It also lets you compare those financials informations against competitors and the average value of the industry.
""")

st.sidebar.header('Features selection')

# Define a function to load data using caching to improve performance
@st.cache_data
def load_data():
    # Get the content of the Wikipedia page for Nasdaq-100
    url = requests.get('https://en.wikipedia.org/wiki/Nasdaq-100')
    soup = BeautifulSoup(url.content, "html.parser")
    # Find the table with the list of constituents
    data = soup.find("table",{"class":"wikitable sortable", "id":"constituents"})
    # Convert the table to a DataFrame
    df = pd.read_html(str(data))[0]
    
    # Create a list of Ticker objects using yfinance library
    tickers = [yf.Ticker(ticker) for ticker in df.Ticker]

    symbol = []
    forwardPE = []
    pegRatio = []
    # Collect data on symbol, forwardPE, and pegRatio for each ticker
    for i in tickers:
        try:
            symbol.append(i.info['symbol'])
        except KeyError:
            symbol.append('i')   
        try:
            forwardPE.append(i.info['forwardPE'])
        except KeyError:
            forwardPE.append(0)
        try:
            pegRatio.append(i.info['pegRatio'])
        except KeyError:
            pegRatio.append(0)

    # Create a DataFrame with the collected data
    df_data = pd.DataFrame(columns=['Ticker', 'ForwardPE', 'PegRatio'])

    df_data['Ticker'] = symbol
    df_data['ForwardPE'] = forwardPE
    df_data['PegRatio'] = pegRatio
    # Merge the data with the original DataFrame and return it
    df = df.merge(df_data, on=['Ticker'])
    df = df[df.PegRatio <= 50]
    return df

df = load_data()

# Get a sorted list of unique industries from the data and add a selectbox to the sidebar to select an industry
sorted_industry = sorted(df['GICS Sector'].unique(), key=str)
selected_industry = st.sidebar.selectbox('Industry', options=sorted_industry)
df_selected_industry = df[ (df['GICS Sector'].str.contains(str(selected_industry))) ]

# # Group the data by ticker and get a sorted list of unique tickers from the selected industry. Add a multiselect to the sidebar to select multiple tickers.
ticker = df_selected_industry.groupby('Ticker')

sorted_ticker_unique = sorted(df_selected_industry['Ticker'].unique(), key=str)
selected_ticker = st.sidebar.multiselect('Ticker', sorted_ticker_unique, sorted_ticker_unique)
                                         

df_selected_ticker = df[ (df['Ticker'].isin(selected_ticker)) ]

# # Get a sorted list of unique sectors from selected tickers and add a multiselect to the sidebar to select multiple sectors.
sector = df_selected_ticker.groupby('GICS Sub-Industry')

sorted_sector_unique = sorted(df_selected_ticker['GICS Sub-Industry'].unique(), key=str)
selected_sector = st.sidebar.multiselect('Sector', sorted_sector_unique, sorted_sector_unique)

df_selected_sector = df_selected_ticker[ (df_selected_ticker['GICS Sub-Industry'].isin(selected_sector)) ]

st.header('Display companies in selected sector')
st.write('Data dimension: ' + str(df_selected_sector.shape[0]) + 'rows and ' + str(df_selected_sector.shape[1]) + 'columns.')

st.dataframe(df_selected_sector)

plt.style.use('seaborn-v0_8-dark')

def ratio_plot(ratio):
    # Get the list of company symbols and their ratios from the selected sector dataframe
    symbol = list(df_selected_sector.Ticker)
    ratio_values = list(df_selected_sector[ratio])

    fig = plt.figure()  # Initialize the figure
    
    # Check if the number of companies is less than or equal to 15
    if len(symbol) <= 15:
        # Create a bar plot of ratios for each company
        ax = sns.barplot(x=symbol, y=ratio_values, palette=['tab:grey', 'tan', 'tab:brown', 'steelblue'])

        # Add a horizontal line representing the mean ratio across the industry
        ax.axhline(df_selected_sector[ratio].mean(), color='rebeccapurple', label='Mean ratio across industry')

        # Add labels to the bars
        for rect in ax.patches:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width() / 2, height, f'{height:.2f}', ha='center', va='bottom')

        ax.set_xlabel('Company')
        ax.set_ylabel(ratio)
        ax.tick_params(axis='x', labelsize=7)
        ax.text(1.02, df_selected_sector[ratio].mean(), f'{round(df_selected_sector[ratio].mean(), 2):.2f}',
                va='center', transform=ax.get_yaxis_transform())
        ax.legend()
    else:
        # Create two subplots if the number of companies is greater than 15
        fig, (ax1, ax2) = plt.subplots(2, 1)

        # Create bar plots of ratios for each company in both subplots
        bar1 = sns.barplot(x=symbol[:15], y=ratio_values[:15], palette=['tab:grey', 'tan', 'tab:brown', 'steelblue'], ax=ax1)
        bar2 = sns.barplot(x=symbol[15:30], y=ratio_values[15:30], palette=['tab:grey', 'tan', 'tab:brown', 'steelblue'], ax=ax2)

        # Add horizontal lines representing the mean ratio across the industry in both subplots
        ax1.axhline(df_selected_sector[ratio].mean(), color='rebeccapurple', label='Mean ratio across industry')
        ax2.axhline(df_selected_sector[ratio].mean(), color='rebeccapurple', label='Mean ratio across industry')

        # Add labels to the bars in both subplots
        for rect in bar1.patches:
            height = rect.get_height()
            ax1.text(rect.get_x() + rect.get_width() / 2, height, f'{height:.2f}', ha='center', va='bottom')
        
        for rect in bar2.patches:
            height = rect.get_height()
            ax2.text(rect.get_x() + rect.get_width() / 2, height, f'{height:.2f}', ha='center', va='bottom')

        ax1.set_xlabel('Company')
        ax1.set_ylabel(ratio)
        ax1.text(1.02, df_selected_sector[ratio].mean(), f'{round(df_selected_sector[ratio].mean(), 2):.2f}',
                 va='center', transform=ax1.get_yaxis_transform())
        ax1.legend()

        ax2.set_xlabel('Company')
        ax2.set_ylabel(ratio)
        ax2.text(1.02, df_selected_sector[ratio].mean(), f'{round(df_selected_sector[ratio].mean(), 2):.2f}',
                 va='center', transform=ax2.get_yaxis_transform())
        ax2.legend()

        fig.tight_layout()
    
    return st.pyplot(fig)


st.header('PEG Ratio over mean accros industry')
ratio_plot("PegRatio")

st.header('Forward P/E Ratio over mean accros industry')
ratio_plot("ForwardPE")