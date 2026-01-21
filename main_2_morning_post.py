"""
■ 朝の業務報告 (Slack通知)
"""

import logging
from datetime import date

from common.data_converter import unpack_report
from common.data_loader import find_today_row, load_data
from common.log_handler import log_error, log_info
from config.settings import EXCEL_FILE_PATH, TARGET_MODES_MORNING
from services.slack_service import send_report


def main():
    log_info("🌅 朝の報告処理を開始します")

    try:
        # データ取得
        data_rows = load_data(EXCEL_FILE_PATH)
        today_row = find_today_row(data_rows, date.today())

        if not today_row:
            log_error("本日のデータが見つからないため、朝の報告をスキップします")
            return

        report_data = unpack_report(today_row)

        if report_data["通所形態"] == "休日":
            log_info("本日は休日です")
            return
        elif report_data["通所形態"] not in TARGET_MODES_MORNING:
            log_info(
                f"処理対象外の通所形態のためスキップします: {report_data['通所形態']}"
            )
            return

        # スタッフ宛に送信 (to_staff=True)
        send_report(report_data, report_type="morning", to_staff=True)
        # 自分宛にも送信したい場合は以下を有効化
        # send_report(report_data, report_type="morning", to_staff=False)

    except Exception as e:
        log_error("朝の報告処理でエラーが発生しました", e)
        logging.shutdown()


if __name__ == "__main__":
    main()
