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
sorted_industry = sorted(df['GICS Sector'].unique())
selected_industry = st.sidebar.selectbox('Industry', options=sorted_industry)
df_selected_industry = df[ (df['GICS Sector'].str.contains(str(selected_industry))) ]

# # Group the data by ticker and get a sorted list of unique tickers from the selected industry. Add a multiselect to the sidebar to select multiple tickers.
ticker = df_selected_industry.groupby('Ticker')

sorted_ticker_unique = sorted(df_selected_industry['Ticker'].unique())
selected_ticker = st.sidebar.multiselect('Ticker', sorted_ticker_unique, sorted_ticker_unique)
                                         

df_selected_ticker = df[ (df['Ticker'].isin(selected_ticker)) ]

# # Get a sorted list of unique sectors from selected tickers and add a multiselect to the sidebar to select multiple sectors.
sector = df_selected_ticker.groupby('GICS Sub-Industry')

sorted_sector_unique = sorted(df_selected_ticker['GICS Sub-Industry'].unique())
selected_sector = st.sidebar.multiselect('Sector', sorted_sector_unique, sorted_sector_unique)

df_selected_sector = df_selected_ticker[ (df_selected_ticker['GICS Sub-Industry'].isin(selected_sector)) ]

st.header('Display companies in selected sector')
st.write('Data dimension: ' + str(df_selected_sector.shape[0]) + 'rows and ' + str(df_selected_sector.shape[1]) + 'columns.')

st.dataframe(df_selected_sector)

plt.style.use('seaborn-v0_8')
# Define a function to plot PeG ratio for companies in a selected sector.

def peg_plot():
    # Get the list of company symbols and their PeG ratios from the selected sector dataframe
    symbol = list(df_selected_sector.Ticker)
    peg_ratio = list(df_selected_sector.PegRatio)
    
    # Check if the number of companies is less than or equal to 10
    if len(symbol) <= 15:
        fig, ax = plt.subplots()

        # Plot a horizontal line representing the mean PeG ratio across the industry
        ax.axhline(df_selected_sector.PegRatio.mean(), color='rebeccapurple', label='Mean peg ratio across industry')

        # Create a bar plot of PeG ratios for each company
        bar = sns.barplot(x=symbol, y=peg_ratio, palette=['tab:grey', 'tan', 'tab:brown', 'steelblue'])

        # Add labels to the bars
        for rect in bar.patches:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width() / 2, height, height, ha='center', va='bottom')

        ax.set_xlabel('Company')
        ax.set_ylabel('PeG Ratio')
        ax.tick_params(axis='x', labelsize=7)
        ax.text(1.02, df_selected_sector.PegRatio.mean(), round(df_selected_sector.PegRatio.mean(), 2), va='center', transform=ax.get_yaxis_transform())
        ax.legend()
    else:
        # Create two subplots if the number of companies is greater than 10
        fig, (ax1, ax2) = plt.subplots(2, 1)

        # Plot a horizontal line representing the mean PeG ratio across the industry in both subplots
        ax1.axhline(df_selected_sector.PegRatio.mean(), color='rebeccapurple', label='Mean peg ratio across industry')
        ax2.axhline(df_selected_sector.PegRatio.mean(), color='rebeccapurple', label='Mean peg ratio across industry')

        # Create bar plots of PeG ratios for each company in both subplots
        bar1 = sns.barplot(x=symbol[:15], y=peg_ratio[:15], palette=['tab:grey', 'tan', 'tab:brown', 'steelblue'], ax=ax1)
        bar2 = sns.barplot(x=symbol[15:30], y=peg_ratio[15:30], palette=['tab:grey', 'tan', 'tab:brown', 'steelblue'], ax=ax2)

        # Add labels to the bars in both subplots
        for rect in bar1.patches:
            height = rect.get_height()
            ax1.text(rect.get_x() + rect.get_width() / 2, height, height, ha='center', va='bottom')
        
        for rect in bar2.patches:
            height = rect.get_height()
            ax2.text(rect.get_x() + rect.get_width() / 2, height, height, ha='center', va='bottom')

        ax1.set_xlabel('Company')
        ax1.set_ylabel('PeG Ratio')
        ax1.text(1.02, df_selected_sector.PegRatio.mean(), round(df_selected_sector.PegRatio.mean(), 2), va='center', transform=ax1.get_yaxis_transform())
        ax1.legend()

        ax2.set_xlabel('Company')
        ax2.set_ylabel('PeG Ratio')
        ax2.text(1.02, df_selected_sector.PegRatio.mean(), round(df_selected_sector.PegRatio.mean(), 2), va='center', transform=ax2.get_yaxis_transform())
        ax2.legend()

        fig.tight_layout()
    return st.pyplot(fig)


def FPE_plot():
    # Get the list of company symbols and their Forward P/E ratios from the selected sector dataframe
    symbol = list(df_selected_sector.Ticker)
    FPE_ratio = list(df_selected_sector.ForwardPE)
    
    # Check if the number of companies is less than or equal to 10
    if len(symbol) <= 15:
        fig, ax = plt.subplots()

        # Plot a horizontal line representing the mean Forward P/E ratio across the industry
        ax.axhline(df_selected_sector.ForwardPE.mean(), color='rebeccapurple', label='Mean Forward P/E ratio across industry')

        # Create a bar plot of Forward P/E ratios for each company
        bar = sns.barplot(x=symbol, y=FPE_ratio, palette=['tab:grey', 'tan', 'tab:brown', 'steelblue'])

        # Add labels to the bars
        for rect in bar.patches:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width() / 2, height, height, ha='center', va='bottom')

        ax.set_xlabel('Company')
        ax.set_ylabel('Forward P/E Ratio')
        ax.tick_params(axis='x', labelsize=7)
        ax.text(1.02, df_selected_sector.ForwardPE.mean(), round(df_selected_sector.ForwardPE.mean(), 2), va='center', transform=ax.get_yaxis_transform())
        ax.legend()
    else:
        # Create two subplots if the number of companies is greater than 10
        fig, (ax1, ax2) = plt.subplots(2, 1)

        # Plot a horizontal line representing the mean Forward P/E ratio across the industry in both subplots
        ax1.axhline(df_selected_sector.ForwardPE.mean(), color='rebeccapurple', label='Mean Forward P/E ratio across industry')
        ax2.axhline(df_selected_sector.ForwardPE.mean(), color='rebeccapurple', label='Mean Forward P/E ratio across industry')

        # Create bar plots of Forward P/E ratios for each company in both subplots
        bar1 = sns.barplot(x=symbol[:15], y=FPE_ratio[:15], palette=['tab:grey', 'tan', 'tab:brown', 'steelblue'], ax=ax1)
        bar2 = sns.barplot(x=symbol[15:30], y=FPE_ratio[15:30], palette=['tab:grey', 'tan', 'tab:brown', 'steelblue'], ax=ax2)

        # Add labels to the bars in both subplots
        for rect in bar1.patches:
            height = rect.get_height()
            ax1.text(rect.get_x() + rect.get_width() / 2, height, height, ha='center', va='bottom')
        
        for rect in bar2.patches:
            height = rect.get_height()
            ax2.text(rect.get_x() + rect.get_width() / 2, height, height, ha='center', va='bottom')

        ax1.set_xlabel('Company')
        ax1.set_ylabel('Forward P/E Ratio')
        ax1.text(1.02, df_selected_sector.ForwardPE.mean(), round(df_selected_sector.ForwardPE.mean(), 2), va='center', transform=ax1.get_yaxis_transform())
        ax1.legend()

        ax2.set_xlabel('Company')
        ax2.set_ylabel('Forward P/E Ratio')
        ax2.text(1.02, df_selected_sector.ForwardPE.mean(), round(df_selected_sector.ForwardPE.mean(), 2), va='center', transform=ax2.get_yaxis_transform())
        ax2.legend()

        fig.tight_layout()
    return st.pyplot(fig)


st.header('PEG Ratio over mean accros industry')
peg_plot()

st.header('Forward P/E Ratio over mean accros industry')
FPE_plot()
