
def is_trading_day(acc):
    return acc.sdk.get_market_status()['is_trading_day']

def format_datetime_with_chinese_weekday(datetime):
    days = {
        "Monday": "一",
        "Tuesday": "二",
        "Wednesday": "三",
        "Thursday": "四",
        "Friday": "五",
        "Saturday": "六",
        "Sunday": "日"
    }

    formatted_time = datetime.strftime('%Y-%m-%d') + f"({days[datetime.strftime('%A')]}) " + datetime.strftime('%H:%M:%S')
    return formatted_time

