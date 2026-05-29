"""
■ 夕方の業務報告 (Slack通知)
"""

import logging
from datetime import date

from common.data_converter import convert_to_model
from common.data_loader import find_today_row, load_data
from common.log_handler import log_error, log_info
from config.settings import EXCEL_FILE_PATH
from services.slack_service import send_error_alert, send_report

PROGRAM_NAME = "main_2_evening_post"


def main():
    log_info("🌆 夕方の報告処理を開始します")

    try:
        # データ取得
        data_rows = load_data(EXCEL_FILE_PATH)
        today_row = find_today_row(data_rows, date.today())

        if not today_row:
            message = "本日のデータが見つからないため、夕方の報告をスキップします"
            log_error(message, level="WARN")
            send_error_alert(
                PROGRAM_NAME, message, urgency="WARN", status="処理スキップ"
            )
            return

        report_data = convert_to_model(today_row)

        if not report_data:
            message = "レポートデータの生成に失敗しました"
            log_error(message)
            send_error_alert(PROGRAM_NAME, message, status="異常終了")
            return

        if report_data.usage_type == "休日":
            log_info("本日は休日です")
            return
        # elif report_data.usage_type not in TARGET_MODES_EVENING:
        #     log_info(
        #         f"処理対象外の通所形態のためスキップします: {report_data.usage_type}"
        #     )
        #     return

        # スタッフ宛
        send_report(report_data, report_type="evening", to_staff=True)
        # 自分宛にも送信したい場合は以下を有効化
        # send_report(report_data, report_type="evening", to_staff=False)

    except Exception as e:
        log_error("夕方の報告処理でエラーが発生しました", e, level="FATAL")
        send_error_alert(
            PROGRAM_NAME,
            "夕方の報告処理でエラーが発生しました",
            urgency="FATAL",
            status="異常終了",
            exception=e,
        )
        logging.shutdown()


if __name__ == "__main__":
    main()
