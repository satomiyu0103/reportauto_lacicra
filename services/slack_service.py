"""==========
■ Slack通知サービス (Integrated)
=========="""

import json
from datetime import datetime, timedelta, timezone
from typing import Any

import requests

from common.data_converter import DailyReport
from common.log_handler import log_error, log_info
from config.settings import SLACK_WEBHOOK_URL_TOME, SLACK_WEBHOOK_URL_TOSTUFF

URGENCY_LABELS = {
    "WARN": "⚠️ 低（警告）",
    "ERROR": "❌ 中（エラー）",
    "FATAL": "🚨 高（致命的）",
}


def _send_slack(message: str, webhook_url: str | None) -> Any:
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


def send_error_alert(
    program_name: str,
    message: str,
    urgency: str = "ERROR",
    status: str = "異常終了",
    exception: Exception | None = None,
) -> None:
    """エラー発生時に SLACK_WEBHOOK_URL_TOME へ通知する"""
    if not SLACK_WEBHOOK_URL_TOME:
        log_error("Slack Webhook URL (TOME) が設定されていません")
        return

    jst = timezone(timedelta(hours=9), "JST")
    now = datetime.now(jst).strftime("%Y-%m-%d %H:%M:%S")
    urgency_display = URGENCY_LABELS.get(urgency, urgency)
    detail = str(exception) if exception else "なし"

    msg = f"""🚨 【RPAエラー通知】
■ プログラム: {program_name}
■ 緊急度: {urgency_display}
■ 実行状況: {status}
■ 内容: {message}
■ 詳細: {detail}
■ 発生日時: {now} (JST)
"""
    _send_slack(msg, SLACK_WEBHOOK_URL_TOME)


def create_morning_message(data: DailyReport) -> str:
    """朝報のメッセージを作成"""
    # 必須項目のチェック
    if not data:
        return "⚠️ 日付データが取得できませんでした。"

    msg = f"""【定時報告】
①体調｜{data.condition}（理由：{data.condition_reason or "なし"}）
②{data.usage_type}
　午前｜{data.am_plan}
　午後｜{data.pm_plan}
③体温｜{data.body_temp}℃　{data.wake_up_time}
④ルーティン
　昨日｜散歩{data.walk_steps}歩　自学習{data.study_time}分
　　　｜入浴{data.bath_status}　ストレッチ{data.stretch_status}　就寝(7h↑){data.sleep_status}
　今日｜測定(体温・体重・腹囲){data.measurement_status}　朝食(1.食べた 2.食べてない){data.breakfast_score}
"""
    return msg


def create_evening_message(data: DailyReport) -> str:
    """夕報のメッセージを作成"""
    msg = f"""【終了報告】
〇学習内容/進捗
・午前｜{data.am_activity or ""}
・午後｜{data.pm_activity or ""}

〇感想
{data.activity_report or ""}

〇ルーティン/仕事術
・わんこそば仕事術　{data.wanko_method}％
・一極集中仕事術　{data.ikkyoku_method}％
・耳と目で確認するミス防止術　{data.mimoku_check}％
・フォルダ命名規則を作る仕事術　{data.naming_rule}％

〇次回の目標/ToDo
{data.next_plan}を進めます。
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
