import pandas as pd

def read_warnings_from_log(log_filepath):
    warnings = []
    with open(log_filepath, 'r', encoding='utf-8') as log_file:
        for line in log_file:
            if ' - WARNING - ' in line:
                warnings.append(line.strip())
    return warnings

def is_trading_day(acc):
    return acc.sdk.get_market_status()['is_trading_day']

def get_current_formatted_datetime():
    now = pd.Timestamp.now()

    days = {
        "Monday": "一",
        "Tuesday": "二",
        "Wednesday": "三",
        "Thursday": "四",
        "Friday": "五",
        "Saturday": "六",
        "Sunday": "日"
    }

    formatted_time = now.strftime('%Y-%m-%d') + f"({days[now.strftime('%A')]}) " + now.strftime('%H:%M:%S')
    return formatted_time

if __name__ == '__main__':
    print(get_current_formatted_datetime())
    print(type(get_current_formatted_datetime()))