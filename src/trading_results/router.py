from typing import List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select, desc

from trading_results.models import SpimexTrading
from trading_results.schemas import LastTrade, DynamicTrade, FilterTrade, TradingResult
from database import get_async_session


router_result = APIRouter(
    prefix='/results', tags=['Get results']
)


@router_result.get('/last-dates', response_model=Optional[List[LastTrade]])
async def get_last_trading_dates(
    count_day: int = Query(
        ..., ge=1, le=60, description='Output last days dates', example=5
    ),
    session: AsyncSession = Depends(get_async_session)
) -> Union[LastTrade, HTTPException]:
    
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

    return [LastTrade(date=item) for item in result]


@router_result.get('/dynamics', response_model=Optional[List[DynamicTrade]])
async def get_dynamic(
    data_params: FilterTrade = Depends(),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        if data_params.start_date > data_params.end_date:
            raise ValueError('Incorrect date')

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

        return [DynamicTrade.model_validate(item) for item in result]
    
    except ValueError as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Validation error: {str(e)}"
        )

@router_result.get('/trading-result', response_model=List[DynamicTrade])
async def get_trading_result(
    data_params: TradingResult = Depends(),
    session: AsyncSession = Depends(get_async_session)
) -> Union[DynamicTrade, HTTPException]:
    
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
    
    return [
        DynamicTrade.model_validate(item) for item in result
    ]
