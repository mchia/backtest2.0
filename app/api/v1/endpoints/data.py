from typing import Any
from pydantic import BaseModel, Field
from app.db.database import db_manager
from fastapi import APIRouter, HTTPException
from app.services.market_data import market_data_pipeline

router: APIRouter = APIRouter(prefix="/data", tags=["Market Data"])

class MarketRequestFields(BaseModel):
    ticker: str = Field(..., description="Stock ticker, e.g., NVDA", examples=["NVDA"])
    interval: str = Field("1d", description="Candle interval, e.g., 1d, 1h", examples=["1d"])

@router.post("/sync")
# params: MarketRequestFields = Depends() -> If parameters are to appear in URL
# params: MarketRequestFields -> JSON Payload
def sync_market_data(params: MarketRequestFields) -> dict[str, Any]:
    """
    POST request route which calls market_data_pipeline.
    
    Args:
        ticker: Stock ticker to POST to market_data_pipeline.
        interval: Candle interval to POST to market_data_pipeline.

    Returns:
        A dictionary containing the execution status, processed ticker, interval, and total rows inserted.

    Raises:
        HTTPException: Code 500 internal server error
    """
    try:
        rows_inserted: int = market_data_pipeline(ticker=params.ticker, interval=params.interval)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return {
            "status": "success",
            "ticker": params.ticker,
            "interval": params.interval,
            "rows_processed": rows_inserted,
        }

@router.get("/verify")
def table_verfication():
    """
    Verify tables have been created (Where applicable) and populated once sync_market_data has run.
    """
    tables: list[str] = db_manager.table_verification()
    if len(tables) > 0:
        return {
            "status": "success",
            "tables": tables
        }
    else:
        return {
            "status": "failure",
            "tables": []
        }