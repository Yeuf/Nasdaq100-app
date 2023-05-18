# Nasdaq 100 App

This is a Streamlit app that retrieves the list of the **Nasdaq 100** and some of the financial information about their respective stock.

It also lets you compare those financials informations against competitors and the average value of the industry.

## Features

- You can select an industry from the sidebar and see the list of companies in that industry.
- You can select multiple tickers from the sidebar and see their financial information such as forward P/E ratio and PeG ratio.
- You can select multiple sectors from the sidebar and see how the selected companies compare to the mean values of their sectors.
- You can see bar plots of PeG ratio and forward P/E ratio for each company and the mean value across the industry.

## Installation

To run this app locally, you need to have Python 3.6 or higher and install the following libraries:

- pandas
- numpy
- yfinance
- streamlit
- matplotlib
- bs4
- requests

You can install them using pip:

```bash
pip install -r requirements.txt
```

## Usage

To run this app, you need to clone this repository and run the following command in your terminal:

```bash
streamlit run app.py
```

This will open a browser window where you can interact with the app.

## Screenshots

![Industry selection](/IMG/Industry_selection.png)

![dataframe](/IMG/dataframe.png)

![peg](/IMG/peg.png)

![Wide peg](/IMG/peg_wide.png)

![Forward PE](/IMG/ForwardPE.png)

![wide forward PE](/IMG/Forward_PE_wide.png)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.