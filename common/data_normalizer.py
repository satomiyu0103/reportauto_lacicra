"""==========
■ 読み取りデータの自動補正
=========="""

import re
import unicodedata
from datetime import datetime, time
from typing import Any

from common.log_handler import log_info

TIME_FIELDS = {
    "開始予定",
    "終了予定",
    "就寝時間",
    "起床時間",
    "開始時間",
    "終了時間",
}

INTEGER_FIELDS = {
    "寝覚め",
    "やる気",
    "散歩",
    "昼食",
    "夕食",
    "朝食",
}

FLOAT_FIELDS = {"体温", "体重", "腹囲"}

PERCENT_FIELDS = {"わんこ", "一極", "耳目確認", "命名規則"}

TEXT_FIELDS = {
    "体調",
    "体調の理由",
    "利用形態",
    "午前予定",
    "午後予定",
    "入浴",
    "ストレッチ",
    "睡眠",
    "測定",
    "午前活動",
    "午後活動",
    "次回の予定",
    "活動報告",
}

# 利用形態の表記ゆれ（よくある入力ミス）
USAGE_TYPE_ALIASES = {
    "在宅勤務": "在宅",
    "在宅　": "在宅",
    "休日　": "休日",
}


def to_halfwidth(value: str) -> str:
    """全角英数字・記号を半角に変換する"""
    return unicodedata.normalize("NFKC", value)


def normalize_whitespace(value: str) -> str:
    """前後・連続空白（全角スペース含む）を正規化する"""
    return " ".join(value.replace("\u3000", " ").split())


def _is_empty(value: Any) -> bool:
    return value is None or value == ""


def normalize_text(value: Any) -> Any:
    """テキスト項目の空白・全角を正規化する"""
    if _is_empty(value):
        return value
    if not isinstance(value, str):
        return value

    normalized = normalize_whitespace(to_halfwidth(value))
    return USAGE_TYPE_ALIASES.get(normalized, normalized)


def normalize_time(value: Any) -> Any:
    """時刻項目を HH:MM 形式に揃える"""
    if _is_empty(value):
        return value
    if isinstance(value, datetime):
        return value.strftime("%H:%M")
    if isinstance(value, time):
        return value.strftime("%H:%M")

    text = normalize_whitespace(to_halfwidth(str(value)))

    match = re.fullmatch(r"(\d{1,2})[時:：](\d{1,2})分?", text)
    if match:
        hour, minute = int(match.group(1)), int(match.group(2))
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return f"{hour:02d}:{minute:02d}"

    match = re.fullmatch(r"(\d{1,2})[:：](\d{2})", text)
    if match:
        hour, minute = int(match.group(1)), int(match.group(2))
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return f"{hour:02d}:{minute:02d}"

    match = re.fullmatch(r"\d{3,4}", text)
    if match:
        digits = text.zfill(4)
        hour, minute = int(digits[:2]), int(digits[2:])
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return f"{hour:02d}:{minute:02d}"

    return text


def _strip_numeric_suffix(value: str) -> str:
    """数値末尾の単位・記号を除去する"""
    value = re.sub(r"[度℃％%個歩分点]+(?:[以上以下]?)?$", "", value)
    value = re.sub(r"(?i)(kg|g|km|m|cm|mm)$", "", value)
    return value


def _extract_numeric_text(value: str) -> str:
    """先頭の数値部分を取り出す（単位付き入力向け）"""
    value = _strip_numeric_suffix(value)
    match = re.match(r"^[+-]?\d+(?:\.\d+)?", value)
    if match:
        return match.group(0)
    return value


def normalize_number(value: Any) -> Any:
    """数値項目の全角・単位付き表記を数値文字列に揃える"""
    if _is_empty(value):
        return value
    if isinstance(value, (int, float)):
        return value

    text = normalize_whitespace(to_halfwidth(str(value)))
    text = text.replace(",", "").replace("，", "")
    text = text.replace("、", "")
    text = _extract_numeric_text(text)
    return text


def normalize_integer(value: Any) -> Any:
    """整数項目を正規化する（小数表記は四捨五入）"""
    if _is_empty(value):
        return value
    if isinstance(value, int):
        return value

    text = normalize_number(value)
    if text == "":
        return value

    try:
        return int(round(float(text)))
    except (ValueError, TypeError):
        return value


def normalize_percent(value: Any) -> Any:
    """パーセント表記を数値文字列に揃える"""
    if _is_empty(value):
        return value
    if isinstance(value, (int, float)):
        return str(int(round(float(value))))

    text = normalize_number(value)
    if text == "":
        return value

    try:
        return str(int(round(float(text))))
    except (ValueError, TypeError):
        return value


def normalize_report_dict(report_dict: dict[str, Any]) -> dict[str, Any]:
    """日報1行分の辞書を自動補正する"""
    normalized = dict(report_dict)

    for key, value in report_dict.items():
        if key == "日付" or _is_empty(value):
            continue

        if key in TIME_FIELDS:
            new_value = normalize_time(value)
        elif key in INTEGER_FIELDS:
            new_value = normalize_integer(value)
        elif key in FLOAT_FIELDS:
            new_value = normalize_number(value)
        elif key in PERCENT_FIELDS:
            new_value = normalize_percent(value)
        elif key == "自習時間":
            new_value = normalize_integer(value)
            if isinstance(new_value, int):
                new_value = str(new_value)
        elif key in TEXT_FIELDS:
            new_value = normalize_text(value)
        else:
            continue

        if new_value != value:
            log_info(f"📝 [Data Fix] {key}: {value!r} → {new_value!r}")
            normalized[key] = new_value

    return normalized
