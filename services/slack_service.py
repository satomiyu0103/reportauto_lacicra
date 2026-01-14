"""==========
■ Slack通知サービス (Integrated)
=========="""

import json

import requests

from common.log_handler import log_error, log_info
from config.settings import SLACK_WEBHOOK_URL_TOME, SLACK_WEBHOOK_URL_TOSTUFF


def _send_slack(message, webhook_url):
    """内部利用: SlackにメッセージをPOSTする"""
    if not webhook_url:
        log_error("Slack Webhook URLが設定されていません")
        return

    payload = {"text": message}
    try:
        response = requests.post(
            webhook_url,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )
        if response.status_code == 200:
            log_info("Slack通知を送信しました")
        else:
            log_error(f"Slack送信失敗: {response.status_code} - {response.text}")
    except Exception as e:
        log_error("Slack送信中にエラーが発生", e)


def create_morning_message(data):
    """朝報のメッセージを作成"""
    # 必須項目のチェック
    if not data.get("日付"):
        return "⚠️ 日付データが取得できませんでした。"

    msg = f"""【定時報告】
①体調｜{data.get("体調")}（理由：{data.get("体調の理由")}）
②{data.get("通所形態")}
　午前｜{data.get("午前予定")}
　午後｜{data.get("午後予定")}
③体温｜{data.get("体温")}℃　{data.get("起床時刻")}
④ルーティン
　昨日｜散歩{data.get("歩数")}歩　自学習{data.get("自習時間")}分
　　　｜入浴{data.get("入浴")}　ストレッチ{data.get("ストレッチ")}　就寝(7h↑){data.get("睡眠")}
　今日｜測定(体温・体重・腹囲){data.get("測定")}　朝食(1.食べた 2.食べてない){data.get("朝食")}
"""
    return msg


def create_evening_message(data):
    """夕報のメッセージを作成"""
    msg = f"""【終了報告】
〇学習内容/進捗
・午前｜{data.get("午前業務")}
・午後｜{data.get("午後業務")}

〇感想
{data.get("日報")}

〇ルーティン/仕事術
・わんこそば仕事術　{data.get("わんこそば仕事術")}％
・一極集中仕事術　{data.get("一極集中仕事術")}％
・耳と目で確認するミス防止術　{data.get("耳目確認")}％
・フォルダ命名規則を作る仕事術　{data.get("ファイル命名規則")}％

〇次回の目標/ToDo
{data.get("次回活動予定")}を進めます。
"""
    return msg


def send_report(data, report_type="morning", to_staff=False):
    """
    レポートを送信するファサード関数
    report_type: "morning" or "evening"
    """
    if report_type == "morning":
        msg = create_morning_message(data)
    else:
        msg = create_evening_message(data)

    # 送信先切り替え
    target_url = SLACK_WEBHOOK_URL_TOSTUFF if to_staff else SLACK_WEBHOOK_URL_TOME

    log_info(f"📨 [Slack] 送信中... ({'スタッフ宛' if to_staff else '自分宛'})")
    _send_slack(msg, target_url)
