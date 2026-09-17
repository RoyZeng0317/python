import time
from datetime import datetime

def main():
    while True:
        now = datetime.now()
        print(now.strftime("%Y-%m-%d %H:%M:%S"))
        time.sleep(1)
if __name__ == "__main__":
    main()