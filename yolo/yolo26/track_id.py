import cv2, numpy as np
from collections import defaultdict
from ultralytics import YOLO

# loading the yolo26 model
model = YOLO("yolo26n.pt")

# open the need track video
video = cv2.VideoCapture("2026-09-13 18-48-07.mp4")

# according Track ID to save the goal per history cnter point
track_history = defaultdict(list)

# loop to read the video per
while video.isOpened():
    success, frame = video.read()

    # when finished to read the video exit the loop
    if not success:
        break

    # current goal to track the goal
    # persist = True means the current fps and previous fps is same video
    result = model.track(
        frame,
        persist=True,
    )[0]

    # draw the model to create the check box, type, and Track ID
    annotated_frme = result.plot()

    # skip frame when no box detected or no track ID assigned yet
    if result.boxes is not None and result.boxes.id is not None:
        boxes = result.boxes.xywh.cpu()  # type: ignore[attr-defined]
        track_ids = result.boxes.id.int().cpu().tolist()  # type: ignore[attr-defined]

        # save the history track and the current fps location
        for box, track_id in zip(boxes, track_ids):
            x, y, w, h = box

            track = track_history[track_id]
            track.append((float(x), float(y)))

            # only save the recent 30 fps of location, avoid the track are going to unlimited
            if len(track) > 30:
                track.pop(0)
            # use the history center to convert OpenCV draw the plot need format
            points = np.array(track, dtype=np.int32).reshape((-1, 1, 2))

            # connection history center point, draw the goal of sport track
            cv2.polylines(
                annotated_frme,
                [points],
                isClosed=False,
                color=(0, 255, 255),
                thickness=3,
            )

    # show the fix it of fps
    cv2.imshow("YOLO26 Tracking", annotated_frme)

    # press Q key to exit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# release the video resource and close the window
video.release()
cv2.destroyAllWindows()