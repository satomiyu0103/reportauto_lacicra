"""==========
■ ログの処理
=========="""

## logの記入
import logging
import logging.handlers
import os
import shutil
import sys

# rootなど
from config.settings import (
    LOG_DIR,
)

ARCHIVE_DIR_NAME = "logs_archives"


# ログ設定の初期化（一度だけ行う
# info.log: 通常の実行ログ / error.log: エラーログ
def _setup_logger():
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # ルートロガーの設定
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # アーカイブ用ディレクトリのパス定義と作成
    archive_dir = LOG_DIR / ARCHIVE_DIR_NAME
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)

    def custom_namer(default_name):
        """命名規則の変更

        Args:
            default_name (_str_): _description_

        Returns:
            _str_: _description_
        """
        return str(archive_dir / os.path.basename(default_name))

    def custom_rotator(source, dest):
        """移動処理の変更
        ソースファイルをnamerで決めたパスへ移動する
        Args:
            source (_str_): _description_
            dest (_str_): _description_
        """
        if os.path.exists(source):
            if os.path.exists(dest):
                os.remove(dest)
            shutil.move(source, dest)

    # ハンドラが重複しないようにチェック
    if not logger.handlers:
        # 1. Info用ファイルハンドラ
        info_log_path = LOG_DIR / "app_info.log"
        info_handler = logging.handlers.TimedRotatingFileHandler(
            filename=info_log_path,
            when="MIDNIGHT",
            interval=1,
            backupCount=30,
            encoding="utf-8",
        )
        info_handler.namer = custom_namer
        info_handler.rotator = custom_rotator

        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(formatter)

        # 【追加】ERROR以上のログを除外するフィルタを追加
        # levelnoがERROR(40)より小さい場合のみTrueを返す
        info_handler.addFilter(lambda record: record.levelno < logging.ERROR)

        logger.addHandler(info_handler)

        # 2. Error用ファイルハンドラ
        error_log_path = LOG_DIR / "error_info.log"
        error_handler = logging.handlers.TimedRotatingFileHandler(
            filename=error_log_path,
            when="MIDNIGHT",
            interval=1,
            backupCount=30,
            encoding="utf-8",
        )

        error_handler.namer = custom_namer
        error_handler.rotator = custom_rotator

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


def log_error(message, exception=None, level="ERROR"):
    """エラーの際にerror.logに記録する

    Args:
        message (str): error内容を明記する
        exception (Exception, optional): エラーメッセージ. Defaults to None.
        level(str): "WARN", "ERROR", "FATAL" のいずれか
    """
    icons = {
        "WARN": "⚠️",
        "ERROR": "❌",
        "FATAL": "🚨",
    }

    icon = icons.get(level, "❌")

    formatted_message = f"{icon} {message}"

    if exception:
        logging.error(f"{formatted_message}: {exception}")
    else:
        logging.error(formatted_message)


def log_info(message):
    """実行ログを出力 (NDFのwrite_log代替)"""
    logging.info(message)
