"""==========
■ データ取得
=========="""

## パスやIDの取得
from pathlib import Path
from dotenv import load_dotenv
import os

## Excelの操作
from datetime import datetime
import openpyxl

# log_handler.py
from modules.log_handler import log_error


def get_env_keys():
    # excelファイルの取得
    try:
        PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    except NameError:
        PROJECT_ROOT = Path.cwd()
    # configフォルダ内にあるenvファイルの場所を指定する
    file_path = PROJECT_ROOT / "config" / ".env"
    load_dotenv(file_path)
    try:
        # ExcelパスとLacicraのusername/passwordを取得
        EXCEL_FILE_PATH = os.getenv("EXCEL_FILE_PATH")
        your_username = os.getenv("LACICRA_USERNAME")
        your_password = os.getenv("LACICRA_PASSWORD")

        if not EXCEL_FILE_PATH:
            raise ValueError("EXCEL_FILE_PATHが.envから読み込めません")
        if not your_username or not your_password:
            raise ValueError("ユーザ名/パスワードが.envにありません")
        return EXCEL_FILE_PATH, your_username, your_password
    except Exception as e:
        log_error(".envファイル読み込みエラー：", e)
        raise


def get_excel_data(EXCEL_FILE_PATH):
    try:
        # Excelから記入するデータを取得
        ## Excelファイルの読み込み
        wb = openpyxl.load_workbook(EXCEL_FILE_PATH)
        ws = wb["日報DB"]
    except FileNotFoundError:
        log_error("Excelファイルが見つかりません")
        exit()
    except KeyError:
        log_error("指定されたシート『日報DB』が見つかりません")
        exit()

    return ws


def get_today_report(ws):
    ## 今日の日付を文字列で取得
    today_str = datetime.now().strftime("%Y/%m/%d")

    ## 今日の行を探す
    report = None
    for row_today in ws.iter_rows(min_row=2, values_only=True):
        if row_today[0] and row_today[0].strftime("%Y/%m/%d") == today_str:
            report = row_today
            break
    if report is None:
        log_error("今日の日付のデータが存在しません")
        exit()

    return report


def unpack_report(report):
    keys = [
        "日付",
        "体調",
        "体調の理由",
        "通所形態",
        "開始予定時刻",
        "終了予定時刻",
        "午前予定",
        "午後予定",
        "就寝時刻",
        "起床時刻",
        "寝起き",
        "起床時のやる気",
        "体温",
        "体重",
        "腹囲",
        "歩数",
        "自習時間",
        "入浴",
        "ストレッチ",
        "睡眠",
        "測定",
        "昼食",
        "夕食",
        "朝食",
        "開始時刻",
        "終了時刻",
        "午前業務",
        "午後業務",
        "次回活動予定",
        "わんこそば仕事術",
        "一極集中仕事術",
        "耳目確認",
        "ファイル命名規則",
        "日報",
    ]
    return dict(zip(keys, report))
