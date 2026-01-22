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


# ログイン後、今日の日報ボタンをクリック
def today_report_click(wait, btn_id):
    today_report_button = wait.until(EC.element_to_be_clickable((By.ID, btn_id)))
    today_report_button.click()


def today_report_btn_click(wait):
    # button-1110-btnIconEl
    TODAY_REPORT_BTN_ID = "button-1111-btnIconEl"
    handle_exceptions(
        lambda: today_report_click(wait, TODAY_REPORT_BTN_ID), TODAY_REPORT_BTN_ID
    )


# 日報のワードを送信する
def input_summary(wait: WebDriverWait, input_id: str, summary: str | None) -> None:
    if summary is None:
        summary = "未入力"

    summary_input: WebElement = wait.until(
        EC.element_to_be_clickable((By.ID, input_id))
    )

    summary_input = wait.until(EC.element_to_be_clickable((By.ID, input_id)))
    summary_input.clear()
    summary_input.send_keys(summary)


# 今日の日報を入力する
def input_today_summarys(wait: WebDriverWait, report_dict: dict[str, Any]) -> None:
    # 通所について
    TEMP_INPUT_ID = "textfield-1132-inputEl"  # 体温
    START_PLAN_INPUT_ID = "timefield-1136-inputEl"  # 開始予定時間
    END_PLAN_INPUT_ID = "timefield-1140-inputEl"  # 終了予定時間
    START_ACTUAL_INPUT_ID = "timefield-1145-inputEl"  # 開始実績時間
    END_ACTUAL_INPUT_ID = "timefield-1149-inputEl"  # 終了実績時間

    AM_TASKS_INPUT_ID = "textarea-1156-inputEl"  # 午前予定
    PM_TASKS_INPUT_ID = "textarea-1160-inputEl"  # 午後予定

    DAILY_REPORT_INPUT_ID = "textarea-1172-inputEl"  # 日報

    SLP_TIME_INPUT_ID = "timefield-1175-inputEl"  # 就寝時間
    WK_TIME_INPUT_ID = "timefield-1180-inputEl"  # 起床時間
    SLP_MEMO_INPUT_ID = "textarea-1195-inputEl"  # 睡眠メモ

    REMARKS_INPUT_ID = "textarea-1213-inputEl"  # 備考

    handle_exceptions(
        lambda: input_summary(wait, TEMP_INPUT_ID, report_dict["体温"]), TEMP_INPUT_ID
    )  # 体温を入力
    handle_exceptions(
        lambda: input_summary(wait, START_PLAN_INPUT_ID, report_dict["開始予定時刻"]),
        START_PLAN_INPUT_ID,
    )  # 来所予定時間を入力
    handle_exceptions(
        lambda: input_summary(wait, END_PLAN_INPUT_ID, report_dict["終了予定時刻"]),
        END_PLAN_INPUT_ID,
    )  # 退所予定時間を入力
    handle_exceptions(
        lambda: input_summary(wait, START_ACTUAL_INPUT_ID, report_dict["開始時刻"]),
        START_ACTUAL_INPUT_ID,
    )  # 来所時間を入力
    handle_exceptions(
        lambda: input_summary(wait, END_ACTUAL_INPUT_ID, report_dict["終了時刻"]),
        END_ACTUAL_INPUT_ID,
    )  # 退所時間を入力

    # 午前・午後の取組
    handle_exceptions(
        lambda: input_summary(wait, AM_TASKS_INPUT_ID, report_dict["午前業務"]),
        AM_TASKS_INPUT_ID,
    )  # 午前の取組を入力
    handle_exceptions(
        lambda: input_summary(wait, PM_TASKS_INPUT_ID, report_dict["午後業務"]),
        PM_TASKS_INPUT_ID,
    )  # 午後の取組を入力

    ## 日報を入力
    handle_exceptions(
        lambda: input_summary(wait, DAILY_REPORT_INPUT_ID, report_dict["日報"]),
        DAILY_REPORT_INPUT_ID,
    )  # 日報を入力

    ## 睡眠についてを入力
    handle_exceptions(
        lambda: input_summary(wait, SLP_TIME_INPUT_ID, report_dict["就寝時刻"]),
        SLP_TIME_INPUT_ID,
    )  # 就寝時刻を入力
    handle_exceptions(
        lambda: input_summary(wait, WK_TIME_INPUT_ID, report_dict["起床時刻"]),
        WK_TIME_INPUT_ID,
    )  # 起床時刻を入力
    handle_exceptions(
        lambda: input_summary(wait, SLP_MEMO_INPUT_ID, " "), SLP_MEMO_INPUT_ID
    )  # memoを入力

    # 備考を入力
    handle_exceptions(
        lambda: input_summary(wait, REMARKS_INPUT_ID, ""), REMARKS_INPUT_ID
    )  # 備考を入力


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


def today_slp_status_click(wait, report_dict):
    # 睡眠について選択
    WAKE_FEEL_BTN_ID_1 = "radiofield-1184-inputEl"
    WAKE_FEEL_BTN_ID_2 = "radiofield-1185-inputEl"
    WAKE_FEEL_BTN_ID_3 = "radiofield-1186-inputEl"
    WAKE_FEEL_BTN_ID_4 = "radiofield-1187-inputEl"
    WAKE_MOT_BTN_ID_1 = "radiofield-1190-inputEl"
    WAKE_MOT_BTN_ID_2 = "radiofield-1191-inputEl"
    WAKE_MOT_BTN_ID_3 = "radiofield-1192-inputEl"
    WAKE_MOT_BTN_ID_4 = "radiofield-1193-inputEl"

    wake_feel_btn_ids = {
        1: WAKE_FEEL_BTN_ID_1,
        2: WAKE_FEEL_BTN_ID_2,
        3: WAKE_FEEL_BTN_ID_3,
        4: WAKE_FEEL_BTN_ID_4,
    }

    wake_mot_btn_ids = {
        1: WAKE_MOT_BTN_ID_1,
        2: WAKE_MOT_BTN_ID_2,
        3: WAKE_MOT_BTN_ID_3,
        4: WAKE_MOT_BTN_ID_4,
    }

    # wake_feel, wake_mot
    handle_exceptions(
        lambda: slp_status_click(wait, report_dict["寝起き"], wake_feel_btn_ids),
        wake_feel_btn_ids,
    )
    handle_exceptions(
        lambda: slp_status_click(wait, report_dict["起床時のやる気"], wake_mot_btn_ids),
        wake_mot_btn_ids,
    )


def meal_click(wait, meal, meal_btn_ids):
    try:
        meal = int(meal)
    except (ValueError, TypeError):
        log_error(f"食事の値が不正です: {meal}")
        meal = 1

    if meal not in [1, 2]:
        log_error(f"{meal}が範囲外です。1を設定します")
        meal = 1
    btn_id = meal_btn_ids.get(meal)
    meal_btn_id = wait.until(EC.element_to_be_clickable((By.ID, btn_id)))
    meal_btn_id.click()


def today_meal_click(wait, report_dict):
    # 食事について選択
    LUNCH_BTN_ID_1 = "radiofield-1198-inputEl"
    LUNCH_BTN_ID_2 = "radiofield-1199-inputEl"
    DINNER_BTN_ID_1 = "radiofield-1202-inputEl"
    DINNER_BTN_ID_2 = "radiofield-1203-inputEl"
    BF_BTN_ID_1 = "radiofield-1206-inputEl"
    BF_BTN_ID_2 = "radiofield-1207-inputEl"

    lunch_btn_ids = {1: LUNCH_BTN_ID_1, 2: LUNCH_BTN_ID_2}

    dinner_btn_ids = {1: DINNER_BTN_ID_1, 2: DINNER_BTN_ID_2}

    bf_btn_ids = {1: BF_BTN_ID_1, 2: BF_BTN_ID_2}
    handle_exceptions(
        lambda: meal_click(wait, report_dict["昼食"], lunch_btn_ids), lunch_btn_ids
    )
    handle_exceptions(
        lambda: meal_click(wait, report_dict["夕食"], dinner_btn_ids), dinner_btn_ids
    )
    handle_exceptions(
        lambda: meal_click(wait, report_dict["朝食"], bf_btn_ids), bf_btn_ids
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
