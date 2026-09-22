from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class SeriesAdapter(ABC):
    source_name: str

    @abstractmethod
    def fetch(self, series_id: str, **kwargs) -> pd.DataFrame:
        """Return a dataframe containing at least date, value and source."""
        raise NotImplementedError
