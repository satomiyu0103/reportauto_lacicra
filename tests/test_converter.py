# tests/test_converter.py
from common.data_converter import temp_conv


def test_temp_conv_valid():
    assert temp_conv({"体温": 36.5}) == "36.5"


def test_temp_conv_invalid():
    assert temp_conv({"体温": None}) == ""  # または適切なデフォルト値


test_temp_conv_valid()
test_temp_conv_invalid()
