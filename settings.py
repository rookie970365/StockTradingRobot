import os

# данные аккаунта для доступа к торговле
TOKEN = os.environ["INVEST_TOKEN"]
ACCOUNT_ID = ""

# флаг переключения рабочего контура
SANDBOX = True

# телеграм
BOT_TOKEN = ""
CHAT_ID = ""

# набор ETF Тинкофф без комиссии
ETFs = ["BBG333333333", "BBG000000001", "TCS00A1039N1"]

# набор акций
STOCKS = ["BBG000K3STR7", "BBG001M2SC01", "BBG0014PFYM2"]

# размер позиции в лотах
QUATITY_LIMIT = 2

# временной интервал пересчета границ диапазона в секундах
CHECK_INTERVAL = 60

# временное окно исторических данных
DAYS_BACK = 10
