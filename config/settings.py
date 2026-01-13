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

#
CONFIG_DIR = PROJECT_ROOT / "config"
COMMON_DIR = PROJECT_ROOT / "common"
DATA_DIR = PROJECT_ROOT / "data"
SERVICES_DIR = PROJECT_ROOT / "services"
LOG_DIR = PROJECT_ROOT / "logs"
