from tinkoff.invest import Client, MoneyValue
from settings import TOKEN


def open_sandbox_account():
    with Client(TOKEN) as client:
        return client.sandbox.open_sandbox_account()


def pay_in_sandbox_account(account_id, units=100000):
    with Client(TOKEN) as client:
        client.sandbox.sandbox_pay_in(
            account_id=account_id,
            amount=MoneyValue(units=units, nano=000000000, currency="rub"),
        )


new_account = open_sandbox_account()
pay_in_sandbox_account(new_account.account_id)
