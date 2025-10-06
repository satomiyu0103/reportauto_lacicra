"""==========
■ データの変換
=========="""

from modules.log_handler import log_error


def temp_conv(report_dict):
    ## 体温を小数点以下まで表示
    try:
        if not report_dict["体温"]:
            return ""
        else:
            return f"{float(report_dict["体温"]):.1f}"  # 明示的にfloat型へ変換
    except (ValueError, TypeError) as e:
        log_error("体温の値が正しくありません", e)
        return "99.9"  # エラー時の代替値


def time_conv(report_dict):
    ## 時刻をstr型(00:00)に変換
    type_check_times = [
        report_dict["開始予定時刻"],
        report_dict["終了予定時刻"],
        report_dict["開始時刻"],
        report_dict["終了時刻"],
        report_dict["就寝時刻"],
        report_dict["起床時刻"],
    ]
    converted_times = []
    for t in type_check_times:
        try:
            if not isinstance(t, str):
                t = t.strftime("%H:%M")
            converted_times.append(t)
        except Exception as e:
            log_error(f"{t}の時刻の変換でエラーが発生しました: ", e)
            converted_times.append("18:00")  # エラー時のデフォルト
    return converted_times


def data_conv(report_dict):
    report_dict["体温"] = temp_conv(report_dict)
    (
        report_dict["開始予定時刻"],
        report_dict["終了予定時刻"],
        report_dict["開始時刻"],
        report_dict["終了時刻"],
        report_dict["就寝時刻"],
        report_dict["起床時刻"],
    ) = time_conv(report_dict)
