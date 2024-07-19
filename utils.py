import pandas as pd

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