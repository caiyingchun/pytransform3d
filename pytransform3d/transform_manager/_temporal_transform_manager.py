import abc
from typing import Any

import numpy as np

from ._transform_graph_base import TransformGraphBase
from ..transformations import (check_transform, invert_transform, concat)


class TimeTransform(abc.ABC):
    """Base class passed to TemporalTransformManager.add_transform() to deal with time.
    """
    
    @abc.abstractmethod
    def as_matrix(self, time) -> np.ndarray:
        ...

    @abc.abstractmethod
    def check_transforms(self) -> "TimeTransform":
        """Checks all transformation in a sequence. If checks are successful,
        returns the original object"""
        ...


class StaticTransform(TimeTransform):
    """Transformation, which does not change over time."""

    def __init__(self, A2B):
        """Initialize a StaticTransform with a transformation matrix.

        Args:
            A2B (matrix): 4x4 transformation 
        """
        self._A2B = A2B

    def as_matrix(self, time):
        return self._A2B
    
    def check_transforms(self):
        self._A2B = check_transform(self._A2B)
        return self


class TemporalTransformManager(TransformGraphBase):

    def __init__(self, strict_check=True, check=True):
        self._transforms = {}
        self._current_time = 0.0
        super(TemporalTransformManager, self).__init__(strict_check, check)
    
    @property
    def current_time(self):
        return self._current_time

    def set_time(self, time):
        self._current_time = time
    
    @property
    def transforms(self):
        """Rigid transformations between nodes."""
        return {tf_direction: transform.as_matrix(self.current_time) for
                tf_direction, transform in self._transforms.items()}
    
    def get_transform_in_time(self, from_frame, to_frame, time):
        previous_time = self._current_time
        self.set_time(time)

        A2B = self.get_transform(from_frame, to_frame)

        # revert internal state
        self.set_time(previous_time)
        return A2B

    def _transform_available(self, key):
        return key in self._transforms

    def _set_transform(self, key, A2B):
        if not isinstance(A2B, TimeTransform):
            A2B = StaticTransform(A2B)
        self._transforms[key] = A2B

    def _get_transform(self, key):
        return self.transforms[key]

    def _del_transform(self, key):
        del self._transforms[key]

    def _check_transform(self, A2B):
        """Check validity of rigid transformation."""
        return A2B.check_transforms()
