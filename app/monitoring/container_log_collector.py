
from datetime import datetime, timezone

import docker

from app.core.container_models import ContainerLogSnapshot


DEFAULT_TAIL_LINES = 50
MAX_LINE_LENGTH = 500


def collect_container_logs(
    container_name: str,
    tail: int = DEFAULT_TAIL_LINES,
    client=None,
) -> ContainerLogSnapshot:
    if tail < 1:
        raise ValueError("tail must be at least 1")

    owns_client = client is None
    client = client or docker.from_env()

    try:
        container = client.containers.get(container_name)
        raw_logs = container.logs(tail=tail, timestamps=True)

        if isinstance(raw_logs, bytes):
            decoded_logs = raw_logs.decode("utf-8", errors="replace")
        else:
            decoded_logs = raw_logs

        all_lines = decoded_logs.splitlines()
        selected_lines = all_lines[-tail:]
        truncated = len(all_lines) > tail

        lines = []
        for line in selected_lines:
            if len(line) > MAX_LINE_LENGTH:
                line = line[:MAX_LINE_LENGTH]
                truncated = True
            lines.append(line)

        attrs = container.attrs
        labels = attrs.get("Config", {}).get("Labels") or {}
        service = labels.get(
            "com.docker.compose.service",
            container_name,
        )

        return ContainerLogSnapshot(
            container_name=container_name,
            service=service,
            lines=lines,
            truncated=truncated,
            observed_at=datetime.now(timezone.utc),
        )
    finally:
        if owns_client:
            client.close()
