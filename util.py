import pickle

from skimage.transform import resize
import numpy as np
import cv2

EMPTY = True
OCCUPIED = False

MODEL = pickle.load(open("data/model.p", "rb"))


def empty_or_occupied(spot_bgr):
    flat_data = []
    img_resized = resize(spot_bgr, (15, 15, 3))
    flat_data.append(img_resized.flatten())
    flat_data = np.array(flat_data)

    y_output = MODEL.predict(flat_data)

    if y_output[0] == 1:
        return EMPTY  # Changed from OCCUPIED
    else:
        return OCCUPIED  # Changed from EMPTY


def get_parking_lot_spots_bboxes(connected_components):
    (total_labels, label_ids, values, centroid) = connected_components

    spots = []
    coef = 1
    for i in range(1, total_labels):
        x1 = int(values[i, cv2.CC_STAT_LEFT] * coef)
        y1 = int(values[i, cv2.CC_STAT_TOP] * coef)
        w = int(values[i, cv2.CC_STAT_WIDTH] * coef)
        h = int(values[i, cv2.CC_STAT_HEIGHT] * coef)

        spots.append((x1, y1, w, h))

    return spots
