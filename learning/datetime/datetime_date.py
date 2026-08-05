from datetime import date
from datetime import timedelta

datetime = date.today()
# datetime.datetime(2026, 8, 1, 21, 4, 14, 1523472)

today = datetime.today()

type(today)
# <class 'datetime.datetime'>

today_date = date.today()

today_date
# datetime.date(2026, 8, 1)

type(today_date)
# <class 'datetime.date'>

today_date.month
# 8
today_date.year

# 2026

today_date.day
# 1

Daniel_brithday = date(today_date.year + 1, 5, 17)
Daniel_brithday
# datetime.date(2027, 5, 17)

# We need to use != & == rather than is / is not for comparison. Sorry for the mistake in the video.
if Daniel_brithday != today_date:
    print("Sorry there are still " + str((Daniel_brithday - today_date).days) + " days until Daniel's birthday!")
else:
    print("Yay it's Daniel's birthday!")