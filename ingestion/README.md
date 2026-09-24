<p align="center">
  <a href="../README.md"><img src="../docs/assets/august-brand-banner.svg" alt="AUGUST brand banner" width="560" /></a>
</p>

# Public-data ingestion

AUGUST is public-data first.

Adapters must return explicit provenance and must not silently fall back to synthetic values.

Planned source families:

- INEGI
- Banco de México SIE
- FRED
- Inside Airbnb
- public/open geospatial datasets

If an adapter needs a token, configure it through environment variables. Never commit credentials.
