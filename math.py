import numpy as np

def involute(r: float, phi_r: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    x: np.ndarray =  r*np.cos(phi_r) + r*phi_r*np.sin(phi_r)
    y: np.ndarray = r*np.sin(phi_r) - r*phi_r*np.cos(phi_r)
    return x, y

