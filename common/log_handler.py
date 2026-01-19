"""==========
■ ログの処理
=========="""

## logの記入
import logging
import logging.handlers
import sys

# rootなど
from config.settings import (
    LOG_DIR,
)


# ログ設定の初期化（一度だけ行う
# info.log: 通常の実行ログ / error.log: エラーログ
def _setup_logger():
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # ルートロガーの設定
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # ハンドラが重複しないようにチェック
    if not logger.handlers:
        # 1. Info用ファイルハンドラ
        info_log_path = LOG_DIR / "app_info.log"
        info_handler = logging.handlers.TimedRotatingFileHandler(
            filename=info_log_path,
            when="D",
            interval=1,
            backupCount=30,
            encoding="utf-8",
        )
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(formatter)
        logger.addHandler(info_handler)

        # 【追加】ERROR以上のログを除外するフィルタを追加
        # levelnoがERROR(40)より小さい場合のみTrueを返す
        info_handler.addFilter(lambda record: record.levelno < logging.ERROR)

        logger.addHandler(info_handler)

        # 2. Error用ファイルハンドラ
        error_log_path = LOG_DIR / "error_info.log"
        error_handler = logging.handlers.TimedRotatingFileHandler(
            filename=error_log_path,
            when="D",
            interval=1,
            backupCount=30,
            encoding="utf-8",
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)

        # 3. コンソール出力（オプション：動作確認用）
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)


# 初期化実行
_setup_logger()


def log_error(message, exception=None):
    """エラーの際にerror.logに記録する

    Args:
        message (str): error内容を明記する
        exception (_type_, optional): エラーメッセージ. Defaults to None.
    """
    if exception:
        logging.error(f"{message}: {exception}")
    else:
        logging.error(message)


def log_info(message):
    """実行ログを出力 (NDFのwrite_log代替)"""
    logging.info(message)
