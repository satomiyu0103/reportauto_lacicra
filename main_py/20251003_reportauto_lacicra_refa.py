"""
ラシクラに自動で日報を記入して一時保存するプログラム
"""

# 必要なライブラリ・モジュールをインポート
## pathlib
from pathlib import Path
from datetime import datetime, timezone, timedelta  # 日付取得用
from dotenv import load_dotenv

# データ取得
from modules.data_io import (
    get_env_keys,
    load_data,
    find_today_row,
)

# データ変換
from modules.data_converter import data_conv, unpack_report

# logerror
from modules.log_handler import log_error

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
    # 設定と環境変数の読み込み
    EXCEL_FILE_PATH, your_username, your_password = get_env_keys()

    # データの読み込み（ExcelまたはGoogleシート）
    # data_io.py内のDATA_SAUCEに基づいて取得先が変更される
    data_list = load_data(EXCEL_FILE_PATH)

    # 今日のデータ行を検索
    ## JSTを定義
    JST = timezone(timedelta(hours=9), "JST")
    ## JSTを指定して現在時刻を取得
    today = datetime.now(JST).date()
    print(f"📅 検索対象の日付(JST): {today}")  # 確認用ログ

    report = find_today_row(data_list, today)

    # ws = get_excel_data(EXCEL_FILE_PATH)
    # report = get_today_report(ws)

    # データが見つからない場合は終了
    if report is None:
        message = f"❌ {today} の日報データが見つかりませんでした。処理を終了します。"
        log_error(message)
        return

    # データの辞書化と変換
    report_dict = unpack_report(report)
    (
        report_dict["体温"],
        report_dict["開始予定時刻"],
        report_dict["終了予定時刻"],
        report_dict["開始時刻"],
        report_dict["終了時刻"],
        report_dict["就寝時刻"],
        report_dict["起床時刻"],
    ) = data_conv(report_dict)

    # Web操作
    if report_dict["通所形態"] == "休日":
        pass
    else:
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
