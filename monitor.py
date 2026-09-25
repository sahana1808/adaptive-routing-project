import subprocess
import re
import time
import sys


TARGET = "10.0.4.10"


if len(sys.argv) != 2:
    print("Usage: python3 monitor.py <h1_pid>")
    sys.exit(1)


H1_PID = sys.argv[1]


def measure_latency():
    result = subprocess.run(
        [
            "sudo",
            "mnexec",
            "-a",
            H1_PID,
            "ping",
            "-c",
            "3",
            "-W",
            "1",
            TARGET
        ],
        capture_output=True,
        text=True
    )

    match = re.search(
        r"rtt min/avg/max/mdev = [0-9.]+/([0-9.]+)/",
        result.stdout
    )

    if match:
        return float(match.group(1))

    return None


while True:
    latency = measure_latency()

    if latency is not None:
        print(f"Current latency: {latency:.2f} ms")

        if latency > 50:
            print("HIGH LATENCY DETECTED")
            print("Recommended action: Switch to alternate route")
        else:
            print("Network condition: NORMAL")

    else:
        print("Unable to measure latency")

    print("-" * 40)
    time.sleep(5)
