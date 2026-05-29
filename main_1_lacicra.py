"""
ラシクラに自動で日報を記入して一時保存するプログラム
"""

# 必要なライブラリ・モジュールをインポート
import logging
import sys

# 日付取得用
from datetime import datetime, timedelta, timezone

# データ変換
from common.data_converter import convert_to_model

# データ取得
from common.data_loader import (
    find_today_row,
    load_data,
)

# logerror
from common.log_handler import log_error, log_info

# 定数の取得
from config.settings import (
    EXCEL_FILE_PATH,
    LACICRA_PASSWORD,
    LACICRA_USERNAME,
)

# Lacicra操作
from services.lacicra_service import (
    input_today_summarys,
    login_lacicra,
    open_lacicra,
    save_button_click,
    today_meal_click,
    today_report_btn_click,
    today_slp_status_click,
)
from services.slack_service import send_error_alert

PROGRAM_NAME = "main_1_lacicra"


def main():
    try:
        log_info("🚀 Lacicra処理を開始します")

        # データの読み込み（ExcelまたはGoogleシート）
        # data_io.py内のDATA_SOURCEに基づいて取得先が変更される
        data_list = load_data(EXCEL_FILE_PATH)
        if not data_list:
            log_error("データが空です")
            send_error_alert(PROGRAM_NAME, "データが空です", status="異常終了")
            return

        # 今日のデータ行を検索
        JST = timezone(timedelta(hours=9), "JST")
        today = datetime.now(JST).date()
        log_info(f"📅 検索対象の日付(JST): {today}")  # 確認用ログ

        report = find_today_row(data_list, today)

        # report内にデータが見つからない場合は終了
        if report is None:
            message = (
                f"❌ {today} の日報データが見つかりませんでした。処理を終了します。"
            )
            log_info(message)
            return

        # データの辞書化と変換
        report_data = convert_to_model(report)

        if not report_data:
            log_info("❌ レポートデータの生成に失敗しました")
            return

        # Web操作
        if report_data.usage_type == "休日":
            log_info("本日はお休みです")
            return
        # elif report_data.usage_type not in TARGET_MODES_LACICRA:
        #     log_info(
        #         f"処理対象外の通所形態のためスキップします: {report_data.usage_type}"
        #     )
        #     return

        LACICRA_URL = "https://lacicra.jp/login.php"
        _, wait = open_lacicra(LACICRA_URL)
        login_lacicra(
            wait,
            LACICRA_USERNAME,
            LACICRA_PASSWORD,
        )

        # 手動でログイン
        log_info("⌛ ログイン作業中")

        log_info("📒 本日のページを開きます")
        today_report_btn_click(wait)

        log_info("✍ 本日の報告を入力します")
        input_today_summarys(wait, report_data)
        today_slp_status_click(wait, report_data)
        today_meal_click(wait, report_data)

        log_info("💾 本日の報告を保存します")
        save_button_click(wait)

        log_info("✅ Lacicra処理が正常終了しました")

    except Exception as e:
        log_error("実行中に予期せぬエラーが発生しました", e, level="FATAL")
        send_error_alert(
            PROGRAM_NAME,
            "実行中に予期せぬエラーが発生しました",
            urgency="FATAL",
            status="異常終了",
            exception=e,
        )
        log_info("⛔ プログラムを異常終了します")
        logging.shutdown()
        # error時はウィンドウを閉じずに確認
        sys.exit(1)


if __name__ == "__main__":
    main()
