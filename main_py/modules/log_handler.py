"""==========
■ ログの処理
=========="""

from pathlib import Path

## logの記入
import logging


def log_error(message, exception=None):
    try:
        PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    except NameError:
        PROJECT_ROOT = Path.cwd()

    log_path = PROJECT_ROOT / "logs" / "error_log.txt"

    logging.basicConfig(
        filename=str(log_path),
        level=logging.ERROR,
        # DEBUG(開発中推奨), INFO(本番), WARNING, ERROR(情報保守重視), CRITICAL
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    if exception:
        logging.error(f"{message}: {exception}")
    else:
        logging.error(message)
