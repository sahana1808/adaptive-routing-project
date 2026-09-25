import subprocess
import re
import time
import sys


if len(sys.argv) != 3:
    print("Usage: python3 adaptive_router.py <h1_pid> <r1_pid>")
    sys.exit(1)

H1_PID = sys.argv[1]
R1_PID = sys.argv[2]
TARGET = "10.0.4.10"

PRIMARY_NEXT_HOP = "10.0.3.2"
ALTERNATE_NEXT_HOP = "10.0.2.2"

THRESHOLD = 50


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


def change_route(next_hop):
    subprocess.run(
        [
            "sudo",
            "mnexec",
            "-a",
            R1_PID,
            "ip",
            "route",
            "replace",
            "10.0.4.0/24",
            "via",
            next_hop
        ],
        check=True
    )


current_route = "primary"

print("Adaptive Routing Controller Started")
print("-----------------------------------")

while True:

    latency = measure_latency()

    if latency is None:
        print("Unable to measure latency")
        time.sleep(5)
        continue

    print(f"Measured latency: {latency:.2f} ms")

    if latency > THRESHOLD and current_route != "alternate":

        print("HIGH LATENCY DETECTED")
        print("Switching to alternate route...")

        change_route(ALTERNATE_NEXT_HOP)

        current_route = "alternate"

        print("Route changed:")
        print("h1 -> r1 -> r2 -> r3 -> h2")

    elif latency <= THRESHOLD and current_route != "primary":

        print("Network recovered")
        print("Switching back to primary route...")

        change_route(PRIMARY_NEXT_HOP)

        current_route = "primary"

        print("Route changed:")
        print("h1 -> r1 -> r3 -> h2")

    else:

        print(f"Route status: {current_route}")

    print("-----------------------------------")

    time.sleep(5)
