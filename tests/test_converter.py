from datetime import datetime

import pytest

from common.data_converter import DailyReport, convert_to_model


def _build_raw_row(**overrides):
    base = {
        "日付": datetime(2026, 4, 15),
        "体調": "良好",
        "体調の理由": "睡眠が取れた",
        "利用形態": "在宅",
        "開始予定": "09:30",
        "終了予定": "16:00",
        "午前予定": "資料作成",
        "午後予定": "実装",
        "就寝時間": "23:30",
        "起床時間": "07:00",
        "寝覚め": 3,
        "やる気": 4,
        "体温": 36.5,
        "体重": 52.0,
        "腹囲": 70.0,
        "散歩": 3000,
        "自習時間": "30",
        "入浴": "1",
        "ストレッチ": "1",
        "睡眠": "1",
        "測定": "1",
        "昼食": 1,
        "夕食": 1,
        "朝食": 1,
        "開始時間": "09:45",
        "終了時間": "15:55",
        "午前活動": "朝会",
        "午後活動": "コーディング",
        "次回の予定": "レビュー",
        "わんこ": "80",
        "一極": "75",
        "耳目確認": "90",
        "命名規則": "85",
        "活動報告": "予定通り進捗",
    }
    base.update(overrides)

    keys = [
        "日付",
        "体調",
        "体調の理由",
        "利用形態",
        "開始予定",
        "終了予定",
        "午前予定",
        "午後予定",
        "就寝時間",
        "起床時間",
        "寝覚め",
        "やる気",
        "体温",
        "体重",
        "腹囲",
        "散歩",
        "自習時間",
        "入浴",
        "ストレッチ",
        "睡眠",
        "測定",
        "昼食",
        "夕食",
        "朝食",
        "開始時間",
        "終了時間",
        "午前活動",
        "午後活動",
        "次回の予定",
        "わんこ",
        "一極",
        "耳目確認",
        "命名規則",
        "活動報告",
    ]
    return [base[key] for key in keys]


def test_convert_to_model_returns_daily_report():
    report = convert_to_model(_build_raw_row())

    assert isinstance(report, DailyReport)
    assert report.usage_type == "在宅"
    assert report.body_temp == 36.5


def test_convert_to_model_converts_empty_string_to_none_for_scores():
    report = convert_to_model(_build_raw_row(寝覚め="", やる気="", 朝食=""))

    assert report.wake_up_score is None
    assert report.motivation_score is None
    assert report.breakfast_score is None


def test_convert_to_model_handles_invalid_temperature_as_none():
    report = convert_to_model(_build_raw_row(体温="abc"))

    assert report.body_temp is None


def test_convert_to_model_raises_for_missing_required_field():
    row = _build_raw_row()
    row[1] = None  # 体調

    with pytest.raises(Exception):
        convert_to_model(row)
