# 06 - read the tranning result, draw key metric
# tranning Ultralytics can all of result save to runs/train/<your run>/:
# results.csv           every epoch of loss / mAP / precision / recall
# confusion_matrix.png  confustion matrix (where typs will be mix it)
# label.jps             tranning label
# val_batch*.jpg        verify batch vs 

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei"]
plt.rcParams["axes.unicode_minus"] = False

BASE = Path(__file__).parent

# auto to find the newest of results.csv (two locatoin need to scan)
search_dirs = [BASE / "runs", BASE.parent.parent / "runs"]
candidates = []
for d in search_dirs:
    if d.exists():
        candidates.extend(d.rglob("results.csv"))
candidates = sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True)
if not candidates:
    raise FileNotFoundError(
        "can't find the results.csv, need to run 05_訓練自己的yolo.py"
    )
results_csv = candidates[0]
RUN_DIR = results_csv.parent
print(f"read: {results_csv}")

df = pd.read_csv(results_csv)
# Ultralytics 的欄位前面通常有空白，清掉
df.columns = [c.strip() for c in df.columns]
print("可用欄位: ", df.columns.tolist())

# --- draw 4 picture learning 曲線: loss / mAP / precision / recall ----
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle(f"tranning result: {RUN_DIR.name}", fontsize=14, fontweight="bold")

epochs = df["epoch"]

# 1) box loss + cls loss + dfl loss
ax = axes[0, 0]
for col, name in [("train/box_loss", "train box"),
                  ("train/cls_loss", "train cls"),
                  ("val/box_loss", "verify box"),
                  ("val/cls_loss", "verify box")]:
    if col in df.columns:
        ax.plot(epochs, df[col], label=name)
ax.set_title("Loss 曲線")
ax.set_xlabel("epoch"); ax.set_ylabel("loss")
ax.legend(); ax.grid(alpha=0.3)

# 2) mAP
ax = axes[0, 1]
for col, name in [("metrics/mAP50(B)", "mAP@0.5"),
                  ("metrics/mAP50-95(B)", "mAP@0.5:0.95")]:
    if col in df.columns:
        ax.plot(epochs, df[col], label=name)
ax.set_title("mAP 曲線")
ax.set_xlabel("epoch"); ax.set_ylabel("mAP")
ax.legend(); ax.grid(alpha=0.3)

# 3) precision
ax = axes[1, 0]
if "metrics/precision(B)" in df.columns:
    ax.plot(epochs, df["metrics/precision(B)"], color="#3498db", marker="o", markersize=3)
ax.set_title("Precision (精確率: 預測為正的裡面真正是正的比例)")
ax.set_xlabel("epoch"); ax.set_ylabel("precision")
ax.grid(alpha=0.3)

# 4) recall
ax = axes[1, 1]
if "metrics/recall(B)" in df.columns:
    ax.plot(epochs, df["metrics/recall(B)"], color="#e74c3c", marker="o", markersize=3)
ax.set_title("Recall (招回率: 所有真正的裡面被找的比例)")
ax.set_xlabel("epoch"); ax.set_ylabel("recall")
ax.grid(alpha=0.3)

plt.tight_layout()
plt.show()

# print final 指標
last = df.iloc[-1]
print()
print("=" * 60)
print(f"final epoch{int(last['epoch'])}指標")
print("=" * 60)
for col in ["metrics/mAP50(B)", "metrics/mAP50-95(B)",
            "metrics/precision(B)", "metrics/recall(B)"]:
    if col in df.columns:
        print(f"    {col:30s}{last[col]:.4f}")

print()
print("if trainning are not:")
print(" - add epochs(05 of EPOCHS turn 50-100)")
print(" - check data.yaml of types is ture or not")
print(" - check confusion_matrix.png to mix which two types, add the data")
print(" - data amounts so less can manual to augmentation or use Roboflow inside augementation")
print()
print(f"confusion matrix diagram: {RUN_DIR / 'confusion_matrix.png'}")
print(f"val batch: {RUN_DIR / 'val_batch0_pred.jpg'}")