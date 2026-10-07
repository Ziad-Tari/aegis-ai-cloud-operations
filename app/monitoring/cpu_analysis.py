from app.core.models import CpuSample


def calculate_average_cpu(history: list[CpuSample]) -> float:
    if not history:
        return 0.0

    return sum(
        sample.cpu_percent for sample in history
    ) / len(history)