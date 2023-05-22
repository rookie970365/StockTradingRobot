import os
from pandas import DataFrame
from tinkoff.invest import Client
from tinkoff.invest.services import InstrumentsService

token = os.environ["INVEST_TOKEN"]

TICKER = "SBER"  # BBG004730N88


# TICKER = "LKOH" # BBG004731032
# TICKER = "SPY"  # BBG000BDTBL9
# TICKER = "RIM3" # FUTRTS062300


def run():
    with Client(token) as client:
        instruments: InstrumentsService = client.instruments

        lst = []
        for method in ['shares', 'bonds', 'etfs', 'currencies', 'futures']:
            for item in getattr(instruments, method)().instruments:
                lst.append({
                    'ticker': item.ticker,
                    'figi': item.figi,
                    'type': method,
                    'name': item.name,
                })

        df = DataFrame(lst)
        df = df[df['ticker'] == TICKER]
        if df.empty:
            print(f"Нет тикера {TICKER}")
            return
        print(df.iloc[0])
        # print(df.to_json())


if __name__ == '__main__':
    run()
