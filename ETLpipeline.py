from dotenv import load_dotenv
import os
import numpy as np
import yfinance as yf
import pandas as pd
import psycopg2
pd.set_option('display.max_columns', 100)

load_dotenv()

conn = psycopg2.connect(
    host = os.getenv('DB_HOST'),
    port = os.getenv('DB_PORT'),
    dbname = os.getenv('DB_NAME'),
    user = os.getenv('DB_USER'),
    password = os.getenv('DB_PASSWORD')
)

def extract(symbol):
    data = yf.download(
        symbol,
        start="2006-01-01",
        end="2026-08-15",
        interval="1d"
    )

    return data

df = extract("^HSI")

def summarize(df, n:int):
    print('\n')
    print(f'=============LAST {n} BUSINESS DAYS============')
    print(df.tail(n))
    print(f'=============DATA TYPE INFORMATION=============')
    print(df.info())
    print(f'=============DESCRIPTIVE STATISTICS=============')
    print(df.describe().T)
    print(f'=============COLUMNS==============')
    print(df.columns)

summarize(df, 8)

def transform(df):
    try: 
        df = df.reset_index()
        df = df.droplevel('Ticker', axis = 1)
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        df = df.rename(columns = {'date':'trade_date'})
        df['daily_return'] = df['close'].pct_change()
        df['daily_range'] = df['high'] - df['low']
        df['adr_14d'] =  df['daily_range'].rolling(window = 14).mean()
        df['gap_pct'] = 100 * (df['open'] - df['close'].shift(1))/df['close'].shift(1)
        range_span = (df['high'] - df['low']).replace(0, np.nan)
        df['clv'] = ((df['close'] - df['low']) - (df['high'] - df['close'])) / range_span
        df['vol_change'] = (df['volume'] - df['volume'].shift(1)) / df['volume'].shift(1)
        df['vol_ag_20dayavg'] = df['volume'] / df['volume'].shift(1).rolling(window = 20).mean()
        df = df.where(pd.notnull(df), None)
        return df
    except KeyError as e:
        print(e)
        raise
    except IndexError as f:
        print(f)
        raise
    except Exception as g:
        print('Unexpected failure: ', g)
        raise
