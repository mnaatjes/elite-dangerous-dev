from src.core import SystemMonitor, DataMeasurer
import psutil
import sys
def test_core_memory():
    print(SystemMonitor().get_full_diagnostic())
    print(SystemMonitor().is_performant())
    print(SystemMonitor().is_safe_for_atomic(102400000))

    print(f"Sys: {sys.getsizeof({})}")

    print(f"DM: {DataMeasurer().estimate_bytes({})}")