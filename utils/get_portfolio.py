from tinkoff.invest import Client
from utils.quotation import quotation_to_float
from settings import TOKEN, ACCOUNT_ID

# Просмотр текущих позиций

def get_portfolio(account_id):
    with Client(TOKEN) as client:
        return client.operations.get_portfolio(account_id=account_id)


def get_sandbox_portfolio(account_id):
    with Client(TOKEN) as client:
        return client.sandbox.get_sandbox_portfolio(account_id=account_id)


def get_orders(account_id):
    with Client(TOKEN) as client:
        return client.sandbox.get_sandbox_orders(account_id=account_id)


if __name__ == "__main__":
    portfolio = get_sandbox_portfolio(ACCOUNT_ID)
    # orders = get_sandbox_portfolio(ACCOUNT_ID)
    print("ACCOUNT_ID: ", ACCOUNT_ID)
    print("Total amount currencies: ", quotation_to_float(portfolio.total_amount_currencies))
    print("Positions: ")
    for p in portfolio.positions[1:]:
        # print(p.positions)
        print(p.figi, f"lots: {quotation_to_float(p.quantity_lots)}, average position price: {quotation_to_float(p.average_position_price)}")
