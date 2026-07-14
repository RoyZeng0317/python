# tranning my yolo11n model
# this will be to:
# 1) auto scan the dataset folder and under all data.yaml rows for me to choice
# 2) check the GPU or not, if not will be choice CPU to training (will be slowest)
# 3) according the GPU  auto advise the batch size
# 4) tranning result will be always to save the yolo/runs\ under
# tranning time  (YOLO11n, 640x640, 20 epochs, 1200 datasheet of paper)
# - CPU (i5 / i7 laptop)        30 min
# - RTX 4060 8GB                6-10mins
# enivorments:
# pip install -r requirements.txt

from pathlib import Path
import sys

import torch
from ultralytics import YOLO

BASE     = Path(__file__).parent
DATASETS = BASE / "datasets"
PROJECT_DIR = BASE / "runs"     # abouslt lcation, tranning result are always at the yolo/runs

# trainning numer
EPOCHS      = 20        # trainning run, 20 is . 看 mAP 取線沒收斂再加
IMG_SIZE    = 640       # 影像解析度。320 快、640 準、1280 GPU 才吃得動
RUN_NAME    = "train"   # save to runs/train, run/traning2, ...
PATIENCE    = 10        # continue N epoch mAP, are not improving will be early stopping

# auto to find the dataset
def find_all_dataset():
    """reply[(name, data_yaml_path), ...]"""
    if not DATASETS.exists():
        return []
    results = []
    for yaml in sorted(DATASETS.rglob("data.yaml")):
        # yaml file of dad folder name is dataset
        results.append((yaml.parent.name, yaml))
    return results

def choice_dataset(datasets):
    if not datasets:
        print()
        print("=" * 60)
        print("can't find any dataset")
        print("=" * 60)
        print(f"預期位置: {DATASETS}/<name>/data.yaml")
        print()
        print("有兩條路取得dataset:")
        print(" a) run 04_download example dataset.py from Roboflow download")
        print(" b) use Label Studio label it, run convert_ls_json_to_yolo.py")
        sys.exit(1)

    if len(datasets) == 1:
        name, path = datasets[0]
        print(f"only find a dataset: {name}")
        return path
    print()
    print("find all dataset, choice one to tranning:")
    for i, (name, path) in enumerate(datasets, 1):
        # show the types info
        try:
            import yaml as yaml_lib
            info = yaml_lib.safe_load(open(path, encoding = "utf-8"))
            nc = info.get("nc", "?")
            names = info.get("names", [])
            print(f"    [{i}] {name:20s}   {nc} types: {names}")
        except Exception:
            print(f"    [{i}] {name}")
        print()

    while True:
        try:
            choice = input(f"choice [1-{len(datasets)}] (Enter use 1) :").strip()
        except(EOFError, KeyboardInterrupt):
            sys.exit(1)
        if not choice:
            return datasets[0][1]
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(datasets):
                return datasets[idx][1]
        except ValueError:
            pass
        print("Please enter vauble of number")

# according the GPU 顯存 advise the batch size
def advise_batch_size():
    if not torch.cuda.is_available():
        return 8, "cpu", None
    device_name = torch.cuda.get_device_name(0)
    total_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3

    # 粗略對照: 640 tranning yolo11n almost need(batch x 1.5) GB
    if total_gb >= 20:
        batch = 32
    elif total_gb >= 10:
        batch = 16
    elif total_gb >= 6:
        batch = 8
    elif total_gb >= 4:
        batch = 4
    else:
        batch = 2
    return batch, "cuda:0", f"{device_name} ({total_gb:.1f} GB)"

def main():
    print("=" * 60)
    print("yolo11n tranning (ultralytics)")
    print("=" * 60)

    # 1) choose dataset
    datasets = find_all_dataset()
    data_yaml = choice_dataset(datasets)
    print(f"use dataset: {data_yaml}")

    # 2) show devices and batch size advice
    batch, device, gpu_info = advise_batch_size()
    print()
    if gpu_info:
        print(f"check GPU: {gpu_info}")
        print(f"advice batch size: {batch}")
        print(" when tanning out of memory, batch need to trun to small (or clsoe eat the GPU of app)")
    else:
        print("no check GPU, use CPU to tranning")
        print(f"advices batch size: {batch}(CPU also too big)")
        print(" time remanning: small datasets 30-60 mins, middle: 1-3 hours")

    print()
    print(f"tranning value: epochs={EPOCHS}, imgs={IMG_SIZE}, patience={PATIENCE}")
    print(f"result save to: {PROJECT_DIR}")
    print()

    # 3) make sure: (avoid start long time trainning)
    try:
        proceed = input("press enter to start trainning (ctrl+c to cancel:").strip()
    except(EOFError, KeyboardInterrupt):
        sys.exit(0)

    # 4) tranning
    model = YOLO("yolo11n.pt") # first will be run auto download 5.5MB
    results = model.train(
        data        = str(data_yaml),
        epochs      = EPOCHS,
        imgsz       = IMG_SIZE,
        batch       = batch,
        device      = device,
        project     = str(PROJECT_DIR),
        name        = RUN_NAME,
        exist_ok    = False,
        patience    = PATIENCE,
        verbose     = True,
    )

    # 5) show the result
    save_dir = Path(results.save_dir)
    print()
    print("=" * 60)
    print("finished to tranning")
    print("=" * 60)
    print(f"best weights: {save_dir / 'weights' / 'best.pt'}")
    print(f"final weights: {save_dir / 'weights' / 'best.pt'}")
    print(f"trainning result: {save_dir / 'results.png'}")
    print(f"confusion matrix: {save_dir / 'confusion_matrix.png'}")
    print()
    print("Next step:")
    print(" 06_評估訓練結果.py      看 mAP / Loss 取線")
    print(" 07_自動訓練模型推論.py    接 webcam 有 GUI 版")
    print(" 08_webcam串流推論.py  接 webcam 串流到瀏覽器 (recommand)")

if __name__ == "__main__":
    main()