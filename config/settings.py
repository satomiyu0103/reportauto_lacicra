# config/settings.py
from pathlib import Path
from dotenv import load_dotenv
import os

# このファイルの親configの親がルート
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# .envの読み込み
ENV_PATH = PROJECT_ROOT / "config" / ".env"
load_dotenv(ENV_PATH)

# 定数として外部から利用可能にする
EXCEL_FILE_PATH = os.getenv("EXCEL_FILE_PATH")
SLACK_WEBHOOK_URL_TOME = os.getenv("SLACK_WEBHOOK_URL_TOME")
SLACK_WEBHOOK_URL_TOSTUFF = os.getenv("SLACK_WEBHOOK_URL_TOSTUFF")  # 統合時に使用
your_username = os.getenv("LACICRA_USERNAME")
your_password = os.getenv()

# [設定スイッチ]
# "EXCEL" ： ローカルExcelファイルを使用
# "GOOGLE"：Googleスプレッドシートを使用
DATA_SAUCE = "GOOGLE"

# [Google Sheets設定]
KEY_FILE_NAME = "service_account.json"
SPREADSHEET_NAME = "日報"
SHEET_NAME = "日報DB"

#
CONFIG_DIR = PROJECT_ROOT / "config"
COMMON_DIR = PROJECT_ROOT / "common"
DATA_DIR = PROJECT_ROOT / "data"
SERVICES_DIR = PROJECT_ROOT / "services"
LOG_DIR = PROJECT_ROOT / "logs"
os.makedirs(LOG_DIR, exist_ok=True)
