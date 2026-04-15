from datetime import date, datetime

from common.data_loader import find_today_row


def test_find_today_row_returns_matching_datetime_row():
    target = date(2026, 4, 15)
    rows = [
        [datetime(2026, 4, 14, 9, 0), "a"],
        [datetime(2026, 4, 15, 9, 0), "b"],
    ]

    found = find_today_row(rows, target)

    assert found == rows[1]


def test_find_today_row_returns_matching_string_date_row():
    target = date(2026, 4, 15)
    rows = [
        ["2026/04/14", "a"],
        ["2026/04/15", "b"],
    ]

    found = find_today_row(rows, target)

    assert found == rows[1]


def test_find_today_row_returns_none_when_not_found():
    target = date(2026, 4, 15)
    rows = [
        [datetime(2026, 4, 14, 9, 0), "a"],
        ["", "blank-date"],
        [],
    ]

    found = find_today_row(rows, target)

    assert found is None
