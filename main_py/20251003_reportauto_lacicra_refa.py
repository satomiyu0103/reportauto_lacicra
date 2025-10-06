"""
ラシクラに自動で日報を記入して一時保存するプログラム
"""

# 必要なライブラリ・モジュールをインポート
## pathlib
from pathlib import Path

# データ取得
from modules.data_io import (
    get_env_keys,
    get_excel_data,
    get_today_report,
    unpack_report,
)

# データ変換
from modules.data_converter import data_conv

# Lacicra操作
from modules.webui import (
    open_lacicra,
    login_lacicra,
    today_report_btn_click,
    input_today_summarys,
    today_slp_status_click,
    today_meal_click,
    save_button_click,
)


def main():
    file_path = r"config\.env"
    EXCEL_FILE_PATH, your_username, your_password = get_env_keys(file_path)
    ws = get_excel_data(EXCEL_FILE_PATH)
    report = get_today_report(ws)
    report_dict = unpack_report(report)
    if report_dict["通所形態"] == "休日":
        pass
    else:
        report_dict = data_conv(report_dict)
        LACICRA_URL = "https://lacicra.jp/login.php"
        driver, wait = open_lacicra(LACICRA_URL)
        login_lacicra(wait, your_username, your_password)

        # 手動でログイン

        today_report_btn_click(wait)
        input_today_summarys(wait, report_dict)
        today_slp_status_click(wait, report_dict)
        today_meal_click(wait, report_dict)
        save_button_click(wait)


if __name__ == "__main__":
    main()
