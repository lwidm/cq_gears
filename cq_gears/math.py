import numpy as np
from typing import Literal


def ensure_has_zero(arr: np.ndarray) -> np.ndarray:
    if 0.0 in arr:
        return arr
    non_neg_indices: np.ndarray = np.where(arr >= 0)[0]
    if len(non_neg_indices) == 0:
        arr = np.append(arr, 0.0)
        return arr
    else:
        idx: int = non_neg_indices[0]
        return np.insert(arr, idx, 0.0)


def tangent_vectors(points: np.ndarray) -> np.ndarray:
    dx: np.ndarray = np.gradient(points[0])
    dy: np.ndarray = np.gradient(points[1])

    tangents: np.ndarray = np.vstack([dx, dy])
    norms: np.ndarray = np.linalg.norm(tangents, axis=0)
    tangents /= norms

    return tangents


def tangent_angles(points: np.ndarray) -> np.ndarray:
    tangents: np.ndarray = tangent_vectors(points)
    angles: np.ndarray = np.arctan2(tangents[1], tangents[0])
    return angles


def involute(
    r: float, phi_r: np.ndarray, direction: Literal["clockwise", "counterclockwise"]
) -> np.ndarray:
    x = r * np.cos(phi_r) + r * phi_r * np.sin(phi_r)
    y = r * np.sin(phi_r) - r * phi_r * np.cos(phi_r)
    if direction == "clockwise":
        y = -y
    return np.vstack([x, y])  # shape (2, N)


def rotate(points: np.ndarray, rotation: float) -> np.ndarray:
    R: np.ndarray = np.array(
        [[np.cos(rotation), -np.sin(rotation)], [np.sin(rotation), np.cos(rotation)]]
    )
    rotated: np.ndarray = R @ points
    return rotated


def translate(points: np.ndarray, translation: tuple[float, float]) -> np.ndarray:
    dx, dy = translation
    translated: np.ndarray = points + np.array([[dx], [dy]])

    return translated


def hypotrochoid(
    rp: float,
    rf: float,
    alpha_t_r: float,
    phi_r: np.ndarray,
    flank: Literal["left", "right"],
) -> np.ndarray:

    points_inv: np.ndarray
    if flank == "right":
        points_inv = involute(rp, phi_r, "clockwise")
    else:
        points_inv = involute(rp, phi_r, "counterclockwise")

    vx: float = rf - rp
    vy: float = rf * np.tan(alpha_t_r)
    v: np.ndarray = np.array([[vx], [vy]])

    mask_nonneg: np.ndarray = phi_r >= 0
    mask_neg: np.ndarray = phi_r < 0

    theta: np.ndarray = np.zeros(len(phi_r))

    if np.any(mask_nonneg):
        points_inv_nonneg: np.ndarray = points_inv[:, mask_nonneg]
        theta[mask_nonneg] = tangent_angles(points_inv_nonneg)

    if np.any(mask_neg):
        points_inv_neg: np.ndarray = points_inv[:, mask_neg]
        theta[mask_neg] = tangent_angles(points_inv_neg) - np.pi

    theta_0: float = theta[np.argmax(phi_r == 0.0)]
    points_hypo: np.ndarray = np.zeros_like(points_inv)

    for i in np.arange(len(points_inv[0, :])):
        point: tuple[float, float] = (points_inv[0, i], points_inv[1, i])
        point_hypo: np.ndarray = translate(
            rotate(v, theta[i] - theta_0), (point[0], point[1])
        )
        points_hypo[0, i] = point_hypo[0, 0]
        points_hypo[1, i] = point_hypo[1, 0]

    # k=-1
    # v1  = rotate(v, theta[k] - theta_0)
    # v2  = translate(v1, (points_inv[0, k], points_inv[1, k]))
    # vq = np.squeeze(v1)
    # arrow = np.array([[points_inv[0, k], vq[0]],[points_inv[1,k], vq[1]]])
    # arrow = np.array([[0.0, vq[0]],[0.0, vq[1]]])
    return points_hypo
