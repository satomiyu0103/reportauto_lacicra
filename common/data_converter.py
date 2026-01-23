from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from common.log_handler import log_error


class DailyReport(BaseModel):
    # 日本語の列名を alias として定義し、Python内では英語変数名で扱えるようにする
    date: datetime = Field(alias="日付")
    condition: str = Field(alias="体調")
    condition_reason: Optional[str] = Field(default=None, alias="体調の理由")
    usage_type: str = Field(alias="利用形態")

    am_plan: Optional[str] = Field(default=None, alias="午前予定")
    pm_plan: Optional[str] = Field(default=None, alias="午後予定")

    bath_status: Optional[str] = Field(default=None, alias="入浴")
    stretch_status: Optional[str] = Field(default=None, alias="ストレッチ")
    sleep_status: Optional[str] = Field(default=None, alias="睡眠")
    measurement_status: Optional[str] = Field(default=None, alias="測定")

    am_activity: Optional[str] = Field(default=None, alias="午前活動")
    pm_activity: Optional[str] = Field(default=None, alias="午後活動")
    next_plan: Optional[str] = Field(default=None, alias="次回の予定")

    # 仕事術・チェック項目
    wanko_method: Optional[str] = Field(default=None, alias="わんこ")
    ikkyoku_method: Optional[str] = Field(default=None, alias="一極")
    mimoku_check: Optional[str] = Field(default=None, alias="耳目確認")
    naming_rule: Optional[str] = Field(default=None, alias="命名規則")

    activity_report: Optional[str] = Field(default=None, alias="活動報告")

    # --- 時間 (Time) ---
    # 文字列として受け取り、必要ならvalidatorでdatetimeへ変換
    start_plan_time: Optional[str] = Field(default=None, alias="開始予定")
    end_plan_time: Optional[str] = Field(default=None, alias="終了予定")
    bed_time: Optional[str] = Field(default=None, alias="就寝時間")
    wake_up_time: Optional[str] = Field(default=None, alias="起床時間")
    study_time: Optional[str] = Field(default=None, alias="自習時間")
    start_time: Optional[str] = Field(default=None, alias="開始時間")
    end_time: Optional[str] = Field(default=None, alias="終了時間")

    # --- 数字 (Integer) ---
    wake_up_score: Optional[int] = Field(default=None, alias="寝覚め")
    motivation_score: Optional[int] = Field(default=None, alias="やる気")
    walk_steps: Optional[int] = Field(default=None, alias="散歩")
    lunch_score: Optional[int] = Field(default=None, alias="昼食")
    dinner_score: Optional[int] = Field(default=None, alias="夕食")
    breakfast_score: Optional[int] = Field(default=None, alias="朝食")

    # --- 数値 (Float) ---
    body_temp: Optional[float] = Field(default=None, alias="体温")
    body_weight: Optional[float] = Field(default=None, alias="体重")
    waist_circumference: Optional[float] = Field(default=None, alias="腹囲")

    model_config = {
        "populate_by_name": True,  # Python変数名での初期化も許可
        "extra": "ignore",  # 定義にないカラムが来てもエラーにしない
    }

    @field_validator(
        "wake_up_score",
        "motivation_score",
        "lunch_score",
        "dinner_score",
        "breakfast_score",
        "body_temp",
        "body_weight",
        "waist_circumference",
        "walk_steps",
        mode="before",
    )
    @classmethod
    def empty_string_to_none(cls, v: Any) -> Any:
        # 空文字ならNone
        if v == "":
            return None
        return v

    @field_validator("body_temp", mode="before")
    @classmethod
    def validate_temp(cls, v: Any) -> float | Any:
        """
        既存の temp_conv ロジックの移植

        :param cls: 説明
        :param v: 説明
        :type v: Any
        :return: 説明
        :rtype: float
        """
        try:
            if not v:
                return ""  # デフォルト
            return float(v)
        except (ValueError, TypeError) as e:
            log_error("体温の値が正しくありません", e)
            return None

    @field_validator("start_plan_time", "end_plan_time", mode="before")
    @classmethod
    def validate_time(cls, v: Any) -> str:
        try:
            if not isinstance(v, str) and v is None:
                # datetime/timeオブジェクトが来た場合の返還
                return v.strftime("%H:%M")
            elif v is None:
                return ""
            return v
        except Exception as e:
            log_error(f"時刻の変換でエラーが発生しました：{v}", e)
            return "22:00"


def convert_to_model(raw_data: list[Any]) -> DailyReport:
    keys = [
        "日付",
        "体調",
        "体調の理由",
        "利用形態",
        "開始予定",
        "終了予定",
        "午前予定",
        "午後予定",
        "就寝時間",
        "起床時間",
        "寝覚め",
        "やる気",
        "体温",
        "体重",
        "腹囲",
        "散歩",
        "自習時間",
        "入浴",
        "ストレッチ",
        "睡眠",
        "測定",
        "昼食",
        "夕食",
        "朝食",
        "開始時間",
        "終了時間",
        "午前活動",
        "午後活動",
        "次回の予定",
        "わんこ",
        "一極",
        "耳目確認",
        "命名規則",
        "活動報告",
    ]

    report_dict = dict(zip(keys, raw_data))

    return DailyReport(**report_dict)
