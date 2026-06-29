import csv
from pathlib import Path
import pandas as pd, matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei", "SimHei", "DFKai-SB"]

dir = Path(__file__).parent
csv = list(dir.glob("*.csv"))[0]

df = pd.read_csv(csv)
df = df[df["性別"] == "男女合計"]

plt.pie(df["人口數"], labels=df["區域別"], autopct="%1.1f%%")
plt.title("雲林縣各區人口比例")
plt.show()
