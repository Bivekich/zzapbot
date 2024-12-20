import os
import pandas as pd
import requests
import xml.etree.ElementTree as ET
import json
import time

LOGIN = os.getenv("ZZAP_LOGIN")
PASSWORD = os.getenv("ZZAP_PASSWORD")
API_KEY = os.getenv("ZZAP_API_KEY")
BASE_URL = "https://api.zzap.pro/webservice/datasharing.asmx/GetSearchResultInfoV3"

input_file = "input.xlsx"
data = pd.read_excel(input_file)

result_columns = [
    "Артикул", "Бренд", "Категория", "Производитель", "Количество в наличии", "Минимальная цена в наличии", "Средняя цена в наличии", "Максимальная цена в наличии",
    "Количество под заказ", "Минимальная цена под заказ", "Средняя цена под заказ", "Максимальная цена под заказ"
]
results = []

for index, row in data.iterrows():
    partnumber = row.get("catalog_article")
    brand = row.get("brand")

    if pd.isna(partnumber) or pd.isna(brand):
        continue

    params = {
        "login": LOGIN,
        "password": PASSWORD,
        "code_region": 1,
        "partnumber": partnumber,
        "class_man": brand,
        "api_key": API_KEY,
        "code_cur": 1
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=5)
        response.raise_for_status()

        root = ET.fromstring(response.text)
        json_data = json.loads(root.text)

        results.append({
            "Артикул": partnumber,
            "Бренд": brand,
            "Категория": json_data.get("class_cat", ""),
            "Производитель": json_data.get("class_man", ""),
            "Количество в наличии": json_data.get("price_count_instock", 0),
            "Минимальная цена в наличии": json_data.get("price_min_instock", 0.0),
            "Средняя цена в наличии": json_data.get("price_avg_instock", 0.0),
            "Максимальная цена в наличии": json_data.get("price_max_instock", 0.0),
            "Количество под заказ": json_data.get("price_count_order", 0),
            "Минимальная цена под заказ": json_data.get("price_min_order", 0.0),
            "Средняя цена под заказ": json_data.get("price_avg_order", 0.0),
            "Максимальная цена под заказ": json_data.get("price_max_order", 0.0),
        })
    except Exception as e:
        print(f"Error processing partnumber {partnumber} and brand {brand}: {e}")

    time.sleep(30)

result_df = pd.DataFrame(results, columns=result_columns)

numeric_fields = [
    "Количество в наличии", "Минимальная цена в наличии", "Средняя цена в наличии", "Максимальная цена в наличии",
    "Количество под заказ", "Минимальная цена под заказ", "Средняя цена под заказ", "Максимальная цена под заказ"
]
for field in numeric_fields:
    result_df[field] = pd.to_numeric(result_df[field], errors='coerce').fillna(0).round(2)

output_file = "output.xlsx"
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    result_df.to_excel(writer, index=False, float_format="%.2f")

    worksheet = writer.sheets["Sheet1"]
    for column_cells in worksheet.columns:
        max_length = max(len(str(cell.value)) for cell in column_cells)
        column_letter = column_cells[0].column_letter
        worksheet.column_dimensions[column_letter].width = max_length + 2

print(f"Results saved to {output_file}")
