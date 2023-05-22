import math
from typing import Union

from tinkoff.invest import Quotation, MoneyValue


def quotation_to_float(quotation: Union[Quotation, MoneyValue]) -> float:
    """
    конвертирует объект quotation в значение типа float
    """
    return float(quotation.units + quotation.nano / 1000000000)
