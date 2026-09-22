from __future__ import annotations

import os

import httpx
import pandas as pd

from ingestion.base import SeriesAdapter


class InegiIndicatorsAdapter(SeriesAdapter):
    source_name = "INEGI"
    base_url = (
        "https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml"
    )

    def __init__(self, token: str | None = None):
        self.token = token or os.getenv("INEGI_TOKEN")
        if not self.token:
            raise ValueError("INEGI_TOKEN is required")

    def fetch(
        self,
        series_id: str,
        *,
        geography: str = "00",
        language: str = "es",
        latest_only: bool = False,
        source: str = "BISE",
        **kwargs,
    ) -> pd.DataFrame:
        latest = str(latest_only).lower()
        url = (
            f"{self.base_url}/INDICATOR/{series_id}/{language}/{geography}/"
            f"{latest}/{source}/2.0/{self.token}"
        )

        response = httpx.get(url, params={"type": "json"}, timeout=30)
        response.raise_for_status()
        payload = response.json()

        observations = payload["Series"][0].get("OBSERVATIONS", [])
        frame = pd.DataFrame(observations)

        if frame.empty:
            return pd.DataFrame(
                columns=["date", "value", "source", "series_id", "data_classification"]
            )

        frame["date"] = pd.to_datetime(frame["TIME_PERIOD"], errors="coerce")
        frame["value"] = pd.to_numeric(frame["OBS_VALUE"], errors="coerce")
        frame = frame[["date", "value"]].dropna()
        frame["source"] = self.source_name
        frame["series_id"] = series_id
        frame["data_classification"] = "real_public"
        return frame
