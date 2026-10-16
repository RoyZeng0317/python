# conda enviorment
01. create env
```bash
conda create yolo_track # yolo_track is example, you can change it.
```

02. open it.
```bash
conda activate yolo_track
```
result:
```bash
(yolo_track) PS C:\Users\roy\Documents\GitHub\python    # this is example, the location is changed.
```
03. install the ultralytics
```bash
pip install ultralytics
```

# capture training data from webcam
`capture_train_data.py` opens the local webcam (index 0), runs `model.track()` every frame,
and auto-saves the frame + YOLO-format label whenever a detection's confidence is below
`CONF_THRESH` (a "hard sample" the model is unsure about). Files are saved to
`dataset/images/` and `dataset/labels/` with a matching timestamp filename.

```bash
python capture_train_data.py
# press q to stop
```

Auto-generated labels are best-effort (from the current model) and should be manually
reviewed/corrected (e.g. with labelImg) before being used to retrain:
```bash
yolo detect train data=dataset.yaml model=yolo26n.pt epochs=50
```
