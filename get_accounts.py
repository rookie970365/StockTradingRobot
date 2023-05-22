import asyncio

from client import broker_client


async def get_account():
    await broker_client.create()
    return (await broker_client.get_accounts()).accounts


if __name__ == "__main__":
    accounts = asyncio.run(get_account())
    for account in accounts:
        print(f"account_id: {account.id}, account_name: {account.name}")
