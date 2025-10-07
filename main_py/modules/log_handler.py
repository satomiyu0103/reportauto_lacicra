"""==========
■ ログの処理
=========="""

## pathlib
from pathlib import Path

## logの記入
import logging

# ログの設定
log_path = "logs/error_log.txt"
# reportauto_lacicra\logs\error_log.txt

logging.basicConfig(
    filename=str(log_path),
    level=logging.ERROR,
    # DEBUG(開発中推奨), INFO(本番), WARNING, ERROR(情報保守重視), CRITICAL
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def log_error(message, exception=None):

    if exception:
        logging.error(f"{message}: {exception}")
    else:
        logging.error(message)
