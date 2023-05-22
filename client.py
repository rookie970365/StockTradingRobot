from tinkoff.invest import (
    AsyncClient,
    PostOrderResponse,
    GetLastPricesResponse,
    OrderState,
    GetTradingStatusResponse,
)

from settings import TOKEN, SANDBOX


class TargetClient:
    """
    Класс для создания экземпляра AsyncClient для работы в песочнице
    или на реальном счете.
    """

    def __init__(self, token: str, sandbox: bool = False):
        self.token = token
        self.sandbox = sandbox
        self.client = None

    async def create(self):
        self.client = await AsyncClient(token=self.token, app_name="").__aenter__()

    async def get_orders(self, **kwargs):
        if self.sandbox:
            return await self.client.sandbox.get_sandbox_orders(**kwargs)
        return await self.client.orders.get_orders(**kwargs)

    async def get_portfolio(self, **kwargs):
        if self.sandbox:
            return await self.client.sandbox.get_sandbox_portfolio(**kwargs)
        return await self.client.operations.get_portfolio(**kwargs)

    async def get_accounts(self):
        if self.sandbox:
            return await self.client.sandbox.get_sandbox_accounts()
        return await self.client.users.get_accounts()

    async def get_all_candles(self, **kwargs):
        async for candle in self.client.get_all_candles(**kwargs):
            yield candle

    async def get_last_prices(self, **kwargs) -> GetLastPricesResponse:
        return await self.client.market_data.get_last_prices(**kwargs)

    async def post_order(self, **kwargs) -> PostOrderResponse:
        if self.sandbox:
            return await self.client.sandbox.post_sandbox_order(**kwargs)
        return await self.client.orders.post_order(**kwargs)

    async def get_order_state(self, **kwargs) -> OrderState:
        if self.sandbox:
            return await self.client.sandbox.get_sandbox_order_state(**kwargs)
        return await self.client.orders.get_order_state(**kwargs)

    async def get_trading_status(self, **kwargs) -> GetTradingStatusResponse:
        return await self.client.market_data.get_trading_status(**kwargs)


broker_client = TargetClient(token=TOKEN, sandbox=SANDBOX)
