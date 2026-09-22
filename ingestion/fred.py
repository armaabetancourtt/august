from __future__ import annotations

from io import StringIO

import httpx
import pandas as pd

from ingestion.base import SeriesAdapter


class FredCsvAdapter(SeriesAdapter):
    source_name = "FRED"

    def __init__(self, base_url: str = "https://fred.stlouisfed.org/graph/fredgraph.csv"):
        self.base_url = base_url

    def fetch(self, series_id: str, **kwargs) -> pd.DataFrame:
        response = httpx.get(
            self.base_url,
            params={"id": series_id},
            timeout=30,
            follow_redirects=True,
        )
        response.raise_for_status()

        frame = pd.read_csv(StringIO(response.text))
        frame.columns = ["date", "value"]
        frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
        frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
        frame = frame.dropna()
        frame["source"] = self.source_name
        frame["series_id"] = series_id
        frame["data_classification"] = "real_public"
        return frame
