from __future__ import annotations

import os

import httpx
import pandas as pd

from ingestion.base import SeriesAdapter


class BanxicoSieAdapter(SeriesAdapter):
    source_name = "Banco de México / SIE"
    base_url = "https://www.banxico.org.mx/SieAPIRest/service/v1"

    def __init__(self, token: str | None = None):
        self.token = token or os.getenv("BANXICO_TOKEN")
        if not self.token:
            raise ValueError("BANXICO_TOKEN is required")

    def fetch(
        self,
        series_id: str,
        *,
        start_date: str,
        end_date: str,
        **kwargs,
    ) -> pd.DataFrame:
        url = f"{self.base_url}/series/{series_id}/datos/{start_date}/{end_date}"
        response = httpx.get(
            url,
            headers={"Bmx-Token": self.token},
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()

        series = payload["bmx"]["series"][0]
        observations = series.get("datos", [])

        frame = pd.DataFrame(observations)
        if frame.empty:
            return pd.DataFrame(
                columns=["date", "value", "source", "series_id", "data_classification"]
            )

        frame["date"] = pd.to_datetime(frame["fecha"], dayfirst=True, errors="coerce")
        frame["value"] = pd.to_numeric(
            frame["dato"].astype(str).str.replace(",", "", regex=False),
            errors="coerce",
        )
        frame = frame[["date", "value"]].dropna()
        frame["source"] = self.source_name
        frame["series_id"] = series_id
        frame["data_classification"] = "real_public"
        return frame
