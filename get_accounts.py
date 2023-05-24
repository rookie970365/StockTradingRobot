from grpc import StatusCode
from tinkoff.invest import Client, RequestError, AccountType

from settings import TOKEN


def get_sandbox_accounts():
    with Client(TOKEN) as client:
        sb_accounts = client.sandbox.get_sandbox_accounts().accounts
        if len(sb_accounts) == 0:
            client.sandbox.open_sandbox_account()
        return client.sandbox.get_sandbox_accounts().accounts


def get_accounts():
    with Client(TOKEN) as client:
        try:
            return client.users.get_accounts().accounts
        except RequestError as e:
            if e.code == StatusCode.UNAUTHENTICATED:
                return get_sandbox_accounts()


if __name__ == "__main__":
    accounts = get_accounts()
    for account in accounts:
        print(f"id: {account.id}, name: {account.name}, type: {str(AccountType(account.type))}")

