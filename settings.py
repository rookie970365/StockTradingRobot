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
stocks = ["BBG000K3STR7", "BBG001M2SC01", "BBG0014PFYM2"]

# размер позиции в лотах
quantity_limit = 2

# временной интервал пересчета границ диапазона в секундах
check_interval = 60

# временное окно исторических данных
days_back = 10
