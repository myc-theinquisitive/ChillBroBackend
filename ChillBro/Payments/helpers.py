from datetime import datetime, date

def getTodayDay():
    day = datetime.now().weekday()
    if day == 6:
        return 0
    return day + 1

def getTodayDate():
    today = date.today().strftime("%d")
    return int(today) - 1