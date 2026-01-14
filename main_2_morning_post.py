"""
■ 朝の業務報告 (Slack通知)
"""

from datetime import date
from config.settings import EXCEL_FILE_PATH
from common.data_loader import load_data, find_today_row
from common.data_converter import unpack_report
from common.log_handler import log_info, log_error
from services.slack_service import send_report


def main():
    log_info("🌅 朝の報告処理を開始します")

    try:
        # データ取得
        data_rows = load_data(EXCEL_FILE_PATH)
        today_row = find_today_row(data_rows, date.today())

        if today_row:
            report_data = unpack_report(today_row)
            # スタッフ宛に送信 (to_staff=True)
            send_report(report_data, report_type="morning", to_staff=True)
            # 自分宛にも送信したい場合は以下を有効化
            # send_report(report_data, report_type="morning", to_staff=False)
        else:
            log_error("本日のデータが見つからないため、朝の報告をスキップします")

    except Exception as e:
        log_error("朝の報告処理でエラーが発生", e)


if __name__ == "__main__":
    main()
