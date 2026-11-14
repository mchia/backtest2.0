import pandas as pd
import yfinance as yf
from app.db.database import db_manager

EXPECTED_SCHEMA: list[str] = [
    "timestamp",
    "symbol",
    "interval",
    "open",
    "high",
    "low",
    "close",
    "volume",
]

def market_data_pipeline(ticker: str|list[str], interval: str) -> int:
    """
    Wrapper function around yfinance's download function.
    This wrapper enforces 'max' as the period and a consistent schema.
    Also enforces UTC as the datetime format for consistency.
    
    Args:
        ticker: Ticker to source data for (Accepts a string or a list of strings).
        interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo

    Returns:
        int: Count of rows ingested.
    """
    df: pd.DataFrame = yf.download(tickers=ticker, period="max", interval=interval, progress=False)
    if isinstance(df.columns, tuple) or hasattr(df.columns, "levels"):
        df: pd.DataFrame = df.stack(level=1, future_stack=True).reset_index()
    else:
        df: pd.DataFrame = df.reset_index()

    df.columns = [str(c).lower() for c in df.columns]
    time_col = "datetime" if "datetime" in df.columns else "date"
    df: pd.DataFrame = df.rename(columns={time_col: "timestamp"})

    if "symbol" not in df.columns:
        df["symbol"] = ticker if isinstance(ticker, str) else ticker[0]

    if "interval" not in df.columns:
        df["interval"] = interval

    if df["timestamp"].dt.tz is not None:
        df["timestamp"] = df["timestamp"].dt.tz_convert("UTC").dt.tz_localize(None)

    if "adj close" in df.columns:
        df: pd.DataFrame = df.drop(columns=["adj close"])

    df: pd.DataFrame = df[EXPECTED_SCHEMA]
    df: pd.DataFrame = df.astype({
        "timestamp": "datetime64[ns]",
        "symbol": "string",
        'interval': "string",
        "open": "float64",
        "high": "float64",
        "low": "float64",
        "close": "float64",
        "volume": "Int64",
    })

    # Clean DF and pass to db_manager to handle ingestion.
    cleaned_df: pd.DataFrame = df.dropna()
    db_manager._ingest_data(cleaned_df)

    return len(cleaned_df)
