from dotenv import load_dotenv
import os
import numpy as np
import yfinance as yf
import pandas as pd
import psycopg2
import logging
from psycopg2.extras import execute_values
pd.set_option('display.max_columns', 100)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()
logger = logging.getLogger(__name__)


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
        df = df.replace([np.inf, -np.inf], np.nan)
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

def load(df, conn, table_name):
    if df.empty:
        logger.info('No record to load. Stopping process.')
        return 0
    cols = list(df.columns)
    values = df[cols].values.tolist()
    col_names = ', '.join(cols)
    update_cols = ", ".join(
        f"{c} = EXCLUDED.{c}" for c in cols if c != "trade_date"
    )

    query = f'''INSERT INTO {table_name} ({col_names})
    values %s
    on conflict (trade_date) do update set
    {update_cols}'''
    try:
        with conn.cursor() as cur:
            execute_values(cur, query, values)
        conn.commit()
        logger.info(f'Loaded {len(df)} records into {table_name}.')
        return len(df)
    except Exception as e:
        conn.rollback()
        logger.error(f"Load failed, rolled back: {e}")
        raise
    finally:
        conn.close()

load(transform(extract('^HSI')), conn, 'hsi_features')