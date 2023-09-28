import logging
from datetime import timedelta

import numpy as np
from tinkoff.invest import HistoricCandle, CandleInterval
from tinkoff.invest.utils import now

import settings
from client import broker_client
from utils.quotation import quotation_to_float

logger = logging.getLogger(__name__)


class MomentumStrategy:
    """
    Логика стратегии заключается на торговле от границ диапазона, расчитанного
    на основе экстремумов цен в заданном временном окне.

    """

    def __init__(self, figi: str):
        self.figi = figi
        self.days_back: int = settings.days_back
        self.interval_size: float = 0.8  # статистическая величина для расчета процентиля

    async def get_historical_data(self) -> list[HistoricCandle]:
        """
        Получает исторические данные для инструмента и возвращает список 1-минутных
        свечей с days_back дней назад по настоящее время.
        """
        candles = []
        logger.debug(
            f"Start getting {self.figi} historical data for last {self.days_back} days"
        )
        async for candle in broker_client.get_all_candles(
                figi=self.figi,
                from_=now() - timedelta(days=self.days_back),
                to=now(),
                interval=CandleInterval.CANDLE_INTERVAL_1_MIN,
        ):
            candles.append(candle)
        logger.debug(f"Found {len(candles)} candles {self.figi}")
        return candles

    async def calculate_borders(self) -> list | None:
        """
        Вычисляет новые границы диапазона на основе полученных исторических данных.
        """
        candles = await self.get_historical_data()
        if len(candles) == 0:
            return
        values = []
        for candle in candles:
            values.append(quotation_to_float(candle.close))
        lower_percentile = (1 - self.interval_size) / 2 * 100
        borders = list(
            np.percentile(values, [lower_percentile, 100 - lower_percentile])
        )
        logger.info(f"Channel borders: {borders}")
        return borders
