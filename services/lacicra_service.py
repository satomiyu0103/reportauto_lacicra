"""==========
■ Lacicra操作
=========="""

# 必要なライブラリ・モジュールをインポート
from typing import Any, Callable

## LACICRAの操作
from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    InvalidSessionIdException,
    NoSuchElementException,
    NoSuchWindowException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from common.data_converter import DailyReport
from common.log_handler import log_error, log_info


def handle_exceptions(action: Callable[[], Any], element_id: str) -> None:
    """
    指定されたアクションを実行し、発生した例外に応じて適切なレベルでログを記録する。
    """
    try:
        action()

    # --- [❌ ERROR] 個別の要素操作失敗 (処理は継続可能) ---
    except TimeoutException:
        log_error(f"'{element_id}'の読み込みに時間がかかりすぎています", level="ERROR")
    except NoSuchElementException:
        log_error(
            f"'{element_id}'が見つかりません。IDを確認してください", level="ERROR"
        )
    except ElementClickInterceptedException:
        log_error(f"'{element_id}'がほかの要素によりクリックできません", level="ERROR")
    except ElementNotInteractableException:
        log_error(
            f"'{element_id}'が操作できません。表示状態を確認してください", level="ERROR"
        )
    except StaleElementReferenceException:
        log_error(
            f"'{element_id}'が古くなっています(Stale)。再取得が必要です", level="ERROR"
        )

    # --- [🚨 FATAL] システム・ブラウザ自体のクラッシュ (即時停止) ---
    except NoSuchWindowException as e:
        log_error(
            f"[致命] 対象のウィンドウが見つかりません（手動で閉じられた可能性があります）。処理を中断します: {e}",
            level="FATAL",
        )
        log_info("🚨 処理を中断します。")
        raise  # 停止

    except InvalidSessionIdException as e:
        log_error(
            f"[致命] ブラウザセッションが終了しました。処理を中断します: {e}",
            level="FATAL",
        )
        log_info("🚨 処理を中断します。")
        raise  # 停止

    except WebDriverException as e:
        log_error(
            f"[致命] WebDriverのエラーです。Chromeのバージョン等を確認してください: {e}",
            level="FATAL",
        )
        log_info("🚨 処理を中断します。")
        raise  # 停止

    # --- [❌ ERROR] その他予期せぬエラー ---
    except Exception as e:
        log_error(
            f"[予期せぬエラー] '{element_id}'の処理中に未定義の問題が発生しました: {e}",
            level="ERROR",
        )


def open_lacicra(LACICRA_URL: str) -> tuple[WebDriver, WebDriverWait]:
    # Lacicraのサイトを開く
    ## Selenium実行後もChromeを開いたままにする
    options = Options()
    options.add_experimental_option("detach", True)
    # 常に最新→"stable" ver固定→"141"
    options.set_capability("browserVersion", "stable")

    try:
        # service = Service(ChromeDriverManager().install())
        ## Chromeを起動
        driver = webdriver.Chrome(options=options)  # service=service,
        ## ラシクラのURLにアクセス
        driver.get(LACICRA_URL)
        ## 待機時間の設定
        wait = WebDriverWait(driver, 300)
        return driver, wait
    except Exception as e:
        log_error("ブラウザの起動またはURLアクセスに失敗しました: ", e)
        raise


def send_login_key(wait: WebDriverWait, input_id: str, key: str) -> None:
    x_input_id = wait.until(EC.presence_of_element_located((By.ID, input_id)))
    x_input_id.clear()
    x_input_id.send_keys(key)


def login_lacicra(wait, your_username, your_password):
    # ユーザー名とパスワードを入力
    ## ボタンID、ユーザー名とパスワードをenvファイルから取得
    USERNAME_INPUT_ID = "loginAccount-inputEl"
    USERPASSWORD_INPUT_ID = "textfield-1014-inputEl"
    handle_exceptions(
        lambda: send_login_key(wait, USERNAME_INPUT_ID, your_username),
        USERNAME_INPUT_ID,
    )
    handle_exceptions(
        lambda: send_login_key(wait, USERPASSWORD_INPUT_ID, your_password),
        USERPASSWORD_INPUT_ID,
    )


# button-1110-btnIconEl
TODAY_REPORT_BTN_ID = "button-1130-btnIconEl"
TODAY_REPORT_CLASS_NAME = "x-btn-icon-el"


# ログイン後、今日の日報ボタンをクリック
def today_report_click(wait, btn_id):
    today_report_button = wait.until(EC.element_to_be_clickable((By.ID, btn_id)))
    today_report_button.click()


def today_report_btn_click(wait):
    # button-1110-btnIconEl
    TODAY_REPORT_BTN_ID = "button-1130-btnIconEl"
    handle_exceptions(
        lambda: today_report_click(wait, TODAY_REPORT_BTN_ID), TODAY_REPORT_BTN_ID
    )


def summary_input_by_name(wait: WebDriverWait, input_name: str, summary):
    """Name属性を利用して要素を特定し入力する"""
    summary_input: WebElement = wait.until(
        EC.element_to_be_clickable((By.NAME, input_name))
    )
    summary_input.clear()
    summary_input.send_keys(summary)


def summary_input_by_id(wait: WebDriverWait, input_id: str, summary):
    """ID属性を使用して要素を特定し入力する"""
    summary_input: WebElement = wait.until(
        EC.element_to_be_clickable((By.ID, input_id))
    )
    summary_input.clear()
    summary_input.send_keys(summary)


def input_summary(wait: WebDriverWait, input_name: str, input_id: str, summary) -> None:
    """日報のワードを送信する"""
    if summary is None:
        summary = "未入力"

    summary_str = str(summary)

    if input_name:
        try:
            summary_input_by_name(wait, input_name, summary_str)
            return
        except Exception:
            log_error("入力の要素が見つかりません")
            pass
    summary_input_by_id(wait, input_id, summary_str)


# 入力項目の定義： (辞書のキー, HTML ID, HTML Name)
# ※ Nameが不明な箇所は None としています。判明次第書き換えてください。
INPUT_FIELDS = [
    # 通所・時間系
    {"attr": "body_temp", "id": "textfield-1132-inputEl", "name": "temperature"},
    {
        "attr": "start_plan_time",
        "id": "timefield-1136-inputEl",
        "name": "reserve_start_time",
    },
    {
        "attr": "end_plan_time",
        "id": "timefield-1140-inputEl",
        "name": "reserve_end_time",
    },
    {"attr": "start_time", "id": "timefield-1145-inputEl", "name": "start_time"},
    {"attr": "end_time", "id": "timefield-1149-inputEl", "name": "end_time"},
    # 業務内容
    {
        "attr": "am_activity",
        "id": "textarea-1156-inputEl",
        "name": "program_group1_memo",
    },
    {
        "attr": "pm_activity",
        "id": "textarea-1160-inputEl",
        "name": "program_group11_memo",
    },
    {"attr": "activity_report", "id": "textarea-1172-inputEl", "name": "case_user"},
    # 睡眠系
    {"attr": "bed_time", "id": "timefield-1175-inputEl", "name": "sleep_start_time"},
    {"attr": "wake_up_time", "id": "timefield-1180-inputEl", "name": "sleep_end_time"},
    # 特殊: 固定値入力の項目は辞書キーではなく専用キーで定義し、下部で値を注入
    {"attr": "__SLEEP_MEMO__", "id": "textarea-1195-inputEl", "name": "sleep_remarks"},
    # 備考
    {"attr": "__REMARKS__", "id": "textarea-1213-inputEl", "name": "remarks"},
]


# 今日の日報を入力する
def input_today_summarys(wait: WebDriverWait, report_data: DailyReport) -> None:
    # 通所について

    for field in INPUT_FIELDS:
        summary: Any
        attr_name = field["attr"]
        elem_id = field["id"]
        elem_name = field["name"]

        if attr_name == "__SLEEP_MEMO__":
            summary = " "
        elif attr_name == "__REMARKS__":
            summary = " "
        else:
            summary = getattr(report_data, attr_name, None)
            log_info(f"{attr_name}を入力しています。")

        handle_exceptions(
            lambda: input_summary(wait, elem_name, elem_id, summary),
            f"{elem_id} (attr: {attr_name})",
        )


def slp_status_click(wait, slp_status, btn_ids):
    try:
        slp_status = int(slp_status)
    except (ValueError, TypeError):
        log_error(f"睡眠ステータスの値が不正です : {slp_status}")

    if slp_status not in [1, 2, 3, 4]:
        log_error(f"{slp_status}が範囲外です。1を設定します")
        slp_status = 1

    btn_id = btn_ids.get(slp_status)
    slp_btn_id = wait.until(EC.element_to_be_clickable((By.ID, btn_id)))
    slp_btn_id.click()


# ID定義 (変更なし)
WAKE_FEEL_BTN_IDS = {
    1: "radiofield-1203-inputEl",
    2: "radiofield-1204-inputEl",
    3: "radiofield-1205-inputEl",
    4: "radiofield-1206-inputEl",
}
WAKE_MOT_BTN_IDS = {
    1: "radiofield-1209-inputEl",
    2: "radiofield-1210-inputEl",
    3: "radiofield-1211-inputEl",
    4: "radiofield-1212-inputEl",
}


def today_slp_status_click(wait: WebDriverWait, daily_report: DailyReport) -> None:
    """睡眠・やる気ステータスの選択 (DailyReport対応版)"""

    # 属性アクセスに変更: daily_report.wake_up_score / motivation_score
    log_info("sleep_scoreを選択します")
    handle_exceptions(
        lambda: slp_status_click(wait, daily_report.wake_up_score, WAKE_FEEL_BTN_IDS),
        "WakeUp Score Select",
    )
    handle_exceptions(
        lambda: slp_status_click(wait, daily_report.motivation_score, WAKE_MOT_BTN_IDS),
        "Motivation Score Select",
    )


# ID定義 (変更なし)
LUNCH_BTN_IDS = {1: "radiofield-1217-inputEl", 2: "radiofield-1218-inputEl"}
DINNER_BTN_IDS = {1: "radiofield-1221-inputEl", 2: "radiofield-1222-inputEl"}
BF_BTN_IDS = {1: "radiofield-1225-inputEl", 2: "radiofield-1226-inputEl"}


def meal_click(wait, meal, meal_btn_ids):
    try:
        meal = int(meal)
    except (ValueError, TypeError):
        meal = 1
        log_error(f"食事の値が不正です: {meal}")

    if meal not in [1, 2]:
        log_error(f"{meal}が範囲外です。1を設定します")
        meal = 1
    btn_id = meal_btn_ids.get(meal)
    meal_btn_id = wait.until(EC.element_to_be_clickable((By.ID, btn_id)))
    meal_btn_id.click()


def today_meal_click(wait: WebDriverWait, daily_report: DailyReport) -> None:
    """食事ステータスの選択 (DailyReport対応版)"""
    # 属性アクセスに変更
    log_info("meal_scoreを選択します")
    handle_exceptions(
        lambda: meal_click(wait, daily_report.lunch_score, LUNCH_BTN_IDS),
        "Lunch Select",
    )
    handle_exceptions(
        lambda: meal_click(wait, daily_report.dinner_score, DINNER_BTN_IDS),
        "Dinner Select",
    )
    handle_exceptions(
        lambda: meal_click(wait, daily_report.breakfast_score, BF_BTN_IDS),
        "Breakfast Select",
    )


def save_button(wait, btn_id):
    # 日報を一時保存する
    save_button = wait.until(EC.element_to_be_clickable((By.ID, btn_id)))
    save_button.click()  # 日報を一時保存する


def save_button_click(wait):
    USERCASEDAILYSAVE_BTN_ID = "userCaseDailySaveButton-btnIconEl"
    handle_exceptions(
        lambda: save_button(wait, USERCASEDAILYSAVE_BTN_ID), USERCASEDAILYSAVE_BTN_ID
    )
