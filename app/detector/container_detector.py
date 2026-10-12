
from app.core.container_models import (
    ContainerIncident,
    ContainerSnapshot,
)


class ContainerIncidentDetector:
    def __init__(
        self,
        cpu_threshold_cores: float = 0.5,
        memory_threshold_mib: float = 100.0,
        required_samples: int = 3,
    ) -> None:
        if cpu_threshold_cores < 0:
            raise ValueError("CPU threshold cannot be negative")
        if memory_threshold_mib < 0:
            raise ValueError("Memory threshold cannot be negative")
        if required_samples < 1:
            raise ValueError("required_samples must be at least 1")

        self.cpu_threshold_cores = cpu_threshold_cores
        self.memory_threshold_mib = memory_threshold_mib
        self.required_samples = required_samples

        self._counts: dict[tuple, int] = {}
        self._active: set[tuple] = set()

    def _evaluate(
        self,
        snapshot: ContainerSnapshot,
        metric_type: str,
        value: float | None,
        threshold: float,
        unit: str,
    ) -> ContainerIncident | None:
        key = (
            snapshot.container_name,
            snapshot.service,
            metric_type,
        )

        # Missing data is unknown, not healthy or zero.
        if value is None:
            self._counts[key] = 0
            return None

        # A normal reading resets the streak and resolves
        # the active detector state for this metric.
        if value <= threshold:
            self._counts[key] = 0
            self._active.discard(key)
            return None

        self._counts[key] = self._counts.get(key, 0) + 1

        # Emit once per abnormal period, not on every sample.
        if (
            self._counts[key] < self.required_samples
            or key in self._active
        ):
            return None

        self._active.add(key)

        incident_type = (
            "HIGH_CONTAINER_CPU"
            if metric_type == "cpu"
            else "HIGH_CONTAINER_MEMORY"
        )

        return ContainerIncident(
            incident_type=incident_type,
            container_name=snapshot.container_name,
            service=snapshot.service,
            observed_value=value,
            threshold=threshold,
            unit=unit,
            message=(
                f"{snapshot.container_name} exceeded the "
                f"{metric_type} threshold for "
                f"{self.required_samples} consecutive samples."
            ),
            observed_at=snapshot.observed_at,
        )

    def detect(
        self,
        snapshots: list[ContainerSnapshot],
    ) -> list[ContainerIncident]:
        incidents = []

        for snapshot in snapshots:
            cpu_incident = self._evaluate(
                snapshot=snapshot,
                metric_type="cpu",
                value=snapshot.cpu_cores,
                threshold=self.cpu_threshold_cores,
                unit="cores",
            )

            if cpu_incident is not None:
                incidents.append(cpu_incident)

            memory_incident = self._evaluate(
                snapshot=snapshot,
                metric_type="memory",
                value=snapshot.memory_mib,
                threshold=self.memory_threshold_mib,
                unit="MiB",
            )

            if memory_incident is not None:
                incidents.append(memory_incident)

        return incidents
