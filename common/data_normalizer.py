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


def convert_fullwidth_to_halfwidth(raw_text: str) -> str:
    """全角英数字・記号を半角に変換する"""

    return unicodedata.normalize("NFKC", raw_text)


def collapse_inline_spaces_keep_newlines(raw_text: str) -> str:
    """行内の連続空白を1つにまとめ、改行はそのまま残す"""

    text_lines = raw_text.replace("\u3000", " ").splitlines()

    return "\n".join(" ".join(line.split()) for line in text_lines)


def _is_blank_value(field_value: Any) -> bool:
    return field_value is None or field_value == ""


def normalize_text(raw_field_value: Any) -> Any:
    """テキスト項目の空白・全角を正規化する"""

    if _is_blank_value(raw_field_value):
        return raw_field_value

    if not isinstance(raw_field_value, str):
        return raw_field_value

    normalized_text = collapse_inline_spaces_keep_newlines(
        convert_fullwidth_to_halfwidth(raw_field_value)
    )

    return USAGE_TYPE_ALIASES.get(normalized_text, normalized_text)


def normalize_time(raw_field_value: Any) -> Any:
    """時刻項目を HH:MM 形式に揃える"""

    if _is_blank_value(raw_field_value):
        return raw_field_value

    if isinstance(raw_field_value, datetime):
        return raw_field_value.strftime("%H:%M")

    if isinstance(raw_field_value, time):
        return raw_field_value.strftime("%H:%M")

    time_text = collapse_inline_spaces_keep_newlines(
        convert_fullwidth_to_halfwidth(str(raw_field_value))
    )

    japanese_time_match = re.fullmatch(r"(\d{1,2})[時:：](\d{1,2})分?", time_text)

    if japanese_time_match:
        hour, minute = (
            int(japanese_time_match.group(1)),
            int(japanese_time_match.group(2)),
        )

        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return f"{hour:02d}:{minute:02d}"

    colon_separated_match = re.fullmatch(r"(\d{1,2})[:：](\d{2})", time_text)

    if colon_separated_match:
        hour, minute = (
            int(colon_separated_match.group(1)),
            int(colon_separated_match.group(2)),
        )

        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return f"{hour:02d}:{minute:02d}"

    compact_digits_match = re.fullmatch(r"\d{3,4}", time_text)

    if compact_digits_match:
        four_digit_time = time_text.zfill(4)

        hour, minute = int(four_digit_time[:2]), int(four_digit_time[2:])

        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return f"{hour:02d}:{minute:02d}"

    return time_text


def _remove_unit_suffix_from_number(number_with_unit: str) -> str:
    """数値末尾の単位・記号を除去する"""

    number_with_unit = re.sub(
        r"[度℃％%個歩分点]+(?:[以上以下]?)?$", "", number_with_unit
    )

    number_with_unit = re.sub(r"(?i)(kg|g|km|m|cm|mm)$", "", number_with_unit)

    return number_with_unit


def _extract_leading_number_string(number_with_unit: str) -> str:
    """先頭の数値部分を取り出す（単位付き入力向け）"""

    number_without_suffix = _remove_unit_suffix_from_number(number_with_unit)

    leading_number_match = re.match(r"^[+-]?\d+(?:\.\d+)?", number_without_suffix)

    if leading_number_match:
        return leading_number_match.group(0)

    return number_without_suffix


def normalize_number(raw_field_value: Any) -> Any:
    """数値項目の全角・単位付き表記を数値文字列に揃える"""

    if _is_blank_value(raw_field_value):
        return raw_field_value

    if isinstance(raw_field_value, (int, float)):
        return raw_field_value

    numeric_text = collapse_inline_spaces_keep_newlines(
        convert_fullwidth_to_halfwidth(str(raw_field_value))
    )

    numeric_text = numeric_text.replace(",", "").replace("，", "")

    numeric_text = numeric_text.replace("、", "")

    numeric_text = _extract_leading_number_string(numeric_text)

    return numeric_text


def normalize_integer(raw_field_value: Any) -> Any:
    """整数項目を正規化する（小数表記は四捨五入）"""

    if _is_blank_value(raw_field_value):
        return raw_field_value

    if isinstance(raw_field_value, int):
        return raw_field_value

    numeric_text = normalize_number(raw_field_value)

    if numeric_text == "":
        return raw_field_value

    try:
        return int(round(float(numeric_text)))

    except (ValueError, TypeError):
        return raw_field_value


def normalize_percent(raw_field_value: Any) -> Any:
    """パーセント表記を数値文字列に揃える"""

    if _is_blank_value(raw_field_value):
        return raw_field_value

    if isinstance(raw_field_value, (int, float)):
        return str(int(round(float(raw_field_value))))

    numeric_text = normalize_number(raw_field_value)

    if numeric_text == "":
        return raw_field_value

    try:
        return str(int(round(float(numeric_text))))

    except (ValueError, TypeError):
        return raw_field_value


def normalize_report_dict(raw_report_row: dict[str, Any]) -> dict[str, Any]:
    """日報1行分の辞書を自動補正する"""

    corrected_report_row = dict(raw_report_row)

    for field_name, raw_field_value in raw_report_row.items():
        if field_name == "日付" or _is_blank_value(raw_field_value):
            continue

        if field_name in TIME_FIELDS:
            corrected_field_value = normalize_time(raw_field_value)

        elif field_name in INTEGER_FIELDS:
            corrected_field_value = normalize_integer(raw_field_value)

        elif field_name in FLOAT_FIELDS:
            corrected_field_value = normalize_number(raw_field_value)

        elif field_name in PERCENT_FIELDS:
            corrected_field_value = normalize_percent(raw_field_value)

        elif field_name == "自習時間":
            corrected_field_value = normalize_integer(raw_field_value)

            if isinstance(corrected_field_value, int):
                corrected_field_value = str(corrected_field_value)

        elif field_name in TEXT_FIELDS:
            corrected_field_value = normalize_text(raw_field_value)

        else:
            continue

        if corrected_field_value != raw_field_value:
            log_info(
                f"📝 [Data Fix] {field_name}: {raw_field_value!r} → {corrected_field_value!r}"
            )

            corrected_report_row[field_name] = corrected_field_value

    return corrected_report_row
