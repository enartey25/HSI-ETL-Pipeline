import yfinance as yf

def extract(symbol):
    data = yf.download(
        symbol,
        start="2006-01-01",
        end="2026-08-15",
        interval="1d"
    )

    return data

df = extract("^HSI")
print(df.head())
print(df.info())
print(df.isna().sum())