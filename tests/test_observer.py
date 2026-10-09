
import psutil

from app.core.models import ProcessSnapshot
from app.system import observer


class FakeProcess:
    def __init__(self, pid, name, denied=False):
        self.pid = pid
        self.info = {"pid": pid, "name": name}
        self.denied = denied
        self.cpu_calls = 0

    def cpu_percent(self, interval=None):
        self.cpu_calls += 1
        return 12.5

    def memory_percent(self):
        if self.denied:
            raise PermissionError("Access denied")
        return 3.0


def test_skips_process_when_memory_access_is_denied(monkeypatch):
    inaccessible = FakeProcess(100, "protected.exe", denied=True)
    accessible = FakeProcess(200, "worker.exe")

    monkeypatch.setattr(
        observer.psutil,
        "process_iter",
        lambda attrs: iter([inaccessible, accessible]),
    )
    monkeypatch.setattr(observer.time, "sleep", lambda _: None)

    result = observer.get_running_processes()

    assert len(result) == 1
    assert result[0] == ProcessSnapshot(
        pid=200,
        name="worker.exe",
        cpu_percent=12.5,
        memory_percent=3.0,
    )


def test_skips_process_that_disappears(monkeypatch):
    class DisappearingProcess(FakeProcess):
        def cpu_percent(self, interval=None):
            self.cpu_calls += 1
            if self.cpu_calls == 2:
                raise psutil.NoSuchProcess(self.pid)
            return 12.5

    disappearing = DisappearingProcess(300, "temporary.exe")
    accessible = FakeProcess(200, "worker.exe")

    monkeypatch.setattr(
        observer.psutil,
        "process_iter",
        lambda attrs: iter([disappearing, accessible]),
    )
    monkeypatch.setattr(observer.time, "sleep", lambda _: None)

    result = observer.get_running_processes()

    assert [process.pid for process in result] == [200]