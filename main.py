import asyncio
import logging

from client import broker_client
from robot import TradingRobot
from settings import ETFs, stocks

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)-5s] %(asctime)-19s %(name)s: %(message)s",
)


async def main_process():
    await broker_client.create()
    # await asyncio.gather(*[TradingRobot(instrument).start() for instrument in ETFs])
    await asyncio.gather(*[TradingRobot(instrument).start() for instrument in stocks])


if __name__ == "__main__":
    asyncio.run(main_process())
