import datetime
from typing import Optional

from fastapi import Query
from pydantic import BaseModel


class LastTrade(BaseModel):
    date: datetime.date


class DynamicTrade(BaseModel):
    product_id: str
    oil_id: str
    delivery_id: str
    delivery_type: str
    date: datetime.date

    model_config = {
        'from_attributes': True
    }


class FilterTrade(BaseModel):
    oil_id: Optional[str] = Query(None)
    delivery_id: Optional[str] = Query(None)
    delivery_type: Optional[str] = Query(None)
    start_date: datetime.date
    end_date: datetime.date


class TradingResult(BaseModel):
    oil_id: Optional[str] = Query(None)
    delivery_id: Optional[str] = Query(None)
    delivery_type: Optional[str] = Query(None)