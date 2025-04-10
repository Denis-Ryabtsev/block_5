import pytest


class TestDynamics():
    @pytest.mark.parametrize(
            'params, status_code, count_resp, exception',
            [
                (
                    {
                        "oil_id": "A100",
                        "delivery_id": "ANK",
                        "delivery_type": "F",
                        "start_date": "2025-01-01",
                        "end_date": "2025-03-01"
                    },
                    200,
                    1,
                    None
                ),
                (
                    {
                        "oil_id": "A101",
                        # "delivery_id": "AAA",
                        # "delivery_type": "A",
                        "start_date": "2025-02-01",
                        "end_date": "2025-02-20"
                    },
                    200,
                    1,
                    None
                ),
                (
                    {
                        "oil_id": "A101",
                        "delivery_id": "AAA",
                        "delivery_type": "A",
                        "start_date": "2025-02-05",
                        "end_date": "2025-02-01"
                    },
                    400,
                    None,
                    'Validation error: Incorrect date'
                )
            ]
    )
    @pytest.mark.asyncio
    async def test_get_dynamics(self, async_client, params, status_code, count_resp, exception):
        response = await async_client.get("/results/dynamics", params=params)

        assert response.status_code == status_code
        if response.status_code == 200:
            assert len(response.json()) == count_resp
        else:
            assert response.json()['detail'] == exception


class TestLastDates():
    @pytest.mark.parametrize(
            'count_days, status_code, count_resp',
            [
                (1, 200, 1),
                (2, 200, 2),
                (3, 200, 2),
                (0, 422, 1)
            ]
    )
    @pytest.mark.asyncio
    async def test_get_last_trading_dates(self, async_client, count_days, status_code, count_resp):
        resp = await async_client.get(f'/results/last-dates?count_day={count_days}')

        assert resp.status_code == status_code
        assert len(resp.json()) == count_resp


class TestTradingResult():
    @pytest.mark.parametrize(
            'params, status_code, exception',
            [
                (
                    {
                        "oil_id": "A100",
                        "delivery_id": "ANK",
                        "delivery_type": "F"
                    },
                    200,
                    None
                ),
                (
                    {
                        "oil_id": "A100",
                        "delivery_id": "ANK",
                        "delivery_type": "FF"
                    },
                    400,
                    'With input params trades not found'
                )
            ]
    )
    @pytest.mark.asyncio
    async def test_get_trading_result(self, async_client, params, status_code, exception):
        response = await async_client.get("/results/trading-result", params=params)

        assert response.status_code == status_code
        if response.status_code == 400:
            assert response.json()['detail'] == exception