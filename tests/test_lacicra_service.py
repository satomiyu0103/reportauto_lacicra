from selenium.common.exceptions import NoSuchWindowException, WebDriverException

from services.lacicra_service import BrowserClosedError, _is_browser_closed


def test_is_browser_closed_detects_no_such_window():
    assert _is_browser_closed(NoSuchWindowException("no such window"))


def test_is_browser_closed_detects_closed_window_message():
    exc = WebDriverException("target window already closed")
    assert _is_browser_closed(exc)


def test_is_browser_closed_ignores_other_webdriver_errors():
    exc = WebDriverException("chrome not reachable")
    assert not _is_browser_closed(exc)


def test_browser_closed_error_is_exception():
    assert issubclass(BrowserClosedError, Exception)
