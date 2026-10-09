import json
import os
from urllib.parse import urlencode
from urllib.request import urlopen


class PrometheusClient:
    def __init__(
        self,
        base_url: str | None = None,
        timeout: float = 5.0,
    ) -> None:
        self.base_url = (
            base_url or os.getenv(
                "PROMETHEUS_URL",
                "http://localhost:9090",
            )
        ).rstrip("/")
        self.timeout = timeout

    def query(self, expression: str) -> list[dict]:
        params = urlencode({"query": expression})
        url = f"{self.base_url}/api/v1/query?{params}"

        with urlopen(url, timeout=self.timeout) as response:
            payload = json.load(response)

        if payload.get("status") != "success":
            raise RuntimeError(
                f"Prometheus query failed: {payload}"
            )

        return payload["data"]["result"]