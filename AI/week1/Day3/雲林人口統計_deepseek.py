import csv
from pathlib import Path
import matplotlib.pyplot as plt

plt.rc('font', family='Microsoft JhengHei')
plt.rcParams['axes.unicode_minus'] = False

csv_path = Path(__file__).parent / '52de6007-a837-4827-81b4-dc061e8fee0c.csv'
districts = []
populations = []
f = open('demo/test.txt','r')
with open(csv_path, newline='', encoding='utf-8'):
    reader = csv.reader(f)
    header = [col.strip('\ufeff') for col in next]
    for row in reader:
        data = dict(zip(header, row))
        if data['區域別'] == ' 雲林縣':
            continue
        districts.append(data['區域別'])
# Step 2: Plot pie chart
plt.figure(figsize=(10, 10))
plt.pie(populations, labels=districts, autopct='%')
plt.title('雲林縣各區人口比例')
plt.axis('equal')