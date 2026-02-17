from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

LossFn = Callable[[np.ndarray, np.ndarray, pd.DataFrame | None], np.ndarray]
StateFn = Callable[[np.ndarray, pd.DataFrame | None], np.ndarray]


def mse_loss(y_true, y_pred, context=None):
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    return (y_true - y_pred) ** 2


@dataclass
class LossStates:
    loss_fn: LossFn = mse_loss
    state_fn: StateFn | None = None
    state_params: dict[str, Any] | None = None
    _loss: np.ndarray | None = None
    _state: np.ndarray | None = None

    def fit(self, y_true, y_pred, context: pd.DataFrame | None = None):
        self._loss = self.loss_fn(y_true, y_pred, context)
        if self.state_fn is None:
            from .states import quantile_states

            params = self.state_params or {"q": [0.25, 0.5, 0.75]}
            self._state = quantile_states(self._loss, **params)
        else:
            self._state = self.state_fn(self._loss, context)
        return self

    def report(self) -> pd.DataFrame:
        from .decompose import decompose

        return decompose(self._loss, self._state)
