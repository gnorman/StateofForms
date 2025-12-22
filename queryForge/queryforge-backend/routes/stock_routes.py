from datetime import datetime
from typing import Optional, List
import logging
import pandas as pd

from fastapi import APIRouter, Query, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, validator

from db import database
from models import stock_queries
from cache import get_cache, set_cache

logger = logging.getLogger(__name__)

try:
    # OpenBB SDK import pattern (2025) – falls back gracefully if unavailable
    from openbb import obb  # type: ignore
except Exception:  # pragma: no cover
    obb = None  # Allow app to start; endpoints will raise informative error
    logger.error("OpenBB SDK not available")

router = APIRouter(tags=["stock"])  # Included in main.py with prefix /api/stock


class StockQueryRequest(BaseModel):
    symbol: str
    start_date: Optional[str] = None  # YYYY-MM-DD
    end_date: Optional[str] = None    # YYYY-MM-DD
    limit: int = 100

    @validator("symbol")
    def symbol_upper(cls, v: str) -> str:
        return v.upper()

    @validator("limit")
    def limit_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("limit must be > 0")
        return v

    def parsed_dates(self):
        start = datetime.strptime(self.start_date, "%Y-%m-%d").date() if self.start_date else None
        end = datetime.strptime(self.end_date, "%Y-%m-%d").date() if self.end_date else None
        return start, end


class StockQueryResponse(BaseModel):
    symbol: str
    start_date: Optional[str]
    end_date: Optional[str]
    created_at: str
    rows: int
    data: List[dict]


def _fetch_stock_historical(symbol: str, start, end, limit: int):
    if obb is None:
        raise RuntimeError("OpenBB SDK not available in backend container.")
    
    logger.info(f"Fetching stock data for {symbol} from {start} to {end}")
    
    try:
        # Try different OpenBB API patterns for stocks
        result = None
        
        # Try pattern 1: obb.stocks.price.historical
        if hasattr(obb, 'stocks'):
            logger.info("Using obb.stocks.price.historical")
            result = obb.stocks.price.historical(symbol)
        # Try pattern 2: obb.equity or obb.price
        elif hasattr(obb, 'equity'):
            logger.info("Using obb.equity.price.historical")
            result = obb.equity.price.historical(symbol)
        elif hasattr(obb, 'price'):
            logger.info("Using obb.price")
            result = obb.price(symbol)
        else:
            # List available attributes for debugging
            available = [attr for attr in dir(obb) if not attr.startswith('_')]
            logger.error(f"OpenBB App object has no 'stocks' attribute. Available: {available}")
            raise AttributeError(f"OpenBB API structure unknown. Available attributes: {available}")
        
        logger.info(f"OpenBB result type: {type(result)}")
        
        if result is None or (hasattr(result, '__len__') and len(result) == 0):
            logger.warning(f"No data returned for symbol {symbol}")
            return []
        
        df = result.to_dataframe()
        logger.info(f"DataFrame shape: {df.shape}, columns: {df.columns.tolist()}")
        
        if df.empty:
            logger.warning(f"Empty DataFrame for symbol {symbol}")
            return []
        
        # Date filtering (if provided)
        # Ensure index is datetime type for date filtering
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        
        if start:
            df = df[df.index.date >= start]
        if end:
            df = df[df.index.date <= end]
        
        # Limit rows (most recent first)
        df = df.sort_index(ascending=False).head(limit).sort_index()
        
        result_data = [
            {"date": idx.isoformat(), **{k: (v.item() if hasattr(v, "item") else v) for k, v in row.items()}}
            for idx, row in df.to_dict(orient="index").items()
        ]
        logger.info(f"Returning {len(result_data)} rows for {symbol}")
        return result_data
        
    except Exception as e:
        logger.error(f"Error fetching stock data for {symbol}: {type(e).__name__}: {str(e)}", exc_info=True)
        raise


@router.get("/{symbol}", response_model=StockQueryResponse)
async def get_stock_query(
    symbol: str,
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    limit: int = Query(100, ge=1, le=500, description="Max rows to return")
):
    symbol = symbol.upper()
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
        end = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    # Create cache key from query parameters
    cache_key = f"stock:{symbol}:{start_date}:{end_date}:{limit}"
    
    # Try to get from cache
    cached_response = await get_cache(cache_key)
    if cached_response:
        logger.info(f"Cache HIT for {cache_key}")
        return StockQueryResponse(**cached_response)
    
    created_at = datetime.utcnow()

    try:
        data = await run_in_threadpool(_fetch_stock_historical, symbol, start, end, limit)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:  # Catch SDK-related issues
        error_msg = f"OpenBB fetch failed: {type(e).__name__}: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=502, detail=error_msg)

    # Persist query metadata even if no data found
    try:
        insert_stmt = stock_queries.insert().values(
            symbol=symbol,
            start_date=start,
            end_date=end,
            created_at=created_at
        )
        await database.execute(insert_stmt)
    except Exception as e:
        logger.error(f"Failed to save stock query metadata: {str(e)}")

    response = StockQueryResponse(
        symbol=symbol,
        start_date=start.isoformat() if start else None,
        end_date=end.isoformat() if end else None,
        created_at=created_at.isoformat(),
        rows=len(data),
        data=data,
    )
    
    # Cache the response for 1 hour
    await set_cache(cache_key, response.dict(), ttl=3600)
    
    return response


@router.post("/query", response_model=StockQueryResponse)
async def post_stock_query(payload: StockQueryRequest):
    try:
        start, end = payload.parsed_dates()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    # Create cache key from query parameters
    cache_key = f"stock:{payload.symbol}:{payload.start_date}:{payload.end_date}:{payload.limit}"
    
    # Try to get from cache
    cached_response = await get_cache(cache_key)
    if cached_response:
        logger.info(f"Cache HIT for {cache_key}")
        return StockQueryResponse(**cached_response)

    created_at = datetime.utcnow()

    try:
        data = await run_in_threadpool(_fetch_stock_historical, payload.symbol, start, end, payload.limit)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        error_msg = f"OpenBB fetch failed: {type(e).__name__}: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=502, detail=error_msg)

    # Persist query metadata even if no data found
    try:
        insert_stmt = stock_queries.insert().values(
            symbol=payload.symbol,
            start_date=start,
            end_date=end,
            created_at=created_at
        )
        await database.execute(insert_stmt)
    except Exception as e:
        logger.error(f"Failed to save stock query metadata: {str(e)}")

    response = StockQueryResponse(
        symbol=payload.symbol,
        start_date=start.isoformat() if start else None,
        end_date=end.isoformat() if end else None,
        created_at=created_at.isoformat(),
        rows=len(data),
        data=data,
    )
    
    # Cache the response for 1 hour
    await set_cache(cache_key, response.dict(), ttl=3600)
    
    return response
