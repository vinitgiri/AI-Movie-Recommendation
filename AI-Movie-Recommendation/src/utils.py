"""
utils.py
--------
Shared helper utilities: logging setup, min-max normalization, and small
safe-IO helpers used across the pipeline.
"""

from __future__ import annotations

import logging
import sys
from typing import Iterable

import numpy as np


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger that prints to stdout with a clean format."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
                                       datefmt="%H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


def min_max_normalize(values: Iterable[float]) -> np.ndarray:
    """
    Min-max normalize a 1D array of scores into the [0, 1] range.

    If every value is identical (zero range), returns an array of 0.5 for
    every element so the score neither helps nor hurts the hybrid ranking.
    """
    arr = np.asarray(list(values), dtype=float)
    if arr.size == 0:
        return arr
    v_min, v_max = arr.min(), arr.max()
    if np.isclose(v_max, v_min):
        return np.full_like(arr, 0.5)
    return (arr - v_min) / (v_max - v_min)


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Divide, returning `default` instead of raising on a zero denominator."""
    if denominator == 0:
        return default
    return numerator / denominator
