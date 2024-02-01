"""
Common functions for bounding boxes.

This module mostly contains variants of bounding box non-maximum suppression (NMS).
"""
import numpy as np
import torch


def iou(box1, box2):
    """
    Calculate the intersection over union of a pair of boxes.

    The boxes are expected to be in [x_min, y_min, x_max, y_max] (pascal) format.

    Modified from Matlab code:
    https://www.computervisionblog.com/2011/08/blazing-fast-nmsm-from-exemplar-svm.html
    """
    # These are inner (overlapping) box dimensions, so we want
    # the maximum of the minimums and the minimum of the maximums
    x_min = max(box1[0], box2[0])
    y_min = max(box1[1], box2[1])
    x_max = min(box1[2], box2[2])
    y_max = min(box1[3], box2[3])

    inter = max(0, x_max - x_min) * max(0, y_max - y_min)
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    return inter / (area1 + area2 - inter)


def find_box_groups(boxes, threshold=0.3, scores=None):
    """
    Find overlapping sets of bounding boxes.

    Groups are by abs() where the positive value indicates the "best" box in the
    group and negative values indicate all other boxes in the group.
    """
    if len(boxes) == 0:
        return np.array([])

    if boxes.dtype.kind == "i":
        boxes = boxes.astype("float64")

    # Simplify access to box components
    x0, y0, x1, y1 = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]

    area = np.maximum(0.0, x1 - x0) * np.maximum(0.0, y1 - y0)

    idx = scores if scores else area
    idx = idx.argsort()

    overlapping = np.zeros_like(idx)
    group = 0
    while len(idx) > 0:
        group += 1

        # Pop the largest box
        curr = idx[-1]
        idx = idx[:-1]

        overlapping[curr] = group

        # Get interior (overlap) coordinates
        xx0 = np.maximum(x0[curr], x0[idx])
        yy0 = np.maximum(y0[curr], y0[idx])
        xx1 = np.minimum(x1[curr], x1[idx])
        yy1 = np.minimum(y1[curr], y1[idx])

        # Get the intersection over the union (IOU) with the current box
        iou_ = np.maximum(0.0, xx1 - xx0) * np.maximum(0.0, yy1 - yy0)
        iou_ /= area[idx] + area[curr] - iou_

        # Find IOUs larger than threshold & group them
        iou_ = np.where(iou_ >= threshold)[0]
        overlapping[idx[iou_]] = -group

        # Remove all indices in an IOU group
        idx = np.delete(idx, iou_)

    return overlapping


def overlapping_boxes(boxes, threshold=0.3, scores=None):
    """Group overlapping boxes."""
    groups = find_box_groups(boxes, threshold=threshold, scores=scores)
    return np.abs(groups)


def nms(boxes, threshold=0.3, scores=None):
    """Remove overlapping boxes via non-maximum suppression."""
    groups = find_box_groups(boxes, threshold=threshold, scores=scores)
    reduced = np.argwhere(groups > 0).squeeze(1)
    return boxes[reduced]


def small_box_overlap(boxes, threshold=0.5):
    """
    Get overlapping box groups using the intersection over area of the smaller box.

    This is analogous to the classic "non-maximum suppression" algorithm except:
        1. I return the groups of boxes rather than prune the overlapping ones.
        2. The measure is: intersection over the area of the smaller box.

    Also see: small_box_suppression().
    """
    if len(boxes) == 0:
        return np.array([])

    if boxes.dtype.kind == "i":
        boxes = boxes.astype("float64")

    # Simplify access to box components
    x0, y0, x1, y1 = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]

    area = np.maximum(0.0, x1 - x0) * np.maximum(0.0, y1 - y0) + 1e-8

    idx = area.argsort()

    overlapping = np.zeros_like(idx)
    group = 0
    while len(idx) > 0:
        group += 1

        # Pop the largest box
        curr = idx[-1]
        idx = idx[:-1]

        overlapping[curr] = group

        # Get interior (overlap) coordinates
        xx0 = np.maximum(x0[curr], x0[idx])
        yy0 = np.maximum(y0[curr], y0[idx])
        xx1 = np.minimum(x1[curr], x1[idx])
        yy1 = np.minimum(y1[curr], y1[idx])

        # Get the intersection as a fraction of the smaller box
        inter = np.maximum(0.0, xx1 - xx0) * np.maximum(0.0, yy1 - yy0)
        inter /= area[idx]

        # Find overlaps larger than threshold & group them
        inter = np.where(inter >= threshold)[0]
        overlapping[idx[inter]] = group

        # Remove all indices in an overlap group
        idx = np.delete(idx, inter)

    return overlapping


def small_box_suppression(boxes, threshold=0.9, eps=1e-8):
    """
    Remove overlapping small bounding boxes, analogous to non-maximum suppression.

    I can't just remove all small boxes because there are genuinely small labels.
    So I use the intersection of the boxes (over the area of the smaller box) to
    weed out small boxes that are covered by a bigger bounding box. Just using
    non-maximum suppression is not going to work because it uses the intersection
    over union (IoU) as a filtering metric and a tiny box contained in a larger box
    will not have an IoU over the threshold used for NMS. Using the intersection
    over the area of the smaller box gets around the issue.
    """
    if boxes.numel() == 0:
        return torch.empty((0, 4), dtype=torch.float32)

    # Simplify access to box components
    x0, y0, x1, y1 = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]

    area1 = torch.maximum(torch.tensor([0.0]), x1 - x0)
    area2 = torch.maximum(torch.tensor([0.0]), y1 - y0)
    area = area1 * area2 + eps

    idx = area.argsort()

    keep = torch.zeros(idx.numel(), dtype=torch.bool)

    while idx.numel() > 0:
        # Pop the largest box
        curr = idx[-1]
        idx = idx[:-1]

        keep[curr] = True

        # Get interior (overlap) coordinates
        xx0 = torch.maximum(x0[curr], x0[idx])
        yy0 = torch.maximum(y0[curr], y0[idx])
        xx1 = torch.minimum(x1[curr], x1[idx])
        yy1 = torch.minimum(y1[curr], y1[idx])

        # Get the intersection as a fraction of the smaller box
        inter1 = torch.maximum(torch.tensor([0.0]), xx1 - xx0)
        inter2 = torch.maximum(torch.tensor([0.0]), yy1 - yy0)
        inter = (inter1 * inter2) / area[idx]

        # Find overlaps larger than threshold & delete them
        inter = torch.where(inter >= threshold)[0]
        mask = torch.ones(idx.numel(), dtype=torch.bool)
        mask[inter] = False
        idx = idx[mask]

    return torch.where(keep)[0]
