import asyncio
import logging
from uuid import uuid4

from tinkoff.invest import (
    AioRequestError,
    OrderExecutionReportStatus,
)
from tinkoff.invest.grpc.orders_pb2 import (
    ORDER_DIRECTION_SELL,
    ORDER_DIRECTION_BUY,
    ORDER_TYPE_MARKET,
)

from client import broker_client
from db.db_logger import DBLogger
from settings import ACCOUNT_ID

from strategies.MomentumStrategy import MomentumStrategy
from telegram.telegram_service import telegram_bot
from utils.quotation import quotation_to_float

FINAL_ORDER_STATUSES = [
    OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_CANCELLED,
    OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_REJECTED,
    OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_FILL,
]
logger = logging.getLogger(__name__)


class TradingRobot:
    """
    Торговый робот. Получает данные из стратегии и совершает сделки.
    """

    def __init__(self, figi: str):
        self.figi = figi
        self.account_id = ACCOUNT_ID
        self.strategy = MomentumStrategy(figi)
        self.check_interval: int = 60
        self.quantity_limit: int = 2
        self.db_logger = DBLogger("dblogger.db")

    async def is_market_open(self):
        """
        Проверяет открыт ли рынок и доступен ли для торговли текущий инструмент.
        """
        trading_status = await broker_client.get_trading_status(figi=self.figi)
        while not (
            trading_status.market_order_available_flag
            and trading_status.api_trade_available_flag
        ):
            logger.debug(f"Waiting for the market to open. figi={self.figi}")
            await asyncio.sleep(60)
            trading_status = await broker_client.get_trading_status(figi=self.figi)

    async def get_last_price(self) -> float:
        """
        Возвращает цену закрытия последней свечи инструмента
        """
        response = await broker_client.get_last_prices(figi=[self.figi])
        last_prices = response.last_prices
        return quotation_to_float(last_prices.pop().price)

    async def get_position_lots(self) -> int:
        """
        Возвращает размер позици
        """
        portfolio = await broker_client.get_portfolio(account_id=self.account_id)
        for position in portfolio.positions:
            if position.figi == self.figi:
                return int(quotation_to_float(position.quantity_lots))

    async def place_sell_order(self, last_price: float) -> None:
        """
        Определяет размер позиции и отправляет SELL ордер.
        """
        position_lots = await self.get_position_lots()
        if not position_lots:
            logger.debug(f"{self.figi} There are no open long positions. Waiting")
            return
        if position_lots > 0:
            try:
                posted_order = await broker_client.post_order(
                    order_id=str(uuid4().time_low),
                    figi=self.figi,
                    direction=ORDER_DIRECTION_SELL,
                    quantity=position_lots,
                    order_type=ORDER_TYPE_MARKET,
                    account_id=self.account_id,
                )
                print(posted_order)
                logger.debug(
                    f"Selling {position_lots} lots of {self.figi}. Last price={last_price}"
                )
            except Exception as exc:
                logger.error(f"Failed to post sell order. figi={self.figi}. {exc}")
                return
            telegram_bot.post(
                f"Sell {position_lots} lots of {self.figi}. Last price={last_price}"
            )

            asyncio.create_task(
                self.logging_to_db(
                    order_id=posted_order.order_id, account_id=self.account_id
                )
            )

    async def place_buy_order(self, last_price: float) -> None:
        """
        Определяет размер позиции и отправляет BUY ордер.
        """
        position_lots = await self.get_position_lots()
        if not position_lots:
            position_lots = 0

        if position_lots >= self.quantity_limit:
            logger.debug(
                f"{self.figi} The limit of open long positions has been reached. Waiting"
            )
        else:
            buy_lots = self.quantity_limit - position_lots
            try:
                posted_order = await broker_client.post_order(
                    order_id=str(uuid4().time_low),
                    figi=self.figi,
                    direction=ORDER_DIRECTION_BUY,
                    quantity=buy_lots,
                    order_type=ORDER_TYPE_MARKET,
                    account_id=self.account_id,
                )

                logger.debug(
                    f"Buying {buy_lots} lots of {self.figi}. Last price={last_price}"
                )
            except Exception as exc:
                logger.error(f"Failed to post buy order figi = {self.figi}. {exc}")
                return
            telegram_bot.post(
                f"Buy {buy_lots} lots of {self.figi}. Last price = {last_price}"
            )

            order_state = await broker_client.get_order_state(
                account_id=ACCOUNT_ID, order_id=posted_order.order_id
            )
            print(order_state)

            asyncio.create_task(
                self.logging_to_db(
                    order_id=posted_order.order_id, account_id=self.account_id
                )
            )

    async def logging_to_db(self, account_id: str, order_id: str) -> None:
        """
        Заносит информацию в базу данных или обновляет
        """
        try:
            order_state = await broker_client.get_order_state(
                account_id=account_id, order_id=order_id
            )
        except AioRequestError:
            return
        self.db_logger.add_order(
            # order_id=order_id,
            order_id=str(uuid4().time_low),
            figi=order_state.figi,
            order_direction=str(order_state.direction),
            price=quotation_to_float(order_state.total_order_amount),
            quantity=order_state.lots_requested,
            status=str(order_state.execution_report_status),
        )
        while order_state.execution_report_status not in FINAL_ORDER_STATUSES:
            await asyncio.sleep(10)
            order_state = await broker_client.get_order_state(
                account_id=account_id, order_id=order_id
            )
        self.db_logger.update_order_status(
            order_id=order_id, status=str(order_state.execution_report_status)
        )

    async def stop_loss(self, last_price: float, borders: list) -> None:
        """
        Отправляет SELL ордер, если достигнут стоп-лосс по текущей позиции.
        """
        portfolio = await broker_client.get_portfolio(account_id=self.account_id)
        for position in portfolio.positions:
            if position.figi == self.figi:
                average_position_price = quotation_to_float(
                    position.average_position_price
                )
                stop_loss_size = (borders[1] - borders[0]) * 0.3
                stop_loss_price = average_position_price - stop_loss_size
                logger.debug(f"{self.figi} Stop loss price = {stop_loss_price}")
                if stop_loss_price > last_price:
                    logger.debug(
                        f"{self.figi} Stop loss triggered. Last price = {last_price}"
                    )
                    position_quantity = int(quotation_to_float(position.quantity_lots))
                    telegram_bot.post(
                        f"{self.figi} Stop loss triggered. Last price = {last_price}"
                    )
                    try:
                        posted_order = await broker_client.post_order(
                            order_id=str(uuid4().time),
                            figi=self.figi,
                            direction=ORDER_DIRECTION_SELL,
                            quantity=position_quantity,
                            order_type=ORDER_TYPE_MARKET,
                            account_id=self.account_id,
                        )
                    except Exception as exc:
                        logger.error(f"{self.figi} Failed to post sell order. {exc}")
                        return
                    asyncio.create_task(
                        self.logging_to_db(
                            order_id=posted_order.order_id, account_id=self.account_id
                        )
                    )

    async def start(self):
        while True:
            try:
                await self.is_market_open()
                borders = await self.strategy.calculate_borders()
                position_lots = await self.get_position_lots()
                orders = await broker_client.get_orders(account_id=self.account_id)
                for order in orders.orders:
                    if order.figi == self.figi:
                        logger.info(
                            f"Order in progress ({self.figi}, lots = {position_lots}). Waiting"
                        )
                        await asyncio.sleep(self.check_interval)
                        continue

                last_price = await self.get_last_price()
                logger.debug(f"{self.figi} Last price: {last_price}")

                await self.stop_loss(last_price, borders)

                # отправляем SELL ордер, если последняя цена выше верхней границы диапазона
                if last_price >= borders[1]:
                    logger.debug(
                        f"{self.figi} Last price {last_price} is higher than top border {borders[1]}"
                    )
                    await self.place_sell_order(last_price=last_price)
                # отправляем BUY ордер, если последняя цена ниже нижней границы диапазона
                elif last_price <= borders[0]:
                    logger.debug(
                        f"{self.figi} Last price {last_price} is lower than bottom border {borders[0]}"
                    )
                    await self.place_buy_order(last_price=last_price)

            except AioRequestError as err:
                logger.error(f"Client error {err}")

            await asyncio.sleep(self.check_interval)
