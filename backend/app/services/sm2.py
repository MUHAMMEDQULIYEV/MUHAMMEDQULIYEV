"""
SM-2 Spaced Repetition Algorithm implementation.
"""

from datetime import datetime, timedelta, timezone
from dataclasses import dataclass


@dataclass
class SM2Result:
    ease_factor: float
    interval: int
    repetitions: int
    next_review: datetime


def calculate_sm2(
    quality: int,
    ease_factor: float,
    interval: int,
    repetitions: int,
) -> SM2Result:
    """
    Apply the SM-2 spaced repetition algorithm.

    :param quality: Review quality rating 0-5 (0=blackout, 5=perfect)
    :param ease_factor: Current ease factor (min 1.3)
    :param interval: Current interval in days
    :param repetitions: Number of successful repetitions so far
    :return: SM2Result with updated values
    """
    if quality < 0 or quality > 5:
        raise ValueError("Quality must be between 0 and 5")

    if quality >= 3:
        if repetitions == 0:
            new_interval = 1
        elif repetitions == 1:
            new_interval = 6
        else:
            new_interval = round(interval * ease_factor)
        new_repetitions = repetitions + 1
    else:
        new_repetitions = 0
        new_interval = 1

    new_ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    new_ease_factor = max(1.3, new_ease_factor)

    next_review = datetime.now(timezone.utc) + timedelta(days=new_interval)

    return SM2Result(
        ease_factor=round(new_ease_factor, 4),
        interval=new_interval,
        repetitions=new_repetitions,
        next_review=next_review,
    )
