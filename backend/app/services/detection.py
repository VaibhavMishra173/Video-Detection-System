import logging
from typing import Tuple, List

import cv2
import numpy as np
import torch
from ultralytics import YOLO

# Setup logger
logger = logging.getLogger(__name__)

# Load model once globally
model = YOLO("yolov8n.pt")

# Constants
CONFIDENCE_THRESHOLD = 0.3
PERSON_CLASS_ID = 0  # COCO class: 0 = person

def detect_people(frame: np.ndarray) -> Tuple[List[List[float]], List[float]]:
    """
    Detect people in a frame using YOLOv8.

    Args:
        frame (np.ndarray): The input image/frame (BGR format)

    Returns:
        Tuple:
        - List of bounding boxes as [x1, y1, x2, y2]
        - List of corresponding confidence scores
    """
    try:
        results = model(frame, verbose=False)
        bounding_boxes = []
        confidences = []

        for result in results:
            if not hasattr(result, "boxes"):
                logger.warning("YOLO result missing 'boxes' attribute.")
                continue

            boxes = result.boxes

            if boxes is None or boxes.cls is None:
                logger.warning("Empty boxes or class info in YOLO result.")
                continue

            classes = boxes.cls.cpu().numpy()
            confs = boxes.conf.cpu().numpy()
            coords = boxes.xyxy.cpu().numpy()

            for cls_id, conf, box in zip(classes, confs, coords):
                if int(cls_id) == PERSON_CLASS_ID and conf >= CONFIDENCE_THRESHOLD:
                    x1, y1, x2, y2 = map(float, box)
                    bounding_boxes.append([x1, y1, x2, y2])
                    confidences.append(float(conf))

        logger.debug(f"Detected {len(bounding_boxes)} people in frame")
        return bounding_boxes, confidences

    except Exception as e:
        logger.error(f"[detect_people] Error during detection: {e}")
        return [], []
