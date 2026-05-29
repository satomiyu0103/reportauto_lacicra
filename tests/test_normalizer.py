from datetime import datetime

import pytest

from common.data_converter import convert_to_model
from common.data_normalizer import (
    normalize_integer,
    normalize_number,
    normalize_percent,
    normalize_report_dict,
    normalize_text,
    normalize_time,
)
from tests.test_converter import _build_raw_row


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("０９：３０", "09:30"),
        ("9:30", "09:30"),
        ("0930", "09:30"),
        ("9時30分", "09:30"),
    ],
)
def test_normalize_time(raw, expected):
    assert normalize_time(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("３６．５度", "36.5"),
        ("３，０００", "3000"),
        ("52.0kg", "52.0"),
    ],
)
def test_normalize_number(raw, expected):
    assert normalize_number(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("１", 1),
        ("2.0", 2),
        ("３，０００", 3000),
    ],
)
def test_normalize_integer(raw, expected):
    assert normalize_integer(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("８０％", "80"),
        ("75.0", "75"),
        ("90%", "90"),
    ],
)
def test_normalize_percent(raw, expected):
    assert normalize_percent(raw) == expected


def test_normalize_text_converts_fullwidth_and_trims():
    assert normalize_text("  在宅　") == "在宅"
    assert normalize_text("在宅勤務") == "在宅"


def test_normalize_report_dict_logs_and_applies_field_rules():
    report_dict = {
        "日付": datetime(2026, 4, 15),
        "体温": "３６．５度",
        "開始予定": "９：００",
        "わんこ": "８０％",
        "散歩": "３，０００",
        "利用形態": "  在宅　",
    }

    normalized = normalize_report_dict(report_dict)

    assert normalized["体温"] == "36.5"
    assert normalized["開始予定"] == "09:00"
    assert normalized["わんこ"] == "80"
    assert normalized["散歩"] == 3000
    assert normalized["利用形態"] == "在宅"


def test_convert_to_model_applies_normalization():
    report = convert_to_model(
        _build_raw_row(
            体温="３６．８度",
            開始予定="９：００",
            わんこ="８０％",
            散歩="３，０００",
            利用形態="  在宅　",
        )
    )

    assert report.body_temp == 36.8
    assert report.start_plan_time == "09:00"
    assert report.wanko_method == "80"
    assert report.walk_steps == 3000
    assert report.usage_type == "在宅"
