"""==========
■ 設集集
=========="""

# config/settings.py
import os
from pathlib import Path

from dotenv import load_dotenv

# 1. Lacicra (Web自動入力) を実行する形態
# 例: 在宅のときだけブラウザ操作をさせたい場合
TARGET_MODES_LACICRA = ["在宅"]

# 2. Morning Post (朝のSlack) を実行する形態
# 例: 在宅と通所のときは挨拶したい
TARGET_MODES_MORNING = ["在宅", "在宅(午前のみ)"]

# 3. Evening Post (夕方のSlack) を実行する形態
# 例: ほぼ全ての日で報告したい
TARGET_MODES_EVENING = ["在宅", "在宅(午後のみ)"]

# [設定スイッチ] "EXCEL" or "GOOGLE"
# "EXCEL" ： ローカルExcelファイルを使用
# "GOOGLE"：Googleスプレッドシートを使用
DATA_SOURCE = "GOOGLE"
# DATA_SOURCE = "EXCEL"

# このファイルの親configの親がルート
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# .envの読み込み
ENV_PATH = PROJECT_ROOT / "config" / ".env"
load_dotenv(ENV_PATH)

# 定数として外部から利用可能にする
EXCEL_FILE_PATH = os.getenv("EXCEL_FILE_PATH")
SLACK_WEBHOOK_URL_TOME = os.getenv("SLACK_WEBHOOK_URL_TOME")
SLACK_WEBHOOK_URL_TOSTUFF = os.getenv("SLACK_WEBHOOK_URL_TOSTUFF")
LACICRA_USERNAME = os.getenv("LACICRA_USERNAME")
LACICRA_PASSWORD = os.getenv("LACICRA_PASSWORD")

# [Google Sheets設定]
KEY_FILE_NAME = "service_account.json"
SPREADSHEET_NAME = "日報"
SHEET_NAME = "日報DB"

# ディレクトリ定義
CONFIG_DIR = PROJECT_ROOT / "config"
COMMON_DIR = PROJECT_ROOT / "common"
DATA_DIR = PROJECT_ROOT / "data"
SERVICES_DIR = PROJECT_ROOT / "services"
LOG_DIR = PROJECT_ROOT / "logs"

# ログフォルダ作成
os.makedirs(LOG_DIR, exist_ok=True)
