from fastapi import FastAPI

from trading_results.router import router_result


app = FastAPI(
    title='Block 5',
    description='Realized 3 endpoints for get trade results'
)

app.include_router(router_result)