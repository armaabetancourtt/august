# Security

AUGUST is an educational/open-source analytics platform, but it is designed with production boundaries in mind.

## Never commit

- API tokens for INEGI, Banxico or other providers;
- cloud credentials;
- database passwords;
- real customer transaction data;
- identity documents;
- proprietary property/financial datasets;
- production model artifacts containing sensitive training metadata.

Use environment variables or a secret manager.

## API

The foundation API is local/demo oriented. Before Internet deployment add authentication, RBAC, rate limiting, request-size limits, audit logs and HTTPS termination.

## Data

Public and synthetic data are separated by provenance. Sensitive financial/transaction data should be minimized, encrypted at rest and access-controlled.

## AI

Ask AUGUST must not receive unrestricted raw sensitive records. The language layer should consume approved structured results and documented knowledge.
