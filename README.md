# growpanel (Python)

Official Python SDK for the [GrowPanel](https://growpanel.io) subscription analytics REST API.

```bash
pip install growpanel
```

```python
from growpanel import GrowPanel

gp = GrowPanel(api_key="gp_...")

summary = gp.reports.get_summary()
print(summary.summary.mrr_current)

mrr = gp.reports.get_mrr(date="20260101-20260531", interval="month")
for period in mrr.result:
    print(period.date, period.total_mrr)
```

## Auth

Issue a key in **app.growpanel.io → Account → API keys**. Pass it as `api_key=` when constructing the client; it\'s sent as `Authorization: Bearer <key>` on every request.

## Surfaces

The SDK mirrors the [interactive docs](https://api.growpanel.io/docs):

**Analytics (read-only):**
- `gp.reports.*` — MRR, leads, cohorts, cashflow, retention, churn
- `gp.customers.*` — list + detail (analytics view)
- `gp.plans.*` — list plans

**Account & integrations:**
- `gp.profile.*`, `gp.notifications.*`, `gp.webhooks.*`

**Data ingestion (CRUD on a data source):**
- `gp.data.customers.*` — create / read / update / delete raw customer rows
- `gp.data.plans.*` — raw plan CRUD
- `gp.data.plan_groups.*` — group plans together
- `gp.data.segments.*` — saved filter combinations
- `gp.data.invoices.*` — raw invoice CRUD
- `gp.data.sources.*` — connected billing systems

`gp.data.*` mirrors the `/data/*` URL prefix and keeps the ingestion API visually separate from the analytics surfaces.

For anything not exposed as a named method, `gp.raw` is the generated module tree — every endpoint in the OpenAPI spec is reachable from there.

## Generating from the live spec

```bash
pip install -e ".[dev]"
openapi-python-client generate \
    --url https://api-dev.growpanel.io/openapi.json \
    --config openapi-python-client.config.yaml \
    --overwrite
```

Output lands in `src/growpanel/_generated/`. In CI, this runs automatically on every API change.

## Errors

```python
from growpanel import GrowPanel, GrowPanelError

gp = GrowPanel(api_key="...")
try:
    gp.customers.detail(id="cus_doesnotexist")
except GrowPanelError as err:
    if err.status == 404:
        ...  # handle not-found
    raise
```

## Interactive docs

The full reference (with try-it-out) lives at [api.growpanel.io/docs](https://api.growpanel.io/docs).
