"""
■ 夕方の業務報告 (Slack通知)
"""

from datetime import date

from common.data_converter import unpack_report
from common.data_loader import find_today_row, load_data
from common.log_handler import log_error, log_info
from config.settings import EXCEL_FILE_PATH
from services.slack_service import send_report


def main():
    log_info("🌆 夕方の報告処理を開始します")

    try:
        # データ取得
        data_rows = load_data(EXCEL_FILE_PATH)
        today_row = find_today_row(data_rows, date.today())

        if today_row:
            report_data = unpack_report(today_row)
            # スタッフ宛
            send_report(report_data, report_type="evening", to_staff=True)
        else:
            log_error("本日のデータが見つからないため、夕方の報告をスキップします")

    except Exception as e:
        log_error("夕方の報告処理でエラーが発生", e)


if __name__ == "__main__":
    main()
