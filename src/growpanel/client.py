"""Ergonomic wrapper around the generated openapi-python-client output.

The generator emits one module per OpenAPI tag under `_generated/api/`, each containing
a `sync()` / `asyncio()` pair per operation. This file groups them under a namespaced
`GrowPanel` class so consumer code reads cleanly:

    from growpanel import GrowPanel
    gp = GrowPanel(api_key="gp_...")
    summary = gp.reports.summary()
    customers = gp.customers.list(limit=50)
    gp.webhooks.create(url="https://hooks.zapier.com/...", event_type="movement.churn")

For everything not exposed as a curated method, use `gp.raw` — a reference to the
generated `_generated.api` module tree.
"""

from typing import Any, Optional

# The generated modules don\'t exist until `openapi-python-client generate` has run;
# imports are deferred to runtime so `import growpanel` doesn\'t crash in source-only
# install scenarios (e.g. CI test stage that runs the generator after dependency install).


class _Namespace:
    """Lazy holder for a generated tag\'s operations. Methods are bound at first access."""

    def __init__(self, client: "GrowPanel", mapping: dict) -> None:
        self._client = client
        self._mapping = mapping

    def __getattr__(self, name: str) -> Any:
        if name not in self._mapping:
            raise AttributeError(f"No operation '{name}' on this namespace.")
        func = self._mapping[name]
        # Generated functions take `client=<AuthenticatedClient>` as a keyword arg.
        def bound(*args: Any, **kwargs: Any) -> Any:
            kwargs.setdefault("client", self._client._inner)
            return func.sync(*args, **kwargs)
        return bound


class GrowPanel:
    """Top-level client. Pass `api_key`; everything else is optional.

    Args:
        api_key: Issued by /account/api-keys in the GrowPanel app.
        base_url: Override the API base URL. Defaults to `https://api.growpanel.io`.
        timeout: Per-request timeout in seconds. Defaults to 30.
    """

    DEFAULT_BASE_URL = "https://api.growpanel.io"

    def __init__(self, api_key: str, base_url: Optional[str] = None, timeout: float = 30.0) -> None:
        try:
            from ._generated.client import AuthenticatedClient
        except ImportError as exc:
            raise ImportError(
                "Generated client not found. Run `openapi-python-client generate "
                "--url https://api-dev.growpanel.io/openapi.json --config "
                "openapi-python-client.config.yaml --overwrite` to produce src/growpanel/_generated/."
            ) from exc

        self._inner = AuthenticatedClient(
            base_url=(base_url or self.DEFAULT_BASE_URL).rstrip("/"),
            token=api_key,
            timeout=timeout,
        )

        # Wire each namespace by importing the generated tag modules. Naming is
        # `_generated.api.<tag_snake>.<operation_id>` where tag_snake is the tag name
        # lower-cased with non-alphanumerics replaced by underscores.
        from ._generated import api  # noqa: F401 — triggers package load

        # Analytics surfaces (read-only top-level metrics & customer views).
        self.reports = _Namespace(self, _resolve_tag_ops(api, "reports"))
        self.customers = _Namespace(self, _resolve_tag_ops(api, "customers"))
        self.plans = _Namespace(self, _resolve_tag_ops(api, "plans"))
        # Account / integrations.
        self.profile = _Namespace(self, _resolve_tag_ops(api, "profile"))
        self.notifications = _Namespace(self, _resolve_tag_ops(api, "settings"))
        self.webhooks = _Namespace(self, _resolve_tag_ops(api, "webhooks"))
        # Data ingestion API (CRUD over the raw billing-source data). Grouped under
        # `gp.data.*` to keep the import surface separate from analytics.
        self.data = _DataNamespace(self, api)
        # Escape hatch: the raw generated module tree.
        self.raw = api

    def close(self) -> None:
        """Close underlying httpx client."""
        self._inner.get_httpx_client().close()

    def __enter__(self) -> "GrowPanel":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


def _resolve_tag_ops(api_pkg: Any, tag_prefix: str) -> dict:
    """Find all operations under `_generated.api.<tag_prefix>...` and return a flat mapping."""
    import importlib
    import pkgutil

    ops: dict = {}
    for module_info in pkgutil.walk_packages(api_pkg.__path__, prefix=f"{api_pkg.__name__}."):
        if not module_info.name.split(".")[-2].startswith(tag_prefix):
            continue
        module = importlib.import_module(module_info.name)
        op_name = module_info.name.split(".")[-1]
        ops[op_name] = module
    return ops


class _DataNamespace:
    """Holder for the `gp.data.*` ingestion namespaces. Each sub-namespace is loaded
    lazily from the generated tag modules so a missing tag (e.g. before first
    `openapi-python-client generate` run) raises an informative error rather than
    crashing module load."""

    def __init__(self, client: "GrowPanel", api_pkg: Any) -> None:
        self.customers   = _Namespace(client, _resolve_tag_ops(api_pkg, "data_customers"))
        self.plans       = _Namespace(client, _resolve_tag_ops(api_pkg, "data_plans"))
        self.plan_groups = _Namespace(client, _resolve_tag_ops(api_pkg, "data_plan_groups"))
        self.segments    = _Namespace(client, _resolve_tag_ops(api_pkg, "data_segments"))
        self.invoices    = _Namespace(client, _resolve_tag_ops(api_pkg, "data_invoices"))
        self.sources     = _Namespace(client, _resolve_tag_ops(api_pkg, "data_data_sources"))
