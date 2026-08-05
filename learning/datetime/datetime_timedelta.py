from datetime import datetime
from datetime import timedelta

t = timedelta(days=4, hours=10)

t.days
# 4

t.seconds
# 36000

# t.hours (python 3.12.10 are not available)
# Traceback (most recent call last):
# File "<pyshell#119>", line 1, in <module> t.hours
# AttributeError: 'datetime.timedelta' object has no attribute 'hours'

t.seconds / 60 / 60
# 10.0
t.seconds / 3600
# 10.0


######

eta = timedelta(hours=6)

today = datetime.today()

today
# datetime.datetime(2026, 8, 1, 21, 4, 14, 1523472)

today + eta
# datetime.datetime(2026, 8, 2, 3, 4, 14, 1523472)

str(today + eta)
# '2026-08-02 03:04:14.152347'
print("The estimated time of arrival is " + str(today + eta))