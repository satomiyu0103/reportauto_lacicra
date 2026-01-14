"""==========
■ データの変換
=========="""

from common.log_handler import log_error


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


def temp_conv(report_dict):
    ## 体温を小数点以下まで表示
    try:
        val = report_dict.get("体温")
        if not val:
            return ""
        else:
            return f"{float(val):.1f}"  # 明示的にfloat型へ変換
    except (ValueError, TypeError) as e:
        log_error("体温の値が正しくありません", e)
        return "99.9"  # エラー時の代替値


def str_to_num(report_dict):
    """データを数値型に変換する

    Args:
        report_dict (_type_): _description_
    """
    numbers_keys = [
        "寝起き",
        "起床時のやる気",
        "昼食",
        "夕食",
        "朝食",
    ]

    to_num_keys = []
    for n in numbers_keys:
        val = report_dict.get(n)
        if not val or None:
            return
        else:
            t = int(val)
            to_num_keys.append(t)

    return to_num_keys


def time_conv(report_dict):
    ## 時刻をstr型(00:00)に変換
    target_keys = [
        "開始予定時刻",
        "終了予定時刻",
        "開始時刻",
        "終了時刻",
        "就寝時刻",
        "起床時刻",
    ]

    converted_times = []

    for key in target_keys:
        t = report_dict.get(key)
        try:
            if not isinstance(t, str) and t is not None:
                t = t.strftime("%H:%M")
            elif t is None:
                t = ""
            converted_times.append(t)
        except Exception as e:
            log_error(f"{key}({t})の時刻の変換でエラーが発生しました: ", e)
            converted_times.append("18:00")  # エラー時のデフォルト
    return converted_times


def data_conv(report_dict):
    """体温・時刻データを整える

    Args:
        report_dict (_dict_): 日報データ

    Returns:
        _float/string_: それぞれ整えたデータ
    """
    report_dict["体温"] = temp_conv(report_dict)

    numbers_keys = [
        "寝起き",
        "起床時のやる気",
        "昼食",
        "夕食",
        "朝食",
    ]
    numebers = str_to_num(report_dict)
    for num_key, num_val in zip(numbers_keys, numebers):
        report_dict[num_key] = num_val

    time_keys = [
        "開始予定時刻",
        "終了予定時刻",
        "開始時刻",
        "終了時刻",
        "就寝時刻",
        "起床時刻",
    ]
    times = time_conv(report_dict)
    for key, time_val in zip(time_keys, times):
        report_dict[key] = time_val

    return (
        report_dict["体温"],
        *[report_dict[k] for k in time_keys],
        *[report_dict[n] for n in numbers_keys],
    )
