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


def half_base_tooth_angle(m: float, dp: float, db: float) -> float:
    dp_db: float = dp / db
    theta_dp: float = np.sqrt(dp_db**2 - 1)
    return (m * np.pi) / (4 * db) + 0.5 * theta_dp - 0.5 * np.arctan(theta_dp)


def involute(r: float, phi_r: np.ndarray) -> np.ndarray:
    x: np.ndarray = r * np.cos(phi_r) + r * phi_r * np.sin(phi_r)
    y: np.ndarray = r * np.sin(phi_r) - r * phi_r * np.cos(phi_r)
    return np.vstack([x, y])  # shape (2, N)


def involute_positioned(
    m: float, dp: float, db: float, phi_r: np.ndarray, flank: Literal["right", "left"]
) -> np.ndarray:
    gamma: float = half_base_tooth_angle(m, dp, db)
    cos_phi: np.ndarray = np.cos(phi_r)
    sin_phi: np.ndarray = np.sin(phi_r)
    cos_gamma: float = np.cos(gamma)
    sin_gamma: float = np.sin(gamma)
    if flank == "left":
        sin_gamma = -sin_gamma
    x: np.ndarray = (
        cos_gamma * cos_phi
        + cos_gamma * phi_r * sin_phi
        + sin_gamma * sin_phi
        - sin_gamma * phi_r * cos_phi
    )
    y: np.ndarray = (
        -sin_gamma * cos_phi
        - sin_gamma * phi_r * sin_phi
        + cos_gamma * sin_phi
        - cos_gamma * phi_r * cos_phi
    )
    return db / 2 * np.vstack([x, y])  # shape (2, N)


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
    dp: float,
    df: float,
    alpha_t_r: float,
    phi_r: np.ndarray,
    flank: Literal["left", "right"],
) -> np.ndarray:
    a: float = df
    b: float
    if flank == "right":
        b = +df * np.tan(alpha_t_r)
    else:
        b = -df * np.tan(alpha_t_r)
    A: np.ndarray = np.array([[a], [b]])
    B: np.ndarray = np.array([[-b], [a]])
    t: np.ndarray = np.vstack([np.sin(phi_r), -np.cos(phi_r)])

    return 1 / 2 * (A * np.cos(phi_r) + B * np.sin(phi_r) + dp * phi_r * t)


def hypotrochoid_positioned(
    m: float,
    df: float,
    dp: float,
    db: float,
    alpha_t_r: float,
    phi: np.ndarray,
    flank: Literal["right", "left"],
) -> np.ndarray:

    a: float = df
    b: float = df*np.tan(alpha_t_r)

    gamma: float = half_base_tooth_angle(m, dp, db)
    angle: float = gamma + alpha_t_r

    cos_phi: np.ndarray = np.cos(phi)
    sin_phi: np.ndarray = np.sin(phi)
    cos_angle: float = np.cos(angle)
    sin_angle: float = np.sin(angle)

    if flank == "left":
        sin_angle = -sin_angle
        b = -b

    x: np.ndarray = (
        a * cos_angle * cos_phi
        - b * cos_angle * sin_phi
        + dp * cos_angle * phi * sin_phi
        + b * sin_angle * cos_phi
        + a * sin_angle * sin_phi
        - dp * sin_angle * phi * cos_phi
    )

    y: np.ndarray = (
        -a * sin_angle * cos_phi
        + b * sin_angle * sin_phi
        - dp * sin_angle * phi * sin_phi
        + b * cos_angle * cos_phi
        + a * cos_angle * sin_phi
        - dp * cos_angle * phi * cos_phi
    )

    return 0.5 * np.vstack([x, y])  # shape (2, N)


def hypotrochoid_intuitive(
    rp: float,
    rf: float,
    alpha_t_r: float,
    phi_r: np.ndarray,
) -> np.ndarray:

    points_inv: np.ndarray = involute(rp, phi_r)

    vx: float = rf - rp
    vy: float = rf * np.tan(alpha_t_r)
    v: np.ndarray = np.array([[vx], [vy]])

    mask_nonneg: np.ndarray = phi_r > 0
    mask_neg: np.ndarray = phi_r <= 0

    theta: np.ndarray = np.zeros(len(phi_r))

    if np.any(mask_nonneg):
        points_inv_nonneg: np.ndarray = points_inv[:, mask_nonneg]
        theta[mask_nonneg] = tangent_angles(points_inv_nonneg) - np.pi

    if np.any(mask_neg):
        points_inv_neg: np.ndarray = points_inv[:, mask_neg]
        theta[mask_neg] = tangent_angles(points_inv_neg)

    points_hypo: np.ndarray = np.zeros_like(points_inv)
    for i in np.arange(len(points_inv[0, :])):
        point: tuple[float, float] = (points_inv[0, i], points_inv[1, i])
        point_hypo: np.ndarray = translate(rotate(v, phi_r[i]), (point[0], point[1]))
        points_hypo[0, i] = point_hypo[0, 0]
        points_hypo[1, i] = point_hypo[1, 0]

    return points_hypo
