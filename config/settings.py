import os
from dotenv import load_dotenv

load_dotenv()

ZZAP_LOGIN = os.getenv("ZZAP_LOGIN")
ZZAP_PASSWORD = os.getenv("ZZAP_PASSWORD")
ZZAP_API_KEY = os.getenv("ZZAP_API_KEY")
ZZAP_BASE_URL = "https://api.zzap.pro/webservice/datasharing.asmx/GetSearchResultInfoV3"

BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")

RESULT_COLUMNS = [
    "Артикул", "Бренд", "Категория", "Производитель", "Количество в наличии",
    "Минимальная цена в наличии", "Средняя цена в наличии", "Максимальная цена в наличии",
    "Количество под заказ", "Минимальная цена под заказ", "Средняя цена под заказ",
    "Максимальная цена под заказ"
]

NUMERIC_FIELDS = [
    "Количество в наличии", "Минимальная цена в наличии", "Средняя цена в наличии",
    "Максимальная цена в наличии", "Количество под заказ", "Минимальная цена под заказ",
    "Средняя цена под заказ", "Максимальная цена под заказ"
]
