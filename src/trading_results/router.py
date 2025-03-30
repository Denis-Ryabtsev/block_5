import hashlib
import json
from typing import List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Query
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select, desc

from trading_results.models import SpimexTrading
from trading_results.schemas import LastTrade, DynamicTrade, FilterTrade, TradingResult
from database import get_async_session, get_redis_client, count_cash_time


router_result = APIRouter(
    prefix='/results', tags=['Get results']
)


@router_result.get('/last-dates', response_model=Optional[List[LastTrade]])
async def get_last_trading_dates(
    count_day: int = Query(
        ..., ge=1, le=60, description='Output last days dates', example=5
    ),
    session: AsyncSession = Depends(get_async_session),
    redis: Redis = Depends(get_redis_client)
) -> Union[LastTrade, HTTPException]:
    
    cache_key = f'last_dates:{count_day}'
    cached = await redis.get(cache_key)
    if cached:
        return [LastTrade.model_validate(item) for item in json.loads(cached)]

    query = \
        select(
            SpimexTrading.date.distinct()
        ).order_by(
            desc(SpimexTrading.date)
        ).limit(
            count_day
        )

    result = (await session.execute(query)).scalars().all()

    if not result:
        raise HTTPException(status_code=404, detail=f'Data not found')
    
    response = [LastTrade(date=item) for item in result]
    response_json = json.dumps([model.model_dump(mode="json") for model in response])

    await redis.set(cache_key, response_json)
    await redis.expireat(cache_key, count_cash_time())

    return [LastTrade(date=item) for item in result]


@router_result.get('/dynamics', response_model=Optional[List[DynamicTrade]])
async def get_dynamic(
    data_params: FilterTrade = Depends(),
    session: AsyncSession = Depends(get_async_session),
    redis: Redis = Depends(get_redis_client)
):
    try:
        if data_params.start_date > data_params.end_date:
            raise ValueError('Incorrect date')

        raw_key = f"{data_params.oil_id}_{data_params.delivery_id}_{data_params.delivery_type}_{data_params.start_date}_{data_params.end_date}"
        cache_key = "dynamics:" + hashlib.md5(raw_key.encode()).hexdigest()

        cached = await redis.get(cache_key)
        if cached:
            data = json.loads(cached)
            return [DynamicTrade.model_validate(item) for item in data]

        query = select(SpimexTrading).where(
            and_(
                SpimexTrading.date >= data_params.start_date, 
                SpimexTrading.date <= data_params.end_date
            )
        )
        
        filters = []

        if data_params.oil_id:
            filters.append(SpimexTrading.oil_id == data_params.oil_id)
        if data_params.delivery_id:
            filters.append(SpimexTrading.delivery_id == data_params.delivery_id)
        if data_params.delivery_type:
            filters.append(SpimexTrading.delivery_type == data_params.delivery_type)
        
        if filters:
            query = query.filter(and_(*filters))

        result = (await session.execute(query)).scalars().all()

        response = [DynamicTrade.model_validate(item) for item in result]
        response_json = json.dumps([item.model_dump(mode="json") for item in response])

        await redis.set(cache_key, response_json)
        await redis.expireat(cache_key, count_cash_time())

        return response
    
    except ValueError as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Validation error: {str(e)}"
        )

@router_result.get('/trading-result', response_model=List[DynamicTrade])
async def get_trading_result(
    data_params: TradingResult = Depends(),
    session: AsyncSession = Depends(get_async_session),
    redis: Redis = Depends(get_redis_client)
) -> Union[DynamicTrade, HTTPException]:
    
    raw_key = f"{data_params.oil_id}_{data_params.delivery_id}_{data_params.delivery_type}"
    cache_key = "trading_result:" + hashlib.md5(raw_key.encode()).hexdigest()

    cached = await redis.get(cache_key)
    if cached:
        data = json.loads(cached)
        return [DynamicTrade.model_validate(item) for item in data]

    query = \
        select(
            SpimexTrading
        ).limit(
            40
        )
    filters = []

    if data_params.oil_id:
        filters.append(SpimexTrading.oil_id == data_params.oil_id)
    if data_params.delivery_id:
        filters.append(SpimexTrading.delivery_id == data_params.delivery_id)
    if data_params.delivery_type:
        filters.append(SpimexTrading.delivery_type == data_params.delivery_type)
    
    query = query.filter(and_(*filters))

    result = (await session.execute(query)).scalars().all()
    if not result:
        raise HTTPException(
            status_code=400, detail=f'With input params trades not found'
        )
    
    response = [DynamicTrade.model_validate(item) for item in result]
    response_json = json.dumps([item.model_dump(mode="json") for item in response])

    await redis.set(cache_key, response_json)
    await redis.expireat(cache_key, count_cash_time())

    return response