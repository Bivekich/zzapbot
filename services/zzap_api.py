import requests
import xml.etree.ElementTree as ET
import json
from config.settings import ZZAP_LOGIN, ZZAP_PASSWORD, ZZAP_API_KEY, ZZAP_BASE_URL

class ZzapAPI:
    @staticmethod
    async def get_part_info(partnumber: str, brand: str) -> dict:
        params = {
            "login": ZZAP_LOGIN,
            "password": ZZAP_PASSWORD,
            "code_region": 1,
            "partnumber": partnumber,
            "class_man": brand,
            "api_key": ZZAP_API_KEY,
            "code_cur": 1
        }

        response = requests.get(ZZAP_BASE_URL, params=params, timeout=5)
        response.raise_for_status()

        root = ET.fromstring(response.text)
        return json.loads(root.text)
